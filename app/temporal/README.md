## How to Start the Temporal Worker

To start the worker locally:

`python -m app.temporal.worker`

This will connect the worker to the Temporal server and start polling the `sync-tasks` task queue.

## Temporal UI

You can view and monitor workflow executions using the Temporal UI:

```
http://localhost:8233/
```

