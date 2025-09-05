# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Temporal batch processing sample that demonstrates processing words from a data file in batches using Temporal Workflows. The system uses a parent-child workflow pattern with src-layout packaging, proper separation of concerns, and comprehensive testing.

## Key Architecture Components

### Project Structure (src-layout)
```
src/temporal_batch/           # Core package
├── shared.py                # Configuration constants and data models
├── workflows.py             # Parent and child workflow definitions  
└── activities.py            # File reading and record processing activities

scripts/                     # CLI executables (separate from library code)
├── start_worker.py          # Worker startup script
└── run_workflow.py          # Workflow execution script

data/                        # Project data files
└── words_alpha.txt          # Word dataset (370k+ words, self-contained)

tests/                       # Comprehensive test suite
├── conftest.py             # Pytest fixtures and configuration
├── test_activities.py      # Unit tests for activities
├── test_workflows.py       # Unit tests for workflows
└── integration/            # Integration tests
```

### Workflow Pattern
- **BatchParentWorkflow**: Orchestrates batch processing with windowing (max 4 concurrent children) and continue-as-new for large datasets (>500 batches)
- **BatchChildWorkflow**: Processes individual batches concurrently using asyncio.gather()
- **Activities**: File reading with offset pagination and record processing with simulated delays

### Import Structure
All imports use absolute package paths:
- `from temporal_batch.shared import ...`
- `from temporal_batch.workflows import ...`
- `from temporal_batch.activities import ...`

## Development Commands

### Running the System
Start a worker:
```bash
uv run scripts/start_worker.py &
echo $! > worker.pid
```

Execute workflow (process N words):
```bash
uv run scripts/run_workflow.py 100
```

Stop the worker:
```bash
kill $(cat worker.pid)
rm worker.pid
```

### Using Installed Commands (after `uv pip install -e .`)
```bash
temporal-worker &           # Start worker
temporal-workflow 100       # Run workflow
```

### Development Tools
Linting and formatting:
```bash
uv run ruff check .
uv run ruff format .
```

Type checking (strict mode):
```bash
uv run mypy --strict src/ scripts/ tests/
```

Testing:
```bash
uv run pytest                           # All tests
uv run pytest tests/test_activities.py  # Unit tests only
uv run pytest tests/integration/        # Integration tests only
uv run pytest --cov=src                # With coverage
```

### Package Management
- Project configuration in root `pyproject.toml` (not nested)
- Package name: `temporal-batch` 
- Uses `uv` for all package operations
- Core dependency: `temporalio>=1.17.0`
- Dev dependencies: `mypy`, `pytest`, `ruff`
- Python >=3.11 required

## Key Features

- **Self-contained**: No external dependencies on sibling projects
- **Standard packaging**: Follows src-layout best practices for Python packages
- **Separation of concerns**: CLI scripts separate from library code
- **Comprehensive testing**: Unit tests, integration tests, and proper fixtures
- **Type safety**: Full type hints with strict mypy checking
- **Batch processing**: Configurable batch size (50) and concurrency (window size 4)
- **Scalability**: Continue-as-new pattern for large datasets

## Environment Configuration
Environment variables for Temporal connection:
- `TEMPORAL_BATCHPROCESSING_TASKQUEUE` (default: "BatchWorkflow")
- `TEMPORAL_ADDRESS` (default: "localhost:7233")  
- `TEMPORAL_NAMESPACE` (default: "default")

## Data Processing
- Processes words from local `data/words_alpha.txt` file (370k+ words)
- `create_single_batch` activity: Sequential file reading with offset-based pagination
- `process_record` activity: Uppercase conversion with simulated delays (10ms normal, 1s for 5% of records)