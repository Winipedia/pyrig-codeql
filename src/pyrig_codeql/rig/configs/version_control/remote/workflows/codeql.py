"""Reusable CodeQL analysis and code-scanning alert gate."""

from collections.abc import Callable
from typing import Any, override

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController

from pyrig_codeql.rig import resources
from pyrig_codeql.rig.configs.version_control.remote.code_analyzer import (
    CodeAnalyzerConfigFile,
)


class CodeqlWorkflowConfigFile(WorkflowConfigFile):
    """Analyze Python and GitHub Actions code and fail on open CodeQL alerts."""

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the analysis and alert-gate jobs."""
        return (self.job_analyze, self.job_check_alerts)

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Allow invocation only through a reusable-workflow call."""
        return self.on_workflow_call()

    def job_check_alerts(self) -> dict[str, Any]:
        """Check CodeQL alerts after all language analyses have completed."""
        return self.job(
            self.job_check_alerts,
            needs=(self.job_analyze,),
            permissions=self.job_check_alerts_permissions(),
            steps=self.steps_check_alerts(),
            timeout_minutes=5,
        )

    def job_analyze(self) -> dict[str, Any]:
        """Build the matrix job that analyzes Python and workflow code."""
        return self.job(
            self.job_analyze,
            strategy=self.strategy_matrix(
                matrix=self.matrix({"language": ["python", "actions"]}),
            ),
            permissions=self.job_analyze_permissions(),
            steps=self.steps_analyze(),
            timeout_minutes=90,
        )

    def job_check_alerts_permissions(self) -> dict[str, str]:
        """Grant read access to code-scanning alerts."""
        return self.permission("security-events")

    def steps_check_alerts(self) -> list[dict[str, Any]]:
        """Return the CodeQL alert-check step."""
        return [self.step_check_alerts()]

    def job_analyze_permissions(self) -> dict[str, str]:
        """Grant the permissions required to analyze and upload CodeQL results."""
        return {
            **self.permission_contents(),
            **self.permission("actions"),
            **self.permission("security-events", write=True),
        }

    def step_check_alerts(self) -> dict[str, Any]:
        """Fail if the analyzed ref has any open CodeQL alerts."""
        return self.step(
            self.step_check_alerts,
            run=RemoteVersionController.I.api_method_args(
                '--raw-field="ref=${GITHUB_REF}"',
                "--raw-field=state=open",
                "--raw-field=tool_name=CodeQL",
                """--jq='if . != [] then error("Alerts found") end'""",
                endpoint='"repos/${GITHUB_REPOSITORY}/code-scanning/alerts"',
                method="GET",
            ).multiline(),
            env={"GH_TOKEN": self.insert_github_token()},
        )

    def steps_analyze(self) -> list[dict[str, Any]]:
        """Return checkout, initialization, and analysis steps."""
        return [
            self.step_checkout_repository(),
            self.step_initialize_codeql(),
            self.step_analyze_code(),
        ]

    def step_analyze_code(self) -> dict[str, Any]:
        """Run the CodeQL analysis and upload its results."""
        return self.step(
            self.step_analyze_code,
            uses=self.action_codeql_analyze(),
        )

    def step_initialize_codeql(self) -> dict[str, Any]:
        """Initialize CodeQL for the current matrix language."""
        return self.step(
            self.step_initialize_codeql,
            uses=self.action_codeql_init(),
            with_={
                "languages": self.insert_expression("matrix.language"),
                "config-file": CodeAnalyzerConfigFile.I.path().as_posix(),
            },
        )

    def action_codeql_analyze(self) -> tuple[str, str, str]:
        """Return the pinned CodeQL analyze action metadata."""
        return self.action_from_resource(self.action_codeql_analyze, resources)

    def action_codeql_init(self) -> tuple[str, str, str]:
        """Return the pinned CodeQL init action metadata."""
        return self.action_from_resource(self.action_codeql_init, resources)
