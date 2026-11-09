"""Health check workflow extended with code analysis and an open-alert gate."""

from collections.abc import Callable
from typing import Any, override

from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile as BaseHealthCheckWorkflowConfigFile,
)

from pyrig_codeql.rig.configs.version_control.remote.workflows.code_analysis import (
    CodeAnalysisWorkflowConfigFile,
)


class HealthCheckWorkflowConfigFile(BaseHealthCheckWorkflowConfigFile):
    """Include the reusable code-analysis workflow in the health check."""

    @override
    def jobs_health_check(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the base health-check jobs followed by the code-analysis call."""
        return (
            *super().jobs_health_check(),
            self.job_code_analysis,
        )

    def job_code_analysis(self) -> dict[str, Any]:
        """Call the reusable code-analysis workflow."""
        return self.job(
            self.job_code_analysis,
            uses=CodeAnalysisWorkflowConfigFile.I.workflow_call_reference(),
            permissions=self.job_code_analysis_permissions() or None,
            secrets=CodeAnalysisWorkflowConfigFile.I.used_secrets_mapping() or None,
        )

    def job_code_analysis_permissions(self) -> dict[str, str]:
        """Return permissions required by the reusable code-analysis workflow."""
        return CodeAnalysisWorkflowConfigFile.I.used_permissions()
