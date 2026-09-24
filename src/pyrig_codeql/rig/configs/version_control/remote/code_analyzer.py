"""CodeQL configuration that restricts analysis to shipped source code."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yaml import YMLDictConfigFile
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class CodeAnalyzerConfigFile(YMLDictConfigFile):
    """Configuration consumed by the CodeQL `init` action's `config-file` input.

    Manages `.github/codeql.yml`, including the query suite and ignored paths.
    """

    def parent_path(self) -> Path:
        """Return GitHub's special repository configuration directory."""
        return RemoteVersionController.I.config_dir()

    def stem(self) -> str:
        """Return `'codeql'`."""
        return "codeql"

    def _configs(self) -> dict[str, Any]:
        """Build the CodeQL configuration.

        Runs the `security-and-quality` query suite. Excludes the project's
        test package, as determined by `ProjectTester.I.package_root()`, so
        CodeQL scans shipped source code without test-only patterns.

        Returns:
            Dict with the codeql configurations.
        """
        return {
            "paths-ignore": [f"{ProjectTester.I.package_root().as_posix()}/**"],
            "queries": [{"uses": "security-and-quality"}],
        }
