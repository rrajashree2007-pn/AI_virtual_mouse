"""
gesture_classifier.py
An optional, trainable classifier for custom gestures using scikit-learn's
KNeighborsClassifier. This is a step up from the simple nearest-vector
matching in gestures/custom_gestures.py -- useful once you have many
samples across many gesture classes and want more robust recognition.

Usage:
    clf = GestureClassifier()
    clf.add_training_example(landmark_vector, "thumbs_up")
    ... (many examples across classes) ...
    clf.fit()
    clf.save()
    ...
    clf.load()
    label = clf.predict(landmark_vector)
"""

import os

try:
    from sklearn.neighbors import KNeighborsClassifier
    import joblib
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False


class GestureClassifier:
    def __init__(self, model_path=None, n_neighbors=3):
        self.model_path = model_path
        self.n_neighbors = n_neighbors
        self._model = None
        self._X, self._y = [], []
        self.is_fitted = False

    def add_training_example(self, feature_vector, label):
        self._X.append(feature_vector)
        self._y.append(label)

    def fit(self):
        if not _SKLEARN_AVAILABLE or len(set(self._y)) < 2:
            return False
        k = min(self.n_neighbors, len(self._X))
        self._model = KNeighborsClassifier(n_neighbors=k)
        self._model.fit(self._X, self._y)
        self.is_fitted = True
        return True

    def predict(self, feature_vector):
        if not self.is_fitted or self._model is None:
            return None
        return self._model.predict([feature_vector])[0]

    def predict_proba_top(self, feature_vector):
        """Returns (label, confidence) for the top predicted class."""
        if not self.is_fitted or self._model is None:
            return None, 0.0
        probs = self._model.predict_proba([feature_vector])[0]
        classes = self._model.classes_
        best_idx = probs.argmax()
        return classes[best_idx], float(probs[best_idx])

    def save(self, path=None):
        path = path or self.model_path
        if not _SKLEARN_AVAILABLE or not path or self._model is None:
            return False
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self._model, path)
        return True

    def load(self, path=None):
        path = path or self.model_path
        if not _SKLEARN_AVAILABLE or not path or not os.path.exists(path):
            return False
        self._model = joblib.load(path)
        self.is_fitted = True
        return True
