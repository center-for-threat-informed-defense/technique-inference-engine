import copy
import unittest
from datetime import date

from scripts.migrate_attack_datasets import (
    get_technique_migration,
    migrate_dataset,
    migrate_technique_counts,
)


REPLACEMENTS = {"T0001": "T2000.001"}


def attack_pattern(stix_id: str, external_id: str, revoked: bool = False) -> dict:
    return {
        "type": "attack-pattern",
        "id": stix_id,
        "revoked": revoked,
        "external_references": [
            {"source_name": "mitre-attack", "external_id": external_id}
        ],
    }


def attack_bundle() -> dict:
    return {
        "objects": [
            {
                "type": "x-mitre-collection",
                "id": "collection--1",
                "x_mitre_version": "19.2",
            },
            attack_pattern("attack-pattern--old", "T0001", revoked=True),
            attack_pattern("attack-pattern--parent", "T2000"),
            attack_pattern("attack-pattern--new", "T2000.001"),
            attack_pattern("attack-pattern--unchanged", "T1000"),
            {
                "type": "relationship",
                "id": "relationship--1",
                "relationship_type": "revoked-by",
                "source_ref": "attack-pattern--old",
                "target_ref": "attack-pattern--new",
            },
        ]
    }


# Covers:
# - revoked-by source: technique, non-technique
# - revoked-by target: technique, missing
# - requested ID: active, revoked, unknown
# - result: direct replacement map, assertion failure
class TestGetTechniqueMigration(unittest.TestCase):
    # Covers:
    # - revoked-by source: technique, non-technique
    # - revoked-by target: technique
    # - requested ID: active, revoked
    # - result: direct replacement map
    def test_returns_direct_technique_replacements(self) -> None:
        bundle = attack_bundle()
        bundle["objects"].append(
            {
                "type": "relationship",
                "id": "relationship--software",
                "relationship_type": "revoked-by",
                "source_ref": "malware--1",
                "target_ref": "attack-pattern--new",
            }
        )

        replacements = get_technique_migration(
            bundle, frozenset({"T0001", "T1000"})
        )

        self.assertEqual(REPLACEMENTS, replacements)

    # Covers:
    # - revoked-by source: technique
    # - revoked-by target: missing
    # - result: assertion failure
    def test_rejects_technique_replacement_without_technique_target(
        self,
    ) -> None:
        bundle = attack_bundle()
        bundle["objects"][-1]["target_ref"] = "malware--1"

        with self.assertRaises(AssertionError):
            get_technique_migration(bundle, frozenset({"T0001"}))

    # Covers:
    # - requested ID: unknown
    # - result: assertion failure
    def test_rejects_id_without_active_technique_or_replacement(self) -> None:
        with self.assertRaisesRegex(AssertionError, "No active replacement"):
            get_technique_migration(
                attack_bundle(), frozenset({"T9999"})
            )


# Covers:
# - input IDs: unchanged, replaced
# - replacement collision: absent, present
# - result: unchanged frequencies, summed frequencies
class TestMigrateTechniqueCounts(unittest.TestCase):
    # Covers:
    # - input IDs: unchanged
    # - replacement collision: absent
    # - result: unchanged frequencies
    def test_preserves_active_counts(self) -> None:
        techniques = {"T1000": 2, "T2000.001": 1}

        result = migrate_technique_counts(techniques, REPLACEMENTS)

        self.assertEqual(techniques, result)

    # Covers:
    # - input IDs: active and revoked
    # - replacement collision: present
    # - result: summed frequencies
    def test_replaces_and_sums_counts(self) -> None:
        techniques = {"T0001": 2, "T2000.001": 3}

        result = migrate_technique_counts(techniques, REPLACEMENTS)

        self.assertEqual({"T2000.001": 5}, result)


# Covers:
# - positive observations: active and revoked with a collision
# - negative set: active and revoked with a collision
# - effects: input unchanged, migrated dataset returned
class TestMigrateDataset(unittest.TestCase):
    # Covers:
    # - positive observations: active and revoked with a collision
    # - negative set: active and revoked with a collision
    # - effects: input unchanged, migrated dataset returned
    def test_migrates_full_frequency_dataset(self) -> None:
        full_dataset = {
            "name": "full",
            "attack_version": 15.0,
            "description": "Full dataset.",
            "update_date": "01/01/2024",
            "reports": [
                {
                    "id": 7,
                    "mitre_techniques": {
                        "T0001": 2,
                        "T2000.001": 3,
                        "T1000": 4,
                    },
                    "negative_set": ["T0001", "T1000", "T2000.001"],
                }
            ],
        }
        original_full = copy.deepcopy(full_dataset)

        migrated_full = migrate_dataset(attack_bundle(), full_dataset)

        self.assertEqual(original_full, full_dataset)
        self.assertEqual(
            {"T2000.001": 5, "T1000": 4},
            migrated_full["reports"][0]["mitre_techniques"],
        )
        self.assertEqual(
            {"T2000.001", "T1000"},
            set(migrated_full["reports"][0]["negative_set"]),
        )
        self.assertEqual(19.2, migrated_full["attack_version"])
        self.assertEqual(
            date.today().strftime("%m/%d/%Y"), migrated_full["update_date"]
        )
        self.assertEqual("Full dataset.", migrated_full["description"])
