import tensorflow as tf
import math
import numpy as np
import keras
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
        init_stddev = math.sqrt(1 / k)

        U = np.random.normal(loc=0, scale=init_stddev, size=(m, k))
        V = np.random.normal(loc=0, scale=init_stddev, size=(n, k))

        self._U = U
        self._V = V

        self._checkrep()

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

    def _sample_dataset(self, data: np.ndarray) -> tuple[int, int, int]:
        """Samples the dataset according to the bootstrapped sampling for BPR.

        Sampling is performed uniformly over all triples of the form (u, i, j),
        where u is a user, i is an item for which there is an observation for that user,
        and j is an item for which there is no observation for that user.

        Args:
            data: an mxn matrix observations.

        Returns:
            A tuple of the form (u, i, j) where u is the index for the user,
            i is the index of an item with an observation for that user,
            and j is the index of an item with no observation for that user.
        """
        m, n = data.shape

        data = np.nan_to_num(data)

        observations_per_user = np.sum(data, axis=1)
        assert observations_per_user.shape == (m,)

        samples_per_user = observations_per_user * (n - observations_per_user)
        sample_user_probability = samples_per_user / np.sum(samples_per_user)

        u = np.random.choice(np.arange(m), p=sample_user_probability)

        user_observations = data[u, :]
        user_non_observations = 1 - user_observations

        # each observation is filled with prob 1, so sample with that prob
        i = np.random.choice(
            len(user_observations), p=user_observations / np.sum(user_observations)
        )
        j = np.random.choice(
            len(user_observations),
            p=user_non_observations / np.sum(user_non_observations),
        )

        return u, i, j

    def _predict_for_single_entry(self, u, i) -> float:
        """Predicts the value for a single user-item pair."""
        return np.dot(self._U[u, :], self._V[i, :])

    def fit(
        self,
        data: tf.SparseTensor,
        learning_rate: float,
        num_iterations: int,
        w_regularization: float,
        v_i_regularization: float,
        v_j_regularization: float,
    ):
        data = tf.sparse.reorder(data)
        data = tf.sparse.to_dense(data)

        # initialize theta - done - init
        # repeat
        for i in range(num_iterations):

            # draw u, i, j from D_s
            u, i, j = self._sample_dataset(data)
            # print("u", u, "i", i, "j", j)

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
                sigmoid_derivative * d_w + (w_regularization * np.sum(self._U[u, :]))
            )
            self._V[i, :] += learning_rate * (
                sigmoid_derivative * d_hi + (v_i_regularization * np.sum(self._V[i, :]))
            )
            self._V[j, :] += learning_rate * (sigmoid_derivative * d_hj) + (
                v_j_regularization * np.sum(self._V[j, :])
            )

        # return theta
        # set in rep

    def _get_estimated_matrix(self) -> np.ndarray:
        return np.dot(self._U, self._V.T)

    def evaluate(self, test_data: tf.SparseTensor) -> float:
        pred = self._get_estimated_matrix()
        predictions = tf.gather_nd(pred, test_data.indices)

        loss = keras.losses.MeanSquaredError()

        return loss(test_data.values, predictions).numpy()

    def predict(self) -> np.ndarray:
        return self._get_estimated_matrix()

    def predict_new_entity(
        self,
        entity: tf.SparseTensor,
        learning_rate: float,
        num_iterations: int,
        w_regularization: float,
        **kwargs,
    ) -> np.array:
        new_entity = tf.sparse.reorder(entity)
        new_entity = tf.sparse.to_dense(new_entity)

        new_entity_embedding = np.random.normal(
            loc=0, scale=math.sqrt(1 / self._U.shape[1]), size=(1, self._U.shape[1])
        )

        # initialize theta - done - init
        # repeat
        for i in range(num_iterations):

            # draw u, i, j from D_s
            _, i, j = self._sample_dataset(tf.expand_dims(new_entity, axis=0))
            # print("u", u, "i", i, "j", j)

            # theta = theta + alpha * (e^(-x) sigma(x) d/dtheta x + lambda theta)
            # TODO factor out
            x_ui = np.dot(new_entity_embedding, self._V[i, :])
            x_uj = np.dot(new_entity_embedding, self._V[j, :])
            x_uij = x_ui - x_uj

            sigmoid_derivative = (math.e ** (-x_uij)) / (1 + math.e ** (-x_uij))

            d_w = self._V[i, :] - self._V[j, :]

            new_entity_embedding += learning_rate * (
                sigmoid_derivative * d_w
                + (w_regularization * np.sum(new_entity_embedding))
            )

        # return theta
        # set in rep

        return np.squeeze(np.dot(new_entity_embedding, self._V.T).T)


Recommender.register(BPRRecommender)
