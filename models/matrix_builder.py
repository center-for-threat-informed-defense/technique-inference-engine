import json
from matrix import ReportTechniqueMatrix
from utils import get_mitre_technique_ids_to_names


class ReportTechniqueMatrixBuilder:
    """A builder for report technique matrices."""

    # Abstraction function:
    # 	AF(combined_datset_filepath, enterprise_attack_filepath) = a builder for
    #       ReportTechniqueMatrix objects which adds m reports from the json object
    #       located at combined_dataset_filepath, zero-indexing them according to their
    #       location in the json, and n techniques according to the cardinality of the
    #       set of all techniques from all bags of techniques in the json at
    #       combined_dataset_filepath.  Techniques are indexed by MITRE ATT&CK id.
    # Rep invariant:
    #   - len(combined_dataset_filepath) >= 0
    #   - len(enterprise_attack_filepath) >= 0
    # Safety from rep exposure:
    #   - rep is private, and immutable and never reasssigned

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

        Reports are in order of appearance in the json combined dataset located at filepath.

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

        reports = data["bags_of_techniques"]

        report_techniques = []

        for report in reports:

            techniques = report["mitre_techniques"]
            report_techniques.append(frozenset(techniques.keys()))

        self._checkrep()

        return tuple(report_techniques)

    def build(self) -> ReportTechniqueMatrix:
        """Builds a ReportTechniqueMatrix.

        The rows of the matrix consist of the reports sourced from the combined dataset,
        zero-indexed in their order of appearance in the json file.  The columns consist
        of the set of all techniques in the MITRE ATT&CK 2.* series framework mentioned
        in the json.  Value i,j of the matrix is 1.0 if technique j is mentioned in
        report i, 0.0 otherwise.

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
