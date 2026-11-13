"""Test module."""

from pyrig_codeql.rig.configs.version_control.remote.workflows.code_analysis import (
    CodeAnalysisWorkflowConfigFile,
)
from pyrig_codeql.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_job_code_analysis(self) -> None:
        """Test method."""
        job = HealthCheckWorkflowConfigFile.I.job_code_analysis()
        assert job["job_id"] == "code-analysis"
        assert job["name"] == "Code Analysis"
        assert job["uses"] == "$/.github/workflows/code-analysis.yml"
        assert job["permissions"] == CodeAnalysisWorkflowConfigFile.I.permissions_used()
        assert job.get("secrets") == (
            CodeAnalysisWorkflowConfigFile.I.used_secrets_mapping() or None
        )

    def test_jobs_health_check(self) -> None:
        """Test method."""
        assert (
            HealthCheckWorkflowConfigFile.I.job_code_analysis
            in HealthCheckWorkflowConfigFile.I.jobs_health_check()
        )
