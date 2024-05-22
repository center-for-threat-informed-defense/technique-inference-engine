from .recommender import Recommender
import numpy as np
import tensorflow as tf
from implicit.bpr import BayesianPersonalizedRanking
from scipy import sparse
from sklearn.metrics import mean_squared_error


class ImplicitBPRRecommender:
    """A matrix factorization recommender model to suggest items for a particular entity."""

    # Abstraction function:
    #   AF(k, model) = model to be trained with embedding dimension k if model is None,
    #       or model with embedding dimension k if model
    # Rep invariant:
    #   - k > 0
    # Safety from rep exposure:
    #   - k is private and immutable
    #   - model is never returned

    def __init__(self, k: int):
        """Initializes an ImplicitBPRRecommender object.

        Args:
            k: the embedding dimension.  Requires k > 0.
        """
        # assert preconditions
        assert k > 0

        self._k = k
        self._model = None

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        assert self._k > 0

    @property
    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T.  Requires model to be trained."""
        assert self._model

        self._checkrep()
        return np.copy(self._model.user_factors)

    @property
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T.  Requires model to be trained."""
        assert self._model

        self._checkrep()
        return np.copy(self._model.item_factors)

    def fit(
        self,
        data: tf.SparseTensor,
        learning_rate: float,
        num_iterations: int,
        regularization: float,
        **kwargs,
    ):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data.
            learning_rate: the learning rate.
                Requires learning_rate > 0.
            num_iterations: number of training iterations to execute.
                Requires num_iterations > 0.
            regularization: coefficient on the embedding regularization term.

        Mutates:
            The recommender to the new trained state.
        """

        self._model = BayesianPersonalizedRanking(
            factors=self._k,
            learning_rate=learning_rate,
            regularization=regularization,
            iterations=num_iterations,
            verify_negative_samples=True,
        )

        row_indices = tuple(index[0] for index in data.indices)
        column_indices = tuple(index[1] for index in data.indices)
        sparse_data = sparse.csr_matrix(
            (data.values, (row_indices, column_indices)), shape=data.shape
        )

        self._model.fit(sparse_data)

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
