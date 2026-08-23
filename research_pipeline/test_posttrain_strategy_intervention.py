from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    ARMS,
    BOUNDARY_MARKER,
    audit_posttrainbench_run_task_surface,
    build_zero_authority_harness_manifest,
    compose_segmented_prompts,
    manifest_sha256,
    render_posttrainbench_self_contained_solve_sh,
    validate_zero_authority_harness_manifest,
    verify_phase1_boundary,
)


STRATEGY = (
    "Use supervised fine-tuning only as a small formatting warm-up. Reserve the main training "
    "budget for reinforcement learning, and omit SFT if the base model already satisfies the "
    "required output-format contract."
)
EXECUTION = (
    "Keep the training paradigm, data-source type, and stage structure fixed. For the next training "
    "only, halve the current learning rate and leave the rest of the strategy unchanged."
)
CONFLICT_FREE = (
    "Preserve the current checkpoint and completed training. Add a reinforcement-learning stage for "
    "the remaining budget without requiring rollback of already completed work."
)


class PostTrainStrategyInterventionTest(unittest.TestCase):
    def prompts(self, arm: str):
        return compose_segmented_prompts(
            base_prompt="Improve the assigned base model on AIME 2025.",
            arm=arm,
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
        )

    def test_pre_and_post_strategy_use_identical_frozen_strategy_payload(self) -> None:
        pre = self.prompts(ARM_PRE_STRATEGY)
        post = self.prompts(ARM_POST_STRATEGY)
        self.assertEqual(pre.strategy_instruction_sha256, post.strategy_instruction_sha256)
        self.assertIn(STRATEGY, pre.phase1_prompt)
        self.assertNotIn(STRATEGY, pre.phase2_prompt)
        self.assertNotIn(STRATEGY, post.phase1_prompt)
        self.assertIn(STRATEGY, post.phase2_prompt)
        self.assertIn(BOUNDARY_MARKER, pre.phase1_prompt)
        self.assertIn(BOUNDARY_MARKER, post.phase1_prompt)

    def test_reduction_controls_are_post_boundary_only(self) -> None:
        execution = self.prompts(ARM_POST_EXECUTION)
        conflict_free = self.prompts(ARM_POST_CONFLICT_FREE)
        self.assertNotIn(EXECUTION, execution.phase1_prompt)
        self.assertIn(EXECUTION, execution.phase2_prompt)
        self.assertNotIn(CONFLICT_FREE, conflict_free.phase1_prompt)
        self.assertIn(CONFLICT_FREE, conflict_free.phase2_prompt)

    def test_boundary_probe_requires_marker_and_training_like_command(self) -> None:
        trace = '\n'.join(
            [
                'Command: python train_sft.py --model Qwen3-1.7B-Base',
                'training finished successfully',
                BOUNDARY_MARKER,
            ]
        )
        probe = verify_phase1_boundary(trace)
        self.assertTrue(probe["mechanical_probe_passed"])
        self.assertTrue(probe["requires_semantic_parameter_update_verification"])
        self.assertFalse(probe["scientific_authority"])
        self.assertEqual(len(probe["candidate_training_commands"]), 1)

    def test_boundary_probe_fails_closed_without_training_candidate(self) -> None:
        probe = verify_phase1_boundary("evaluation only\n" + BOUNDARY_MARKER)
        self.assertFalse(probe["mechanical_probe_passed"])

    def test_manifest_is_zero_authority_and_contains_all_reduction_arms(self) -> None:
        manifest = build_zero_authority_harness_manifest(
            candidate_id="V19R-003-BOUNDARY-REPAIR-R2",
            candidate_snapshot_sha256="47ea60fb13e3ec723d2a871b58ab1a3c6e9e565eea01e1cd838c67f9f2b39777",
            source_paper_ref="arXiv:2608.19072",
            source_paper_source_sha256="a" * 64,
            substrate_repo="aisa-group/PostTrainBench",
            substrate_commit="3ed1d32ff1ec1f41282be6f8ebbcec07b19fc3d1",
            task="aime2025",
            base_model="Qwen/Qwen3-1.7B-Base",
            agent_scaffold="claude-segmented-resume",
            agent_model="claude-opus-4-6",
            expected_hardware="source-matched-declared-host",
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
        )
        self.assertEqual(validate_zero_authority_harness_manifest(manifest), [])
        self.assertFalse(manifest["scientific_authority"])
        self.assertTrue(all(value is False for value in manifest["authority"].values()))
        self.assertEqual(
            [row["arm"] for row in manifest["intervention"]["arm_contracts"]],
            list(ARMS),
        )
        self.assertEqual(len(manifest_sha256(manifest)), 64)

    def test_official_run_task_surface_supports_self_contained_overlay(self) -> None:
        official = Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/run_task.sh")
        if not official.is_file():
            self.skipTest("official PostTrainBench cache not present")
        audit = audit_posttrainbench_run_task_surface(official.read_text(encoding="utf-8"))
        self.assertTrue(audit["probe_passed"], msg=json.dumps(audit, indent=2))
        self.assertFalse(audit["scientific_authority"])

    def test_shell_adapter_delivers_post_strategy_only_after_boundary(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        adapter = repo_root / "research_pipeline" / "adapters" / "posttrainbench_segmented_strategy_resume.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            phase1_stdin = root / "phase1.stdin"
            phase2_stdin = root / "phase2.stdin"
            fake = bin_dir / "claude"
            fake.write_text(
                textwrap.dedent(
                    f"""\
                    #!/bin/bash
                    set -euo pipefail
                    input=$(cat)
                    if printf '%s\\n' "$*" | grep -q -- '--continue'; then
                      printf '%s' "$input" > "{phase2_stdin}"
                      printf '{{"type":"assistant","message":{{"content":[{{"type":"text","text":"continued"}}]}}}}\\n'
                    else
                      printf '%s' "$input" > "{phase1_stdin}"
                      printf '{{"type":"assistant","message":{{"content":[{{"type":"text","text":"Command: python train_sft.py --model base\\n{BOUNDARY_MARKER}"}}]}}}}\\n'
                    fi
                    """
                ),
                encoding="utf-8",
            )
            fake.chmod(0o755)

            strategy_file = root / "strategy.txt"
            execution_file = root / "execution.txt"
            conflict_file = root / "conflict.txt"
            strategy_file.write_text(STRATEGY, encoding="utf-8")
            execution_file.write_text(EXECUTION, encoding="utf-8")
            conflict_file.write_text(CONFLICT_FREE, encoding="utf-8")
            env = os.environ.copy()
            env.update(
                {
                    "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
                    "PROMPT": "Improve the assigned base model.",
                    "AGENT_CONFIG": "fake-opus",
                    "PTB_INTERVENTION_ARM": ARM_POST_STRATEGY,
                    "PTB_SESSION_BACKEND": "claude",
                    "PTB_STRATEGY_INSTRUCTION_FILE": str(strategy_file),
                    "PTB_EXECUTION_CONTROL_FILE": str(execution_file),
                    "PTB_CONFLICT_FREE_STRATEGY_FILE": str(conflict_file),
                    "PTB_PHASE1_TRACE": str(root / "phase1.jsonl"),
                    "PTB_PHASE2_TRACE": str(root / "phase2.jsonl"),
                    "PTB_SKIP_AGENT_UPDATE": "1",
                }
            )
            result = subprocess.run(
                ["bash", str(adapter)],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            p1 = phase1_stdin.read_text(encoding="utf-8")
            p2 = phase2_stdin.read_text(encoding="utf-8")
            self.assertNotIn(STRATEGY, p1)
            self.assertIn(BOUNDARY_MARKER, p1)
            self.assertIn(STRATEGY, p2)
            self.assertIn("PTB_INTERVENTION_BOUNDARY_ACCEPTED", result.stdout)

    def test_corrected_generated_manifest_core_digest_matches(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        generated = repo_root / "generated" / "v19r003-forced-switch-pre-f0-harness-manifest-r2-20260823.json"
        if not generated.is_file():
            self.skipTest("corrected V19R-003 harness manifest not present")
        payload = json.loads(generated.read_text(encoding="utf-8"))
        stored = payload.get("manifest_sha256")
        core = {
            key: value
            for key, value in payload.items()
            if key not in {"artifact_kind", "canonical_projection", "frozen_payloads", "manifest_sha256"}
        }
        self.assertEqual(stored, manifest_sha256(core))

    def test_self_contained_solve_sh_survives_official_single_file_copy_surface(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        adapter = repo_root / "research_pipeline" / "adapters" / "posttrainbench_segmented_strategy_resume.sh"
        rendered = render_posttrainbench_self_contained_solve_sh(
            adapter_text=adapter.read_text(encoding="utf-8"),
            arm=ARM_POST_STRATEGY,
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
            backend="claude",
        )
        self.assertNotIn(STRATEGY, rendered)
        self.assertIn("export PTB_INTERVENTION_ARM='POST_STRATEGY'", rendered)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied_solve = root / "agent_solve.sh"
            copied_solve.write_text(rendered, encoding="utf-8")
            copied_solve.chmod(0o755)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            phase1_stdin = root / "phase1.stdin"
            phase2_stdin = root / "phase2.stdin"
            fake = bin_dir / "claude"
            fake.write_text(
                textwrap.dedent(
                    f"""\\
                    #!/bin/bash
                    set -euo pipefail
                    input=$(cat)
                    if printf '%s\\n' "$*" | grep -q -- '--continue'; then
                      printf '%s' "$input" > "{phase2_stdin}"
                      printf '{{"type":"assistant","message":{{"content":[{{"type":"text","text":"continued"}}]}}}}\\n'
                    else
                      printf '%s' "$input" > "{phase1_stdin}"
                      printf '{{"type":"assistant","message":{{"content":[{{"type":"text","text":"Command: python train_sft.py --model base\\n{BOUNDARY_MARKER}"}}]}}}}\\n'
                    fi
                    """
                ),
                encoding="utf-8",
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
                    "PROMPT": "Improve the assigned base model.",
                    "AGENT_CONFIG": "fake-opus",
                    "PTB_PHASE1_TRACE": str(root / "phase1.jsonl"),
                    "PTB_PHASE2_TRACE": str(root / "phase2.jsonl"),
                    "PTB_SKIP_AGENT_UPDATE": "1",
                }
            )
            result = subprocess.run(["bash", str(copied_solve)], env=env, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn(STRATEGY, phase1_stdin.read_text(encoding="utf-8"))
            self.assertIn(STRATEGY, phase2_stdin.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
