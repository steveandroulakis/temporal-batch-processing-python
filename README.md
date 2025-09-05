# Temporal Batch Processing (Python)

A Python implementation demonstrating batch processing using Temporal Workflows. This sample processes words from a data file in batches, showcasing the parent-child workflow pattern with concurrency control and automatic continuation.

## Architecture

The system implements a parent-child workflow pattern:

- **BatchParentWorkflow**: Orchestrates batch processing with windowing (max 4 concurrent child workflows) and continue-as-new for large datasets
- **BatchChildWorkflow**: Processes individual batches of records concurrently
- **Activities**: File reading and record processing with simulated delays

## Project Structure

```
temporal-batch-processing-python/
├── src/temporal_batch/          # Core package
│   ├── shared.py               # Configuration and data models
│   ├── workflows.py            # Workflow definitions
│   └── activities.py           # Activity implementations
├── scripts/                    # CLI executables
│   ├── start_worker.py         # Worker startup script
│   └── run_workflow.py         # Workflow execution script
├── data/                       # Project data files
│   └── words_alpha.txt         # Word dataset (370k+ words)
├── tests/                      # Test suite
│   ├── test_activities.py      # Unit tests for activities
│   ├── test_workflows.py       # Unit tests for workflows
│   └── integration/            # Integration tests
└── pyproject.toml              # Project configuration
```

## Getting Started

### Prerequisites

- Python 3.11+
- uv package manager
- Running Temporal server (localhost:7233 by default)

### Installation

```bash
# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Running the System

1. **Start the worker:**
   ```bash
   uv run scripts/start_worker.py &
   echo $! > worker.pid
   ```

2. **Execute workflow (process N words):**
   ```bash
   uv run scripts/run_workflow.py 100
   ```

3. **Stop the worker:**
   ```bash
   kill $(cat worker.pid)
   rm worker.pid
   ```

### Using Installed Commands

After installation, you can also use the installed commands:

```bash
# Start worker
temporal-worker &

# Run workflow
temporal-workflow 100
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test types
uv run pytest tests/test_activities.py     # Unit tests
uv run pytest tests/integration/          # Integration tests
```

### Code Quality

```bash
# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy --strict src/ scripts/ tests/
```

## Configuration

Environment variables for Temporal connection:

- `TEMPORAL_BATCHPROCESSING_TASKQUEUE`: Task queue name (default: "BatchWorkflow")
- `TEMPORAL_ADDRESS`: Temporal server address (default: "localhost:7233")
- `TEMPORAL_NAMESPACE`: Temporal namespace (default: "default")

## Key Features

- **Batch Processing**: Configurable batch size (default: 50 records)
- **Concurrency Control**: Window-based processing (max 4 concurrent batches)
- **Continue-as-New**: Automatic continuation for large datasets (>500 batches)
- **Error Handling**: Built-in retry mechanisms via Temporal
- **Observability**: Structured logging and Temporal's built-in monitoring

## Sample Data

The project includes a dataset of 370,000+ English words for processing. The `process_record` activity converts words to uppercase with simulated processing delays (10ms normal, 1s for 5% of records).

## License

MIT License - see LICENSE file for details.