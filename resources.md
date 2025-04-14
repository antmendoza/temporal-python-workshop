# Temporal Failures reference
- https://docs.temporal.io/references/failures

```
An error in a Workflow can cause either a Workflow Task Failure (the Task will be retried) or a Workflow Execution Failure (the Workflow is marked as failed).
```





# General considerations
- Never block the async io loop in an async function
  - https://github.com/temporalio/dev-success/blob/main/python/troubleshooting_guide.md#the-thread-inside-an-async-def-python-function-is-blocked
- Watch the payload size //TODO
- Watch the workflow history length //TODO
    - ContinueAsNew



// add data converters to encrypt/decrypt data