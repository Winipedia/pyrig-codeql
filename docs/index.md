# Home

<!-- project-status -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-codeql/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig-codeql/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-codeql/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig-codeql/actions/workflows/release.yml)
[![ProjectTester](https://codecov.io/gh/Winipedia/pyrig-codeql/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig-codeql)
<!-- code-quality -->
[![ByteOrderMarkerFormatter](https://img.shields.io/badge/BOM-fix--byte--order--marker-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![CICDLinter](https://img.shields.io/badge/CI/CD-actionlint-blue)](https://github.com/rhysd/actionlint)
[![CICDSecurityChecker](https://img.shields.io/badge/CI/CD--security-zizmor-yellow)](https://github.com/zizmorcore/zizmor)
[![CaseConflictChecker](https://img.shields.io/badge/case--conflict-check--case--conflict-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![DependencyChecker](https://img.shields.io/badge/dependencies-deptry-blue)](https://github.com/osprey-oss/deptry)
[![EndOfFileFormatter](https://img.shields.io/badge/EOF-end--of--file--fixer-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![EndOfLineFormatter](https://img.shields.io/badge/EOL-mixed--line--ending-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![JSONFormatter](https://img.shields.io/badge/JSON-pretty--format--json-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![JSONLinter](https://img.shields.io/badge/JSON-check--json-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![LargeFileChecker](https://img.shields.io/badge/large--files-check--added--large--files-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![MarkdownLinter](https://img.shields.io/badge/Markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![MergeConflictChecker](https://img.shields.io/badge/merge--conflict-check--merge--conflict-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![ModuleTestNamingChecker](https://img.shields.io/badge/test--naming-name--tests--test-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SecretsChecker](https://img.shields.io/badge/secrets-detect--secrets-blue)](https://github.com/Yelp/detect-secrets)
[![SecurityChecker](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![ShellFormatter](https://img.shields.io/badge/shell-shfmt-orange)](https://github.com/mvdan/sh)
[![ShellLinter](https://img.shields.io/badge/shell-shellcheck-blue)](https://github.com/koalaman/shellcheck)
[![SpellChecker](https://img.shields.io/badge/spell--check-typos-blue)](https://github.com/crate-ci/typos)
[![TOMLLinter](https://img.shields.io/badge/TOML-tombi-blueviolet)](https://github.com/tombi-toml/tombi)
[![TrailingWhitespaceFormatter](https://img.shields.io/badge/whitespace-trailing--whitespace--fixer-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![YAMLLinter](https://img.shields.io/badge/YAML-ryl-red)](https://github.com/owenlamont/ryl)
<!-- tooling -->
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pyrigger](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig-codeql?style=social)](https://github.com/Winipedia/pyrig-codeql)
[![VersionControlHookManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
<!-- project-info -->
[![DocsBuilder](https://img.shields.io/badge/Documentation-zensical-326CE5)](https://Winipedia.github.io/pyrig-codeql)
[![PackageIndex](https://img.shields.io/pypi/v/pyrig-codeql?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig-codeql)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig-codeql)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig-codeql)](https://github.com/Winipedia/pyrig-codeql/blob/main/LICENSE)

---

> A pyrig plugin that integrates GitHub CodeQL.

---

## Overview

`pyrig-codeql` is a [pyrig](https://github.com/Winipedia/pyrig) plugin that
extends pyrig's generated GitHub Actions health-check workflow with a CodeQL
analysis job. Install it as a development dependency, then run `pyrig sync`;
plugin discovery applies the override automatically.

```bash
uv add pyrig-codeql --dev
uv run pyrig sync
```

## Analysis job

The plugin adds an `analyze` job to the generated health-check workflow. Its
matrix runs two independent analyses:

| Language | Scope |
| --- | --- |
| `python` | Python source code |
| `actions` | GitHub Actions workflow files |

Each matrix job checks out the repository, initializes CodeQL, and performs the
analysis. The initialization step uses advanced setup with:

- `build-mode: none`, because neither analyzed language requires compilation;
- `queries: security-and-quality`, which is the strictest setting available.

The analysis step uploads the results to GitHub code scanning. Findings reported
by CodeQL do not make the action step fail; failures to run the analysis still
fail the job.

The `analyze` job is added to the aggregate `health-check` job's `needs` list.
As a result, the aggregate health check waits for CodeQL as well as the normal
project checks and remains the workflow's release gate.

## API Reference

For class- and method-level details, see the [API Reference](api.md), generated
automatically from the source.
