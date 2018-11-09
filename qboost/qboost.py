#    Copyright 2018 D-Wave Systems Inc.

#    Licensed under the Apache License, Version 2.0 (the "License")
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http: // www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, AdaBoostRegressor
import numpy as np
from copy import deepcopy

def weight_penalty(prediction, y, percent = 0.1): 
    """
    For Regression we have to introduce a metric to penalize differences of the prediction from the label y.
    Percent gives the maximum deviation of the prediction from the label that is not penalized.
    """
    diff = np.abs(prediction-y)
    min_ = diff.min()
    max_ = diff.max()
    norm = (diff-min_)/(max_-min_)
    norm = 1.0*(norm  < percent)  
    return norm

class WeakClassifiers(object):
    """
    Weak Classifiers based on DecisionTree
    """

    def __init__(self, n_estimators=50, max_depth=3):
        self.n_estimators = n_estimators
        self.estimators_ = []
        self.max_depth = max_depth
        self.__construct_wc()

    def __construct_wc(self):

        self.estimators_ = [DecisionTreeClassifier(max_depth=self.max_depth,
                                                   random_state=np.random.randint(1000000,10000000))
                            for _ in range(self.n_estimators)]

    def fit(self, X, y):
        """
        fit estimators
        :param X:
        :param y:
        :return:
        """

        self.estimator_weights = np.zeros(self.n_estimators)

        d = np.ones(len(X)) / len(X)
        for i, h in enumerate(self.estimators_):
            h.fit(X, y, sample_weight=d)
            pred = h.predict(X)
            eps = d.dot(pred != y)
            if eps == 0: # to prevent divided by zero error
                eps = 1e-20
            w = (np.log(1 - eps) - np.log(eps)) / 2
            d = d * np.exp(- w * y * pred)
            d = d / d.sum()
            self.estimator_weights[i] = w

    def predict(self, X):
        """
        predict label of X
        :param X:
        :return:
        """

        if not hasattr(self, 'estimator_weights'):
            raise Exception('Not Fitted Error!')

        y = np.zeros(len(X))

        for (h, w) in zip(self.estimators_, self.estimator_weights):
            y += w * h.predict(X)

        y = np.sign(y)

        return y

    def copy(self):

        classifier = WeakClassifiers(n_estimators=self.n_estimators, max_depth=self.max_depth)
        classifier.estimators_ = deepcopy(self.estimators_)
        if hasattr(self, 'estimator_weights'):
            classifier.estimator_weights = np.array(self.estimator_weights)

        return classifier


class QBoostClassifier(WeakClassifiers):
    """
    Qboost Classifier
    """
    def __init__(self, n_estimators=50, max_depth=3):
        super(QBoostClassifier, self).__init__(n_estimators=n_estimators,
                                              max_depth=max_depth)

    def fit(self, X, y, sampler, lmd=0.2, **kwargs):

        n_data = len(X)

        # step 1: fit weak classifiers
        super(QBoostClassifier, self).fit(X, y)

        # step 2: create QUBO
        hij = []
        for h in self.estimators_:
            hij.append(h.predict(X))

        hij = np.array(hij)
        # scale hij to [-1/N, 1/N]
        hij = 1. * hij / self.n_estimators

        ## Create QUBO
        qii = n_data * 1. / (self.n_estimators ** 2) + lmd - 2 * np.dot(hij, y)
        qij = np.dot(hij, hij.T)
        Q = dict()
        Q.update(dict(((k, k), v) for (k, v) in enumerate(qii)))
        for i in range(self.n_estimators):
            for j in range(i + 1, self.n_estimators):
                Q[(i, j)] = qij[i, j]

        # step 3: optimize QUBO
        res = sampler.sample_qubo(Q, **kwargs)
        samples = np.array([[samp[k] for k in range(self.n_estimators)] for samp in res])

        # take the optimal solution as estimator weights
        self.estimator_weights = samples[0]

    def predict(self, X):
        n_data = len(X)
        pred_all = np.array([h.predict(X) for h in self.estimators_])
        temp1 = np.dot(self.estimator_weights, pred_all)
        T1 = np.sum(temp1, axis=0) / (n_data * self.n_estimators * 1.)
        y = np.sign(temp1 - T1) #binary classes are either 1 or -1

        return y


class WeakRegressor(object):
    """
    Weak Regressor based on DecisionTreeRegressor
    """

    def __init__(self, n_estimators=50, max_depth=3, DT = True, Ada = False, ):
        self.n_estimators = n_estimators
        self.estimators_ = []
        self.max_depth = max_depth
        self.__construct_wc()

    def __construct_wc(self):

        self.estimators_ = [DecisionTreeRegressor(max_depth=self.max_depth,
                                                   random_state=np.random.randint(1000000,10000000))
                            for _ in range(self.n_estimators)]
#        self.estimators_ = [AdaBoostRegressor(random_state=np.random.randint(1000000,10000000))
#                            for _ in range(self.n_estimators)]

    def fit(self, X, y):
        """
        fit estimators
        :param X:
        :param y:
        :return:
        """

        self.estimator_weights = np.zeros(self.n_estimators) #initialize all estimator weights to zero

        d = np.ones(len(X)) / len(X)
        for i, h in enumerate(self.estimators_): #fit all estimators
            h.fit(X, y, sample_weight=d)
            pred = h.predict(X)
            # For classification one simply compares (pred != y)
            # For regression we have to define another metric
            norm = weight_penalty(pred, y)
            eps = d.dot(norm)
            if eps == 0: # to prevent divided by zero error
                eps = 1e-20
            w = (np.log(1 - eps) - np.log(eps)) / 2
            d = d * np.exp(- w * y * pred)
            d = d / d.sum()
            self.estimator_weights[i] = w

    def predict(self, X):
        """
        predict label of X
        :param X:
        :return:
        """

        if not hasattr(self, 'estimator_weights'):
            raise Exception('Not Fitted Error!')

        y = np.zeros(len(X))

        for (h, w) in zip(self.estimators_, self.estimator_weights):
            y += w * h.predict(X)

        y = np.sign(y)

        return y

    def copy(self):

        classifier = WeakRegressor(n_estimators=self.n_estimators, max_depth=self.max_depth)
        classifier.estimators_ = deepcopy(self.estimators_)
        if hasattr(self, 'estimator_weights'):
            classifier.estimator_weights = np.array(self.estimator_weights)

        return classifier


class QBoostRegressor(WeakRegressor):
    """
    Qboost Regressor
    """
    def __init__(self, n_estimators=50, max_depth=3):
        super(QBoostRegressor, self).__init__(n_estimators=n_estimators,
                                              max_depth=max_depth)
        self.Qu = 0.0
        self.hij = 0.0
        self.var1 = 0.0
        self.qij = 0.0

    def fit(self, X, y, sampler, lmd=0.2, **kwargs):

        n_data = len(X)

        # step 1: fit weak classifiers
        super(QBoostRegressor, self).fit(X, y)

        # step 2: create QUBO
        hij = []
        for h in self.estimators_:
            hij.append(h.predict(X))

        hij = np.array(hij)
        # scale hij to [-1/N, 1/N]
        hij = 1. * hij / self.n_estimators
        self.hij = hij
        ## Create QUBO
        qii = n_data * 1. / (self.n_estimators ** 2) + lmd - 2 * np.dot(hij, y)
        self.var1 = qii
        qij = np.dot(hij, hij.T)
        self.qij = qij
        Q = dict()
        Q.update(dict(((k, k), v) for (k, v) in enumerate(qii)))
        for i in range(self.n_estimators):
            for j in range(i + 1, self.n_estimators):
                Q[(i, j)] = qij[i, j]

        self.Qu = Q
        # step 3: optimize QUBO
        res = sampler.sample_qubo(Q, **kwargs)
        samples = np.array([[samp[k] for k in range(self.n_estimators)] for samp in res])

        # take the optimal solution as estimator weights
        # self.estimator_weights = np.mean(samples, axis=0)
        self.estimator_weights = samples[0]

    def predict(self, X):
        n_data = len(X)
        pred_all = np.array([h.predict(X) for h in self.estimators_])
        temp1 = np.dot(self.estimator_weights, pred_all)
        norm = np.sum(self.estimator_weights)
        if norm > 0:
            y = temp1 / norm
        else:
            y = temp1
        return y


class QboostPlus(object):
    """
    Only for Classifiers
    Quantum boost existing (weak) classifiers
    """

    def __init__(self, weak_classifier_list):
        self.estimators_ = weak_classifier_list
        self.n_estimators = len(self.estimators_)
        self.estimator_weights = np.ones(self.n_estimators) #estimator weights will be binary (Dwave output)

    def fit(self, X, y, sampler, lmd=0.2, **kwargs):

        n_data = len(X)
        # step 1: create QUBO
        hij = []
        for h in self.estimators_:
            hij.append(h.predict(X))

        hij = np.array(hij)
        # scale hij to [-1/N, 1/N]
        hij = 1. * hij / self.n_estimators

        ## Create QUBO
        qii = n_data * 1. / (self.n_estimators ** 2) + lmd - 2 * np.dot(hij, y)
        qij = np.dot(hij, hij.T)
        Q = dict()
        Q.update(dict(((k, k), v) for (k, v) in enumerate(qii)))
        for i in range(self.n_estimators):
            for j in range(i + 1, self.n_estimators):
                Q[(i, j)] = qij[i, j]

        # step 3: optimize QUBO
        res = sampler.sample_qubo(Q, **kwargs)
        samples = np.array([[samp[k] for k in range(self.n_estimators)] for samp in res])

        # take the optimal solution as estimator weights
        self.estimator_weights = samples[0]

    def predict(self, X):

        n_data = len(X)
        T = 0
        y = np.zeros(n_data)
        for i, h in enumerate(self.estimators_):
            y0 = self.estimator_weights[i] * h.predict(X)  # prediction of weak classifier
            y += y0
            T += np.sum(y0)

        y = np.sign(y - T / (n_data*self.n_estimators))

        return y

class QboostPlusRegression(object):
    """
    Quantum boost existing (weak) regressors
    """

    def __init__(self, weak_Regressor_list):
        self.estimators_ = weak_Regressor_list
        self.n_estimators = len(self.estimators_)
        self.estimator_weights = np.ones(self.n_estimators)

    def fit(self, X, y, sampler, lmd=0.2, **kwargs):

        n_data = len(X)
        # step 1: create QUBO
        hij = []
        for h in self.estimators_:
            hij.append(h.predict(X))

        hij = np.array(hij)
        # scale hij to [-1/N, 1/N]
        hij = 1. * hij / self.n_estimators

        ## Create QUBO
        qii = n_data * 1. / (self.n_estimators ** 2) + lmd - 2 * np.dot(hij, y)
        qij = np.dot(hij, hij.T)
        Q = dict()
        Q.update(dict(((k, k), v) for (k, v) in enumerate(qii)))
        for i in range(self.n_estimators):
            for j in range(i + 1, self.n_estimators):
                Q[(i, j)] = qij[i, j]

        # step 3: optimize QUBO
        res = sampler.sample_qubo(Q, **kwargs)
        samples = np.array([[samp[k] for k in range(self.n_estimators)] for samp in res])

        # take the optimal solution as estimator weights
        self.estimator_weights = samples[0]

    def predict(self, X):

        n_data = len(X)
        T = 0
        y = np.zeros(n_data)
        for i, h in enumerate(self.estimators_):
            y0 = self.estimator_weights[i] * h.predict(X)  # prediction of weak classifier
            y += y0
            T += np.sum(y0)

        norm = np.sum(self.estimator_weights)
        if norm > 0:
            y = y / norm
        else:
            y = y

        return y

