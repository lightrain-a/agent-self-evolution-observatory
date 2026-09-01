from __future__ import annotations
import json, subprocess
from pathlib import Path
import pytest

from research_pipeline import c1_pacta_rb_qwen397_t0_runtime as runtime
from research_pipeline import run_c1_pacta_rb_qwen397_t0_rootful_20260901 as runner


def completed(args=(), returncode=0, stdout="", stderr=""):
 return subprocess.CompletedProcess(args, returncode, stdout, stderr)


def test_rootful_host_is_explicit():
 assert runtime.ROOTFUL_DOCKER_HOST == "unix:///var/run/docker.sock"


def test_exact_base_accepts_clean_descendant_and_persists(tmp_path: Path, monkeypatch):
 container=object.__new__(runtime.Container)
 container.docker_host=runtime.ROOTFUL_DOCKER_HOST
 container.digest_ref="repo@sha256:abc"
 values={
  ("rev-parse","HEAD"):[completed(stdout="descendant\n"),completed(stdout="base\n")],
  ("status","--porcelain"):[completed(stdout=""),completed(stdout="")],
  ("cat-file","-e","base^{commit}"):[completed()],
  ("merge-base","--is-ancestor","base","descendant"):[completed()],
  ("reset","--hard","base"):[completed(stdout="HEAD is now at base\n")],
 }
 def fake_git(*args,check=True):
  return values[args].pop(0)
 monkeypatch.setattr(container,"_git",fake_git)
 container._normalize_exact_base("base",tmp_path)
 audit=json.loads((tmp_path/"exact-base-normalization.json").read_text())
 assert audit["observed_initial_head"]=="descendant"
 assert audit["post_reset_head_exact"] is True
 assert audit["exact_base_normalization_pass"] is True
 assert audit["persisted_before_provider_call"] is True


def test_exact_base_rejects_non_ancestor_but_persists(tmp_path: Path, monkeypatch):
 container=object.__new__(runtime.Container)
 container.docker_host=runtime.ROOTFUL_DOCKER_HOST
 container.digest_ref="repo@sha256:abc"
 values={
  ("rev-parse","HEAD"):[completed(stdout="other\n"),completed(stdout="other\n")],
  ("status","--porcelain"):[completed(stdout=""),completed(stdout="")],
  ("cat-file","-e","base^{commit}"):[completed()],
  ("merge-base","--is-ancestor","base","other"):[completed(returncode=1)],
 }
 monkeypatch.setattr(container,"_git",lambda *args,check=True: values[args].pop(0))
 with pytest.raises(RuntimeError,match="STOP_EXACT_BASE_NORMALIZATION_FAILED"):
  container._normalize_exact_base("base",tmp_path)
 audit=json.loads((tmp_path/"exact-base-normalization.json").read_text())
 assert audit["base_is_ancestor"] is False
 assert audit["reset_attempted"] is False
 assert audit["exact_base_normalization_pass"] is False


def test_credential_failure_precedes_provider_call(monkeypatch):
 monkeypatch.delenv("AA_API_KEY",raising=False)
 with pytest.raises(RuntimeError,match="STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED"):
  runner.require_key()


def test_prepare_freezes_all_eleven_without_future_execution(tmp_path: Path, monkeypatch):
 ids=list(runner.FUTURES)
 units={instance:{"source_task_id":instance,"task_family":instance.split("__")[0],
  "source_task_sha256":"a"*64,"source_base_commit":f"base-{i}"} for i,instance in enumerate(ids)}
 monkeypatch.setattr(runner,"frozen",lambda:(
  {"frozen_output_token_budget":512},
  {"requested_model":"qwen3.5-397b-a17b","resolved_model":"qwen3.5-397b-a17b"},
  {},{}))
 monkeypatch.setattr(runner,"pool_units",lambda:units)
 monkeypatch.setattr(runner,"spec_map",lambda:{instance:f"digest-{i}" for i,instance in enumerate(ids)})
 monkeypatch.setattr(runner,"image_repo",lambda instance:"repo/"+instance)
 monkeypatch.setattr(runner,"CONFIG",tmp_path/"config.yaml")
 (tmp_path/"config.yaml").write_text("x")
 root=tmp_path/"run"
 result=runner.prepare(root)
 schedule=json.loads((root/"acquisition-schedule.json").read_text())
 assert len(result["schedule"])==11
 assert schedule["scheduled_count"]==11
 assert schedule["replacement"] is False and schedule["top_up"] is False
 assert all(item["logical_attempts"]==1 for item in schedule["schedule"])
 assert all(item["future_task_executed"] is False for item in schedule["schedule"])
 contract=json.loads((root/"contract.json").read_text())
 assert contract["future_task_executions"]==0
 assert {"writer","binder","shadow","gate","final"}.issubset(set(contract["forbidden"]))


def test_rootful_runner_has_no_method_execution_surface():
 source=Path(runner.__file__).read_text()
 assert 'choices=("smoke","prepare","bridge","acquire")' in source
 assert "execute_writer" not in source
 assert "execute_binder" not in source
 assert "execute_shadow" not in source
 assert "execute_final" not in source
 assert '"future_task_executed":False' in source


def test_old_roots_are_not_targets():
 source=Path(runner.__file__).read_text()
 assert "c1-pacta-rb-qwen397-t0-source-trajectory-20260901-v2" not in source
 assert "c1-pacta-rb-qwen397-t05-images-20260901-v1" not in source
 assert "c1-pacta-rb-qwen397-t0-rootful-source-20260901-v1" in source
 assert "c1-pacta-rb-qwen397-t05r-images-rootful-20260901-v1" in source


def test_trajectory_signature_carries_base_and_rootful_host():
 source=Path(runtime.__file__).read_text()
 assert "base_commit:str|None" in source
 assert 'container=Container(digest_ref,docker_host=docker_host,base_commit=base_commit' in source
 assert '"persisted_before_provider_call":True' in source
