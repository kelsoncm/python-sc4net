# Contributing

Thank you for considering a contribution to sc4net!

---

## Development setup

### 1. Clone the repository

```bash
git clone https://github.com/kelsoncm/sc4net.git
cd sc4net
```

### 2. Create a virtual environment

=== "Linux / macOS"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

### 3. Install all development dependencies

```bash
pip install -e ".[dev]"
```

This installs `sc4net` in editable mode plus the full dev toolchain:
`pytest`, `pytest-cov`, `pyftpdlib`, `flake8`, `flake8-bandit`, `black`, `isort`, `bandit`.

---

## Running the test suite

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=sc4net --cov-report=term-missing --cov-report=xml
```

The project enforces 100 % test coverage.

---

## Code quality

### Install pre-commit hooks

```bash
pip install pre-commit
pre-commit install                     # runs on every commit
pre-commit install --hook-type pre-push  # runs tests + coverage gate before push
```

### Hooks summary

| Stage | Hook | What it does |
|-------|------|--------------|
| `pre-commit` | black | Auto-formats code (line length 127) |
| `pre-commit` | isort | Sorts imports |
| `pre-commit` | bandit | Security static analysis |
| `pre-commit` | flake8 + flake8-bandit | Style and security lint |
| `pre-push` | pytest | Runs full test suite with coverage |
| `pre-push` | pytest-coverage-gate | Fails if coverage regresses below baseline |

### Run hooks manually

```bash
pre-commit run --all-files          # pre-commit stage
pre-commit run --all-files --hook-stage pre-push  # pre-push stage
```

---

## Submitting a pull request

1. Fork the repository and create a feature branch.
2. Write tests that cover your changes — the CI enforces 100 % coverage.
3. Commit with a meaningful message; all pre-commit hooks will run automatically.
4. Open a pull request against `main`.

---

## Building the documentation locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

Open <http://127.0.0.1:8000> in your browser.
