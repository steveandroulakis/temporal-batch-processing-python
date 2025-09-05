#!/usr/bin/env python3
"""Start the batch processing workflow."""

import asyncio
import logging
import sys
import time

from temporalio.client import Client

from temporal_batch.shared import ADDRESS, TASK_QUEUE, BatchParentWorkflowParams
from temporal_batch.workflows import BatchParentWorkflow


async def main() -> None:
    """Start the batch processing workflow."""
    logging.basicConfig(level=logging.INFO)
    num_words = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    client = await Client.connect(ADDRESS)
    await client.execute_workflow(
        BatchParentWorkflow.run,
        BatchParentWorkflowParams(num_words, 0),
        id=f"batch-parent-workflow-{int(time.time())}",
        task_queue=TASK_QUEUE,
    )
    print("Batch processing complete")


if __name__ == "__main__":
    asyncio.run(main())