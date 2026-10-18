"""驗證 CI workflow 與多環境設定的結構檢查邏輯。"""

import pytest

from scripts.cache_estimate import estimate
from scripts.run_ci_local import job_order
from scripts.validate_yaml import (
    ROOT,
    check_ci_workflow,
    check_env_configs,
    find_yaml_files,
    load_yaml,
)

ENV_DIR = ROOT / "config" / "environments"


def test_all_yaml_parse():
    files = find_yaml_files(ROOT)
    assert len(files) >= 4
    for path in files:
        assert load_yaml(path) is not None, path


def test_ci_workflow_meets_spec():
    assert check_ci_workflow(load_yaml(ROOT / ".github" / "workflows" / "ci.yml")) == []


def test_ci_check_detects_missing_needs():
    workflow = load_yaml(ROOT / ".github" / "workflows" / "ci.yml")
    del workflow["jobs"]["lint"]["needs"]
    assert any("lint.needs" in e for e in check_ci_workflow(workflow))


def test_env_configs_meet_spec():
    staging = load_yaml(ENV_DIR / "staging.yaml")
    production = load_yaml(ENV_DIR / "production.yaml")
    assert check_env_configs(staging, production) == []


def test_env_check_rejects_secret_value():
    bad = {"variables": {"DATABASE_URL": {"secret": True, "value": "postgres://leak"}}}
    assert any("不可在檔案中寫 value" in e for e in check_env_configs(bad, bad))


def test_job_order_follows_needs():
    jobs = {"security": {"needs": "lint"}, "lint": {"needs": "test"}, "test": {}}
    assert job_order(jobs) == ["test", "lint", "security"]


def test_job_order_cycle_raises():
    with pytest.raises(ValueError):
        job_order({"a": {"needs": "b"}, "b": {"needs": "a"}})


def test_cache_estimate():
    assert estimate(10, 2) == {"first_run": 20, "cached_run": 0, "saved": 20}
    with pytest.raises(ValueError):
        estimate(-1, 2)
