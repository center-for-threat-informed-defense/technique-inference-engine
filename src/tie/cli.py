import argparse
import os

import numpy as np

from tie.constants import PredictionMethod
from tie.engine import TechniqueInferenceEngine
from tie.matrix_builder import ReportTechniqueMatrixBuilder
from tie.recommender import WalsRecommender


def export_model(dataset_filepath: str, enterprise_attack_filepath: str, outfile: str):
    """Trains the TechniqueInferenceEngine and exports the model.

    Trains the TechniqueInferenceEngine based on dataset and exports the model to
    outfile.

    Args:
        dataset_filepath: A JSON file formatted according the provided specification.
        enterprise_attack_filepath: A JSON file containing an Enterprise ATT&CK STIX
            bundle.
        outfile: A .npz file in which to save the resulting embeddings.

    Mutates:
        Saves the results to an npz outfile with the following keys:
            - hyperparameters: Array where the first column is the hyperparameter
                name and the second contains the value
            - u: mxk array of the m entity embeddings
            - v: nxk array of the n user embeddings
            - report_ids: Length-m array of the m report ids
            - technique_ids: Length-n array of the n technique ids
    """
    # could be added to arguments later
    validation_ratio = 0.1
    test_ratio = 0.2
    k = 4

    data_builder = ReportTechniqueMatrixBuilder(
        combined_dataset_filepath=dataset_filepath,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )
    (
        training_data,
        test_data,
        validation_data,
    ) = data_builder.build_train_test_validation(test_ratio, validation_ratio)
    m, n = training_data.shape

    # most models performed better with embedding dimension 4
    model = WalsRecommender(m=training_data.m, n=training_data.n, k=k)
    tie = TechniqueInferenceEngine(
        training_data=training_data,
        validation_data=validation_data,
        test_data=test_data,
        model=model,
        prediction_method=PredictionMethod.DOT,
        enterprise_attack_filepath=enterprise_attack_filepath,
    )

    hyperparameters = {
        "epochs": [25],  # default
        # parameters combinations from https://dl.acm.org/doi/10.1145/3522672
        # with the addition of c 0.0001 and regularization_coefficient 0.00001
        # since experimentally, we saw these used at times in optimal hyperparameter
        # combination
        "c": [0.001, 0.005, 0.01, 0.05, 0.1, 0.3, 0.5, 0.7],
        "regularization_coefficient": [0.0, 0.0001, 0.001, 0.01],
    }

    best_hyperparameters = tie.fit_with_validation(**hyperparameters)
    hyperparameters_array = np.array(
        [
            (
                best_hyperparameters["c"],
                best_hyperparameters["epochs"],
                best_hyperparameters["regularization_coefficient"],
            )
        ],
        dtype=np.dtype(
            [
                ("c", "<f4"),
                ("epochs", "<f4"),
                ("regularization_coefficient", "<f4"),
            ]
        ),
    )

    U = tie.get_U().astype("float32")
    V = tie.get_V().astype("float32")
    assert U.shape == (m, k)
    assert V.shape == (n, k)

    report_ids = np.array(training_data.report_ids)
    technique_ids = np.array(training_data.technique_ids)
    assert report_ids.shape == (m,)
    assert technique_ids.shape == (n,)

    np.savez_compressed(
        outfile,
        U=U,
        V=V,
        technique_ids=technique_ids,
        hyperparameters=hyperparameters_array,
    )
    if not outfile.endswith(".npz"):
        os.rename(outfile + ".npz", outfile)


def main():
    parser = argparse.ArgumentParser(
        prog="TechniqueInferenceEngine",
        description=(
            "Generates .npz files containing the embedding matrices from the "
            "TechniqueInferenceEngine recommender system."
        ),
        epilog="For further help and support, please reach out to CTID.",
    )

    parser.add_argument("-r", "--report-data", required=True)
    parser.add_argument("-a", "--attack-data", required=True)
    parser.add_argument("-o", "--outfile", required=True)

    args = parser.parse_args()

    export_model(args.report_data, args.attack_data, args.outfile)


if __name__ == "__main__":
    main()
