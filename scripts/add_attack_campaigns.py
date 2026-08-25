"""Add missing Enterprise ATT&CK campaigns to a TIE dataset."""

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

# COMMENT: Remove the if block
if __package__:
    from .migrate_attack_datasets import (
        attack_reference,
        get_attack_version,
        is_active,
    )
else:
    from migrate_attack_datasets import (
        attack_reference,
        get_attack_version,
        is_active,
    )

# COMMENT: Can just put this in function
CAMPAIGN_DATA_SOURCE = "MITRE ATT&CK Campaigns"


def add_missing_campaigns(
    attack_bundle: dict[str, Any], dataset: dict[str, Any]
) -> tuple[int, list[str]]:
    """Adds missing active ATT&CK campaign reports to a TIE dataset.

    Campaigns are matched by ATT&CK external ID or campaign name. Technique
    targets may be active, revoked, or deprecated so the dataset can be passed
    through the ATT&CK migration script afterward. Campaigns without technique
    relationships are skipped.

    Args:
        attack_bundle: An Enterprise ATT&CK STIX bundle.
        dataset: A full-frequency TIE dataset, which this function mutates.

    Returns:
        A tuple containing the number of reports added and the ATT&CK IDs of
        skipped campaigns.
    """
    attack_objects = attack_bundle["objects"]
    technique_id_by_stix_id = {
        item["id"]: attack_reference(item)["external_id"]
        for item in attack_objects
        if item["type"] == "attack-pattern"
    }
    active_campaigns = [
        (attack_reference(item)["external_id"], item)
        for item in attack_objects
        if item["type"] == "campaign" and is_active(item)
    ]

    existing_campaign_identifiers = {
        identifier
        for report in dataset["reports"]
        if report.get("origin_of_data") == CAMPAIGN_DATA_SOURCE
        for identifier in report["associated_campaigns"]
    }
    missing_campaigns = [
        (attack_id, campaign)
        for attack_id, campaign in active_campaigns
        if attack_id not in existing_campaign_identifiers
        and campaign["name"] not in existing_campaign_identifiers
    ]
    missing_campaigns.sort(key=lambda campaign: campaign[0])

    techniques_by_campaign = {
        campaign["id"]: set() for _, campaign in missing_campaigns
    }
    for item in attack_objects:
        source_ref = item.get("source_ref", "")
        target_ref = item.get("target_ref", "")
        is_campaign_technique_relationship = (
            item["type"] == "relationship"
            and item.get("relationship_type") == "uses"
            and is_active(item)
            and source_ref in techniques_by_campaign
            and target_ref in technique_id_by_stix_id
        )
        if is_campaign_technique_relationship:
            techniques_by_campaign[source_ref].add(
                technique_id_by_stix_id[target_ref]
            )

    campaigns_with_techniques = [
        (attack_id, campaign)
        for attack_id, campaign in missing_campaigns
        if techniques_by_campaign[campaign["id"]]
    ]
    skipped_campaign_ids = [
        attack_id
        for attack_id, campaign in missing_campaigns
        if not techniques_by_campaign[campaign["id"]]
    ]

    next_report_id = max(
        (report["id"] for report in dataset["reports"]), default=-1
    ) + 1
    new_reports = []
    for _, campaign in campaigns_with_techniques:
        references = [
            {"name": reference["source_name"], "url": reference["url"]}
            for reference in campaign.get("external_references", [])
            if reference.get("source_name") != "mitre-attack"
            and reference.get("url")
        ]
        new_reports.append(
            {
                "mitre_techniques": {
                    technique_id: 1
                    for technique_id in sorted(
                        techniques_by_campaign[campaign["id"]]
                    )
                },
                "references": references,
                "associated_groups": [],
                "associated_software": [],
                "associated_campaigns": [campaign["name"]],
                "origin_of_data": CAMPAIGN_DATA_SOURCE,
                "id": next_report_id + len(new_reports),
            }
        )

    dataset["reports"].extend(new_reports)
    if new_reports:
        dataset["update_date"] = date.today().strftime("%m/%d/%Y")
    return len(new_reports), skipped_campaign_ids


def parse_args() -> argparse.Namespace:
    """Returns command-line arguments for adding ATT&CK campaigns."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enterprise-stix", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    """Adds missing campaigns and updates the dataset file in place."""
    args = parse_args()
    attack_bundle = json.loads(args.enterprise_stix.read_text())
    dataset = json.loads(args.dataset.read_text())

    added_count, skipped_campaign_ids = add_missing_campaigns(
        attack_bundle, dataset
    )
    args.dataset.write_text(json.dumps(dataset, indent=4) + "\n")

    version = get_attack_version(attack_bundle)
    print(f"Added {added_count} Enterprise ATT&CK {version} campaign reports.")
    if skipped_campaign_ids:
        print(
            "Skipped campaigns without technique relationships: "
            f"{skipped_campaign_ids}"
        )


if __name__ == "__main__":
    main()
