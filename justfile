set quiet := true
set unstable := true
set positional-arguments := true
set script-interpreter := ['uv', 'run', '--frozen', '--script', '--quiet', '--all-extras', '--all-groups']

# Paths to check when running on all files

PATHS := "dral tests"

# Default recipe - shows available commands
default:
    @just --list

# Run full quality assurance suite for CHANGED FILES (lint, format, fix, hooks, test)
all: fix hooks format lint tests

# Run tests with pytest
tests *args:
    uv run --frozen pytest {{ args }} tests

# Check ALL PYTHON FILES for linting issues with ruff
lint *args:
    echo ">>> Linting all files..."
    uv run --frozen ruff check {{ args }} {{ PATHS }}

# Format ALL PYTHON FILES with ruff
format *args:
    echo ">>> Formatting all files..."
    uv run --frozen ruff format {{ args }} {{ PATHS }}

# Auto-fix ALL PYTHON FILES linting issues with ruff
fix:
    echo ">>> Auto-fixing all files..."
    uv run --frozen ruff check --fix {{ PATHS }}

# Run pre-commit hooks on ALL FILES
hooks $SKIP="ruff-format":
    echo ">>> Running pre-commit hooks on all files..."
    uv run --frozen --active pre-commit run --all-files --show-diff-on-failure --color=always

# Install dependencies using uv
install:
    echo ">>> Installing dependencies..."
    uv sync --locked --all-groups --all-extras
