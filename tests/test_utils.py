import unittest
import math
import pandas as pd
import tie.utils as utils
import numpy as np
from sklearn.metrics import ndcg_score


class TestPrecisionAtK(unittest.TestCase):
    # Testing strategy:
    # Partitions over precision_at_k:
    #   value: 0, 0 < precision < 1, 1
    #   # entities: 1, >1
    #   # items: 1, >1
    #   # test data: 0, 1, >1
    #   |test data| / k: <1, 1, >1
    #   k: 1, >1

    # Covers:
    #   value: 0
    #   # entities: >1
    #   # items: 1
    #   # test data: 0
    #   |test data| / k: <1
    #   k: 1
    def test_precision_no_test_data(self):
        """Precision with no test data is always 0."""

        predictions = pd.DataFrame(
            [
                [-4.0],
                [-2003479837.57348593429],
            ]
        )
        test_data = pd.DataFrame(
            [
                [0.0],
                [0.0],
            ]
        )
        k = 1

        expected_precision = 0.0

        precision = utils.precision_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_precision, precision)

    # Covers:
    #   value: 0 < precision < 1
    #   # entities: 1
    #   # items: >1
    #   # test data: >1
    #   |test data| / k: >1
    #   k: >1
    def test_precision_max_one(self):
        """Precision with theoretical max of 1, but < half of test set in top-k."""

        predictions = pd.DataFrame(
            [
                [8.0, 2.0, 6.0, 4.0, 1.0, 5.0, 3.0, 7.0],
            ]
        )
        # first and last predictions are in test set
        test_data = pd.DataFrame(
            [
                [1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0],
            ]
        )
        k = 4

        expected_precision = 0.5

        precision = utils.precision_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_precision, precision)

    # Covers:
    #   value: 1
    #   # entities: >1
    #   # items: >1
    #   # test data: 1
    #   |test data| / k: 1
    #   k: 1
    def test_precision_one_shot(self):
        """Perfect precision on k of 1 by ranking test set first."""

        predictions = pd.DataFrame([[-3.0, -2.9], [-1.1, -1.2]])
        # first and last predictions are in test set
        test_data = pd.DataFrame([[0.0, 1.0], [1.0, 0.0]])
        k = 1

        expected_precision = 1.0

        precision = utils.precision_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_precision, precision)


class TestRecallAtK(unittest.TestCase):
    # Testing strategy:
    # Partitions over recall_at_k:
    #   value: 0, 0 < recall < 1, 1
    #   # entities: 1, >1
    #   # items: 1, >1
    #   # test data: 0, 1, >1
    #   |test data|/k: <1, 1, >1
    #   k: 1, >1

    # Covers:
    #   value: 1
    #   # entities: 1
    #   # items: 1
    #   # test data: 1
    #   |test data|/k: 1
    #   k: 1
    def test_perfect_recall_simple(self):
        """Test get recall for a single correct prediction."""

        predictions = pd.DataFrame([[742.3849827]])
        test_data = pd.DataFrame([[1.0]])
        k = 1

        expected_recall = 1.0

        recall = utils.recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)

    # Covers:
    #   value: 0
    #   # entities: 1
    #   # items: >1
    #   # test data: 0
    #   |test data|/k: <1
    #   k: >1
    def test_recall_no_test_data(self):
        """Test that recall with no test data is nan."""

        predictions = pd.DataFrame([[1.0, 2.0, 3.0]])
        test_data = pd.DataFrame([[0.0, 0.0, 0.0]])
        k = 2

        recall = utils.recall_at_k(predictions, test_data, k=k)

        self.assertTrue(np.isnan(recall))

    # Covers:
    #   value: 0
    #   # entities: 1
    #   # items: >1
    #   # test data: 0
    #   |test data|/k: <1
    #   k: >1
    def test_recall_multiple_entities(self):
        """Test recall with one completely correct entity and one completely incorrect."""

        predictions = pd.DataFrame(
            [
                [1.0, 2.0, 3.0, 2.0, 1.0],
                [2.9, 2.0, 1.0, 2.0, 3.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                # test data is every other point except predicted, so recall is 0
                [1.0, 1.0, 0.0, 1.0, 1.0],
                # test data is 1 of tied for highest prediction, so should be 1
                [0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        )
        k = 1

        expected_recall = 0.5

        recall = utils.recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)

    # Glass box testing
    def test_recall_items_no_test_data_excluded(self):
        """Items that have no test data shouldn't factor into recall calculation.

        When the number of test items for an entity is 0,
        that entity is excluded from the calculation.
        Recall should only be averaged over entities with some test data.
        """
        predictions = pd.DataFrame(
            [
                [1.0, 1.0],
                [0.0, 1.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [0.0, 0.0],
                [0.0, 1.0],
            ]
        )
        k = 1

        expected_recall = 1.0

        recall = utils.recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)

    # first - np.mean
    # second - tie

    def test_recall_tied_predictions(self):
        """If multiple predictions tied, don't get points for all if they don't fit in top k.

        Only get points for tied predictions if they all fit in the top k.
        Example:
            prediction: [2, 1, 1] with k=2 would get recall of 50%
            for test set of [1, 1, 0] since both 1's do not fit in
            the top k predictions.
        """
        predictions = pd.DataFrame(
            [
                [0.0, 0.0, 1.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [1.0, 0.0, 1.0],
            ]
        )
        k = 2

        expected_recall = 0.5

        recall = utils.recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)


class TestNormalizedDiscountedCumulativeGain(unittest.TestCase):
    # Testing strategy:
    # Partitions over normalized_discounted_cumulative_gain:
    #   value: 0, 0 < ndcg < 1
    #   # entities: 1, >1
    #   # items: 1, >1
    #   # test data: 0, 1, >1
    #   |test data|/k: <1, 1, >1
    #   k: 1, >1

    # Covers:
    #   value: 0
    #   # entities: 1
    #   # items: 1
    #   # test data: 0
    #   |test data|/k: <1
    #   k: 1
    def test_ndcg_no_test_data(self):
        """NDCG with no test data should be 1, since max ranking allowed."""

        predictions = pd.DataFrame(
            [
                [7.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [0.0],
            ]
        )
        k = 1

        ndcg = utils.normalized_discounted_cumulative_gain(predictions, test_data, k=k)

        self.assertTrue(np.isnan(ndcg))

    # Covers:
    #   value: 0 < ndcg < 1
    #   # entities: 1
    #   # items: >1
    #   # test data: >1
    #   |test data|/k: >1
    #   k: >1
    def test_ndcg_one_correct(self):
        """NDCG with one correct ranking in last place"""

        predictions = pd.DataFrame(
            [
                [1.0, 3.0, 2.0, 0.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [1.0, 0.0, 1.0, 1.0],
            ]
        )
        k = 2

        expected_dcg = 1 / math.log2(3)
        expected_idcg = (1 / math.log2(2)) + (1 / math.log2(3))
        expected_ndcg = expected_dcg / expected_idcg

        ndcg = utils.normalized_discounted_cumulative_gain(predictions, test_data, k=k)

        self.assertEqual(expected_ndcg, ndcg)

    # Covers:
    #   value: 1
    #   # entities: >1
    #   # items: >1
    #   # test data: 1
    #   |test data|/k: <1
    #   k: >1
    def test_ndcg_max_normalized(self):
        """NDCG with value 1 despite fewer test items than k."""

        predictions = pd.DataFrame(
            [
                [1.0, 3.0, 2.0],
                [2.0, 1.0, 3.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        k = 2

        expected_ndcg = 1.0

        ndcg = utils.normalized_discounted_cumulative_gain(predictions, test_data, k=k)

        self.assertEqual(expected_ndcg, ndcg)

    # Covers:
    #   value: 0 < ndcg < 1
    #   # entities: >1
    #   # items: 1
    #   # test data: 1
    #   |test data|/k: 1
    #   k: 1
    def test_ndcg_average(self):
        """Average NDCG across users."""

        predictions = pd.DataFrame(
            [
                [1.0],
                [2.0],
                [3.0],
            ]
        )
        test_data = pd.DataFrame(
            [
                [1.0],
                [1.0],
                [0.0],
            ]
        )
        k = 1

        expected_ndcg = 1.0

        ndcg = utils.normalized_discounted_cumulative_gain(predictions, test_data, k=k)

        self.assertEqual(expected_ndcg, ndcg)

    # BENCHMARK TESTING

    def test_ndcg_benchmark(self):
        """Benchmark against sklearn NDCG."""

        np.random.seed(9)
        data_size = (1, 13)
        k = 7

        predictions = pd.DataFrame(np.random.normal(size=data_size))
        test_data = pd.DataFrame(np.random.binomial(n=1, p=0.2, size=data_size))

        ndcg = utils.normalized_discounted_cumulative_gain(predictions, test_data, k=k)

        sklearn_ndcg = ndcg_score(test_data, predictions, k=7)

        self.assertAlmostEqual(sklearn_ndcg, ndcg, delta=0.00001)
