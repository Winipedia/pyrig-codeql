"""Explicit references for reviewed dead code false positives."""

from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.tools.base.tool import Tool

from pyrig_codeql.rig.configs.version_control.remote.code_analyzer import (
    CodeAnalyzerConfigFile,
)

_CONFIG_FILE_OVERRIDES = (
    ConfigFile._configs,  # noqa: SLF001
    ConfigFile.parent_path,
    ConfigFile.stem,
    WorkflowConfigFile.jobs,
    WorkflowConfigFile.workflow_triggers,
)
_CONFIG_FILES = (CodeAnalyzerConfigFile,)
_TOOL_OVERRIDES = (
    Tool.dev_dependencies,
    Tool.group,
    Tool.image_url,
    Tool.link_url,
)
