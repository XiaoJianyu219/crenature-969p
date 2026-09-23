import numpy as np
import pytest

from crenature.geometry import NUM_KINDS, corolla_outline, grow_stem, rotate, stem_style


@pytest.mark.parametrize("kind", range(NUM_KINDS))
def test_corolla_is_small_closed_curve(kind):
    dx, dy = corolla_outline(kind, np.random.default_rng(0))
    assert dx.shape == dy.shape and dx.size >= 100
    assert np.hypot(dx, dy).max() < 0.06  # stays a small flower on the unit canvas
    # parametrised over [0, 2pi]: the outline closes on itself (up to kind 0's noise)
    assert np.hypot(dx[0] - dx[-1], dy[0] - dy[-1]) < 0.01


def test_unknown_kind_rejected():
    with pytest.raises(ValueError):
        corolla_outline(NUM_KINDS, np.random.default_rng(0))


def test_rotation_preserves_distance_and_quarter_turn():
    rng = np.random.default_rng(1)
    dx, dy = rng.normal(size=(2, 50))
    rx, ry = rotate(dx, dy, 0.7)
    np.testing.assert_allclose(np.hypot(rx, ry), np.hypot(dx, dy))
    qx, qy = rotate(np.array([1.0]), np.array([0.0]), np.pi / 2)
    np.testing.assert_allclose([qx[0], qy[0]], [0, 1], atol=1e-12)


def test_stem_walk_step_lengths_and_turns():
    stem = grow_stem(np.random.default_rng(2), 10)
    assert stem.shape == (11, 2)
    steps = np.diff(stem, axis=0)
    lengths = np.hypot(*steps.T)
    assert np.all((lengths >= 0.01) & (lengths <= 0.04))
    headings = np.unwrap(np.arctan2(steps[:, 1], steps[:, 0]))
    assert np.all(np.abs(np.diff(headings)) <= np.pi / 6 + 1e-9)


def test_stem_style_gets_lighter_and_thinner():
    colors, widths = stem_style(5)
    assert colors.shape == (5, 3)
    assert widths[0] == 3 and np.all(np.diff(widths) < 0)
    assert np.all(np.diff(colors, axis=0) > 0)
