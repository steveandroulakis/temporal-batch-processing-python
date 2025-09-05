from dataclasses import dataclass
import os

TASK_QUEUE = os.getenv("TEMPORAL_BATCHPROCESSING_TASKQUEUE", "BatchWorkflow")
ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")


@dataclass
class BatchParentWorkflowParams:
    num_words: int
    offset: int = 0
