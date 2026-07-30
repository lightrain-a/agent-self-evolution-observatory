#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import socket
import subprocess
from base64 import b64decode, b64encode
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HOST = os.getenv("EXPECTED_RESEARCH_HOST", "admin01-NF5468M5")
GITHUB_ED25519_LINE = "github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl"
GITHUB_ED25519_FINGERPRINT = "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"
SSH_REMOTE = "git@github.com:lightrain-a/agent-self-evolution-observatory.git"


def run(*args: str, check: bool = True, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=PROJECT_ROOT, text=True, capture_output=True,
        check=check, timeout=timeout,
    )


def openssh_fingerprint(public_key_line: str) -> str:
    parts = public_key_line.split()
    if len(parts) < 3 or parts[1] != "ssh-ed25519":
        raise ValueError("Expected an ssh-ed25519 known-host entry")
    digest = hashlib.sha256(b64decode(parts[2])).digest()
    return "SHA256:" + b64encode(digest).decode("ascii").rstrip("=")


def ensure_known_host() -> Path:
    if openssh_fingerprint(GITHUB_ED25519_LINE) != GITHUB_ED25519_FINGERPRINT:
        raise RuntimeError("Embedded GitHub host key does not match the pinned official fingerprint")
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    known_hosts = ssh_dir / "known_hosts"
    existing = known_hosts.read_text(encoding="utf-8") if known_hosts.exists() else ""
    lines = [line.strip() for line in existing.splitlines() if line.strip()]
    github_lines = [line for line in lines if line.startswith("github.com ")]
    if github_lines and GITHUB_ED25519_LINE not in github_lines:
        raise RuntimeError("github.com already has a different pinned host key; refusing to overwrite it")
    if GITHUB_ED25519_LINE not in lines:
        with known_hosts.open("a", encoding="utf-8", newline="\n") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(GITHUB_ED25519_LINE + "\n")
    known_hosts.chmod(0o600)
    return known_hosts


def verify_authentication() -> str:
    private_key = Path.home() / ".ssh" / "id_rsa"
    if not private_key.exists():
        raise RuntimeError(f"Missing SSH private key: {private_key}")
    completed = run(
        "ssh", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
        "-o", f"IdentityFile={private_key}", "-o", "StrictHostKeyChecking=yes",
        "-T", "git@github.com", check=False, timeout=30,
    )
    output = (completed.stdout + completed.stderr).strip()
    if "successfully authenticated" not in output.lower():
        raise RuntimeError(f"The server SSH key is not authenticated by GitHub: {output}")
    return output


def verify_repository_access() -> None:
    run(
        "env", f"GIT_SSH_COMMAND=ssh -o BatchMode=yes -o IdentitiesOnly=yes -i {Path.home() / '.ssh' / 'id_rsa'} -o StrictHostKeyChecking=yes",
        "git", "ls-remote", SSH_REMOTE, "refs/heads/main", check=True, timeout=45,
    )
    current = run("git", "remote", "get-url", "origin").stdout.strip()
    run("git", "remote", "set-url", "origin", SSH_REMOTE, check=True)
    try:
        run(
            "env", f"GIT_SSH_COMMAND=ssh -o BatchMode=yes -o IdentitiesOnly=yes -i {Path.home() / '.ssh' / 'id_rsa'} -o StrictHostKeyChecking=yes",
            "git", "push", "--dry-run", "origin", "HEAD:main", check=True, timeout=60,
        )
    except Exception:
        run("git", "remote", "set-url", "origin", current, check=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Pin GitHub's official host key and configure repository-scoped SSH publishing.")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    hostname = socket.gethostname()
    if hostname != EXPECTED_HOST:
        raise SystemExit(f"Refusing to run outside {EXPECTED_HOST}; current host is {hostname}")
    known_hosts = ensure_known_host()
    auth = verify_authentication()
    if not args.check_only:
        verify_repository_access()
    print(f"KNOWN_HOSTS={known_hosts}")
    print(f"FINGERPRINT={GITHUB_ED25519_FINGERPRINT}")
    print(f"AUTH={auth}")
    if not args.check_only:
        print(f"ORIGIN={SSH_REMOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
