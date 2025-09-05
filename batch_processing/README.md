# Batch Processing Sample (Python)

Processes words from `tmp_batch_java/core/words_alpha.txt` in batches using Temporal Workflows.

## Running

Start a worker:

```bash
uv run worker.py &
echo $! > worker.pid
```

Start the workflow (process 20 words):

```bash
uv run starter.py 20
```

Shut down the worker:

```bash
kill $(cat worker.pid)
rm worker.pid
```
