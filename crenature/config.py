"""Tunable parameters. Defaults reproduce the exhibited version."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    # Particle background: three layers share the same positions/colours,
    # so the number of drawn points is 3 * num_dots.
    num_dots: int = 100_000
    highlighted_dots: int = 100  # largest dots of each layer get a higher alpha

    # Growing flowers
    num_flowers: int = 20
    stem_steps: int = 10    # frames used to grow one stem
    flower_steps: int = 10  # frames used to open one corolla

    # "Error 666/669/.../999" texts appearing after the flowers
    num_errors: int = 100

    # Playback
    interval_ms: int = 150      # delay between frames
    duration_s: float = 160.0   # close the window after this time (0 = never)
    fullscreen: bool = True

    seed: Optional[int] = None

    @property
    def frames_per_flower(self) -> int:
        return self.stem_steps + self.flower_steps

    @property
    def flower_frames(self) -> int:
        return self.num_flowers * self.frames_per_flower

    @property
    def total_frames(self) -> int:
        return self.flower_frames + self.num_errors
