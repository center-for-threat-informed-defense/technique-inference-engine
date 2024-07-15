import numpy as np
import pandas as pd
import tensorflow as tf


class ReportTechniqueMatrix:
    """An immutable report technique matrix."""

    # Abstraction function:
    # 	AF(indices, values, report_ids, technique_ids) = a sparse matrix A where
    #       A_{ij} = values[k] where k is the index for (i, j) in indices, if present.
    #       and A_{ij} corresponds to the report report_ids[i] and
    #       technique technique_ids[j]
    # Rep invariant:
    # - len(indices) > 0
    # - len(values) == len(indices)
    # Safety from rep exposure:
    # - all fields in rep are private and immutable

    def __init__(
        self,
        indices: tuple[tuple[int]],
        values: tuple[int],
        report_ids: tuple[int],
        technique_ids: tuple[str],
    ):
        """Initializes a ReportTechniqueMatrix object.

        Args:
            indices: iterable of indices of the format (row, column) of matrix entries
            values: iterable of matrix entry values such that values[i] contains the
                entry for indices[i] for all i.
            report_ids: unique identifiers for reports such that report_ids[i] is the
                identifier for row i of the sparse matrix.
            technique_ids: unique identifiers for techniques such that technique_ids[i]
                is the unique identifier for column j of the sparse matrix.
        """

        self._indices = tuple(indices)
        self._values = tuple(values)
        self._report_ids = tuple(report_ids)
        self._technique_ids = tuple(technique_ids)

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        # - len(indices) > 0
        assert len(self._indices) > 0
        # - len(values) == len(indices)
        assert len(self._values) == len(self._indices)

    @property
    def m(self):
        """The number of rows of the matrix."""
        self._checkrep()
        return len(self._report_ids)

    @property
    def n(self):
        """The number of columns of the matrix."""
        self._checkrep()
        return len(self._technique_ids)

    @property
    def shape(self) -> tuple[int, int]:
        """Gets the shape of the matrix."""
        return (self.m, self.n)

    @property
    def indices(self) -> tuple[tuple[int]]:
        """Gets the nonempty indices of the matrix."""
        # ok since immutable
        self._checkrep()
        return self._indices

    @property
    def report_ids(self) -> tuple[int]:
        """Gets the report ids that make up the row index of the matrix."""
        self._checkrep()
        return self._report_ids

    @property
    def technique_ids(self) -> tuple[str]:
        """Gets the technique ids that make up the column index of the matrix."""
        self._checkrep()
        return self._technique_ids

    def to_sparse_tensor(self) -> tf.SparseTensor:
        """Converts the matrix to a sparse tensor."""
        self._checkrep()
        return tf.SparseTensor(
            indices=self._indices, values=self._values, dense_shape=(self.m, self.n)
        )

    def to_numpy(self) -> np.ndarray:
        """Converts the matrix to a numpy array of shape."""
        data = np.zeros(self.shape)

        horizontal_indices = tuple(index[0] for index in self._indices)
        vertical_indices = tuple(index[1] for index in self._indices)

        data[horizontal_indices, vertical_indices] = self._values

        self._checkrep()
        return data

    def to_pandas(self) -> pd.DataFrame:
        """Converts the matrix to a pandas dataframe."""
        self._checkrep()
        return pd.DataFrame(
            data=self.to_numpy(),
            index=self._report_ids,
            columns=self._technique_ids,
        )

    def mask(self, indices: frozenset[tuple[int]]):  # -> ReportTechniqueMatrix:
        """Generates a new ReportTechniqueMatrix object with a subset of the indices.

        Args:
            indices: indices to include in the new object.

        Returns:
            A new ReportTechniqueMatrix object.
        """
        new_indices = []
        new_values = []

        for i in range(len(self._indices)):
            old_index = self._indices[i]

            if old_index in indices:
                old_value = self._values[i]
                new_indices.append(old_index)
                new_values.append(old_value)

        assert len(new_indices) == len(indices)
        assert len(new_values) == len(indices)

        self._checkrep()

        return ReportTechniqueMatrix(
            indices=new_indices,
            values=new_values,
            report_ids=self._report_ids,
            technique_ids=self._technique_ids,
        )
