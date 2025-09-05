"""Unit tests for temporal batch processing workflows."""

import uuid
from typing import cast

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_batch.shared import BatchParentWorkflowParams
from temporal_batch.workflows import BatchChildWorkflow, BatchParentWorkflow

# Use a consistent task queue for all workflow tests
TEST_TASK_QUEUE = "workflow-test-queue"


class TestBatchChildWorkflow:
    """Test the BatchChildWorkflow."""

    @pytest.mark.asyncio
    async def test_batch_child_workflow_processes_batch(self) -> None:
        """Test that child workflow processes a batch of records."""
        test_batch: list[str] = ['apple', 'banana', 'cherry']
        activity_executions = 0
        
        @activity.defn(name="process_record")
        async def mock_process_record(record: str) -> str:
            nonlocal activity_executions
            activity_executions += 1
            return record.upper()
        
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=TEST_TASK_QUEUE,
                workflows=[BatchChildWorkflow],
                activities=[mock_process_record]
            ):
                result = cast(None, await env.client.execute_workflow(
                    BatchChildWorkflow.run,
                    test_batch,
                    id=str(uuid.uuid4()),
                    task_queue=TEST_TASK_QUEUE
                ))
                
                assert result is None  # Workflow doesn't return a value
                assert activity_executions == len(test_batch)  # All records processed

    @pytest.mark.asyncio
    async def test_batch_child_workflow_empty_batch(self) -> None:
        """Test child workflow with empty batch."""
        test_batch: list[str] = []
        activity_executions = 0
        
        @activity.defn(name="process_record")
        async def mock_process_record(record: str) -> str:
            nonlocal activity_executions
            activity_executions += 1
            return record.upper()
        
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=TEST_TASK_QUEUE,
                workflows=[BatchChildWorkflow],
                activities=[mock_process_record]
            ):
                result = cast(None, await env.client.execute_workflow(
                    BatchChildWorkflow.run,
                    test_batch,
                    id=str(uuid.uuid4()),
                    task_queue=TEST_TASK_QUEUE
                ))
                
                assert result is None  # Workflow doesn't return a value
                assert activity_executions == 0  # No records to process


class TestBatchParentWorkflow:
    """Test the BatchParentWorkflow."""

    @pytest.mark.asyncio
    async def test_batch_parent_workflow_small_dataset(self) -> None:
        """Test parent workflow with a small dataset."""
        params = BatchParentWorkflowParams(num_words=3, offset=0)
        batch_activity_executions = 0
        process_activity_executions = 0
        
        @activity.defn(name="create_single_batch")
        async def mock_create_batch(batch_size: int, read_until_line: int, offset: int) -> list[str]:
            nonlocal batch_activity_executions
            batch_activity_executions += 1
            if offset >= read_until_line:
                return []
            available_words = ['word1', 'word2', 'word3']
            start_idx = min(offset, len(available_words))
            end_idx = min(offset + batch_size, min(read_until_line, len(available_words)))
            return available_words[start_idx:end_idx]
        
        @activity.defn(name="process_record")
        async def mock_process_record(record: str) -> str:
            nonlocal process_activity_executions
            process_activity_executions += 1
            return record.upper()
        
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=TEST_TASK_QUEUE,
                workflows=[BatchParentWorkflow, BatchChildWorkflow],
                activities=[mock_create_batch, mock_process_record]
            ):
                result = cast(None, await env.client.execute_workflow(
                    BatchParentWorkflow.run,
                    params,
                    id=str(uuid.uuid4()),
                    task_queue=TEST_TASK_QUEUE
                ))
                
                assert result is None  # Workflow completes successfully
                assert batch_activity_executions >= 1  # At least one batch created
                assert process_activity_executions == 3  # All 3 words processed

    @pytest.mark.asyncio
    async def test_batch_parent_workflow_no_words(self) -> None:
        """Test parent workflow with no words to process."""
        params = BatchParentWorkflowParams(num_words=0, offset=0)
        batch_activity_executions = 0
        process_activity_executions = 0
        
        @activity.defn(name="create_single_batch")
        async def mock_create_empty_batch(batch_size: int, read_until_line: int, offset: int) -> list[str]:
            nonlocal batch_activity_executions
            batch_activity_executions += 1
            return []  # No words to process
        
        @activity.defn(name="process_record")
        async def mock_process_record(record: str) -> str:
            nonlocal process_activity_executions
            process_activity_executions += 1
            return record.upper()
        
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=TEST_TASK_QUEUE,
                workflows=[BatchParentWorkflow, BatchChildWorkflow],
                activities=[mock_create_empty_batch, mock_process_record]
            ):
                result = cast(None, await env.client.execute_workflow(
                    BatchParentWorkflow.run,
                    params,
                    id=str(uuid.uuid4()),
                    task_queue=TEST_TASK_QUEUE
                ))
                
                assert result is None  # Workflow completes successfully
                assert batch_activity_executions == 1  # One batch activity call
                assert process_activity_executions == 0  # No records to process