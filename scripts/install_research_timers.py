#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
from pathlib import Path

EXPECTED_HOST = os.getenv("EXPECTED_RESEARCH_HOST", "admin01-NF5468M5")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIT_SOURCE = PROJECT_ROOT / "deploy" / "systemd"
UNIT_TARGET = Path("/etc/systemd/system")
UNITS = (
    "agent-evolution-daily.service",
    "agent-evolution-daily.timer",
    "agent-evolution-weekly.service",
    "agent-evolution-weekly.timer",
)


def run(*args: str) -> None:
    subprocess.run(list(args), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install and enable continuous research systemd timers on server 52.")
    parser.add_argument("--disable", action="store_true", help="Disable timers without deleting unit files.")
    args = parser.parse_args()
    if socket.gethostname() != EXPECTED_HOST:
        raise SystemExit(f"Refusing to run outside {EXPECTED_HOST}; current host is {socket.gethostname()}")
    if os.geteuid() != 0:
        raise SystemExit("Root privileges are required to manage /etc/systemd/system")
    timer_units = [unit for unit in UNITS if unit.endswith(".timer")]
    if args.disable:
        run("systemctl", "disable", "--now", *timer_units)
        return 0
    for unit in UNITS:
        source = UNIT_SOURCE / unit
        if not source.exists():
            raise SystemExit(f"Missing unit file: {source}")
        shutil.copy2(source, UNIT_TARGET / unit)
    run("systemctl", "daemon-reload")
    run("systemctl", "enable", "--now", *timer_units)
    run("systemctl", "list-timers", "--all", *timer_units)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
