import copy
import unittest

from scripts.create_parent_only_dataset import (
    create_parent_only_dataset,
    to_parent_techniques,
)


# Covers:
# - input IDs: parent techniques, sub-techniques
# - collision: absent, present
# - result: unchanged parent counts, aggregated parent counts
class TestToParentTechniques(unittest.TestCase):
    # Covers:
    # - input IDs: parent techniques, sub-techniques
    # - collision: present
    # - result: aggregated parent counts
    def test_aggregates_parent_and_sub_technique_counts(self) -> None:
        techniques = {"T1000": 2, "T2000": 3, "T2000.001": 4}

        result = to_parent_techniques(techniques)

        self.assertEqual({"T1000": 2, "T2000": 7}, result)


# Covers:
# - positive observations: parent techniques and sub-techniques
# - non-positive data: metadata and negative sets
# - effects: input unchanged, parent-only copy returned
class TestCreateParentOnlyDataset(unittest.TestCase):
    # Covers:
    # - positive observations: parent techniques and sub-techniques
    # - non-positive data: metadata and negative sets
    # - effects: input unchanged, parent-only copy returned
    def test_creates_parent_only_copy(self) -> None:
        full_dataset = {
            "name": "full",
            "attack_version": 19.2,
            "reports": [
                {
                    "id": 7,
                    "mitre_techniques": {
                        "T1000": 2,
                        "T2000": 3,
                        "T2000.001": 4,
                    },
                    "negative_set": ["T2000.001"],
                }
            ],
        }
        original = copy.deepcopy(full_dataset)

        result = create_parent_only_dataset(full_dataset)

        self.assertEqual(original, full_dataset)
        self.assertEqual(
            {"T1000": 2, "T2000": 7},
            result["reports"][0]["mitre_techniques"],
        )
        self.assertEqual(
            ["T2000.001"], result["reports"][0]["negative_set"]
        )
        self.assertEqual(19.2, result["attack_version"])
