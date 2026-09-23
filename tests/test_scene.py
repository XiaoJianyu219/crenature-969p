import matplotlib.pyplot as plt
import numpy as np
import pytest

from crenature.config import Config
from crenature.scene import Scene

SMALL = dict(num_dots=500, num_flowers=4, num_errors=7)


def make_scene(seed=0, **overrides):
    cfg = Config(seed=seed, **{**SMALL, **overrides})
    fig = plt.figure(figsize=(4, 2.25))
    ax = fig.add_axes((0, 0, 1, 1))
    return fig, Scene(ax, cfg, np.random.default_rng(seed))


def play(scene):
    for frame in range(scene.total_frames):
        artists = scene.update(frame)
    return artists


def test_default_config_matches_exhibited_version():
    cfg = Config()
    assert cfg.num_dots * 3 == 300_000
    assert cfg.total_frames == 500  # 20 flowers x (10 + 10) + 100 texts
    assert cfg.duration_s == 160


def test_full_run_creates_every_element():
    fig, scene = make_scene()
    artists = play(scene)
    cfg = scene.cfg
    assert len(scene.petals) == cfg.num_flowers * cfg.flower_steps
    assert len(scene.hearts) == cfg.num_flowers * 3
    assert len(scene.texts) == cfg.num_errors
    assert all(len(stem.get_segments()) == cfg.stem_steps for stem in scene.stems)
    # everything that changes is handed back to the animation, flower hearts included
    assert set(map(id, artists)) == set(map(id, scene.animated_artists()))
    plt.close(fig)


def test_stem_grows_one_segment_per_frame():
    fig, scene = make_scene()
    for frame in range(scene.cfg.stem_steps):
        scene.update(frame)
        assert len(scene.stems[0].get_segments()) == frame + 1
    assert scene.petals == []
    plt.close(fig)


def test_frames_past_the_end_are_harmless():
    fig, scene = make_scene()
    play(scene)
    before = len(scene.animated_artists())
    scene.update(scene.total_frames + 5)
    assert len(scene.animated_artists()) == before
    plt.close(fig)


def test_error_texts_only_use_6_and_9():
    fig, scene = make_scene(num_errors=50)
    for props in scene.errors:
        label, digits = props["s"].split()
        assert label == "Error" and len(digits) == 3 and set(digits) <= {"6", "9"}
    plt.close(fig)


def test_same_seed_same_picture():
    renders = []
    for _ in range(2):
        fig, scene = make_scene(seed=42)
        play(scene)
        fig.canvas.draw()
        renders.append(np.asarray(fig.canvas.buffer_rgba()).copy())
        plt.close(fig)
    np.testing.assert_array_equal(*renders)


def test_different_seeds_differ():
    _, a = make_scene(seed=1)
    _, b = make_scene(seed=2)
    assert not np.allclose(a.flowers[0].stem, b.flowers[0].stem)
    plt.close("all")
