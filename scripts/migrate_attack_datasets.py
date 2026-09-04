"""Migrate TIE training datasets to a newer Enterprise ATT&CK release."""

import argparse
import copy
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

def is_active(stix_object: Mapping[str, Any]) -> bool:
    """Returns whether a STIX object is neither revoked nor deprecated."""
    return not stix_object.get("revoked", False) and not stix_object.get(
        "x_mitre_deprecated", False
    )


def attack_reference(stix_object: Mapping[str, Any]) -> Mapping[str, Any]:
    """Returns the object's sole MITRE ATT&CK external reference."""
    references = [
        reference
        for reference in stix_object.get("external_references", [])
        if reference.get("source_name") == "mitre-attack"
    ]
    assert len(references) == 1
    return references[0]


def get_attack_version(bundle: Mapping[str, Any]) -> str:
    """Returns the Enterprise ATT&CK collection version in a STIX bundle."""
    collections = [
        item
        for item in bundle["objects"]
        if item["type"] == "x-mitre-collection"
    ]
    assert len(collections) == 1
    return collections[0]["x_mitre_version"]


def get_technique_migration(
    bundle: Mapping[str, Any],
    dataset_technique_ids: frozenset[str],
) -> dict[str, str]:
    """Returns direct replacements needed to migrate dataset technique IDs.

    Every dataset technique ID must be active or have a direct active
    replacement in the bundle.

    Args:
        bundle: An Enterprise ATT&CK STIX bundle.
        dataset_technique_ids: Technique IDs to validate and migrate.

    Returns:
        Requested revoked technique IDs mapped to active replacement IDs.
    """
    objects = bundle["objects"]
    technique_ids = {
        item["id"]: attack_reference(item)["external_id"]
        for item in objects
        if item["type"] == "attack-pattern"
    }
    active_ids = frozenset(
        technique_ids[item["id"]]
        for item in objects
        if item["type"] == "attack-pattern" and is_active(item)
    )
    replacements = {}
    for relationship in objects:
        source = relationship.get("source_ref", "")
        target = relationship.get("target_ref", "")
        is_revocation = (
            relationship["type"] == "relationship"
            and is_active(relationship)
            and relationship.get("relationship_type") == "revoked-by"
        )
        if not is_revocation or source not in technique_ids:
            continue

        revoked_id = technique_ids[source]
        if revoked_id not in dataset_technique_ids:
            continue

        # A relevant technique must have a direct, active technique replacement.
        # This fails fast if the requested migration spans multiple revocations.
        assert target in technique_ids
        replacement_id = technique_ids[target]
        assert revoked_id not in active_ids
        assert replacement_id in active_ids
        replacements[revoked_id] = replacement_id
    unmapped_ids = dataset_technique_ids.difference(
        active_ids, replacements.keys()
    )
    assert not unmapped_ids, f"No active replacement for {sorted(unmapped_ids)}"
    return replacements


def migrate_technique_counts(
    techniques: Mapping[str, int],
    replacements: Mapping[str, str],
) -> dict[str, int]:
    """Returns frequencies with replaced ATT&CK technique IDs.

    IDs absent from replacements remain unchanged. Frequencies are summed when
    several input IDs resolve to the same ID.

    Args:
        techniques: Frequencies indexed by current or revoked technique IDs.
        replacements: Revoked technique IDs mapped to active replacements.

    Returns:
        Frequencies indexed by migrated technique IDs.
    """
    migrated = {}
    for technique_id, frequency in techniques.items():
        migrated_id = replacements.get(technique_id, technique_id)
        migrated[migrated_id] = migrated.get(migrated_id, 0) + frequency
    return migrated


def migrate_dataset(
    new_attack_bundle: Mapping[str, Any],
    full_dataset: Mapping[str, Any],
) -> dict[str, Any]:
    """Returns a full-frequency dataset migrated to a newer ATT&CK release.

    The input dataset is not mutated. Negative sets retain sub-techniques and are
    migrated to active IDs without duplicates.

    Args:
        new_attack_bundle: An Enterprise ATT&CK STIX bundle.
        full_dataset: A full-frequency TIE dataset.

    Returns:
        A migrated copy of the full-frequency dataset.
    """
    migrated_full = copy.deepcopy(full_dataset)
    full_reports = migrated_full["reports"]

    attack_version = get_attack_version(new_attack_bundle)
    dataset_technique_ids = set()
    for report in full_reports:
        dataset_technique_ids.update(report["mitre_techniques"])
        dataset_technique_ids.update(report.get("negative_set", []))
    replacements = get_technique_migration(
        new_attack_bundle, frozenset(dataset_technique_ids)
    )

    for report in full_reports:
        report["mitre_techniques"] = migrate_technique_counts(
            report["mitre_techniques"], replacements
        )
        negative_set = report.get("negative_set", [])
        if negative_set:
            report["negative_set"] = list(
                migrate_technique_counts(
                    dict.fromkeys(negative_set, 1), replacements
                )
            )

    migrated_full["attack_version"] = float(attack_version)
    migrated_full["update_date"] = date.today().strftime("%m/%d/%Y")
    return migrated_full


def parse_args() -> argparse.Namespace:
    """Returns command-line arguments for an ATT&CK dataset migration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attack-data", type=Path, required=True)
    parser.add_argument("--full-frequency", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    """Migrates a full-frequency dataset and writes it to a new path.

    Raises:
        FileExistsError: The output path already exists.
    """
    args = parse_args()
    new_attack_bundle = json.loads(args.attack_data.read_text())
    full_dataset = json.loads(args.full_frequency.read_text())
    migrated_full = migrate_dataset(new_attack_bundle, full_dataset)
    with args.output.open("x") as output_file:
        json.dump(migrated_full, output_file, indent=4)
        output_file.write("\n")

    version = get_attack_version(new_attack_bundle)
    print(f"Enterprise ATT&CK {version} dataset written: {args.output}")


if __name__ == "__main__":
    main()
