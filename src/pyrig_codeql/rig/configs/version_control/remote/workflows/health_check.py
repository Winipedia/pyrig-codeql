"""Health check workflow extended with a CodeQL analysis job."""

from types import MethodType
from typing import Any

from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile as BaseHealthCheckWorkflowConfigFile,
)

from pyrig_codeql.rig import resources


class HealthCheckWorkflowConfigFile(BaseHealthCheckWorkflowConfigFile):
    """Health check workflow extended with a CodeQL analysis job."""

    def jobs(self) -> dict[str, Any]:
        """Return the base class's jobs, extended with the CodeQL analysis job.

        Returns:
            The base class jobs plus the CodeQL analysis job.
        """
        return {
            **self.job_analyze(),
            **super().jobs(),
        }

    def job_health_check_needs(self) -> tuple[MethodType, ...]:
        """Return the upstream jobs required before the aggregate job runs.

        Prepends the CodeQL analysis job to the two base health-check jobs so
        the aggregate status remains a release gate for every analysis.

        Returns:
            The base class's dependencies plus the CodeQL analysis job.
        """
        return (self.job_analyze, *super().job_health_check_needs())

    def job_analyze(self) -> dict[str, Any]:
        """Return the CodeQL analysis job.

        Returns:
            Job configuration with a matrix over `("python", "actions")`,
            the permissions CodeQL needs to build a database and upload its
            results, and the analysis steps.
        """
        return self.job(
            self.job_analyze,
            strategy=self.strategy_matrix(
                matrix=self.matrix({"language": ["python", "actions"]}),
            ),
            permissions={
                **self.permission_contents(),
                **self.permission("actions"),
                **self.permission("security-events", write=True),
            },
            steps=self.steps_analyze(),
        )

    def steps_analyze(self) -> list[dict[str, Any]]:
        """Return the steps for the CodeQL analysis job.

        Returns:
            Steps that check out the repository, initialize CodeQL for the
            current matrix language, and run the analysis.
        """
        return [
            self.step_checkout_repository(),
            self.step_initialize_codeql(),
            self.step_perform_codeql_analysis(),
        ]

    def step_initialize_codeql(self) -> dict[str, Any]:
        """Build a step that initializes the CodeQL database.

        Neither analyzed language is compiled, so no build step is
        required between initialization and analysis. Runs the
        `security-and-quality` query suite, the strictest built-in suite,
        which is only available via advanced setup, not the default-setup
        API (whose `query_suite` field is limited to `default`/`extended`).

        Returns:
            Step using `github/codeql-action/init@<ref>`.
        """
        return self.step(
            self.step_initialize_codeql,
            uses=self.codeql_init_action(),
            with_={
                "languages": self.insert_expression("matrix.language"),
                "build-mode": "none",
                "queries": "security-and-quality",
            },
        )

    def step_perform_codeql_analysis(self) -> dict[str, Any]:
        """Build a step that runs the CodeQL analysis and uploads results.

        Fails the job if the analysis itself fails to run; code scanning
        alerts found by the analysis do not fail the step.

        Returns:
            Step using `github/codeql-action/analyze@<ref>`.
        """
        return self.step(
            self.step_perform_codeql_analysis,
            uses=self.codeql_analyze_action(),
        )

    def codeql_init_action(self) -> tuple[str, str, str]:
        """Return action metadata for `github/codeql-action/init`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.codeql_init_action, resources)

    def codeql_analyze_action(self) -> tuple[str, str, str]:
        """Return action metadata for `github/codeql-action/analyze`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.codeql_analyze_action, resources)
