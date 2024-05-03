import unittest
import pandas as pd
from models.utils import recall_at_k


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

        recall = recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)

    # Covers:
    #   value: 0
    #   # entities: 1
    #   # items: >1
    #   # test data: 0
    #   |test data|/k: <1
    #   k: >1
    def test_recall_no_test_data(self):
        """Test that recall with no test data is 0."""

        predictions = pd.DataFrame([[1.0, 2.0, 3.0]])
        test_data = pd.DataFrame([[0.0, 0.0, 0.0]])
        k = 2

        expected_recall = 0.0

        recall = recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)

    # Covers:
    #   value: 0
    #   # entities: 1
    #   # items: >1
    #   # test data: 0
    #   |test data|/k: <1
    #   k: >1
    def test_recall_multiple_entities(self):
        """Test recall with one completely correct entity and one completely incorrect.."""

        predictions = pd.DataFrame(
            [
                [1.0, 2.0, 3.0, 2.0, 1.0],
                [3.0, 2.0, 1.0, 2.0, 3.0],
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

        recall = recall_at_k(predictions, test_data, k=k)

        self.assertEqual(expected_recall, recall)
