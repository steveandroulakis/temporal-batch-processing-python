import asyncio
import logging
import sys
import time

from temporalio.client import Client

from shared import ADDRESS, TASK_QUEUE, BatchParentWorkflowParams
from workflow import BatchParentWorkflow


async def main() -> None:
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
