import math

import numpy as np
import pandas as pd
from mitreattack.stix20 import MitreAttackData

from tie.constants import PredictionMethod


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
    top_k_predictions = predictions.rank(axis=1, method="max", ascending=False) <= k
    assert m, 1 == top_k_predictions.shape
    test_items_in_top_k = (test_data > 0) & top_k_predictions
    num_test_items_in_top_k = test_items_in_top_k.sum(axis=1)
    assert m, 1 == num_test_items_in_top_k.shape

    return num_test_items_in_top_k


def precision_at_k(predictions: pd.DataFrame, test_data: pd.DataFrame, k: int) -> float:
    r"""Calculates the precision of the top k predictions based on test data.

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
        The computed precision for the top k predictions, or np.nan if the test set is
        empty.
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
    return num_test_items_in_top_k.mean(skipna=True) / k


def recall_at_k(predictions: pd.DataFrame, test_data: pd.DataFrame, k: int) -> float:
    r"""Calculates the recall of the top k predictions based on test data.

    Recall is defined as the average fraction of items in the test set which appear
    in the top k predictions.  If k >= the number of items in the test set for a
    particular user, then the maximum recall is 1.0.

    Mathematically, it is defined as
    recall@k =
        (1\m) \sum_u (\sum_{i=1}^k [[pred_i in test set]] / |test set for entity i|

    Args:
        predictions: an mxn matrix of predictions where m is the number of entities
            and n is the number of items.  Requires m > 0 and n > 0.
        test_data: an mxn matrix of test data where each entry is 1 if observed in the
            test set, 0 otherwise.
        k: the number of predictions to include in the top k.  Requires 0 < k <= n.

    Returns:
        The computed recall for the top k predictions, or np.,nan if the test set is
        empty.
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
    return fraction_recalled_predictions.mean(skipna=True)


def normalized_discounted_cumulative_gain(
    predictions: pd.DataFrame, test_data: pd.DataFrame, k: int = 10
) -> float:
    r"""Computes the Normalized Discounted Cumulative Gain (NDCG) on test_data.

    NDCG measures the goodness of a ranking based on the relative ordering of
    test set entries in the top-k predictions.  Test set predictions
    that appear near the top of the top-k predictions (in descending order)
    contribute more to NDCG than predictions which are ranked lower.
    NDCG ranges from 0 to 1, where 1 is a perfect ranking.

    Mathematically, NDCG is defined as
    NDCG@K = DCG@K / IDCG@K
    DCG@K = (1/m) \sum_u \sum_{i=1}^k (2^[[pred_i in test set]] - 1)/(log_2 (i+1))
    IDCG@K is a normalization constant corresponding to the maximum possible value
        of DCG@K

    Args:
        predictions: an mxn matrix of predictions where m is the number of entities
            and n is the number of items.  Requires m > 0 and n > 0.
        test_data: an mxn matrix of test data where each entry is 1 if observed in the
            test set, 0 otherwise.
        k: the number of predictions to include in the top k.  Requires 0 < k <= n.

    Returns:
        NDCG computed on the top k predictions, or np.nan if the test set is empty.
    """
    # assert preconditions
    m, n = test_data.shape
    assert m > 0
    assert n > 0
    assert m, n == predictions.shape
    assert 0 < k <= n

    # calculate idcg
    test_set_size = test_data.sum(axis=1).astype("int")
    assert m, 1 == test_set_size.shape

    def max_idcg(test_size, k) -> float:
        return sum(1 / math.log2(i + 1) for i in range(1, min(test_size, k) + 1))

    user_idcg = test_set_size.apply(lambda x: max_idcg(x, k))

    idcg = np.mean(np.where(lambda x: x > 0, user_idcg, np.nan))

    prediction_ranking = predictions.rank(axis=1, method="first", ascending=False)
    assert m, 1 == prediction_ranking.shape

    # calculating dcg
    # numerator: 1 if test set is in prediction, 0 otherwise
    numerator = np.logical_and(
        (prediction_ranking <= k).to_numpy(), test_data.to_numpy()
    )
    # denominator: log_2 of ranking + 1
    denominator = np.log2(prediction_ranking.to_numpy() + 1)

    dcg = np.divide(numerator, denominator)
    # in test set or rank should never be nan
    assert not np.any(np.isnan(dcg))

    entity_dcg = np.sum(dcg, axis=1)
    # only count for test
    dcg = np.mean(np.where(lambda x: x > 0, entity_dcg, np.nan))

    return dcg / idcg


def calculate_predicted_matrix(
    U: np.ndarray, V: np.ndarray, method: PredictionMethod = PredictionMethod.DOT
) -> np.ndarray:
    """Calculates the prediction matrix UV^T according to the dot or cosine product.

    Args:
        U: mxk array of entity embeddings
        V: nxk array of item embeddings
        method: Matrix product method to use.

    Returns:
        The matrix product UV^T, according to method.
    """
    if method == PredictionMethod.DOT:
        U_scaled = U
        V_scaled = V
    elif method == PredictionMethod.COSINE:
        U_norm = np.expand_dims(np.linalg.norm(U, ord=2, axis=1), axis=1)
        V_norm = np.expand_dims(np.linalg.norm(V, ord=2, axis=1), axis=1)

        # if norm is 0, ie if the embedding is 0
        # then do not scale by norm at all
        U_norm[U_norm == 0.0] = 1.0
        V_norm[V_norm == 0.0] = 1.0

        assert U_norm.shape == (U.shape[0], 1)
        assert V_norm.shape == (V.shape[0], 1)

        assert not np.isnan(U_norm).any()
        assert not np.isnan(V_norm).any()

        U_scaled = np.divide(U, U_norm)
        V_scaled = np.divide(V, V_norm)

    return U_scaled @ V_scaled.T
