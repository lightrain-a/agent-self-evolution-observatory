from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = "/home/wyt/code/agent-self-evolution-observatory-automation"
CANONICAL_ENV = "/home/wyt/code/agent-self-evolution-observatory/.env"


class AutomationCheckoutIsolationTest(unittest.TestCase):
    def test_systemd_services_use_isolated_checkout_and_ff_only_preflight(self) -> None:
        for name in ("agent-evolution-daily.service", "agent-evolution-weekly.service"):
            text = (ROOT / "deploy" / "systemd" / name).read_text(encoding="utf-8")
            self.assertIn(f"WorkingDirectory={AUTOMATION_ROOT}", text)
            self.assertIn(f"Environment=PROJECT_ROOT={AUTOMATION_ROOT}", text)
            self.assertIn(f"Environment=RESEARCH_ENV_FILE={CANONICAL_ENV}", text)
            self.assertIn("ExecStartPre=/usr/bin/git restore --source=HEAD --staged --worktree -- generated", text)
            self.assertIn("ExecStartPre=/usr/bin/git clean -fd -- generated", text)
            self.assertIn("ExecStartPre=/usr/bin/git -c http.proxy= -c https.proxy= fetch origin main", text)
            self.assertIn("ExecStartPre=/usr/bin/git merge --ff-only origin/main", text)

    def test_systemd_timeouts_leave_headroom_for_full_projection_and_publication(self) -> None:
        daily = (ROOT / "deploy" / "systemd" / "agent-evolution-daily.service").read_text(encoding="utf-8")
        weekly = (ROOT / "deploy" / "systemd" / "agent-evolution-weekly.service").read_text(encoding="utf-8")
        self.assertIn("TimeoutStartSec=90min", daily)
        self.assertIn("TimeoutStartSec=3h", weekly)

    def test_on_52_supports_external_env_file_for_isolated_checkout(self) -> None:
        text = (ROOT / "scripts" / "on-52.sh").read_text(encoding="utf-8")
        self.assertIn('ENV_FILE="${RESEARCH_ENV_FILE:-${PROJECT_ROOT}/.env}"', text)

    def test_timer_installer_bootstraps_detached_automation_worktree(self) -> None:
        text = (ROOT / "scripts" / "install_research_timers.py").read_text(encoding="utf-8")
        self.assertIn('"worktree", "add", "--detach"', text)
        self.assertIn('"restore", "--source=HEAD", "--staged", "--worktree", "--", "generated"', text)
        self.assertIn('"clean", "-fd", "--", "generated"', text)
        self.assertIn('"merge", "--ff-only", "origin/main"', text)
        self.assertIn("recover_automation_generated_state()", text)
        self.assertIn("ensure_automation_checkout()", text)


if __name__ == "__main__":
    unittest.main()
