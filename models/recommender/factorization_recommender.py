# Code adapted from https://colab.research.google.com/github/google/eng-edu/blob/main/ml/recommendation-systems/recommendation-systems.ipynb?utm_source=ss-recommendation-systems&utm_campaign=colab-external&utm_medium=referral&utm_content=recommendation-systems

import tensorflow as tf
import numpy as np
import keras

tf.config.run_functions_eagerly(True)
tf.compat.v1.enable_eager_execution()


class FactorizationRecommender:
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
    #   - loss is not None
    # Safety from rep exposure:
    #   - U and V are private and not reassigned

    def __init__(self, m, n, k):
        """Initializes a FactorizationRecommender object.

        Args:
            m: number of entity embeddings
            n: number of item embeddings
            k: embedding dimension
        """
        init_stddev = 0.5

        U = tf.Variable(tf.random.normal([m, k], stddev=init_stddev))
        V = tf.Variable(tf.random.normal([n, k], stddev=init_stddev))

        self._U = U
        self._V = V

        self._loss = keras.losses.MeanSquaredError()

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
        #   - loss is not None
        assert self._loss is not None

    def _get_estimated_matrix(self) -> tf.Tensor:
        """Gets the estimated matrix UV^T."""
        return tf.matmul(self._U, self._V, transpose_b=True)

    def _predict(self, data: tf.SparseTensor) -> tf.Tensor:
        """Predicts the results for data.

        Requires that data be the same shape as the training data.
        Where each row corresponds to the same entity as the training data
        and each column represents the same item to recommend.  However,
        the tensor may be sparse and contain more, fewer, or the same number
        of entries as the training data.

        Args:
            data: An mxn sparse tensor of data.

        Returns:
            A tensor of predictions.
        """

        # indices contains indices of non-null entries
        # of data
        # gather_nd will get those entries in order and
        # add to an array
        return tf.gather_nd(self._get_estimated_matrix(), data.indices)

    def _calculate_mean_square_error(self, data: tf.SparseTensor) -> tf.Tensor:
        """Calculates the mean squared error between observed values in the
        data and predictions from UV^T.

        MSE = \sum_{(i,j) \in \Omega} (data_{ij} U_i \dot V_j)^2
        where Omega is the set of observed entries in training_data.

        Args:
            data: A matrix of observations of dense_shape [N, M]
            UY: A dense Tensor of shape [N, k] where k is the embedding
            dimension, such that U_i is the embedding of element i.
            V: A dense Tensor of shape [M, k] where k is the embedding
            dimension, such that V_j is the embedding of element j.

        Returns:
            A scalar Tensor representing the MSE between the true ratings and the
            model's predictions.
        """
        predictions = self._predict(data)
        loss = self._loss(data.values, predictions)
        return loss

    def fit(self, data: tf.SparseTensor, num_iterations: int, learning_rate: float):
        """Fits the model to data.

        Args:
            data: an mxn tensor of training data
            num_iterations: number of training iterations to execute
            learning_rate: the learning rate
        """
        # preliminaries
        optimizer = keras.optimizers.legacy.SGD(learning_rate=learning_rate)

        for i in range(num_iterations + 1):
            with tf.GradientTape() as tape:
                predictions = tf.gather_nd(
                    tf.matmul(self._U, self._V, transpose_b=True), data.indices
                )
                loss = self._loss(data.values, predictions)
            gradients = tape.gradient(loss, [self._U, self._V])
            optimizer.apply_gradients(zip(gradients, [self._U, self._V]))

    def evaluate(self, test_data: tf.SparseTensor) -> float:
        """Evaluates the solution.

        Requires that the model has been trained.

        Args:
            test_data: mxn tensor on which to evaluate the model.
                Requires that mxn match the dimensions of the training tensor and
                each row i and column j correspond to the same entity and item
                in the training tensor, respectively.

        Returns: the mean squared error of the test data.
        """
        error = self._calculate_mean_square_error(test_data)
        return error.numpy()

    def predict(self) -> np.ndarray:
        """Gets the model predictions.

        The predictions consist of the estimated matrix A_hat of the truth
        matrix A, of which the training data contains a sparse subset of the entries.

        Returns:
            An mxn array of values.
        """
        return self._get_estimated_matrix().numpy()
