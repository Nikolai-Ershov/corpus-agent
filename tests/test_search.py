from index.search import cos
import pytest


def test_cos_same_direction():
    result = cos([3, 4], [6, 8])
    assert result == pytest.approx(1)


def test_cos_perpendicular():
    result = cos([3, 4], [4, -3])
    assert result == pytest.approx(0)
