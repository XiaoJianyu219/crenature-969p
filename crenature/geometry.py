"""Pure geometry: corolla outlines, rotation and stem random walks.

Coordinates live in the unit square of a 16:9 canvas, which is why the
vertical component of some shapes is stretched by 16/9 to look round.
"""

import numpy as np

ASPECT = 16 / 9
NUM_KINDS = 3


def corolla_outline(kind: int, rng: np.random.Generator):
    """Return the (dx, dy) outline of a corolla centred on the origin.

    kind 0: rose curve |sin 3t + 0.5 sin 6t| with radial noise (6 petals)
    kind 1: two-lobed heart-like curve, orientation picked at random
    kind 2: 5-fold star from a sum of harmonics with a modulated radius
    """
    if kind == 0:
        theta = np.linspace(0, 2 * np.pi, 1000)
        r = np.abs(np.sin(3 * theta) + 0.5 * np.sin(6 * theta)) + 0.1 * rng.random(theta.size)
        r = r / r.max() * rng.uniform(0.02, 0.03)
        return r * np.cos(theta), r * np.sin(theta)

    if kind == 1:
        t = np.linspace(0, 2 * np.pi, 100)
        orientation = rng.integers(-1, 2)  # -1, 0 or 1
        r = 0.015
        dx = 0.5 * r * (np.sin(t) + orientation * np.sin(2 * t))
        dy = ASPECT * 0.5 * r * (np.cos(t) - orientation * np.cos(2 * t))
        return dx, dy

    if kind == 2:
        theta = np.linspace(0, 2 * np.pi, 1000)
        r = 0.015 * (1 + 0.3 * np.sin(5 * theta))
        dx = 0.5 * r * (0.5 * np.sin(theta) - 0.5 * np.sin(2 * theta) + np.sin(5 * theta))
        dy = ASPECT * 0.5 * r * (0.5 * np.cos(theta) + 0.5 * np.cos(2 * theta) + np.cos(5 * theta))
        return dx, dy

    raise ValueError(f"unknown corolla kind: {kind}")


def rotate(dx, dy, angle: float):
    """Rotate points around the origin by `angle` radians."""
    c, s = np.cos(angle), np.sin(angle)
    return dx * c - dy * s, dx * s + dy * c


def grow_stem(rng: np.random.Generator, steps: int):
    """Random walk with bounded turning: returns an array of shape (steps + 1, 2).

    Each step has length U(0.01, 0.04) and turns by U(-30deg, +30deg),
    which gives the gently curving stems.
    """
    x, y = rng.uniform(0.1, 0.9, 2)
    angle = rng.uniform(0, 2 * np.pi)
    points = [(x, y)]
    for _ in range(steps):
        length = rng.uniform(0.01, 0.04)
        angle += rng.uniform(-np.pi / 6, np.pi / 6)
        x += length * np.cos(angle)
        y += length * np.sin(angle)
        points.append((x, y))
    return np.array(points)


def stem_style(num_segments: int):
    """Colour and width of each stem segment: dark/thick at the root,
    lighter/thinner towards the tip."""
    t = np.arange(num_segments) / num_segments
    colors = np.column_stack([0.1 + 0.2 * t, 0.5 + 0.4 * t, 0.1 + 0.3 * t])
    widths = 3 - 2 * t
    return colors, widths
