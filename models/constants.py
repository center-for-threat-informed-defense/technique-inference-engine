from enum import Enum


class PredictionMethod(Enum):
    """A method for predicting values in the data matrix."""

    DOT = "dot"
    COSINE = "cosine"
