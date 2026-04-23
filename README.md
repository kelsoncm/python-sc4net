# sc4net

[![Publish](https://github.com/kelsoncm/sc4net/actions/workflows/pythonapp.yml/badge.svg)](https://github.com/kelsoncm/sc4net/actions/workflows/publish.yml)
![Version](https://img.shields.io/pypi/v/sc4net)
[![Coverage](https://codecov.io/gh/kelsoncm/sc4net/branch/main/graph/badge.svg?flag=sc4net)](https://codecov.io/gh/kelsoncm/sc4net)

Network helpers for HTTP(S) and FTP downloads, with convenience JSON and ZIP readers.

## Installation

```bash
pip install sc4net
```

## Security

Please report vulnerabilities according to [SECURITY.md](SECURITY.md).

## How to contribute

```bash
git clone git@github.com:kelsoncm/sc4.git ~/projetos/PESSOAL/sc4net
code ~/projetos/PESSOAL/sc4net
```

## Pre-commit

This repository uses [pre-commit](https://pre-commit.com/) to run quality checks
before each commit and coverage regression checks before each push.

Setup:

```bash
python -m venv .venv
.venv\bin\activate
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip uv
uv pip install --upgrade -e ".[dev]"
pre-commit install
pre-commit install --hook-type pre-push
```

Run manually:

```bash
pre-commit run --all-files
pre-commit run --hook-stage pre-push --all-files
```

Hooks:

* **pre-commit**: `black`, `isort`, `bandit`, `flake8` (with `flake8-bandit`)
* **pre-push**:
  1. Runs `pytest --cov=sc4net --cov-report=xml` to produce `coverage.xml`
  2. [`pytest-coverage-gate`](https://github.com/kelsoncm/pytest-coverage-gate) reads
     `coverage.xml`, compares against `.coverage-baseline` (2 decimal places), blocks
     the push on regression and updates the baseline on improvement
* **GitHub Actions only**: `semgrep` SAST
