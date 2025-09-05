"""Pytest configuration and fixtures for temporal batch processing tests."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from temporalio.testing import WorkflowEnvironment



@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def temporal_env() -> AsyncGenerator[WorkflowEnvironment, None]:
    """Provide a Temporal test environment."""
    env = await WorkflowEnvironment.start_time_skipping()
    try:
        yield env
    finally:
        await env.shutdown()


@pytest.fixture
def test_words_file() -> Generator[Path, None, None]:
    """Create a temporary words file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
        for word in test_words:
            f.write(f"{word}\n")
        f.flush()
        yield Path(f.name)
    
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def mock_words_file(monkeypatch: pytest.MonkeyPatch, test_words_file: Path) -> Path:
    """Mock the WORDS_FILE constant to use test data."""
    from temporal_batch import activities
    monkeypatch.setattr(activities, 'WORDS_FILE', test_words_file)
    return test_words_file