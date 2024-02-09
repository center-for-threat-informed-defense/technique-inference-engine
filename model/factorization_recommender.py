import numpy as np

class FactorizationRecommender:

    def __init__(self):
        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        pass

    def train(self, data: np.ndarray):

        svd = np.linalg.svd(data)

        self._u = svd.U
        self.sigma = svd.S
        self.v = svd.Vh

    def evaluate(sefl, data: np.ndarray) -> np.array:

        return 