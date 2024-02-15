# Code adapted from https://colab.research.google.com/github/google/eng-edu/blob/main/ml/recommendation-systems/recommendation-systems.ipynb?utm_source=ss-recommendation-systems&utm_campaign=colab-external&utm_medium=referral&utm_content=recommendation-systems

import collections
import tensorflow as tf

tf.compat.v1.disable_v2_behavior()
tf.compat.v1.disable_eager_execution()

class FactorizationRecommender:
    """A matrix factorization collaborative filtering recommender model."""

    # Abstraction function:
    #   AF(m, n, k) = a matrix factorization recommender model
    #       on m entities, n items to recommend, and 
    #       embedding dimension k (a hyperparameter)
    # Rep invariant:
    #   - U.shape[1] == V.shape[1]
    #   - U and V are 2D
    #   - U.shape[0] > 0
    #   - U.shape[1] > 0
    #   - V.shape[0] > 0
    #   - V.shape[1] > 0
    # Safety from rep exposure:
    #   - U and V are private and not reassigned

    def __init__(self, m, n, k):
        """Initializes a FactorizationRecommender object.

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

        self._checkrep()

    def _checkrep(self):
        """Asserts the rep invariant."""
        #   - U.shape[1] == V.shape[1]
        assert self._U.shape[1] == self._V.shape[1]
        #   - U and V are 2D
        assert len(self._U.shape) == 2
        assert len(self._V.shape) == 2
        #   - U.shape[0] > 0
        assert self._U.shape[0] > 0
        #   - U.shape[1] > 0
        assert self._U.shape[1] > 0
        #   - V.shape[0] > 0
        assert self._V.shape[0] > 0
        #   - V.shape[1] > 0
        assert self._V.shape[1] > 0

    @tf.function
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

    def fit(self, data: tf.SparseTensor, num_iterations: int, learning_rate: float):
        """Fits the model to data.
        
        Args:
            data: an mxn tensor of training data
            num_iterations: number of training iterations to execute
            learning_rate: the learning rate
        """
        # preliminaries
        optimizer = tf.compat.v1.train.GradientDescentOptimizer

        loss = self._calculate_mean_square_error(data, self._U, self._V)
        metrics = [{
            'train_error': loss,
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
                    iterations.append(i)
                    for metric_val, result in zip(metrics_vals, results):
                        for k, v in result.items():
                            metric_val[k].append(v)
    
    def evaluate(self, test_data: tf.SparseTensor) -> float:
        """Evaluates the solution.

        Requires that the model has been trained.
        
        Args:
            test_data: mxn tensor on which to evaluate the model.
                Requires that mxn match the dimensions of the training tensor and
                each row i and column j correspond to the same entity and item
                in the training tensor, respectively.

        Returns: the mean squared error of the test data.
        """

        with self._session as sess:
            error = self._calculate_mean_square_error(test_data, self._U, self._V).eval()

        return error
 