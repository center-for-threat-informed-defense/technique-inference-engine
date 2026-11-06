"""Print training-data counts and coverage of the bundled ATT&CK catalog.

Run with ``python3 scripts/dataset_metrics.py`` from the repository root;
no third-party packages are needed.
Coverage includes active parent techniques and sub-techniques. Observation
counts include every recorded frequency, including any retired technique IDs.
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=root / "data/combined_dataset_full_frequency.json",
    )
    parser.add_argument(
        "--attack-data",
        type=Path,
        default=root / "data/stix/enterprise-attack.json",
    )
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    bundle = json.loads(args.attack_data.read_text(encoding="utf-8"))
    reports = dataset["reports"]

    observations = sum(
        sum(report["mitre_techniques"].values()) for report in reports
    )
    observed_ids = {
        technique_id for report in reports for technique_id in report["mitre_techniques"]
    }
    active_ids = {
        reference["external_id"]
        for obj in bundle["objects"]
        if obj["type"] == "attack-pattern"
        and not obj.get("revoked", False)
        and not obj.get("x_mitre_deprecated", False)
        for reference in obj.get("external_references", [])
        if reference.get("source_name") == "mitre-attack"
    }
    if not active_ids:
        parser.error("The ATT&CK catalog contains no active technique IDs.")

    covered_ids = observed_ids & active_ids
    coverage = 100 * len(covered_ids) / len(active_ids)

    print(f"Technique observations (sum of frequencies): {observations:,}")
    print(f"Report records (including CTI reports): {len(reports):,}")
    print(
        f"Active ATT&CK technique coverage: {coverage:.2f}% "
        f"({len(covered_ids):,} of {len(active_ids):,} techniques and sub-techniques)"
    )


if __name__ == "__main__":
    main()
