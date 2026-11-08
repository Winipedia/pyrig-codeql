"""Test module."""

from pyrig_codeql.rig.configs.version_control.remote.workflows.codeql import (
    CodeqlWorkflowConfigFile,
)
from pyrig_codeql.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_job_codeql(self) -> None:
        """Test method."""
        job = HealthCheckWorkflowConfigFile.I.job_codeql()
        assert job["job_id"] == "codeql"
        assert job["name"] == "Codeql"
        assert job["uses"] == "$/.github/workflows/codeql.yml"
        assert (
            job["permissions"]
            == HealthCheckWorkflowConfigFile.I.job_codeql_permissions()
        )

    def test_job_codeql_permissions(self) -> None:
        """Test method."""
        permissions = HealthCheckWorkflowConfigFile.I.job_codeql_permissions()
        assert permissions == CodeqlWorkflowConfigFile.I.used_permissions()

    def test_jobs_health_check(self) -> None:
        """Test method."""
        assert (
            HealthCheckWorkflowConfigFile.I.job_codeql
            in HealthCheckWorkflowConfigFile.I.jobs_health_check()
        )
