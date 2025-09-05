"""Unit tests for temporal batch processing activities."""

from pathlib import Path

import pytest

from temporal_batch.activities import create_single_batch, process_record


class TestCreateSingleBatch:
    """Test the create_single_batch activity."""

    @pytest.mark.asyncio
    async def test_read_batch_from_start(self, mock_words_file: Path) -> None:
        """Test reading a batch from the start of the file."""
        result = await create_single_batch(batch_size=3, read_until_line=5, offset=0)
        
        assert len(result) == 3
        assert result == ['apple', 'banana', 'cherry']

    @pytest.mark.asyncio
    async def test_read_batch_with_offset(self, mock_words_file: Path) -> None:
        """Test reading a batch with an offset."""
        result = await create_single_batch(batch_size=2, read_until_line=5, offset=2)
        
        assert len(result) == 2
        assert result == ['cherry', 'date']

    @pytest.mark.asyncio
    async def test_read_beyond_limit(self, mock_words_file: Path) -> None:
        """Test reading beyond the read_until_line limit."""
        result = await create_single_batch(batch_size=10, read_until_line=3, offset=0)
        
        assert len(result) == 3
        assert result == ['apple', 'banana', 'cherry']

    @pytest.mark.asyncio
    async def test_offset_beyond_limit(self, mock_words_file: Path) -> None:
        """Test when offset is beyond the read_until_line limit."""
        result = await create_single_batch(batch_size=5, read_until_line=3, offset=5)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_batch_size_exceeds_available(self, mock_words_file: Path) -> None:
        """Test when batch size exceeds available words."""
        result = await create_single_batch(batch_size=10, read_until_line=5, offset=3)
        
        assert len(result) == 2
        assert result == ['date', 'elderberry']


class TestProcessRecord:
    """Test the process_record activity."""

    @pytest.mark.asyncio
    async def test_process_record_uppercase(self) -> None:
        """Test that process_record converts to uppercase."""
        result = await process_record("hello")
        
        assert result == "HELLO"

    @pytest.mark.asyncio
    async def test_process_record_empty_string(self) -> None:
        """Test processing an empty string."""
        result = await process_record("")
        
        assert result == ""

    @pytest.mark.asyncio
    async def test_process_record_special_characters(self) -> None:
        """Test processing string with special characters."""
        result = await process_record("hello-world_123")
        
        assert result == "HELLO-WORLD_123"