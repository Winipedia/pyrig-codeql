"""Test module."""

import shlex

from pyrig.core.resources import resource_content
from pyrig.core.strings import read_text_utf8

from pyrig_codeql.rig import resources
from pyrig_codeql.rig.configs.version_control.remote.workflows.codeql import (
    CodeqlWorkflowConfigFile,
)


class TestCodeqlWorkflowConfigFile:
    """Test class."""

    def test_action_codeql_analyze(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        assert workflow.action_codeql_analyze() == tuple(
            resource_content("ACTION_CODEQL_ANALYZE", resources).splitlines(),
        )
        action, ref, tag = workflow.action_codeql_analyze()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(workflow.path())

    def test_action_codeql_init(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        assert workflow.action_codeql_init() == tuple(
            resource_content("ACTION_CODEQL_INIT", resources).splitlines(),
        )
        action, ref, tag = workflow.action_codeql_init()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(workflow.path())

    def test_job_analyze(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        job = workflow.job_analyze()
        assert job["job_id"] == "analyze"
        assert job["runs-on"] == "ubuntu-latest"
        assert job["timeout-minutes"] == 90  # noqa: PLR2004
        assert job["strategy"]["matrix"]["language"] == ["python", "actions"]
        assert job["permissions"] == workflow.job_analyze_permissions()
        assert [step["id"] for step in job["steps"]] == [
            "checkout-repository",
            "initialize-codeql",
            "analyze-code",
        ]

    def test_job_analyze_permissions(self) -> None:
        """Test method."""
        assert CodeqlWorkflowConfigFile.I.job_analyze_permissions() == {
            "actions": "read",
            "contents": "read",
            "security-events": "write",
        }

    def test_job_check_alerts(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        job = workflow.job_check_alerts()
        assert job["job_id"] == "check-alerts"
        assert job["timeout-minutes"] == 5  # noqa: PLR2004
        assert job["needs"] == ["analyze"]
        assert job["permissions"] == workflow.job_check_alerts_permissions()
        assert job["steps"] == workflow.steps_check_alerts()

    def test_job_check_alerts_permissions(self) -> None:
        """Test method."""
        assert CodeqlWorkflowConfigFile.I.job_check_alerts_permissions() == {
            "security-events": "read",
        }

    def test_jobs(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        assert workflow.jobs() == (workflow.job_analyze, workflow.job_check_alerts)

    def test_step_analyze_code(self) -> None:
        """Test method."""
        step = CodeqlWorkflowConfigFile.I.step_analyze_code()
        assert "uses" in step
        assert "with" not in step

    def test_step_check_alerts(self) -> None:
        """Test method."""
        step = CodeqlWorkflowConfigFile.I.step_check_alerts()
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
        assert CodeqlWorkflowConfigFile.I.step_initialize_codeql()["with"] == {
            "languages": "${{ matrix.language }}",
            "config-file": ".github/codeql.yml",
        }

    def test_steps_analyze(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        assert [step["id"] for step in workflow.steps_analyze()] == [
            "checkout-repository",
            "initialize-codeql",
            "analyze-code",
        ]

    def test_steps_check_alerts(self) -> None:
        """Test method."""
        workflow = CodeqlWorkflowConfigFile.I
        assert workflow.steps_check_alerts() == [workflow.step_check_alerts()]

    def test_workflow_triggers(self) -> None:
        """Test method."""
        assert CodeqlWorkflowConfigFile.I.workflow_triggers() == {
            "workflow_call": {},
        }
