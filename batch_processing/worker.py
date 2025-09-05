import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import create_single_batch, process_record
from shared import ADDRESS, TASK_QUEUE
from workflow import BatchChildWorkflow, BatchParentWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    client = await Client.connect(ADDRESS)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[BatchParentWorkflow, BatchChildWorkflow],
        activities=[create_single_batch, process_record],
        max_task_queue_activities_per_second=150,
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
