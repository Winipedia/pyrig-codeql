"""Test module."""

from pyrig.core.resources import resource_content
from pyrig.core.strings import read_text_utf8

from pyrig_codeql.rig import resources
from pyrig_codeql.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_jobs(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.jobs()
        assert "analyze" in result, "Expected 'analyze' job"

    def test_job_health_check(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.job_health_check()
        job_name = next(iter(result.keys()))
        assert "analyze" in result[job_name]["needs"], "Expected 'analyze' in needs"

    def test_job_health_check_needs(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.job_health_check_needs() == (
            HealthCheckWorkflowConfigFile.I.job_analyze,
            HealthCheckWorkflowConfigFile.I.job_health_checks,
            HealthCheckWorkflowConfigFile.I.job_matrix_health_checks,
        )

    def test_job_analyze(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.job_analyze()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        job = result[job_name]
        assert "steps" in job, "Expected 'steps' in job"
        assert job["strategy"]["matrix"]["language"] == ["python", "actions"]
        assert job["permissions"]["contents"] == "read"
        assert job["permissions"]["actions"] == "read"
        assert job["permissions"]["security-events"] == "write"

    def test_steps_analyze(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.steps_analyze()
        step_ids = [step["id"] for step in result]
        assert step_ids == [
            "checkout-repository",
            "initialize-codeql",
            "perform-codeql-analysis",
        ]

    def test_codeql_init_action(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.codeql_init_action() == tuple(
            resource_content("CODEQL_INIT_ACTION", resources).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.codeql_init_action()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_codeql_analyze_action(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.codeql_analyze_action() == tuple(
            resource_content("CODEQL_ANALYZE_ACTION", resources).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.codeql_analyze_action()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_step_initialize_codeql(self) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_initialize_codeql()
        assert step["with"] == {
            "languages": "${{ matrix.language }}",
            "build-mode": "none",
            "queries": "security-and-quality",
        }

    def test_step_perform_codeql_analysis(self) -> None:
        """Test method."""
        step = HealthCheckWorkflowConfigFile.I.step_perform_codeql_analysis()
        assert "uses" in step
        assert "with" not in step
