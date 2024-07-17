import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error

from .recommender import Recommender


class TopItemsRecommender(Recommender):
    """A recommender model which always recommends the most observed techniques.

    A recommender model which always recommends the most observed techniques in the
    dataset in frequency order.
    """

    # Abstraction function:
    #   AF(m, n, item_frequencies) = a recommender model which recommends the n
    #       items in order of frequency according to item_frequencies
    #       for each of the m entities
    # Rep invariant:
    #   - m > 0
    #   - n > 0
    #   - item_frequencies.shape == (n,)
    #   - 0 <= item_frequencies[i] <= n-1 for all 0 <= i < n
    # Safety from rep exposure:
    #   - m and n are private and immutable
    #   - item_frequency is private and never returned

    def __init__(self, m, n, k):
        """Initializes a TopItemsRecommender object."""
        self._m = m  # entity dimension
        self._n = n  # item dimension

        # array of item frequencies,
        # ranging from 0 (least frequent) to n-1 (most frequent)
        self._item_frequencies = np.zeros((n,))

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        #   - m > 0
        assert self._m > 0
        #   - n > 0
        assert self._n > 0
        #   - item_frequencies.shape == (n,)
        assert self._item_frequencies.shape == (self._n,)
        #   - 0 <= item_frequencies[i] <= n-1 for all 0 <= i < n
        assert (0 <= self._item_frequencies).all()
        assert (self._item_frequencies <= self._n - 1).all()

    def U(self) -> np.ndarray:
        """Gets U as a factor of the factorization UV^T."""
        raise NotImplementedError

    def V(self) -> np.ndarray:
        """Gets V as a factor of the factorization UV^T."""
        raise NotImplementedError

    def _scale_item_frequency(self, item_frequencies: np.array) -> np.array:
        """Scales the item frequencies from 0 to 1.

        Assigns each item the value 1/(n-1) * rank_i, where rank_i is the rank
        of item i in sorted ascending order by frequency.
        Therefore, the top frequency item will take scaled value 1, while the least
        frequent item will take scaled value 0.

        Args:
            item_frequencies: A length-n vector containing the number of occurrences
                of each item in the dataset.

        Returns:
            A scaled version of item_frequencies.
        """
        # assert 1d array
        assert len(item_frequencies.shape) == 1

        scaled_ranks = item_frequencies / (len(item_frequencies) - 1)

        assert scaled_ranks.shape == item_frequencies.shape

        self._checkrep()
        return scaled_ranks

    def fit(self, data: tf.SparseTensor, **kwargs):
        technique_matrix: np.ndarray = tf.sparse.to_dense(
            tf.sparse.reorder(data)
        ).numpy()

        technique_frequency = technique_matrix.sum(axis=0)
        assert technique_frequency.shape == (self._n,)

        ranks = technique_frequency.argsort().argsort()

        self._item_frequencies = ranks
        self._checkrep()

    def evaluate(self, test_data: tf.SparseTensor, **kwargs) -> float:
        predictions_matrix = self.predict()

        row_indices = tuple(index[0] for index in test_data.indices)
        column_indices = tuple(index[1] for index in test_data.indices)
        prediction_values = predictions_matrix[row_indices, column_indices]

        self._checkrep()
        return mean_squared_error(test_data.values, prediction_values)

    def predict(self, **kwargs) -> np.ndarray:
        scaled_ranks = self._scale_item_frequency(self._item_frequencies)
        matrix = np.repeat(np.expand_dims(scaled_ranks, axis=1), self._m, axis=1).T

        assert matrix.shape == (self._m, self._n)

        self._checkrep()
        return matrix

    def predict_new_entity(self, entity: tf.SparseTensor, **kwargs) -> np.array:
        self._checkrep()
        return self._scale_item_frequency(self._item_frequencies)
