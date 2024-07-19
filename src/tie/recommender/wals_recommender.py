import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error

from tie.constants import PredictionMethod
from tie.utils import calculate_predicted_matrix

from .recommender import Recommender


class WalsRecommender(Recommender):
    """A WALS matrix factorization collaborative filtering recommender model."""

    # Abstraction function:
    # AF(U, V) = a matrix factorization collaborative filtering recommendation model
    #   with user embeddings U and item embeddings V
    # Rep invariant:
    #   - U is not None
    #   - V is not None
    # Safety from rep exposure:
    #   - k is private and immutable
    #   - model is never returned

    def __init__(self, m: int, n: int, k: int = 10):
        """Initializes a new WALSRecommender object.

        Args:
            m: number of entities.  Requires m > 0.
            n: number of items.  Requires n > 0.
            k: embedding dimension.  Requires k > 0.
        """
        assert m > 0
        assert n > 0
        assert k > 0

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
        #   - U is not None
        assert self._U is not None
        #   - V is not None
        assert self._V is not None

    @property
    def m(self) -> int:
        """Gets the number of entities represented by the model."""
        self._checkrep()
        return self._U.shape[0]

    @property
    def n(self) -> int:
        """Gets the number of items represented by the model."""
        self._checkrep()
        return self._V.shape[0]

    @property
    def k(self) -> int:
        """Gets the embedding dimension of the model."""
        self._checkrep()
        return self._U.shape[1]

    @property
    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T. Model must be trained."""
        self._checkrep()
        return np.copy(self._U)

    @property
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T. Model must be trained."""
        self._checkrep()
        return np.copy(self._V)

    def _update_factor(
        self,
        opposing_factors: np.ndarray,
        data: np.ndarray,
        alpha: float,
        regularization_coefficient: float,
    ) -> np.ndarray:
        """Updates factors according to least squares on the opposing factors.

        Determines factors which minimize loss on data based on opposing_factors.
        For example, if opposing_factors are the item factors, determines the entity
        factors which minimize loss on data.

        Args:
            opposing_factors: a pxk array of the fixed factors in the optimization step
                (ie entity or item factors).  Requires p, k > 0.
            predictions: A pxq array of the observed values for each of the
                entities/items associated with the p opposing_factors and the q
                items/entities associated with factors. Requires p, q > 0.
            alpha: Weight for positive training examples such that each positive example
                takes value alpha + 1.  Requires alpha > 0.
            regularization_coefficient: coefficient on the embedding regularization
                term. Requires regularization_coefficient > 0.

        Returns:
            A qxk array of recomputed factors which minimize error.
        """
        # assert preconditions
        p, k = opposing_factors.shape
        q = data.shape[1]
        assert p > 0
        assert k == self.k
        assert p == data.shape[0]
        assert q > 0
        assert alpha > 0
        assert regularization_coefficient >= 0

        def V_T_C_I_V(V, c_array):
            _, k = V.shape

            c_minus_i = c_array - 1
            nonzero_c = tuple(np.nonzero(c_minus_i)[0].tolist())

            product = np.zeros((k, k))

            for i in nonzero_c:
                v_i = np.expand_dims(V[i, :], axis=1)

                square_addition = v_i @ v_i.T
                assert square_addition.shape == (k, k)

                product += square_addition

            return product

        # in line with the paper,
        # we will use variable names as if we are updating user factors based
        # on V, the item factors.  Since the process is the same for both,
        # the variable names are interchangeable.  This just makes following
        # along with the paper easier.
        V = opposing_factors

        new_U = np.ndarray((q, k))
        # for each item embedding

        V_T_V = V.T @ V
        # update each of the q user factors
        for i in range(q):
            P_u = data[:, i]
            # C is c if unobserved, one otherwise
            C_u = np.where(P_u > 0, alpha + 1, 1)
            assert C_u.shape == (p,)

            confidence_scaled_v_transpose_v = V_T_C_I_V(V, C_u)

            # X = (V^T CV + \lambda I)^{-1} V^T CP
            inv = np.linalg.inv(
                V_T_V
                + confidence_scaled_v_transpose_v
                + regularization_coefficient * np.identity(k)
            )

            # removed C_u here since unneccessary in binary case
            # P_u is already binary
            U_i = inv @ V.T @ P_u

            new_U[i, :] = U_i

        return new_U

    def fit(
        self,
        data: tf.SparseTensor,
        epochs: int,
        c: float = 0.024,
        regularization_coefficient: float = 0.01,
    ):
        """Fits the model to data.

        Args:
            data: An mxn tensor of training data.
            epochs: Number of training epochs, where each the model is trained on the
                cardinality dataset in each epoch.
            c: Weight for negative training examples in the loss function,
                ie each positive example takes weight 1, while negative examples take
                discounted weight c.  Requires 0 < c < 1.
            regularization_coefficient: Coefficient on the embedding regularization
                term.

        Mutates:
            The recommender to the new trained state.
        """
        self._reset_embeddings()

        # preconditions
        assert 0 < c < 1

        P: np.ndarray = tf.sparse.to_dense(tf.sparse.reorder(data)).numpy()

        assert P.shape == (self.m, self.n)

        alpha = (1 / c) - 1

        for _ in range(epochs):
            # step 1: update U
            self._U = self._update_factor(
                self._V, P.T, alpha, regularization_coefficient
            )

            # step 2: update V
            self._V = self._update_factor(self._U, P, alpha, regularization_coefficient)

        self._checkrep()

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
        predictions_matrix = self.predict(method)

        row_indices = tuple(index[0] for index in test_data.indices)
        column_indices = tuple(index[1] for index in test_data.indices)
        prediction_values = predictions_matrix[row_indices, column_indices]

        self._checkrep()
        return mean_squared_error(test_data.values, prediction_values)

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
        c: float,
        regularization_coefficient: float,
        method: PredictionMethod = PredictionMethod.DOT,
        **kwargs,
    ) -> np.array:
        """Recommends items to an unseen entity.

        Args:
            entity: A length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.
            c: Weight for negative training examples in the loss function,
                ie each positive example takes weight 1, while negative examples take
                discounted weight c.  Requires 0 < c < 1.
            regularization_coefficient: Coefficient on the embedding regularization
                term.
            method: The prediction method to use.

        Returns:
            An array of predicted values for the new entity.
        """
        entity = tf.sparse.to_dense(tf.sparse.reorder(entity)).numpy()
        assert entity.shape == (self.n,)

        alpha = (1 / c) - 1

        new_entity_factor = self._update_factor(
            opposing_factors=self._V,
            data=np.expand_dims(entity, axis=1),
            alpha=alpha,
            regularization_coefficient=regularization_coefficient,
        )

        assert new_entity_factor.shape == (1, self._U.shape[1])

        return np.squeeze(
            calculate_predicted_matrix(new_entity_factor, self._V, method)
        )


Recommender.register(WalsRecommender)
