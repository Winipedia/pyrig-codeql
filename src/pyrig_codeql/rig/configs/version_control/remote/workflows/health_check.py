"""Health check workflow extended with CodeQL analysis and an open-alert gate."""

from collections.abc import Callable
from typing import Any, override

from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile as BaseHealthCheckWorkflowConfigFile,
)

from pyrig_codeql.rig.configs.version_control.remote.workflows.codeql import (
    CodeqlWorkflowConfigFile,
)


class HealthCheckWorkflowConfigFile(BaseHealthCheckWorkflowConfigFile):
    """Include the reusable CodeQL workflow in the health check."""

    @override
    def jobs_health_check(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the base health-check jobs followed by the CodeQL call."""
        return (
            *super().jobs_health_check(),
            self.job_codeql,
        )

    def job_codeql(self) -> dict[str, Any]:
        """Call the reusable CodeQL workflow."""
        return self.job(
            self.job_codeql,
            uses=CodeqlWorkflowConfigFile.I.workflow_call_reference(),
            permissions=self.job_codeql_permissions() or None,
            secrets=CodeqlWorkflowConfigFile.I.used_secrets_mapping() or None,
        )

    def job_codeql_permissions(self) -> dict[str, str]:
        """Return the permissions required by the reusable CodeQL workflow."""
        return CodeqlWorkflowConfigFile.I.used_permissions()
