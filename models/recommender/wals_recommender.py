from .recommender import Recommender
import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error


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

        init_stddev = 0.5

        U = np.random.normal(loc=0.0, scale=init_stddev, size=(m, k))
        V = np.random.normal(loc=0.0, scale=init_stddev, size=(n, k))

        self._U = U
        self._V = V

        self._checkrep()

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
        """Gets U as a factor of the factorization UV^T.  Requires model to be trained."""
        self._checkrep()
        return np.copy(self._U)

    @property
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T.  Requires model to be trained."""
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
        For example, if opposing_factors are the item factors, determines the entity factors which
        minimize loss on data.

        Args:
            opposing_factors: a pxk array of the fixed factors in the optimization step
                (ie entity or item factors).  Requires p, k > 0.
            predictions: A pxq array of the observed values for each of the entities/items associated
                with the p opposing_factors and the q items/entities associated with factors.
                Requires p, q > 0.
            alpha: Weight for positive training examples such that each positive example takes value
                alpha + 1.  Requires alpha > 0.
            regularization_coefficient: coefficient on the embedding regularization term.  Requires
                regularization_coefficient > 0.


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
        assert regularization_coefficient > 0

        def V_T_C_I_V(V, c_array):
            _, k = V.shape
            # print("v shape", V.shape)

            c_minus_i = c_array - 1
            nonzero_c = tuple(np.nonzero(c_minus_i)[0].tolist())

            product = np.ndarray((k, k))

            for i in nonzero_c:

                v_i = np.expand_dims(V[i, :], axis=1)
                # print("v_i shape", v_i.shape)

                square_addition = v_i @ v_i.T
                # print("square addition shape", square_addition.shape)
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
        num_iterations: int = 20,
        c: float = 0.024,
        regularization_coefficient: float = 0.01,
    ):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data.
            num_iterations: number of training iterations to execute.
            c: weight for negative training examples.  Requires 0 < c < 1.
            regularization_coefficient: coefficient on the embedding regularization term.

        Mutates:
            The recommender to the new trained state.
        """
        # preconditions
        assert 0 < c < 1

        P: np.ndarray = tf.sparse.to_dense(tf.sparse.reorder(data)).numpy()

        assert P.shape == (self.m, self.n)

        alpha = (1 / c) - 1

        for _ in range(num_iterations):

            # step 1: update U
            self._U = self._update_factor(
                self._V, P.T, alpha, regularization_coefficient
            )

            # step 2: update V
            self._V = self._update_factor(self._U, P, alpha, regularization_coefficient)

        self._checkrep()

    def evaluate(self, test_data: tf.SparseTensor) -> float:
        """Evaluates the solution.

        Requires that the model has been trained.

        Args:
            test_data: mxn tensor on which to evaluate the model.
                Requires that mxn match the dimensions of the training tensor and
                each row i and column j correspond to the same entity and item
                in the training tensor, respectively.

        Returns:
            The mean squared error of the test data.
        """
        predictions_matrix = self.predict()

        row_indices = tuple(index[0] for index in test_data.indices)
        column_indices = tuple(index[1] for index in test_data.indices)
        prediction_values = predictions_matrix[row_indices, column_indices]

        self._checkrep()
        return mean_squared_error(test_data.values, prediction_values)

    def predict(self) -> np.ndarray:
        """Gets the model predictions.

        The predictions consist of the estimated matrix A_hat of the truth
        matrix A, of which the training data contains a sparse subset of the entries.

        Returns:
            An mxn array of values.
        """
        self._checkrep()
        return np.dot(self._U, self._V.T)

    def predict_new_entity(
        self, entity: tf.SparseTensor, c: float, regularization_coefficient: float
    ) -> np.array:
        """Recommends items to an unseen entity.

        Args:
            entity: a length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.

        Returns:
            An array of predicted values for the new entity.
        """
        entity = tf.sparse.to_dense(tf.sparse.reorder(entity)).numpy()
        assert entity.shape == (self.n,)

        def V_T_C_I_V(V, c_array):
            _, k = V.shape
            # print("v shape", V.shape)

            c_minus_i = c_array - 1
            nonzero_c = tuple(np.nonzero(c_minus_i)[0].tolist())

            product = np.ndarray((k, k))

            for i in nonzero_c:

                v_i = np.expand_dims(V[i, :], axis=1)
                # print("v_i shape", v_i.shape)

                square_addition = v_i @ v_i.T
                # print("square addition shape", square_addition.shape)
                assert square_addition.shape == (k, k)

                product += square_addition

            return product

        # in line with the paper,
        # we will use variable names as if we are updating user factors based
        # on V, the item factors.  Since the process is the same for both,
        # the variable names are interchangeable.  This just makes following
        # along with the paper easier.
        V = self._V

        alpha = (1 / c) - 1

        # new_U = np.ndarray((q, k))
        # for each item embedding

        V_T_V = V.T @ V
        # update each of the q user factors

        P_u = entity
        # C is c if unobserved, one otherwise
        C_u = np.where(P_u > 0, alpha + 1, 1)
        assert C_u.shape == (self.n,)

        confidence_scaled_v_transpose_v = V_T_C_I_V(V, C_u)

        # X = (V^T CV + \lambda I)^{-1} V^T CP
        inv = np.linalg.inv(
            V_T_V
            + confidence_scaled_v_transpose_v
            + regularization_coefficient * np.identity(self.k)
        )

        # removed C_u here since unneccessary in binary case
        # P_u is already binary
        new_embedding = inv @ V.T @ P_u

        # (UV^T)^T = VU^T where U is 1xk
        predictions = self._V @ new_embedding

        return predictions
