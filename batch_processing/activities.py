import asyncio
import random
from pathlib import Path
from typing import List

from temporalio import activity

# Path to words file located in tmp_batch_java
WORDS_FILE = Path(__file__).parents[1] / "tmp_batch_java" / "core" / "words_alpha.txt"


@activity.defn
async def create_single_batch(batch_size: int, read_until_line: int, offset: int) -> List[str]:
    """Read a batch of words from the words file."""
    if offset >= read_until_line:
        return []

    words: List[str] = []
    with open(WORDS_FILE, "r") as f:
        # Skip already processed lines
        for _ in range(offset):
            if not f.readline():
                return []
        # Read up to batch_size lines, but not beyond read_until_line
        for i in range(batch_size):
            if offset + i >= read_until_line:
                break
            line = f.readline()
            if not line:
                break
            words.append(line.strip())
    return words


@activity.defn
async def process_record(record: str) -> str:
    """Convert a record to uppercase with simulated delay."""
    delay_ms = 10
    if random.random() < 0.05:
        delay_ms = 1000
    await asyncio.sleep(delay_ms / 1000)
    return record.upper()
