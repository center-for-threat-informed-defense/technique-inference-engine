import json
import math
import random

from tie.matrix import ReportTechniqueMatrix
from tie.utils import get_mitre_technique_ids_to_names


class ReportTechniqueMatrixBuilder:
    """A builder for report technique matrices."""

    # Abstraction function:
    # 	AF(combined_dataset_filepath, enterprise_attack_filepath) = a builder for
    #       ReportTechniqueMatrix objects which adds m reports from the json object
    #       located at combined_dataset_filepath, zero-indexing them according to their
    #       location in the json, and n techniques according to the cardinality of the
    #       set of all techniques from all bags of techniques in the json at
    #       combined_dataset_filepath.  Techniques are indexed by MITRE ATT&CK id.
    # Rep invariant:
    #   - len(combined_dataset_filepath) >= 0
    #   - len(enterprise_attack_filepath) >= 0
    # Safety from rep exposure:
    #   - rep is private, and immutable and never reassigned

    def __init__(self, combined_dataset_filepath: str, enterprise_attack_filepath: str):
        """Initializes a ReportTechniqueMatrixBuilder object."""

        self._combined_datset_filepath = combined_dataset_filepath
        self._enterprise_attack_filepath = enterprise_attack_filepath

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        #   - len(combined_dataset_filepath) >= 0
        assert len(self._combined_datset_filepath) >= 0
        #   - len(enterprise_attack_filepath) >= 0
        assert len(self._enterprise_attack_filepath) >= 0

    def _get_report_techniques(self, filepath: str) -> tuple[frozenset[str]]:
        """Gets a set of all MITRE technique ids present in each report.

        Reports are in order of appearance in the json combined dataset located at
        filepath.

        All techniques are returned, regardless of whether they are valid
        MITRE ATT&CK techniques.

        Args:
            filepath: location of the json combined dataset.

        Returns:
            An iterable of sets of techniques, where the ith set represents the set of
            techniques in the ith report in the combined dataset.
        """
        with open(filepath) as f:
            data = json.load(f)

        reports = data["reports"]

        report_techniques = []

        for report in reports:
            techniques = report["mitre_techniques"]
            report_techniques.append(frozenset(techniques.keys()))

        self._checkrep()

        return tuple(report_techniques)

    def build(self) -> ReportTechniqueMatrix:
        """Builds a ReportTechniqueMatrix from the dataset.

        Returns:
            A matrix of report data.
        """
        # want matrix of reports on horizontal, techniques on vertical
        reports = self._get_report_techniques(self._combined_datset_filepath)
        all_mitre_technique_ids_to_names = get_mitre_technique_ids_to_names(
            self._enterprise_attack_filepath
        )

        # get all techniques present in all reports
        all_report_technique_ids = set()
        for report in reports:
            all_report_technique_ids.update(report)
        # some reports contain invalid techniques from ATT&CK v1
        technique_ids = tuple(
            set(all_mitre_technique_ids_to_names.keys()).intersection(
                all_report_technique_ids
            )
        )

        techniques_to_index = {technique_ids[i]: i for i in range(len(technique_ids))}

        indices = []
        values = []
        report_ids = tuple(range(len(reports)))

        # for each campaign, make a vector, filling in each present technique with a 1
        for i in range(len(reports)):
            report = reports[i]

            for mitre_technique_id in report:
                if mitre_technique_id in techniques_to_index:
                    # campaign id, technique id
                    index = (i, techniques_to_index[mitre_technique_id])

                    indices.append(index)
                    values.append(1)

        data = ReportTechniqueMatrix(
            indices=indices,
            values=values,
            report_ids=report_ids,
            technique_ids=technique_ids,
        )

        self._checkrep()

        return data

    def build_train_test_validation(
        self, test_ratio: float, validation_ratio: float
    ) -> tuple[ReportTechniqueMatrix, ReportTechniqueMatrix, ReportTechniqueMatrix]:
        """Builds three matrices for each of the training, test, and validation data.

        The ReportTechniqueMatrices for each of the test and validation datasets contain
        test_ratio and validation_ratio proportion of the positive interactions from the
        dataset, respectively.  The training data contains the remainder of the
        interactions.

        Ensures that each report has at least one technique example.
        To support this, requires the number of reports
        m > (1-test_ratio-validation_ratio) * num_observations, where num_observations
        is the number of observed report-technique interactions.

        Args:
            test_ratio: The ratio of positive interactions to include in the test
                dataset compared to the total number of observed positive interactions.
                Requires 0 <= test_ratio <= 1.
            validation_ratio: The ratio of positive interactions to include in the test
                dataset compared to the total number of observed positive interactions.
                Requires 0 <= test_ratio <= 1 and test_ratio + validation_ratio <= 1.

        Returns:
            A tuple of the form training_data, test_data, validation_data containing
            the training, test, and validation datasets, respectively.
        """
        assert 0 <= test_ratio <= 1
        assert 0 <= validation_ratio <= 1
        assert test_ratio + validation_ratio <= 1

        data = self.build()

        num_observations = data.to_numpy().sum()
        # make sure that we have enough observations
        # to at least provide a single one per report
        assert data.m <= num_observations * (1 - test_ratio - validation_ratio)
        # use floor since we need to have at least one example in the training set for
        # each report may mean slightly less (by 1) items in test or validation set
        num_validation_samples = math.floor(validation_ratio * num_observations)
        num_test_samples = math.floor(test_ratio * num_observations)

        # Strategy:
        # - sample one index per row to make sure we have at least one training item per
        #   row
        # - remove these from the indices available from which to sample the test and
        #   validation data
        # - sample test and validation data
        # - training data = all indices - test indices - validation indices
        # - make sure to sample at least one index per row by splitting indices by row
        #   and sampling from each
        indices_by_row = {index[0]: [] for index in data.indices}
        for index in data.indices:
            row, _ = index
            indices_by_row[row].append(index)

        min_training_indices = set()
        for _, indices in indices_by_row.items():
            minimum_sample_for_row = random.sample(indices, k=1)
            assert len(minimum_sample_for_row) == 1
            min_training_indices.add(minimum_sample_for_row[0])

        remaining_indices_to_sample = frozenset(data.indices).difference(
            min_training_indices
        )

        sampled_validation_indices = frozenset(
            random.sample(sorted(remaining_indices_to_sample), k=num_validation_samples)
        )
        remaining_indices_to_sample = remaining_indices_to_sample.difference(
            sampled_validation_indices
        )

        sampled_test_indices = frozenset(
            random.sample(sorted(remaining_indices_to_sample), k=num_test_samples)
        )

        sampled_train_indices = frozenset(data.indices).difference(
            sampled_validation_indices, sampled_test_indices
        )

        assert sampled_train_indices.isdisjoint(sampled_test_indices)
        assert sampled_train_indices.isdisjoint(sampled_validation_indices)
        assert sampled_test_indices.isdisjoint(sampled_validation_indices)

        training_data = data.mask(sampled_train_indices)
        validation_data = data.mask(sampled_validation_indices)
        test_data = data.mask(sampled_test_indices)

        return (training_data, test_data, validation_data)
