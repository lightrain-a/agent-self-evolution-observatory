from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "configure_github_ssh.py"
SPEC = importlib.util.spec_from_file_location("configure_github_ssh", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

DEPLOY_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "add_github_deploy_key.py"
DEPLOY_SPEC = importlib.util.spec_from_file_location("add_github_deploy_key", DEPLOY_SCRIPT)
assert DEPLOY_SPEC and DEPLOY_SPEC.loader
DEPLOY_MODULE = importlib.util.module_from_spec(DEPLOY_SPEC)
DEPLOY_SPEC.loader.exec_module(DEPLOY_MODULE)


class GithubSshConfigTest(unittest.TestCase):
    def test_embedded_host_key_matches_official_fingerprint(self) -> None:
        self.assertEqual(
            MODULE.openssh_fingerprint(MODULE.GITHUB_ED25519_LINE),
            MODULE.GITHUB_ED25519_FINGERPRINT,
        )

    def test_deploy_key_normalization_drops_comment_only(self) -> None:
        self.assertEqual(
            DEPLOY_MODULE.normalize_public_key("ssh-ed25519 AAAAC3example server-comment"),
            "ssh-ed25519 AAAAC3example",
        )
        self.assertEqual(DEPLOY_MODULE.API_VERSION, "2026-03-10")

    def test_remote_is_repository_scoped(self) -> None:
        self.assertEqual(
            MODULE.SSH_REMOTE,
            "git@github.com:lightrain-a/agent-self-evolution-observatory.git",
        )


if __name__ == "__main__":
    unittest.main()
