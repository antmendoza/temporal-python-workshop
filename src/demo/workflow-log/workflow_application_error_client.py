import asyncio
import uuid

from temporalio.client import Client
from temporalio.common import RetryPolicy

from temporal_worker import queue
from workflow_application_error import WorkflowInput, WorkflowApplicationError


async def main():
    client = await Client.connect("localhost:7233")

    workflow_handle = await client.start_workflow(
        WorkflowApplicationError.run,
        WorkflowInput(
            input_1="input_1",
            input_2=str(uuid.uuid4()),
        ),
        id="my-business-id-" + str(uuid.uuid4()),
        task_queue=queue,
        retry_policy=RetryPolicy(
            non_retryable_error_types=[
                # EntityNotFoundError,
            ]
        )

    )

    print("Workflow started with workflow_id:", workflow_handle.id)
    print("Result:", await workflow_handle.result())


if __name__ == "__main__":
    asyncio.run(main())
