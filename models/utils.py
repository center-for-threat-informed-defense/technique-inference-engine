from mitreattack.stix20 import MitreAttackData
import pandas as pd


def get_mitre_technique_ids_to_names(stix_filepath: str) -> dict[str, str]:
    """Gets all MITRE technique ids mapped to their description."""
    mitre_attack_data = MitreAttackData(stix_filepath)
    techniques = mitre_attack_data.get_techniques(remove_revoked_deprecated=True)

    all_technique_ids = {}

    for technique in techniques:
        external_references = technique.get("external_references")
        mitre_references = tuple(
            filter(
                lambda external_reference: external_reference.get("source_name")
                == "mitre-attack",
                external_references,
            )
        )
        assert len(mitre_references) == 1
        mitre_technique_id = mitre_references[0]["external_id"]
        all_technique_ids[mitre_technique_id] = technique.get("name")

    return all_technique_ids


def _get_num_test_items_in_top_k_per_user(
    predictions: pd.DataFrame, test_data: pd.DataFrame, k: int
) -> pd.Series:
    """Calculates the number of test items in the top k predictions for each user.

    Args:
        predictions: an mxn matrix of predictions where m is the number of entities
            and n is the number of items.  Requires m > 0 and n > 0.
        test_data: an mxn matrix of test data where each entry is 1 if observed in the
            test set, 0 otherwise.
        k: the number of predictions to include in the top k.  Requires 0 < k <= n.

    Returns:
        Array r such that r[i] is the number of items in test_data[i, :] which are in
        the top k ranked predictions of predictions[i, :].
    """
    m, n = test_data.shape
    # get a matrix with a 1 in the top 10 spots
    # find overlap with test set
    # if 1 in both, then predicted in top k
    # min to get lowest rank in group, aka less than k
    top_k_predictions = predictions.rank(axis=1, method="min", ascending=False) <= k
    assert m, 1 == top_k_predictions.shape
    test_items_in_top_k = (test_data > 0) & top_k_predictions
    num_test_items_in_top_k = test_items_in_top_k.sum(axis=1)
    assert m, 1 == num_test_items_in_top_k.shape

    return num_test_items_in_top_k


def precision_at_k(predictions: pd.DataFrame, test_data: pd.DataFrame, k: int) -> float:
    """Calculates the precision of the top k predictions based on test data.

    Precision is defined as the average fraction of items in the top k predictions
    which appear in the test set.  If k < the number of items in the test set for a
    particular user, then the maximum precision is 1.0.

    Mathematically, it is defined as
    precision@k = (1\m) \sum_u (\sum_{i=1}^k [[pred_i in test set]] / k)

    Args:
        predictions: an mxn matrix of predictions where m is the number of entities
            and n is the number of items.  Requires m > 0 and n > 0.
        test_data: an mxn matrix of test data where each entry is 1 if observed in the
            test set, 0 otherwise.
        k: the number of predictions to include in the top k.  Requires 0 < k <= n.

    Returns:
        The computed precision for the top k predictions.
    """
    m, n = test_data.shape
    assert m > 0
    assert n > 0
    assert m, n == predictions.shape
    assert 0 < k <= n

    num_test_items_in_top_k = _get_num_test_items_in_top_k_per_user(
        predictions, test_data, k
    )

    # sum number of predictions in top k, divide by k
    return (1 / m) * num_test_items_in_top_k.sum() / k


def recall_at_k(predictions: pd.DataFrame, test_data: pd.DataFrame, k: int) -> float:
    """Calculates the recall of the top k predictions based on test data.

    Recall is defined as the average fraction of items in the test set which appear
    in the top k predictions.  If k >= the number of items in the test set for a
    particular user, then the maximum recall is 1.0.

    Mathematically, it is defined as
    recall@k = (1\m) \sum_u (\sum_{i=1}^k [[pred_i in test set]] / |test set for entity i|

    Args:
        predictions: an mxn matrix of predictions where m is the number of entities
            and n is the number of items.  Requires m > 0 and n > 0.
        test_data: an mxn matrix of test data where each entry is 1 if observed in the
            test set, 0 otherwise.
        k: the number of predictions to include in the top k.  Requires 0 < k <= n.

    Returns:
        The computed recall for the top k predictions.
    """
    m, n = test_data.shape
    assert m > 0
    assert n > 0
    assert m, n == predictions.shape
    assert 0 < k <= n

    num_test_items_in_top_k = _get_num_test_items_in_top_k_per_user(
        predictions, test_data, k
    )
    num_test_items_per_user = test_data.sum(axis=1)

    fraction_recalled_predictions = num_test_items_in_top_k / num_test_items_per_user
    # sum number of predictions in top k, divide by k
    return (1 / m) * fraction_recalled_predictions.sum()
