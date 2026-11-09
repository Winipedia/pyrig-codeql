"""Test module."""

from pyrig.rig.tools.base.tool import Group

from pyrig_codeql.rig.tools.security.code import CodeAnalyzer


class TestCodeAnalyzer:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert CodeAnalyzer.I.dev_dependencies() == ()

    def test_group(self) -> None:
        """Test method."""
        assert CodeAnalyzer.I.group() == Group.CODE_QUALITY

    def test_image_url(self) -> None:
        """Test method."""
        assert CodeAnalyzer.I.image_url() == (
            "https://img.shields.io/badge/code%20analysis-CodeQL-181717?logo=github"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert CodeAnalyzer.I.link_url() == "https://codeql.github.com/docs/"

    def test_name(self) -> None:
        """Test method."""
        assert CodeAnalyzer.I.name() == "codeql"
