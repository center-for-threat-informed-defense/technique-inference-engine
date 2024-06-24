from abc import ABC, abstractmethod
import numpy as np
import tensorflow as tf

from constants import PredictionMethod


class Recommender(ABC):
    """A matrix factorization recommender model to suggest items for a particular entity."""

    @property
    @abstractmethod
    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T."""

    @property
    @abstractmethod
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T."""

    @abstractmethod
    def fit(
        self,
        data: tf.SparseTensor,
        num_iterations: int,
        **kwargs,
    ):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data
            num_iterations: number of training iterations to execute

        Mutates:
            The recommender to the new trained state.
        """

    @abstractmethod
    def evaluate(self, test_data: tf.SparseTensor, method: PredictionMethod=PredictionMethod.DOT) -> float:
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

    @abstractmethod
    def predict(self, method: PredictionMethod=PredictionMethod.DOT) -> np.ndarray:
        """Gets the model predictions.

        The predictions consist of the estimated matrix A_hat of the truth
        matrix A, of which the training data contains a sparse subset of the entries.

        Args:
            method: The prediction method to use.
        
        Returns:
            An mxn array of values.
        """

    @abstractmethod
    def predict_new_entity(self, entity: tf.SparseTensor, method: PredictionMethod=PredictionMethod.DOT, **kwargs) -> np.array:
        """Recommends items to an unseen entity.

        Args:
            entity: A length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.
            method: The prediction method to use.

        Returns:
            An array of predicted values for the new entity.
        """
