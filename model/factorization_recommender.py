# Code adapted from https://colab.research.google.com/github/google/eng-edu/blob/main/ml/recommendation-systems/recommendation-systems.ipynb?utm_source=ss-recommendation-systems&utm_campaign=colab-external&utm_medium=referral&utm_content=recommendation-systems

import collections
import numpy as np
import tensorflow as tf

tf.compat.v1.disable_v2_behavior()

class FactorizationRecommender:

    def __init__(self, m, n, k):
        """
        Args:
            m: number of individual embeddings
            n: number of item embeddings
            k: embedding dimension
        """
        init_stddev = 0.5

        U = tf.Variable(tf.random.normal(
            [m, k], stddev=init_stddev))
        V = tf.Variable(tf.random.normal(
            [n, k], stddev=init_stddev))

        self._session = None
        self._U = U
        self._V = V
        self._embedding_vars = {
            "user_id": U,
            "movie_id": V
        }
        self._embeddings = {k: None for k in self._embedding_vars}

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        pass

    def _calculate_mean_square_error(self, data: tf.SparseTensor, U: tf.Tensor, V: tf.Tensor):
        """Calculates the mean squared error between observed values in the
        data and predictions from UV^T.

        MSE = \sum_{(i,j) \in \Omega} (data_{ij} U_i \dot V_j)^2
        where Omega is the set of observed entries in training_data.

        Args:
            data: A matrix of observations of dense_shape [N, M]
            UY: A dense Tensor of shape [N, k] where k is the embedding
            dimension, such that U_i is the embedding of element i.
            V: A dense Tensor of shape [M, k] where k is the embedding
            dimension, such that V_j is the embedding of element j.
        Returns:
            A scalar Tensor representing the MSE between the true ratings and the
            model's predictions.
        """
        predictions = tf.gather_nd(
            tf.matmul(U, V, transpose_b=True),
            data.indices)
        loss = tf.losses.mean_squared_error(data.values, predictions)
        return loss

    def train(self, data: np.ndarray, num_iterations: int, learning_rate: float):
        """Trains the model."""
        # preliminaries
        optimizer = tf.compat.v1.train.GradientDescentOptimizer
        loss = self._calculate_mean_square_error(data, self._U, self._V)
        metrics = [{
            'train_error': loss
        }]

        with loss.graph.as_default():
            opt = optimizer(learning_rate)
            # TODO what is impact of defining loss lcoally rather than class var
            train_op = opt.minimize(loss)
            local_init_op = tf.group(
                tf.compat.v1.variables_initializer(opt.variables()),
                tf.compat.v1.local_variables_initializer())
            if self._session is None:
                self._session = tf.compat.v1.Session()
                with self._session.as_default():
                    self._session.run(tf.compat.v1.global_variables_initializer())
                    self._session.run(tf.compat.v1.tables_initializer())
                    tf.compat.v1.train.start_queue_runners()

        with self._session.as_default():
            local_init_op.run()
            iterations = []
            # metrics = self._metrics or ({},)
            metrics_vals = [collections.defaultdict(list) for _ in metrics]

            # Train and append results.
            for i in range(num_iterations + 1):
                _, results = self._session.run((train_op, metrics))
                if (i % 10 == 0) or i == num_iterations:
                    print("\r iteration %d: " % i + ", ".join(
                            ["%s=%f" % (k, v) for r in results for k, v in r.items()]),
                            end='')
                    iterations.append(i)
                    for metric_val, result in zip(metrics_vals, results):
                        for k, v in result.items():
                            metric_val[k].append(v)

            for k, v in self._embedding_vars.items():
                self._embeddings[k] = v.eval()

        return results

 