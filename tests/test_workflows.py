"""Unit tests for temporal batch processing workflows."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from temporalio.testing import WorkflowEnvironment

from temporal_batch.shared import BatchParentWorkflowParams
from temporal_batch.workflows import BatchChildWorkflow, BatchParentWorkflow


class TestBatchChildWorkflow:
    """Test the BatchChildWorkflow."""

    @pytest.mark.asyncio
    async def test_batch_child_workflow_processes_batch(
        self, temporal_env: WorkflowEnvironment
    ) -> None:
        """Test that child workflow processes a batch of records."""
        test_batch = ['apple', 'banana', 'cherry']
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchChildWorkflow]
            worker.activities = [AsyncMock(return_value='PROCESSED')]
            
            result = await temporal_env.get_client().execute_workflow(
                BatchChildWorkflow.run,
                test_batch,
                id='test-child-workflow',
                task_queue=temporal_env.task_queue
            )
            
            assert result is None  # Workflow doesn't return a value

    @pytest.mark.asyncio
    async def test_batch_child_workflow_empty_batch(
        self, temporal_env: WorkflowEnvironment
    ) -> None:
        """Test child workflow with empty batch."""
        test_batch = []
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchChildWorkflow]
            worker.activities = []
            
            result = await temporal_env.get_client().execute_workflow(
                BatchChildWorkflow.run,
                test_batch,
                id='test-child-workflow-empty',
                task_queue=temporal_env.task_queue
            )
            
            assert result is None


class TestBatchParentWorkflow:
    """Test the BatchParentWorkflow."""

    @pytest.mark.asyncio
    async def test_batch_parent_workflow_small_dataset(
        self, temporal_env: WorkflowEnvironment, mock_words_file: Path
    ) -> None:
        """Test parent workflow with a small dataset."""
        params = BatchParentWorkflowParams(num_words=3, offset=0)
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchParentWorkflow, BatchChildWorkflow]
            
            # Mock the activities
            async def mock_create_batch(*args):
                batch_size, read_until_line, offset = args
                if offset >= read_until_line:
                    return []
                return ['word1', 'word2', 'word3'][:min(batch_size, read_until_line - offset)]
            
            async def mock_process_record(record: str):
                return record.upper()
            
            worker.activities = [mock_create_batch, mock_process_record]
            
            result = await temporal_env.get_client().execute_workflow(
                BatchParentWorkflow.run,
                params,
                id='test-parent-workflow',
                task_queue=temporal_env.task_queue
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_batch_parent_workflow_no_words(
        self, temporal_env: WorkflowEnvironment
    ) -> None:
        """Test parent workflow with no words to process."""
        params = BatchParentWorkflowParams(num_words=0, offset=0)
        
        async with temporal_env.get_worker() as worker:
            worker.workflows = [BatchParentWorkflow, BatchChildWorkflow]
            
            async def mock_create_empty_batch(*args):
                return []
            
            worker.activities = [mock_create_empty_batch]
            
            result = await temporal_env.get_client().execute_workflow(
                BatchParentWorkflow.run,
                params,
                id='test-parent-workflow-empty',
                task_queue=temporal_env.task_queue
            )
            
            assert result is None