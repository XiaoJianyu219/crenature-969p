#!/usr/bin/env python3
"""Raspberry Pi side of the installation.

A PIR motion sensor on a GPIO pin detects a visitor; the Pi then asks the
Windows mini PC (over key-based SSH) to run the scheduled task that starts
the animation in the logged-in desktop session.

Usage on the Pi:
    python3 sensor_trigger.py --host 192.168.0.14 --user "exhibit" --task crenature
    python3 sensor_trigger.py --host ... --dry-run   # press Enter to simulate motion

Settings can also come from environment variables:
    CRENATURE_HOST, CRENATURE_USER, CRENATURE_TASK, CRENATURE_PIN, CRENATURE_COOLDOWN

Note: comments are kept ASCII-only on purpose; the Pi image we used choked on
non-ASCII characters in source files.
"""

import argparse
import os
import subprocess
import sys
import time


class Cooldown:
    """Accept an event at most once every `seconds` (debounces the PIR sensor)."""

    def __init__(self, seconds, clock=time.monotonic):
        self.seconds = seconds
        self.clock = clock
        self._last = None

    def ready(self):
        now = self.clock()
        if self._last is not None and now - self._last < self.seconds:
            return False
        self._last = now
        return True


def build_ssh_command(user, host, task):
    """ssh argv that runs the Windows scheduled task `task`.

    BatchMode makes ssh fail instead of waiting for a password if the key
    is not accepted, so a misconfiguration shows up in the log right away.
    """
    return [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=accept-new",
        f"{user}@{host}",
        f'schtasks /run /tn "{task}"',
    ]


def make_trigger(args, cooldown):
    command = build_ssh_command(args.user, args.host, args.task)

    def trigger():
        if not cooldown.ready():
            return
        print(time.strftime("%H:%M:%S"), "motion detected -> starting task", repr(args.task), flush=True)
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            print("  ssh timed out", flush=True)
            return
        output = (result.stdout + result.stderr).strip()
        print(f"  exit code {result.returncode}: {output}", flush=True)

    return trigger


def parse_args(argv=None):
    env = os.environ.get
    p = argparse.ArgumentParser(description="PIR sensor -> start the animation on the Windows PC")
    p.add_argument("--host", default=env("CRENATURE_HOST"), help="IP address of the Windows PC")
    p.add_argument("--user", default=env("CRENATURE_USER"), help="Windows user name (quote it if it has spaces)")
    p.add_argument("--task", default=env("CRENATURE_TASK", "crenature"), help="scheduled task name")
    p.add_argument("--pin", type=int, default=int(env("CRENATURE_PIN", "17")),
                   help="BCM GPIO number of the sensor signal (17 = physical pin 11)")
    p.add_argument("--cooldown", type=float, default=float(env("CRENATURE_COOLDOWN", "10")),
                   help="minimum seconds between two triggers")
    p.add_argument("--dry-run", action="store_true", help="no sensor: press Enter to simulate motion")
    args = p.parse_args(argv)
    if not args.host or not args.user:
        p.error("--host and --user are required (or set CRENATURE_HOST / CRENATURE_USER)")
    return args


def main(argv=None):
    args = parse_args(argv)
    trigger = make_trigger(args, Cooldown(args.cooldown))

    if args.dry_run:
        print("Ready (dry run): press Enter to simulate motion, Ctrl+C to quit")
        for _ in sys.stdin:
            trigger()
        return 0

    from gpiozero import MotionSensor  # only available on the Pi
    from signal import pause

    sensor = MotionSensor(args.pin)
    sensor.when_motion = trigger
    print(f"Ready: watching GPIO{args.pin}, target {args.user}@{args.host}", flush=True)
    pause()
    return 0


if __name__ == "__main__":
    sys.exit(main())
