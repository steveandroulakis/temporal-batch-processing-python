import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow

from temporal_batch.activities import create_single_batch, process_record
from temporal_batch.shared import BatchParentWorkflowParams

BATCH_SIZE = 50
WINDOW_SIZE = 4
CONTINUE_AS_NEW_THRESHOLD = 500


@workflow.defn
class BatchChildWorkflow:
    @workflow.run
    async def run(self, batch: List[str]) -> None:
        tasks = [
            workflow.execute_activity(
                process_record,
                record,
                start_to_close_timeout=timedelta(seconds=60),
            )
            for record in batch
        ]
        await asyncio.gather(*tasks)


@workflow.defn
class BatchParentWorkflow:
    @workflow.run
    async def run(self, params: BatchParentWorkflowParams) -> None:
        active: set[asyncio.Task[None]] = set()
        processed = 0
        current_offset = params.offset

        while True:
            batch = await workflow.execute_activity(
                create_single_batch,
                args=[BATCH_SIZE, params.num_words, current_offset],
                start_to_close_timeout=timedelta(seconds=60),
            )
            if not batch:
                break

            if len(active) >= WINDOW_SIZE:
                done, active = await asyncio.wait(active, return_when=asyncio.FIRST_COMPLETED)

            child_task = asyncio.create_task(
                workflow.execute_child_workflow(BatchChildWorkflow.run, batch)
            )
            active.add(child_task)
            processed += 1
            current_offset += BATCH_SIZE

            if processed >= CONTINUE_AS_NEW_THRESHOLD:
                await asyncio.gather(*active)
                workflow.continue_as_new(
                    BatchParentWorkflowParams(params.num_words, current_offset)
                )

        if active:
            await asyncio.gather(*active)
