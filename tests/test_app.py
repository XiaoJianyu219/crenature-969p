import numpy as np
from PIL import Image, ImageSequence

from crenature.app import main

TINY = ["--seed", "3", "--dots", "200", "--flowers", "2", "--errors", "3", "--dpi", "12"]


def test_snapshot_writes_png(tmp_path):
    out = tmp_path / "shot.png"
    assert main(TINY + ["--snapshot", str(out)]) == 0
    assert Image.open(out).size == (192, 108)


def test_gif_shows_growth_not_just_the_final_picture(tmp_path):
    out = tmp_path / "growth.gif"
    assert main(TINY + ["--gif", str(out), "--gif-step", "5"]) == 0
    frames = [np.asarray(f.convert("RGB"), dtype=int) for f in ImageSequence.Iterator(Image.open(out))]
    assert len(frames) >= 10
    # skipped frames are applied incrementally: the GIF must change over time instead of
    # showing the finished picture from the first frame on
    assert (frames[0] != frames[-1]).any()
    assert len({f.tobytes() for f in frames}) > len(frames) // 2
