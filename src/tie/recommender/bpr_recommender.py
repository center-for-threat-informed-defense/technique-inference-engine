import math

import keras
import numpy as np
import tensorflow as tf

from tie.constants import PredictionMethod
from tie.utils import calculate_predicted_matrix

from .recommender import Recommender


class BPRRecommender(Recommender):
    """A Bayesian Personalized Ranking recommender.

    Based on BPR: Bayesian Personalized Ranking from Implicit Feedback.
    https://arxiv.org/ftp/arxiv/papers/1205/1205.2618.pdf
    """

    # Abstraction function:
    # 	AF(U, V) = a Bayesian Personalized Ranking recommender model
    #       on entity embeddings U and item embeddings V
    # Rep invariant:
    #   - U.shape[1] == V.shape[1]
    #   - U and V are 2D
    #   - U.shape[0] > 0
    #   - U.shape[1] > 0
    #   - V.shape[0] > 0
    #   - V.shape[1] > 0
    # Safety from rep exposure:

    def __init__(self, m: int, n: int, k: int):
        """Initializes a BPRRecommender object.

        Args:
            m: number of entity embeddings.
            n: number of item embeddings.
            k: embedding dimension.
        """
        self._U = np.zeros((m, k))
        self._V = np.zeros((n, k))
        self._reset_embeddings()

        self._checkrep()

    def _reset_embeddings(self):
        """Resets the embeddings to a standard normal."""
        init_stddev = 1

        new_U = np.random.normal(loc=0, scale=init_stddev, size=self._U.shape)
        new_V = np.random.normal(loc=0, scale=init_stddev, size=self._V.shape)

        self._U = new_U
        self._V = new_V

    def _checkrep(self):
        """Asserts the rep invariant."""
        #   - U.shape[1] == V.shape[1]
        assert self._U.shape[1] == self._V.shape[1]
        #   - U and V are 2D
        assert len(self._U.shape) == 2
        assert len(self._V.shape) == 2
        #   - U.shape[0] > 0
        assert self._U.shape[0] > 0
        #   - U.shape[1] > 0
        assert self._U.shape[1] > 0
        #   - V.shape[0] > 0
        assert self._V.shape[0] > 0
        #   - V.shape[1] > 0
        assert self._V.shape[1] > 0

    @property
    def U(self) -> np.ndarray:
        return np.copy(self._U)

    @property
    def V(self) -> np.ndarray:
        return np.copy(self._V)

    def _sample_dataset(
        self,
        data: np.ndarray,
        num_samples: int,
    ) -> tuple[int, int, int]:
        """Samples the dataset according to the bootstrapped sampling for BPR.

        Sampling is performed uniformly over all triples of the form (u, i, j),
        where u is a user, i is an item for which there is an observation for that user,
        and j is an item for which there is no observation for that user.

        Args:
            data: An mxn matrix of observations.
            num_samples: Number of samples to draw. Requires num_samples > 0.

        Returns:
            A tuple of the form (u, i, j) where u is an array of user indices,
            i is an array of item indices with an observation for that user,
            and j is an array of item indices with no observation for that user.
        """
        assert num_samples > 0

        m, n = data.shape

        sample_user_probability = self._calculate_sample_user_probability(data)

        # repeat for each of n items
        num_items_per_user = np.sum(data, axis=1).astype(float)
        assert not np.any(np.isnan(num_items_per_user))
        num_items_per_user[num_items_per_user == 0.0] = np.nan
        assert num_items_per_user.shape == (m,)  # m users
        sample_item_probability = np.nan_to_num(
            data / np.expand_dims(num_items_per_user, axis=1)
        )

        joint_user_item_probability = (
            np.expand_dims(sample_user_probability, axis=1) * sample_item_probability
        )
        assert joint_user_item_probability.shape == (m, n)

        flattened_probability = joint_user_item_probability.flatten("C")
        u_i = np.random.choice(
            np.arange(m * n), size=(num_samples,), p=flattened_probability
        )

        all_u = u_i // n
        all_i = u_i % n
        assert (all_i < 611).all()

        non_observations = 1 - data

        unique_users, counts = np.unique(all_u, return_counts=True)
        value_to_count = dict(zip(unique_users, counts))

        u_to_j = {}

        # for each u
        for u, count in value_to_count.items():
            # get
            potential_j = non_observations[u, :]

            all_j_for_user = np.random.choice(
                n, size=count, replace=True, p=potential_j / np.sum(potential_j)
            )

            u_to_j[u] = all_j_for_user.tolist()

        all_j = []

        for u in all_u:
            j = u_to_j[u].pop()
            all_j.append(j)

        assert len(all_u) == len(all_j) == len(all_i)

        return all_u, all_i, all_j

    def _calculate_sample_user_probability(self, data: np.ndarray) -> np.array:
        """Gets the sample probability for each user.

        Args:
            data: An mxn matrix of observations.

        Returns:
            A length m array containing the probability of sampling each entity.
        """
        m, n = data.shape
        data = np.nan_to_num(data)

        observations_per_user = np.sum(data, axis=1)
        assert observations_per_user.shape == (m,)

        samples_per_user = observations_per_user * (n - observations_per_user)
        sample_user_probability = samples_per_user / np.sum(samples_per_user)
        assert sample_user_probability.shape == (m,)

        return sample_user_probability

    def _predict_for_single_entry(self, u, i) -> float:
        """Predicts the value for a single user-item pair."""
        return np.dot(self._U[u, :], self._V[i, :])

    def fit(
        self,
        data: tf.SparseTensor,
        learning_rate: float,
        epochs: int,
        regularization_coefficient: float,
    ):
        """Fits the model to data.

        Args:
            data: An mxn tensor of training data
            learning_rate: Learning rate for each gradient step performed on a single
                entity-item sample.
            epochs: Number of training epochs, where each the model is trained on the
                cardinality of the dataset in each epoch.
            regularization_coefficient: Coefficient on the L2 regularization term.
            method: The prediction method to use.

        Mutates:
            The recommender to the new trained state.
        """
        # start by resetting embeddings for proper fit
        self._reset_embeddings()

        data = tf.sparse.reorder(data)
        data = tf.sparse.to_dense(data)
        data = data.numpy()

        num_iterations = epochs * data.shape[0] * data.shape[1]

        all_u, all_i, all_j = self._sample_dataset(data, num_samples=num_iterations)

        # initialize theta - done - init
        # repeat
        for iteration_count in range(num_iterations):
            # draw u, i, j from D_s
            u = all_u[iteration_count]
            i = all_i[iteration_count]
            j = all_j[iteration_count]

            assert data[u, i] == 1
            assert data[u, j] == 0

            # theta = theta + alpha * (e^(-x) sigma(x) d/dtheta x + lambda theta)
            x_ui = self._predict_for_single_entry(u, i)
            x_uj = self._predict_for_single_entry(u, j)
            x_uij = x_ui - x_uj

            sigmoid_derivative = (math.e ** (-x_uij)) / (1 + math.e ** (-x_uij))

            d_w = self._V[i, :] - self._V[j, :]
            # derivative wrt h_i
            d_hi = self._U[u, :]
            # derivative wrt h_j
            d_hj = -self._U[u, :]

            self._U[u, :] += learning_rate * (
                sigmoid_derivative * d_w - (regularization_coefficient * self._U[u, :])
            )
            self._V[i, :] += learning_rate * (
                sigmoid_derivative * d_hi - (regularization_coefficient * self._V[i, :])
            )
            self._V[j, :] += learning_rate * (
                sigmoid_derivative * d_hj - (regularization_coefficient * self._V[j, :])
            )

        # return theta
        # set in rep

    def evaluate(
        self,
        test_data: tf.SparseTensor,
        method: PredictionMethod = PredictionMethod.DOT,
    ) -> float:
        """Evaluates the solution.

        Requires that the model has been trained.

        Args:
            test_data: mxn tensor on which to evaluate the model.
                Requires that mxn match the dimensions of the training tensor and
                each row i and column j correspond to the same entity and item
                in the training tensor, respectively.
            method: The prediction method to use.

        Returns:
            The mean squared error of the test data.
        """
        pred = self.predict(method)
        predictions = tf.gather_nd(pred, test_data.indices)

        loss = keras.losses.MeanSquaredError()

        return loss(test_data.values, predictions).numpy()

    def predict(self, method: PredictionMethod = PredictionMethod.DOT) -> np.ndarray:
        """Gets the model predictions.

        The predictions consist of the estimated matrix A_hat of the truth
        matrix A, of which the training data contains a sparse subset of the entries.

        Args:
            method: The prediction method to use.

        Returns:
            An mxn array of values.
        """
        self._checkrep()

        return calculate_predicted_matrix(self._U, self._V, method)

    def predict_new_entity(
        self,
        entity: tf.SparseTensor,
        learning_rate: float,
        epochs: int,
        regularization_coefficient: float,
        method: PredictionMethod = PredictionMethod.DOT,
        **kwargs,
    ) -> np.array:
        """Recommends items to an unseen entity.

        Args:
            entity: A length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.
            learning_rate: Learning rate for each gradient step performed on a single
                entity-item sample.
            epochs: Number of training epochs, where each the model is trained on the
                cardinality dataset in each epoch.
            regularization_coefficient: Coefficient on the L2 regularization term.
            method: The prediction method to use.

        Returns:
            An array of predicted values for the new entity.
        """
        new_entity = tf.sparse.reorder(entity)
        new_entity = tf.sparse.to_dense(new_entity)

        num_iterations = epochs * len(new_entity)

        new_entity_embedding = np.random.normal(
            loc=0, scale=math.sqrt(1 / self._U.shape[1]), size=(1, self._U.shape[1])
        )

        _, all_i, all_j = self._sample_dataset(
            tf.expand_dims(new_entity, axis=0), num_samples=num_iterations
        )

        # initialize theta - done - init
        # repeat
        for iteration_count in range(num_iterations):
            # draw u, i, j from D_s
            # u isn't used since only predicting for new user
            i = all_i[iteration_count]
            j = all_j[iteration_count]

            # theta = theta + alpha * (e^(-x) sigma(x) d/dtheta x + lambda theta)
            x_ui = np.dot(new_entity_embedding, self._V[i, :])
            x_uj = np.dot(new_entity_embedding, self._V[j, :])
            x_uij = x_ui - x_uj

            sigmoid_derivative = (math.e ** (-x_uij)) / (1 + math.e ** (-x_uij))

            d_w = self._V[i, :] - self._V[j, :]

            new_entity_embedding += learning_rate * (
                sigmoid_derivative * d_w
                - (regularization_coefficient * new_entity_embedding)
            )

        # return theta
        # set in rep

        return np.squeeze(
            calculate_predicted_matrix(new_entity_embedding, self._V, method)
        )


Recommender.register(BPRRecommender)
