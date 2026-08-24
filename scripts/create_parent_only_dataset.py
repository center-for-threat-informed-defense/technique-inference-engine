"""Create the parent-only TIE dataset from the full-frequency dataset."""

import argparse
import copy
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

def to_parent_techniques(techniques: Mapping[str, int]) -> dict[str, int]:
    """Returns frequencies aggregated by parent ATT&CK technique ID.

    Args:
        techniques: Frequencies indexed by ATT&CK technique or sub-technique ID.

    Returns:
        Frequencies indexed only by parent ATT&CK technique ID.
    """
    parents = {}
    for technique_id, frequency in techniques.items():
        parent_id = technique_id.split(".")[0]
        parents[parent_id] = parents.get(parent_id, 0) + frequency
    return parents


def create_parent_only_dataset(
    full_dataset: Mapping[str, Any],
) -> dict[str, Any]:
    """Returns a parent-only copy of a full-frequency TIE dataset.

    The input dataset is not mutated. Positive observations are aggregated to
    parent technique IDs. All other report fields and dataset metadata are
    preserved.

    Args:
        full_dataset: A full-frequency TIE dataset.

    Returns:
        A deep copy whose positive observations contain only parent IDs.
    """
    parent_dataset = copy.deepcopy(full_dataset)
    for report in parent_dataset["reports"]:
        report["mitre_techniques"] = to_parent_techniques(
            report["mitre_techniques"]
        )
    assert all(
        "." not in technique_id
        for report in parent_dataset["reports"]
        for technique_id in report["mitre_techniques"]
    )
    return parent_dataset


def parse_args() -> argparse.Namespace:
    """Returns command-line arguments for parent-only dataset creation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-frequency", type=Path, required=True)
    parser.add_argument("--parent-only", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    """Creates a parent-only dataset at a new path.

    Raises:
        FileExistsError: The parent-only output path already exists.
    """
    args = parse_args()
    full_dataset = json.loads(args.full_frequency.read_text())
    parent_dataset = create_parent_only_dataset(full_dataset)
    with args.parent_only.open("x") as output_file:
        json.dump(parent_dataset, output_file, indent=4)
        output_file.write("\n")
    print(f"Parent-only dataset written: {args.parent_only}")


if __name__ == "__main__":
    main()
