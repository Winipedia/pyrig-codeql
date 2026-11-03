"""Health check workflow extended with CodeQL analysis and an open-alert gate."""

from collections.abc import Callable
from types import MethodType
from typing import Any, override

from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile as BaseHealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController

from pyrig_codeql.rig import resources
from pyrig_codeql.rig.configs.version_control.remote.code_analyzer import (
    CodeAnalyzerConfigFile,
)


class HealthCheckWorkflowConfigFile(BaseHealthCheckWorkflowConfigFile):
    """Add CodeQL analysis and an open-alert gate to the health check workflow."""

    @override
    def job_health_check_needs(self) -> tuple[MethodType, ...]:
        """Return the upstream jobs required before the aggregate job runs.

        Prepends the CodeQL analysis job to the two base health-check jobs so
        the aggregate status remains a release gate for every analysis.

        Returns:
            The base class's dependencies plus the CodeQL analysis job.
        """
        return (self.job_analyze, *super().job_health_check_needs())

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the base job builders, extended with the CodeQL analysis builder.

        Returns:
            Tuple of the CodeQL analysis builder followed by the base job builders.
        """
        return (
            self.job_analyze,
            *super().jobs(),
        )

    def job_analyze(self) -> dict[str, Any]:
        """Return the CodeQL analysis job.

        Returns:
            Job configuration with a matrix over `("python", "actions")`,
            the job's permissions, and steps that fail the job on open
            CodeQL alerts.
        """
        return self.job(
            self.job_analyze,
            strategy=self.strategy_matrix(
                matrix=self.matrix({"language": ["python", "actions"]}),
            ),
            permissions=self.job_analyze_permissions(),
            steps=self.steps_analyze(),
            timeout_minutes=90,
        )

    def job_analyze_permissions(self) -> dict[str, Any]:
        """Return the permissions for the CodeQL analysis job.

        Returns:
            Permissions needed to analyze code (`contents: read`), read
            workflow runs (`actions: read`), and upload results and read
            alerts (`security-events: write`).
        """
        return {
            **self.permission_contents(),
            **self.permission("actions"),
            **self.permission("security-events", write=True),
        }

    def steps_analyze(self) -> list[dict[str, Any]]:
        """Return the steps for the CodeQL analysis job.

        Returns:
            Steps that check out the repository, initialize CodeQL for the
            current matrix language, run the analysis, and check open alerts.
        """
        return [
            self.step_checkout_repository(),
            self.step_initialize_codeql(),
            self.step_analyze_code(),
            self.step_check_alerts(),
        ]

    def step_analyze_code(self) -> dict[str, Any]:
        """Build a step that runs the CodeQL analysis and uploads results.

        Returns:
            Step using `github/codeql-action/analyze@<ref>`.
        """
        return self.step(
            self.step_analyze_code,
            uses=self.action_codeql_analyze(),
        )

    def step_check_alerts(self) -> dict[str, Any]:
        """Fail if the analyzed ref has any open CodeQL alerts.

        Returns:
            GitHub CLI step authenticated with the workflow's GitHub token.
        """
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
            env={"GH_TOKEN": self.insert_expression("secrets.GITHUB_TOKEN")},
        )

    def step_initialize_codeql(self) -> dict[str, Any]:
        """Build a step that initializes the CodeQL database.

        Neither analyzed language is compiled, so no build step is
        required between initialization and analysis.

        Returns:
            Step using `github/codeql-action/init@<ref>`.
        """
        return self.step(
            self.step_initialize_codeql,
            uses=self.action_codeql_init(),
            with_={
                "languages": self.insert_expression("matrix.language"),
                "config-file": CodeAnalyzerConfigFile.I.path().as_posix(),
            },
        )

    def action_codeql_analyze(self) -> tuple[str, str, str]:
        """Return action metadata for `github/codeql-action/analyze`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.action_codeql_analyze, resources)

    def action_codeql_init(self) -> tuple[str, str, str]:
        """Return action metadata for `github/codeql-action/init`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.action_codeql_init, resources)
