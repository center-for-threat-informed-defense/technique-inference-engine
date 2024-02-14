import numpy as np
import json
from mitreattack.stix20 import MitreAttackData
import tensorflow as tf
from model import FactorizationRecommender


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

    with open(filepath) as f:
        data = json.load(f)

    campaigns = data["bags_of_techniques"]

    ret = []

    for campaign in campaigns:

        techniques = campaign["mitre_techniques"]
        ret.append(frozenset(techniques.keys()))

    return ret
        


def main():
    # want matrix of campaigns on horizontal, techniques on vertical
    all_mitre_technique_ids = tuple(get_mitre_technique_ids("enterprise-attack.json"))
    mitre_technique_ids_to_index = {all_mitre_technique_ids[i]: i for i in range(len(all_mitre_technique_ids))}

    campaigns = get_campaign_techniques("data/combined_dataset_full_frequency.json")

    indices = []
    values = []

    # for each campaign, make a vector, filling in each present technique with a 1
    for i in range(len(campaigns)):

        campaign = campaigns[i]

        for mitre_technique_id in campaign:
            if mitre_technique_id in mitre_technique_ids_to_index:
                # campaign id, technique id
                index = [i, mitre_technique_ids_to_index[mitre_technique_id]]
                
                indices.append(index)
                values.append(1)

    data = tf.SparseTensor(
        indices=indices,
        values=values,
        dense_shape=(len(campaigns), len(all_mitre_technique_ids))
    )

    # train
    model = FactorizationRecommender(m=len(campaigns), n=len(all_mitre_technique_ids), k=10)
    print(model.train(data, num_iterations=1000, learning_rate=10.))

    

    

    




if __name__ == "__main__":

    main()
