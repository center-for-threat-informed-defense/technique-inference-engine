#!/usr/bin/env python3
"""
Identifies MITRE ATT&CK techniques that are not present in the training data.

This script compares all valid techniques from the STIX enterprise-attack data
against the techniques present in the training datasets to identify gaps in coverage.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from src.tie.utils import get_mitre_technique_ids_to_names


def load_training_techniques(dataset_filepath: Path) -> set[str]:
    """
    Extract all technique IDs present in a training dataset.

    Args:
        dataset_filepath: Path to the combined dataset JSON file

    Returns:
        Set of technique IDs found in the training data
    """
    with open(dataset_filepath) as f:
        data = json.load(f)

    training_techniques = set()
    reports = data.get("reports", [])

    for report in reports:
        mitre_techniques = report.get("mitre_techniques", {})
        training_techniques.update(mitre_techniques.keys())

    return training_techniques


def get_technique_metadata(stix_filepath: Path) -> dict[str, dict[str, Any]]:
    """
    Extract metadata for all techniques from STIX data.

    Args:
        stix_filepath: Path to the STIX enterprise-attack JSON file

    Returns:
        Dictionary mapping technique IDs to metadata (name, tactics, platforms)
    """
    with open(stix_filepath) as f:
        stix_data = json.load(f)

    technique_metadata = {}

    for obj in stix_data.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue

        # Skip deprecated and revoked techniques
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        # Extract technique ID from external references
        external_refs = obj.get("external_references", [])
        technique_id = None

        for ref in external_refs:
            if ref.get("source_name") == "mitre-attack":
                technique_id = ref.get("external_id")
                break

        if not technique_id:
            continue

        # Extract tactics (kill chain phases)
        tactics = []
        for phase in obj.get("kill_chain_phases", []):
            if phase.get("kill_chain_name") == "mitre-attack":
                tactics.append(phase.get("phase_name"))

        technique_metadata[technique_id] = {
            "name": obj.get("name"),
            "tactics": tactics,
            "platforms": obj.get("x_mitre_platforms", []),
        }

    return technique_metadata


def analyze_coverage(
    stix_filepath: Path, dataset_filepath: Path, dataset_name: str
) -> dict[str, Any]:
    """
    Analyze technique coverage for a training dataset.

    Args:
        stix_filepath: Path to STIX data
        dataset_filepath: Path to training dataset
        dataset_name: Name for reporting

    Returns:
        Dictionary with coverage statistics and missing techniques
    """
    # Get all valid techniques from STIX
    all_technique_ids_to_names = get_mitre_technique_ids_to_names(str(stix_filepath))
    technique_metadata = get_technique_metadata(stix_filepath)

    # Get techniques present in training data
    training_techniques = load_training_techniques(dataset_filepath)

    # Find missing techniques
    all_technique_ids = set(all_technique_ids_to_names.keys())
    missing_technique_ids = all_technique_ids - training_techniques

    # Categorize missing techniques
    missing_techniques_with_metadata = []
    for tech_id in sorted(missing_technique_ids):
        metadata = technique_metadata.get(tech_id, {})
        missing_techniques_with_metadata.append(
            {
                "id": tech_id,
                "name": all_technique_ids_to_names.get(tech_id),
                "tactics": metadata.get("tactics", []),
                "platforms": metadata.get("platforms", []),
                "is_subtechnique": "." in tech_id,
            }
        )

    # Calculate statistics
    total_techniques = len(all_technique_ids)
    training_technique_count = len(training_techniques)
    missing_technique_count = len(missing_technique_ids)
    coverage_percentage = (
        (training_technique_count / total_techniques * 100)
        if total_techniques > 0
        else 0
    )

    # Count parent vs sub-techniques
    missing_parents = [
        t for t in missing_techniques_with_metadata if not t["is_subtechnique"]
    ]
    missing_subtechniques = [
        t for t in missing_techniques_with_metadata if t["is_subtechnique"]
    ]

    return {
        "dataset_name": dataset_name,
        "total_valid_techniques": total_techniques,
        "techniques_in_training": training_technique_count,
        "missing_techniques_count": missing_technique_count,
        "coverage_percentage": round(coverage_percentage, 2),
        "missing_parent_techniques": len(missing_parents),
        "missing_subtechniques": len(missing_subtechniques),
        "missing_techniques": missing_techniques_with_metadata,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Identify MITRE ATT&CK techniques not present in training data"
    )
    parser.add_argument(
        "--stix-file",
        type=Path,
        default=Path("data/stix/enterprise-attack.json"),
        help="Path to STIX enterprise-attack JSON file",
    )
    parser.add_argument(
        "--full-dataset",
        type=Path,
        default=Path("data/combined_dataset_full_frequency.json"),
        help="Path to full frequency training dataset",
    )
    parser.add_argument(
        "--parent-dataset",
        type=Path,
        default=Path("data/combined_dataset_parent_only.json"),
        help="Path to parent-only training dataset",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("missing_techniques_report.json"),
        help="Output file for the missing techniques report",
    )
    parser.add_argument(
        "--analyze-both",
        action="store_true",
        help="Analyze both datasets (default: full frequency only)",
    )

    args = parser.parse_args()

    # Verify files exist
    if not args.stix_file.exists():
        print(f"Error: STIX file not found: {args.stix_file}")
        return 1

    if not args.full_dataset.exists():
        print(f"Error: Full dataset not found: {args.full_dataset}")
        return 1

    print("Analyzing technique coverage in training data...\n")

    # Analyze full frequency dataset
    print(f"Analyzing {args.full_dataset.name}...")
    full_analysis = analyze_coverage(
        args.stix_file, args.full_dataset, "combined_dataset_full_frequency"
    )

    # Print summary for full dataset
    print(f"  Total valid techniques: {full_analysis['total_valid_techniques']}")
    print(f"  Techniques in training: {full_analysis['techniques_in_training']}")
    print(f"  Missing techniques: {full_analysis['missing_techniques_count']}")
    print(f"  Coverage: {full_analysis['coverage_percentage']}%")
    print(f"  Missing parent techniques: {full_analysis['missing_parent_techniques']}")
    print(f"  Missing sub-techniques: {full_analysis['missing_subtechniques']}\n")

    results = {
        "analysis_date": "01/18/2026",
        "stix_file": str(args.stix_file),
        "full_frequency_analysis": full_analysis,
    }

    # Optionally analyze parent-only dataset
    if args.analyze_both:
        if args.parent_dataset.exists():
            print(f"Analyzing {args.parent_dataset.name}...")
            parent_analysis = analyze_coverage(
                args.stix_file, args.parent_dataset, "combined_dataset_parent_only"
            )

            print(
                f"  Total valid techniques: {parent_analysis['total_valid_techniques']}"
            )
            print(
                f"  Techniques in training: {parent_analysis['techniques_in_training']}"
            )
            print(
                f"  Missing techniques: {parent_analysis['missing_techniques_count']}"
            )
            print(f"  Coverage: {parent_analysis['coverage_percentage']}%")
            print(
                f"  Missing parent techniques: {parent_analysis['missing_parent_techniques']}"
            )
            print(
                f"  Missing sub-techniques: {parent_analysis['missing_subtechniques']}\n"
            )

            results["parent_only_analysis"] = parent_analysis
        else:
            print(f"Warning: Parent-only dataset not found: {args.parent_dataset}\n")

    # Save results to file
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {args.output}")

    # Print sample of missing techniques
    missing_techs = full_analysis["missing_techniques"]
    if missing_techs:
        print(f"\nSample of missing techniques (first 10):")
        for tech in missing_techs[:10]:
            tactics_str = (
                ", ".join(tech["tactics"]) if tech["tactics"] else "No tactics"
            )
            print(f"  {tech['id']}: {tech['name']} [{tactics_str}]")

        if len(missing_techs) > 10:
            print(f"  ... and {len(missing_techs) - 10} more")

    return 0


if __name__ == "__main__":
    exit(main())
