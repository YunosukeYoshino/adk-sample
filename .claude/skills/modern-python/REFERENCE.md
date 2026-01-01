# Modern Python - Reference Guide

Detailed configurations, project structures, and command references.

## Table of Contents

- [Tool Configurations](#tool-configurations)
- [Project Structure](#project-structure)
- [Command Reference](#command-reference)
- [Monorepo Setup](#monorepo-setup)

---

## Tool Configurations

### uv - Package & Version Management

#### Basic Commands

```bash
# Initialize new project
uv init my-project

# Add dependencies
uv add fastapi pydantic uvicorn
uv add --dev pytest pytest-watch ruff mypy

# Install/sync dependencies
uv sync

# Run commands in virtual environment
uv run python main.py
uv run pytest

# Python version management
uv python install 3.12
uv python pin 3.12

# Remove dependencies
uv remove package-name
```

#### pyproject.toml - Dependencies Section

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Modern Python project"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic>=2.0",
    "uvicorn>=0.32.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-watch>=4.2",
    "pytest-cov>=6.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]
```

### Ruff - Linting & Formatting

#### pyproject.toml Configuration

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "RUF", # ruff-specific rules
]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["my_project"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### Common Commands

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check and format in one go
uv run ruff check --fix . && uv run ruff format .
```

### mypy - Type Checking

#### pyproject.toml Configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

#### Common Commands

```bash
# Type check all files
uv run mypy src/

# Type check specific file
uv run mypy src/my_project/main.py

# Show error codes
uv run mypy --show-error-codes src/
```

### pytest - Testing

#### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

#### Common Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_services.py

# Run tests matching pattern
uv run pytest -k "test_user"

# Watch mode (TDD)
uv run ptw -- tests/unit -v

# Parallel execution
uv add --dev pytest-xdist
uv run pytest -n auto
```

---

## Project Structure

### Single Package Structure (Recommended for Most Projects)

```
my-project/
├── .python-version          # Python version (e.g., 3.12)
├── pyproject.toml           # Project config & dependencies
├── uv.lock                  # Lock file (auto-generated)
├── README.md
├── .gitignore
├── src/
│   └── my_project/          # Main package
│       ├── __init__.py
│       ├── main.py          # Entry point
│       │
│       ├── domain/          # Business logic layer
│       │   ├── __init__.py
│       │   ├── models.py    # Pydantic models, entities
│       │   └── services.py  # Business logic services
│       │
│       ├── ports/           # Interfaces (add when needed)
│       │   ├── __init__.py
│       │   └── repositories.py  # Protocol classes
│       │
│       └── adapters/        # External integrations
│           ├── __init__.py
│           ├── api.py       # FastAPI routes
│           ├── database.py  # Database clients
│           └── llm.py       # LLM clients
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    │
    ├── unit/                # Fast, isolated tests
    │   ├── __init__.py
    │   ├── test_models.py
    │   └── test_services.py
    │
    ├── integration/         # Tests with dependencies
    │   ├── __init__.py
    │   ├── test_database.py
    │   └── test_llm.py
    │
    └── functional/          # E2E tests
        ├── __init__.py
        └── test_api.py
```

### Flat Structure (For Scripts/PoC)

```
my-script/
├── pyproject.toml
├── main.py              # Everything in one file
└── tests/
    └── test_main.py
```

### Monorepo Structure (uv Workspaces)

```
my-monorepo/
├── pyproject.toml           # Workspace root
├── uv.lock                  # Shared lock file
├── README.md
│
├── packages/                # Shared libraries
│   ├── core/
│   │   ├── pyproject.toml
│   │   └── src/core/
│   │       ├── __init__.py
│   │       └── models.py
│   │
│   └── utils/
│       ├── pyproject.toml
│       └── src/utils/
│           ├── __init__.py
│           └── helpers.py
│
└── projects/                # Applications
    ├── api/
    │   ├── pyproject.toml
    │   └── src/api/
    │       ├── __init__.py
    │       └── main.py
    │
    └── worker/
        ├── pyproject.toml
        └── src/worker/
            ├── __init__.py
            └── tasks.py
```

---

## Command Reference

### Project Initialization Workflow

```bash
# 1. Create new project
uv init my-llm-app
cd my-llm-app

# 2. Set Python version
uv python install 3.12
uv python pin 3.12

# 3. Add production dependencies
uv add fastapi pydantic uvicorn instructor openai

# 4. Add development dependencies
uv add --dev pytest pytest-watch pytest-cov ruff mypy

# 5. Create directory structure
mkdir -p src/my_llm_app/{domain,ports,adapters}
mkdir -p tests/{unit,integration,functional}

# 6. Create __init__.py files
touch src/my_llm_app/__init__.py
touch src/my_llm_app/domain/__init__.py
touch src/my_llm_app/ports/__init__.py
touch src/my_llm_app/adapters/__init__.py
touch tests/__init__.py

# 7. Configure tools in pyproject.toml
# (See tool configurations above)

# 8. Initialize git
git init
echo ".venv/" >> .gitignore
echo "uv.lock" >> .gitignore  # Or commit it for reproducibility
```

### Development Workflow

```bash
# Start development server (FastAPI)
uv run uvicorn src.my_llm_app.main:app --reload

# Run tests in watch mode (TDD)
uv run ptw -- tests/unit -v

# Quality checks before commit
uv run ruff check --fix .
uv run ruff format .
uv run mypy src/
uv run pytest --cov=src
```

### Dependency Management

```bash
# Show installed packages
uv pip list

# Show dependency tree
uv pip tree

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add --upgrade package-name

# Export requirements (for compatibility)
uv pip freeze > requirements.txt
```

---

## Monorepo Setup

### Root pyproject.toml

```toml
[tool.uv.workspace]
members = [
    "packages/*",
    "projects/*",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]
```

### Package pyproject.toml Example

```toml
# packages/core/pyproject.toml
[project]
name = "core"
version = "0.1.0"
dependencies = [
    "pydantic>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Application pyproject.toml Example

```toml
# projects/api/pyproject.toml
[project]
name = "api"
version = "0.1.0"
dependencies = [
    "fastapi>=0.115.0",
    "core",  # Reference workspace package
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Monorepo Commands

```bash
# Install all workspace packages
uv sync

# Add dependency to specific package
cd packages/core
uv add new-dependency

# Run tests across all packages
uv run pytest

# Build specific package
cd packages/core
uv build

# Use workspace package in another package
# In projects/api/pyproject.toml:
# dependencies = ["core"]
# uv will automatically link them in editable mode
```

### Benefits of uv Workspaces

- **Editable installs**: Changes to libraries immediately available
- **Shared lock file**: Consistent dependency versions
- **Fast**: uv resolves workspace dependencies efficiently
- **No publish needed**: Direct path-based dependencies

---

## Docker Integration

### Dockerfile with uv

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src ./src

# Run application
CMD ["uv", "run", "uvicorn", "src.my_project.main:app", "--host", "0.0.0.0"]
```

### Multi-stage Build (Optimized)

```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "src.my_project.main:app", "--host", "0.0.0.0"]
```

---

## Pre-commit Hooks (Optional)

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0]
```

### Setup

```bash
uv add --dev pre-commit
uv run pre-commit install
```

---

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
