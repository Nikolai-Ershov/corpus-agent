from index.search import cos
import numpy as np


def test_cos_same_direction():
    query = np.array([1.0, 0.0])
    matrix = np.array([[2.0, 0.0]])   # тот же направление, длиннее
    scores = cos(query, matrix)
    assert np.isclose(scores[0], 1.0)


def test_cos_perpendicular():
    query = np.array([1.0, 0.0])
    matrix = np.array([[0.0, 1.0]])   # перпендикуляр
    scores = cos(query, matrix)
    assert np.isclose(scores[0], 0.0)


def test_cos_multiple_rows():
    query = np.array([1.0, 0.0])
    matrix = np.array([
        [1.0, 0.0],   # совпадает → 1
        [0.0, 1.0],   # перпендикуляр → 0
        [-1.0, 0.0],  # противоположный → -1
    ])
    scores = cos(query, matrix)
    assert np.isclose(scores[0], 1.0)
    assert np.isclose(scores[1], 0.0)
    assert np.isclose(scores[2], -1.0)