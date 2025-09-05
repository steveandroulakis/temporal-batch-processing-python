"""Integration tests for end-to-end batch processing."""

from pathlib import Path

import pytest
from temporalio.testing import WorkflowEnvironment

from temporal_batch.activities import create_single_batch, process_record
from temporal_batch.shared import BatchParentWorkflowParams
from temporal_batch.workflows import BatchChildWorkflow, BatchParentWorkflow


class TestBatchProcessingIntegration:
    """Integration tests for the complete batch processing system."""

    @pytest.mark.asyncio
    async def test_end_to_end_batch_processing(
        self, temporal_env: WorkflowEnvironment, mock_words_file: Path
    ) -> None:
        """Test complete batch processing from start to finish."""
        params = BatchParentWorkflowParams(num_words=5, offset=0)
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchParentWorkflow, BatchChildWorkflow]
            worker.activities = [create_single_batch, process_record]
            
            # Execute the workflow and verify it completes successfully
            result = await temporal_env.get_client().execute_workflow(
                BatchParentWorkflow.run,
                params,
                id='test-integration-workflow',
                task_queue=temporal_env.task_queue
            )
            
            # Workflow should complete without errors
            assert result is None

    @pytest.mark.asyncio
    async def test_batch_processing_with_offset(
        self, temporal_env: WorkflowEnvironment, mock_words_file: Path
    ) -> None:
        """Test batch processing starting from an offset."""
        params = BatchParentWorkflowParams(num_words=3, offset=2)
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchParentWorkflow, BatchChildWorkflow]
            worker.activities = [create_single_batch, process_record]
            
            result = await temporal_env.get_client().execute_workflow(
                BatchParentWorkflow.run,
                params,
                id='test-integration-workflow-offset',
                task_queue=temporal_env.task_queue
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_activity_create_single_batch_integration(
        self, mock_words_file: Path
    ) -> None:
        """Test the create_single_batch activity with real file operations."""
        # Test reading first batch
        batch1 = await create_single_batch(batch_size=2, read_until_line=5, offset=0)
        assert len(batch1) == 2
        assert batch1 == ['apple', 'banana']
        
        # Test reading second batch with offset
        batch2 = await create_single_batch(batch_size=2, read_until_line=5, offset=2)
        assert len(batch2) == 2
        assert batch2 == ['cherry', 'date']
        
        # Test reading final batch
        batch3 = await create_single_batch(batch_size=2, read_until_line=5, offset=4)
        assert len(batch3) == 1
        assert batch3 == ['elderberry']

    @pytest.mark.asyncio
    async def test_activity_process_record_integration(self) -> None:
        """Test the process_record activity with various inputs."""
        # Test normal processing
        result1 = await process_record("test")
        assert result1 == "TEST"
        
        # Test with mixed case
        result2 = await process_record("TeSt")
        assert result2 == "TEST"
        
        # Test with special characters
        result3 = await process_record("test-123_abc")
        assert result3 == "TEST-123_ABC"