#!/usr/bin/env python3
"""Start the Temporal worker for batch processing."""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from temporal_batch.activities import create_single_batch, process_record
from temporal_batch.shared import ADDRESS, TASK_QUEUE
from temporal_batch.workflows import BatchChildWorkflow, BatchParentWorkflow


async def main() -> None:
    """Start the Temporal worker."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Connecting to Temporal at: {ADDRESS}")
    logger.info(f"Using task queue: {TASK_QUEUE}")
    
    try:
        client = await Client.connect(ADDRESS)
        logger.info("Successfully connected to Temporal server")
        logger.info(f"Client identity: {client.identity}")
        logger.info(f"Namespace: {client.namespace}")
        
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[BatchParentWorkflow, BatchChildWorkflow],
            activities=[create_single_batch, process_record],
            max_task_queue_activities_per_second=150,
        )
        logger.info("Worker created successfully, starting worker...")
        await worker.run()
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())