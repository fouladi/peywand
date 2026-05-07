# Contributing to Peywand

Welcome, and thanks for taking the time to contribute!

## Code of Conduct

Everyone participating in this project is expected to treat other people
with respect. Examples of behaviour that contributes to a positive
environment include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Showing empathy towards other participants

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| [uv](https://docs.astral.sh/uv/) | Python version & dependency management | see below |
| Python 3.14+ | Runtime (managed by uv) | via uv |
| [pre-commit](https://pre-commit.com/) | Git hook runner | `uv tool install pre-commit` |

### Installing uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or via pip / pipx if you already have Python available:

```bash
pip install uv
# or
pipx install uv
```

---

## Setting Up the Development Environment

### 1. Clone the repository

```bash
git clone <repository-url>
cd peywand
```

### 2. Create a virtual environment and install all dependencies

`uv` reads `pyproject.toml` and the `[dependency-groups]` dev group
automatically:

```bash
uv sync --group dev
```

This will:
- download and pin the correct Python version (3.14, from `.python-version`)
- create a `.venv` in the project root
- install runtime dependencies (`colored`, `sqlalchemy`, `textual`, `tqdm`)
- install dev dependencies (`pytest`, `pytest-cov`, `ruff`, `ty`, …)

### 3. Activate the virtual environment

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Or prefix every command with `uv run` to skip manual activation (see below).

### 4. Install pre-commit hooks

```bash
uv run pre-commit install
```

---

## Running the Application

```bash
uv run python peywand.py
```

Against a custom database path:

```bash
uv run python peywand.py --db-path ~/bookmarks.db
```

---

## Running the Tests

```bash
uv run pytest
```

With verbose output:

```bash
uv run pytest -v
```

To see `print()` output during tests:

```bash
uv run pytest -s
```

Coverage is reported automatically (configured in `pyproject.toml`).
To generate an HTML report instead:

```bash
uv run pytest --cov-report html
```

---

## Linting and Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting
and formatting. Pre-commit runs it automatically on every commit, but
you can also run it manually:

```bash
# Check for lint issues
uv run ruff check .

# Apply safe auto-fixes
uv run ruff check --fix .

# Format code
uv run ruff format .
```

Type checking is done with [ty](https://github.com/astral-sh/ty):

```bash
uv run ty check
```

---

## Managing Dependencies

Add a runtime dependency:

```bash
uv add <package>
```

Add a dev-only dependency:

```bash
uv add --group dev <package>
```

Remove a dependency:

```bash
uv remove <package>
```

After any dependency change, commit both `pyproject.toml` and `uv.lock`.

---

## Adding a New Import/Export Plugin

1. Create `pw/plugins/<format>_plugin.py` implementing the
   `ImportExportPlugin` protocol:

   ```python
   from pw.plugins.registry import register

   class YAMLPlugin:
       format = "yaml"

       def import_data(self, path, session_factory): ...
       def export_data(self, path, bookmarks): ...

   register(YAMLPlugin())
   ```

2. Import it in `pw/plugins/__init__.py`:

   ```python
   from pw.plugins.yaml_plugin import YAMLPlugin  # noqa
   ```

3. Add tests under `tests/plugins/`.

No changes to the service layer, TUI, or registry are required.

---

## Submitting Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b my-feature
   ```
2. Make your changes and ensure tests and lint pass.
3. Commit with a clear message describing *what* and *why*.
4. Open a pull request against `main`.
