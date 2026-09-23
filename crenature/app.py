"""Command-line entry point: `python -m crenature [options]`."""

import argparse
import sys

import numpy as np

from .config import Config


def parse_args(argv=None):
    d = Config()
    p = argparse.ArgumentParser(
        prog="python -m crenature",
        description="Crenature @969p - generative flowers growing on a particle field.",
    )
    p.add_argument("--seed", type=int, default=None, help="random seed (same seed -> same picture)")
    p.add_argument("--dots", type=int, default=d.num_dots, help=f"points per background layer (default {d.num_dots})")
    p.add_argument("--flowers", type=int, default=d.num_flowers, help=f"number of flowers (default {d.num_flowers})")
    p.add_argument("--errors", type=int, default=d.num_errors, help=f"number of 'Error 969' texts (default {d.num_errors})")
    p.add_argument("--interval", type=int, default=d.interval_ms, help=f"ms between frames (default {d.interval_ms})")
    p.add_argument("--duration", type=float, default=d.duration_s,
                   help=f"seconds before the window closes itself, 0 = never (default {d.duration_s:g})")
    p.add_argument("--windowed", action="store_true", help="do not switch to full screen")

    out = p.add_mutually_exclusive_group()
    out.add_argument("--snapshot", metavar="PNG", help="render the final picture to a file instead of opening a window")
    out.add_argument("--gif", metavar="GIF", help="save the animation as a GIF instead of opening a window")
    p.add_argument("--gif-step", type=int, default=5, help="keep one frame out of N, so the GIF plays N times faster (default 5)")
    p.add_argument("--dpi", type=int, default=100, help="resolution of --snapshot / --gif (canvas is 16x9 inches)")
    return p.parse_args(argv)


def make_config(args) -> Config:
    return Config(
        num_dots=args.dots, num_flowers=args.flowers, num_errors=args.errors,
        interval_ms=args.interval, duration_s=args.duration,
        fullscreen=not args.windowed, seed=args.seed,
    )


def export_gif(fig, scene, path, step, interval_ms, hold_ms=3000, colors=128):
    """Write the growth as a GIF, keeping one frame out of `step`.

    Same trick as the live animation: the background is rendered once and
    restored for every frame. All frames share one palette so that the static
    background encodes identically and GIF delta frames stay small.
    """
    from PIL import Image

    canvas = fig.canvas
    for artist in scene.animated_artists():
        artist.set_animated(True)
    canvas.draw()
    background = canvas.copy_from_bbox(fig.bbox)

    targets = sorted(set(range(0, scene.total_frames, max(1, step))) | {scene.total_frames - 1})
    images, done = [], -1
    for target in targets:
        for frame in range(done + 1, target + 1):  # skipped frames still have to be applied
            scene.update(frame)
        done = target
        canvas.restore_region(background)
        for artist in scene.animated_artists():
            fig.draw_artist(artist)
        images.append(Image.fromarray(np.asarray(canvas.buffer_rgba())[..., :3].copy()))

    palette = images[-1].quantize(colors=colors)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [interval_ms] * (len(frames) - 1) + [hold_ms]  # skipping frames = faster playback
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    return len(frames)


def main(argv=None):
    args = parse_args(argv)
    cfg = make_config(args)
    if args.snapshot or args.gif:
        import matplotlib
        matplotlib.use("Agg")  # no window needed
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    from .scene import Scene

    plt.rcParams["toolbar"] = "None"
    fig = plt.figure(figsize=(16, 9), dpi=args.dpi if (args.snapshot or args.gif) else 100)
    ax = fig.add_axes((0, 0, 1, 1))
    scene = Scene(ax, cfg, np.random.default_rng(cfg.seed))

    if args.snapshot:
        for frame in range(scene.total_frames):
            scene.update(frame)
        fig.savefig(args.snapshot, dpi=args.dpi)
        print(f"saved {args.snapshot} (colormap: {scene.colormap})")
        return 0

    if args.gif:
        count = export_gif(fig, scene, args.gif, args.gif_step, cfg.interval_ms)
        print(f"saved {args.gif} ({count} frames)")
        return 0

    # Interactive / exhibition mode
    if cfg.fullscreen:
        try:
            fig.canvas.manager.full_screen_toggle()
        except AttributeError:  # some backends have no window manager
            pass

    ani = FuncAnimation(fig, scene.update, frames=scene.total_frames,
                        init_func=scene.animated_artists, interval=cfg.interval_ms,
                        blit=True, repeat=False)

    if cfg.duration_s > 0:  # let the installation return to idle on its own
        timer = fig.canvas.new_timer(interval=int(cfg.duration_s * 1000))
        timer.single_shot = True
        timer.add_callback(plt.close, fig)
        timer.start()

    plt.show()
    del ani
    return 0


if __name__ == "__main__":
    sys.exit(main())
