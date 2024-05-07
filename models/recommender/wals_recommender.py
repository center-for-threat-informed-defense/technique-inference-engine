import numpy as np
import tensorflow as tf
from .recommender import Recommender
from implicit.als import AlternatingLeastSquares
from sklearn.metrics import mean_squared_error
from scipy import sparse


class WALSRecommender(Recommender):
    """A WALS matrix factorization recommender model to suggest items for a particular entity."""

    def __init__(self):
        self._model = AlternatingLeastSquares(
            factors=10, regularization=0.2, iterations=20, alpha=40
        )

    @property
    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T."""
        raise NotImplementedError

    @property
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T."""
        raise NotImplementedError

    def fit(
        self,
        data: tf.SparseTensor,
        **kwargs,
    ):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data
            num_iterations: number of training iterations to execute
            learning_rate: the learning rate

        Mutates:
            The recommender to the new trained state.
        """
        row_indices = tuple(index[0] for index in data.indices)
        column_indices = tuple(index[1] for index in data.indices)
        sparse_data = sparse.csr_matrix(
            (data.values, (row_indices, column_indices)), shape=data.shape
        )
        self._model.fit(sparse_data)

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

        return mean_squared_error(test_data.values, prediction_values)

    def predict(self) -> np.ndarray:
        """Gets the model predictions.

        The predictions consist of the estimated matrix A_hat of the truth
        matrix A, of which the training data contains a sparse subset of the entries.

        Returns:
            An mxn array of values.
        """
        return np.dot(self._model.user_factors, self._model.item_factors.T)

    def predict_new_entity(self, entity: tf.SparseTensor, **kwargs) -> np.array:
        """Recommends items to an unseen entity.

        Args:
            entity: a length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.

        Returns:
            An array of predicted values for the new entity.
        """
        raise NotImplementedError
