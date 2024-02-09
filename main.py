import numpy as np
import json
from mitreattack.stix20 import MitreAttackData


def get_mitre_technique_ids(stix_filepath: str) -> frozenset[str]:
    """Gets all MITRE technique ids."""
    mitre_attack_data = MitreAttackData("enterprise-attack.json")
    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)

    all_technique_ids = set()

    for technique in techniques:
        external_references = technique.get("external_references")
        mitre_references = tuple(filter(lambda external_reference: external_reference.get("source_name") == "mitre-attack", external_references))
        assert len(mitre_references) == 1
        mitre_technique_id = mitre_references[0]["external_id"]
        all_technique_ids.add(mitre_technique_id)

    return frozenset(all_technique_ids)

def get_campaign_techniques(filepath: str) -> tuple[frozenset[str]]:
    """Gets a set of MITRE technique ids present in each campaign."""

    data = json.load(filepath)
    campaigns = data["technique_chains"]

    ret = []

    for campaign in campaigns:

        techniques = campaign["list_of_techniques"]
        ret.append(frozenset(techniques))

    return ret
        


def main():
    # want matrix of campaigns on horizontal, techniques on vertical
    all_mitre_technique_ids = tuple(get_mitre_technique_ids("enterprise-attack.json"))
    num_techniques = len(all_mitre_technique_ids)
    mitre_technique_ids_to_index = {all_mitre_technique_ids[i]: i for i in range(len(all_mitre_technique_ids))}

    campaigns = get_campaign_techniques("data/combined_dataset.json")

    campaign_vectors = []

    # for each campaign, make a vector, filling in each present technique with a 1
    for campaign in campaigns:
        
        technique_vector = np.zeros((num_techniques,))

        for mitre_technique_id in campaign:
            index = mitre_technique_ids_to_index[mitre_technique_id]
            technique_vector[index] = 1
        
        campaign_vectors.append(technique_vector)

    data = np.vstack(campaign_vectors)

    # train

    

    

    




if __name__ == "__main__":

    main()
