"""Test module."""

import shlex

from pyrig.core.resources import resource_content
from pyrig.core.strings import read_text_utf8

from pyrig_codeql.rig import resources
from pyrig_codeql.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_action_codeql_analyze(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.action_codeql_analyze() == tuple(
            resource_content("ACTION_CODEQL_ANALYZE", resources).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.action_codeql_analyze()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_action_codeql_init(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.action_codeql_init() == tuple(
            resource_content("ACTION_CODEQL_INIT", resources).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.action_codeql_init()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_job_analyze(self) -> None:
        """Test method."""
        job = HealthCheckWorkflowConfigFile.I.job_analyze()
        assert job["job_id"] == "analyze"
        assert "steps" in job, "Expected 'steps' in job"
        assert job["strategy"]["matrix"]["language"] == ["python", "actions"]
        assert job["permissions"]["contents"] == "read"
        assert job["permissions"]["actions"] == "read"
        assert job["permissions"]["security-events"] == "write"

    def test_job_analyze_permissions(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.job_analyze_permissions() == {
            "contents": "read",
            "actions": "read",
            "security-events": "write",
        }

    def test_job_health_check(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.job_health_check()
        assert "analyze" in result["needs"], "Expected 'analyze' in needs"

    def test_job_health_check_needs(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.job_health_check_needs() == (
            HealthCheckWorkflowConfigFile.I.job_analyze,
            HealthCheckWorkflowConfigFile.I.job_health_checks,
            HealthCheckWorkflowConfigFile.I.job_matrix_health_checks,
        )

    def test_jobs(self) -> None:
        """Test method."""
        workflow = HealthCheckWorkflowConfigFile.I
        assert workflow.job_analyze in workflow.jobs(), "Expected 'analyze' job"

    def test_step_analyze_code(self) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_analyze_code()
        assert "uses" in step
        assert "with" not in step

    def test_step_check_alerts(self) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_check_alerts()
        assert shlex.split(step["run"].replace("\\\n", "")) == [
            "gh",
            "api",
            "repos/${GITHUB_REPOSITORY}/code-scanning/alerts",
            "--method=GET",
            "--raw-field=ref=${GITHUB_REF}",
            "--raw-field=state=open",
            "--raw-field=tool_name=CodeQL",
            '--jq=if . != [] then error("Alerts found") end',
        ]
        assert step["env"] == {"GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}"}

    def test_step_initialize_codeql(self) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_initialize_codeql()
        assert step["with"] == {
            "languages": "${{ matrix.language }}",
            "config-file": ".github/codeql.yml",
        }

    def test_steps_analyze(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.steps_analyze()
        step_ids = [step["id"] for step in result]
        assert step_ids == [
            "checkout-repository",
            "initialize-codeql",
            "analyze-code",
            "check-alerts",
        ]
        assert (
            HealthCheckWorkflowConfigFile.I.load()["jobs"]["analyze"]["steps"] == result
        )
