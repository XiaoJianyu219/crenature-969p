"""The canvas: particle background, growing flowers and error texts.

All randomness is drawn up front in `Scene.__init__`; `update(frame)` only
reveals what was pre-computed. This is what keeps the full-screen animation
smooth on a mini PC: the 3 x 100k-point background is drawn once and kept
as the blitting background, and each frame only touches a few artists.
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

from .config import Config
from .geometry import NUM_KINDS, corolla_outline, grow_stem, rotate, stem_style

# (smallest size range, largest size range, alpha range, alpha of highlighted dots)
BACKGROUND_LAYERS = (
    ((50, 200), (200, 500), (0.1, 0.5), (0.5, 1.0)),  # large soft blobs
    ((5, 20), (20, 50), (0.1, 0.5), (0.5, 1.0)),      # medium dots
    ((1, 2), (2, 5), (0.5, 1.0), (0.9, 1.0)),         # fine grain
)

# Flower heart: three concentric discs, drawn from the largest down
HEART = ((0.006, "yellow"), (0.004, "gold"), (0.002, "orange"))


def draw_background(ax, rng: np.random.Generator, cfg: Config):
    """Three scatter layers over the same random points with one random colormap."""
    n = cfg.num_dots
    x, y = rng.random(n), rng.random(n)
    lo, hi = np.sort(rng.uniform(0, 1, 2))  # a random slice of the colormap
    values = rng.uniform(lo, hi, n)
    cmap = str(rng.choice(plt.colormaps()))

    for size_lo, size_hi, alpha_range, highlight_range in BACKGROUND_LAYERS:
        sizes = rng.uniform(rng.uniform(*size_lo), rng.uniform(*size_hi), n)
        alphas = rng.uniform(*alpha_range, n)
        k = min(cfg.highlighted_dots, n)
        if k:
            largest = np.argpartition(sizes, -k)[-k:]
            alphas[largest] = rng.uniform(*highlight_range, k)
        ax.scatter(x, y, s=sizes, c=values, cmap=cmap, alpha=alphas, marker="o")
    return cmap


@dataclass
class Flower:
    stem: np.ndarray       # (stem_steps + 1, 2)
    outline: tuple         # absolute (fx, fy) of the fully open corolla
    color: np.ndarray      # RGB
    kind: int

    @property
    def center(self):
        return self.stem[-1]


def build_flowers(rng: np.random.Generator, cfg: Config):
    flowers = []
    for _ in range(cfg.num_flowers):
        stem = grow_stem(rng, cfg.stem_steps)
        color = rng.random(3)
        kind = int(rng.integers(0, NUM_KINDS))
        # Align the corolla with the direction of the last stem segment
        (x1, y1), (x2, y2) = stem[-2], stem[-1]
        dx, dy = rotate(*corolla_outline(kind, rng), np.arctan2(y2 - y1, x2 - x1))
        flowers.append(Flower(stem, (x2 + dx, y2 + dy), color, kind))
    return flowers


def build_error_texts(rng: np.random.Generator, n: int):
    """'Error 666' ... 'Error 999': the only digits are 6 and 9, a nod to @969p."""
    texts = []
    for _ in range(n):
        digits = "".join(rng.choice(["6", "9"], 3))
        texts.append(dict(
            x=rng.uniform(0, 1), y=rng.uniform(0, 1),
            s=f"Error {digits}",
            fontsize=int(rng.integers(10, 41)),
            fontweight=str(rng.choice(["normal", "bold"])),
            family=str(rng.choice(["serif", "sans-serif", "monospace"])),
            color=str(rng.uniform(0.1, 1)),  # grey level
        ))
    return texts


class Scene:
    def __init__(self, ax, cfg: Config, rng: np.random.Generator):
        self.ax = ax
        self.cfg = cfg
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        self.colormap = draw_background(ax, rng, cfg)
        self.flowers = build_flowers(rng, cfg)
        self.errors = build_error_texts(rng, cfg.num_errors)

        # One LineCollection per stem, updated in place while it grows
        self.stems = [ax.add_collection(LineCollection([], capstyle="round")) for _ in self.flowers]
        self.petals = []
        self.hearts = []
        self.texts = []

    @property
    def total_frames(self):
        return self.cfg.total_frames

    def animated_artists(self):
        return self.stems + self.petals + self.hearts + self.texts

    def update(self, frame: int):
        cfg = self.cfg
        if frame < cfg.flower_frames:
            index, step = divmod(frame, cfg.frames_per_flower)
            flower = self.flowers[index]
            if step < cfg.stem_steps:
                self._grow_stem(index, step + 1)
            else:
                self._open_corolla(flower, step - cfg.stem_steps + 1)
        elif frame < cfg.total_frames:
            self._show_error(frame - cfg.flower_frames)
        return self.animated_artists()

    def _grow_stem(self, index: int, num_segments: int):
        points = self.flowers[index].stem[: num_segments + 1]
        colors, widths = stem_style(num_segments)
        stem = self.stems[index]
        stem.set_segments(np.stack([points[:-1], points[1:]], axis=1))
        stem.set_colors(colors)
        stem.set_linewidths(widths)

    def _open_corolla(self, flower: Flower, stage: int):
        # Each stage adds a larger translucent copy; the overlap produces
        # the layered, more saturated heart of the flower.
        scale = stage / self.cfg.flower_steps
        cx, cy = flower.center
        fx, fy = flower.outline
        (petal,) = self.ax.fill(cx + (fx - cx) * scale, cy + (fy - cy) * scale,
                                color=flower.color, alpha=0.8)
        self.petals.append(petal)
        if stage == self.cfg.flower_steps:
            for radius, color in HEART:
                disc = Circle((cx, cy), radius, facecolor=color, edgecolor="black",
                              linewidth=0.3, alpha=0.9, zorder=10)
                self.hearts.append(self.ax.add_patch(disc))

    def _show_error(self, i: int):
        props = dict(self.errors[i])
        text = self.ax.text(props.pop("x"), props.pop("y"), props.pop("s"),
                            transform=self.ax.transAxes, ha="center", va="center", **props)
        text.set_alpha(min(1.0, i / 10 + 0.1))  # later texts are more opaque
        self.texts.append(text)
