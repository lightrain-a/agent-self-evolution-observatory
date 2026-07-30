from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "configure_github_ssh.py"
SPEC = importlib.util.spec_from_file_location("configure_github_ssh", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GithubSshConfigTest(unittest.TestCase):
    def test_embedded_host_key_matches_official_fingerprint(self) -> None:
        self.assertEqual(
            MODULE.openssh_fingerprint(MODULE.GITHUB_ED25519_LINE),
            MODULE.GITHUB_ED25519_FINGERPRINT,
        )

    def test_remote_is_repository_scoped(self) -> None:
        self.assertEqual(
            MODULE.SSH_REMOTE,
            "git@github.com:lightrain-a/agent-self-evolution-observatory.git",
        )


if __name__ == "__main__":
    unittest.main()
