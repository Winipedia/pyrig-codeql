"""CodeQL tool identity and code-analysis badge metadata."""

from typing import override

from pyrig.rig.tools.base.tool import Group, Tool


class CodeAnalyzer(Tool):
    """Represent CodeQL, which runs through GitHub Actions."""

    @override
    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no dev dependencies because CodeQL runs in GitHub Actions."""
        return ()

    @override
    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    @override
    def image_url(self) -> str:
        """Return a badge identifying CodeQL as the project's code analyzer."""
        return "https://img.shields.io/badge/code--analysis-CodeQL-181717?logo=github"

    @override
    def link_url(self) -> str:
        """Return the CodeQL documentation URL."""
        return "https://codeql.github.com/docs/"

    @override
    def name(self) -> str:
        """Return the CodeQL tool identity."""
        return "codeql"
