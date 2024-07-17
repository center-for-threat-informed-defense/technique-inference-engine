# Code adapted from https://colab.research.google.com/github/google/eng-edu/blob/main/ml/recommendation-systems/recommendation-systems.ipynb?utm_source=ss-recommendation-systems&utm_campaign=colab-external&utm_medium=referral&utm_content=recommendation-systems

import copy

import keras
import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error

from tie.constants import PredictionMethod
from tie.utils import calculate_predicted_matrix

from .recommender import Recommender

tf.config.run_functions_eagerly(True)
tf.compat.v1.enable_eager_execution()


class FactorizationRecommender(Recommender):
    """A matrix factorization collaborative filtering recommender model."""

    # Abstraction function:
    #   AF(m, n, k) = a matrix factorization recommender model
    #       on m entities, n items to recommend, and
    #       embedding dimension k (a hyperparameter)
    # Rep invariant:
    #   - U.shape[1] == V.shape[1]
    #   - U and V are 2D
    #   - U.shape[0] > 0
    #   - U.shape[1] > 0
    #   - V.shape[0] > 0
    #   - V.shape[1] > 0
    #   - all elements of U are non-null
    #   - all elements of V are non-null
    #   - loss is not None
    # Safety from rep exposure:
    #   - U and V are private and not reassigned
    #   - methods to get U and V return a deepcopy of the numpy representation

    def __init__(self, m, n, k):
        """Initializes a FactorizationRecommender object.

        Args:
            m: number of entities
            n: number of items
            k: embedding dimension
        """
        self._U = tf.Variable(tf.zeros((m, k)))
        self._V = tf.Variable(tf.zeros((n, k)))

        self._reset_embeddings()

        self._loss = keras.losses.MeanSquaredError()

        self._init_stddev = 1

        self._checkrep()

    def _reset_embeddings(self):
        """Resets the embeddings to a standard normal."""
        init_stddev = 1

        new_U = tf.Variable(tf.random.normal(self._U.shape, stddev=init_stddev))
        new_V = tf.Variable(tf.random.normal(self._V.shape, stddev=init_stddev))

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
        #   - all elements of U are non-null
        assert not tf.math.reduce_any(tf.math.is_nan(self._U))
        #   - all elements of V are non-null
        assert not tf.math.reduce_any(tf.math.is_nan(self._V))
        #   - loss is not None
        assert self._loss is not None

    @property
    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T."""
        self._checkrep()
        return copy.deepcopy(self._U.numpy())

    @property
    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T."""
        self._checkrep()
        return copy.deepcopy(self._V.numpy())

    def _get_estimated_matrix(self) -> tf.Tensor:
        """Gets the estimated matrix UV^T."""
        self._checkrep()
        return tf.matmul(self._U, self._V, transpose_b=True)

    def _predict(self, data: tf.SparseTensor) -> tf.Tensor:
        """Predicts the results for data.

        Requires that data be the same shape as the training data.
        Where each row corresponds to the same entity as the training data
        and each column represents the same item to recommend.  However,
        the tensor may be sparse and contain more, fewer, or the same number
        of entries as the training data.

        Args:
            data: An mxn sparse tensor of data containing p nonzero entries.

        Returns:
            A length-p tensor of predictions, where predictions[i] corresponds to the
                prediction for index data.indices[i].
        """
        # indices contains indices of non-null entries
        # of data
        # gather_nd will get those entries in order and
        # add to an array
        self._checkrep()
        return tf.gather_nd(self._get_estimated_matrix(), data.indices)

    def _calculate_regularized_loss(
        self,
        data: tf.SparseTensor,
        predictions: tf.Tensor,
        regularization_coefficient: float,
        gravity_coefficient: float,
    ) -> float:
        r"""Gets the regularized loss function.

        The regularized loss is the sum of:
        - The MSE between data and predictions.
        - A regularization term which is the average of the squared norm of each
            entity embedding, plus the average of the squared norm of each item
            embedding r = 1/m \sum_i ||U_i||^2 + 1/n \sum_j ||V_j||^2
        - A gravity term which is the average of the squares of all predictions.
            g = 1/(MN) \sum_{ij} (UV^T)_{ij}^2

        Args:
            data: the data on which to evaluate.  Predictions will be evaluated for
                every non-null entry of data.
            predictions: the model predictions on which to evaluate.  Requires that
                predictions[i] contains the predictions for data.indices[i].
            regularization_coefficient: the coefficient for the regularization component
                of the loss function.
            gravity_coefficient: the coefficient for the gravity component of the loss
                function.

        Returns:
            The regularized loss.
        """
        regularization_loss = regularization_coefficient * (
            tf.reduce_sum(self._U * self._U) / self._U.shape[0]
            + tf.reduce_sum(self._V * self._V) / self._V.shape[0]
        )

        gravity = (1.0 / (self._U.shape[0] * self._V.shape[0])) * tf.reduce_sum(
            tf.square(tf.matmul(self._U, self._V, transpose_b=True))
        )

        gravity_loss = gravity_coefficient * gravity

        self._checkrep()
        return self._loss(data, predictions) + regularization_loss + gravity_loss

    def _calculate_mean_square_error(self, data: tf.SparseTensor) -> tf.Tensor:
        r"""Calculates the mean squared error between observed values in the
        data and predictions from UV^T.

        MSE = \sum_{(i,j) \in \Omega} (data_{ij} U_i \dot V_j)^2
        where Omega is the set of observed entries in training_data.

        Args:
            data: A matrix of observations of dense_shape m, n

        Returns:
            A scalar Tensor representing the MSE between the true ratings and the
            model's predictions.
        """
        predictions = self._predict(data)
        loss = self._loss(data.values, predictions)
        self._checkrep()
        return loss

    def fit(
        self,
        data: tf.SparseTensor,
        learning_rate: float,
        epochs: int,
        regularization_coefficient: float = 0.1,
        gravity_coefficient: float = 0.0,
    ):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data.
            epochs:
            learning_rate: the learning rate.
            epochs: Number of training epochs, where each the model is trained on the
                cardinality dataset in each epoch.
            regularization_coefficient: coefficient on the embedding regularization
                term.
            gravity_coefficient: coefficient on the prediction regularization term.

        Mutates:
            The recommender to the new trained state.
        """
        self._reset_embeddings()

        # preliminaries
        optimizer = keras.optimizers.SGD(learning_rate=learning_rate)

        for i in range(epochs + 1):
            with tf.GradientTape() as tape:
                # need to predict here and not in loss so doesn't affect gradient
                predictions = self._predict(data)

                loss = self._calculate_regularized_loss(
                    data.values,
                    predictions,
                    regularization_coefficient,
                    gravity_coefficient,
                )
            gradients = tape.gradient(loss, [self._U, self._V])
            optimizer.apply_gradients(zip(gradients, [self._U, self._V]))

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

        return calculate_predicted_matrix(
            np.nan_to_num(self._U.numpy()), np.nan_to_num(self._V.numpy()), method
        )

    def predict_new_entity(
        self,
        entity: tf.SparseTensor,
        learning_rate: float,
        epochs: int,
        regularization_coefficient: float,
        gravity_coefficient: float,
        method: PredictionMethod = PredictionMethod.DOT,
    ) -> np.array:
        """Recommends items to an unseen entity

        Args:
            entity: a length-n sparse tensor of consisting of the new entity's
                ratings for each item, indexed exactly as the items used to
                train this model.
            learning rate: the learning rate for SGD.
            epochs: Number of training epochs, where each the model is trained on the
                cardinality dataset in each epoch.
            regularization_coefficient: coefficient on the embedding regularization
                term.
            gravity_coefficient: coefficient on the prediction regularization term.
            method: The prediction method to use.

        Returns:
            An array of predicted values for the new entity.
        """

        # preliminaries
        optimizer = keras.optimizers.SGD(learning_rate=learning_rate)

        embedding = tf.Variable(
            tf.random.normal(
                [self._U.shape[1], 1],
                stddev=self._init_stddev,
            )
        )

        for i in range(epochs + 1):
            with tf.GradientTape() as tape:
                # need to predict here and not in loss so doesn't affect gradient
                # V is nxk, embedding is kx1
                predictions = tf.matmul(self._V, embedding)

                loss = (
                    self._loss(entity.values, tf.gather_nd(predictions, entity.indices))
                    + (
                        regularization_coefficient
                        * tf.reduce_sum(tf.math.square(embedding))
                        / self._U.shape[0]
                    )
                    + (
                        (gravity_coefficient / (self._U.shape[0] * self._V.shape[0]))
                        * tf.reduce_sum(tf.square(tf.matmul(self._V, embedding)))
                    ),
                )

            gradients = tape.gradient(loss, [embedding])
            optimizer.apply_gradients(zip(gradients, [embedding]))

        assert not np.isnan(embedding.numpy()).any()
        self._checkrep()
        return np.squeeze(
            calculate_predicted_matrix(embedding.numpy().T, self._V.numpy(), method)
        )


Recommender.register(FactorizationRecommender)
