"""Test module."""

from pathlib import Path

from pyrig_codeql.rig.configs.version_control.remote.code_analyzer import (
    CodeAnalyzerConfigFile,
)


class TestCodeAnalyzerConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert CodeAnalyzerConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert CodeAnalyzerConfigFile.I.stem() == "codeql"

    def test__configs(self) -> None:
        """Test method."""
        configs = CodeAnalyzerConfigFile.I._configs()  # noqa: SLF001
        assert configs == {
            "paths-ignore": ["tests/**"],
            "queries": [{"uses": "security-and-quality"}],
        }
