import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker
from workflow_log import WorkflowLog
from workflow_application_error import WorkflowApplicationError
from workflow_NDE import WorkflowNDE
from activities import activity_1, activity_2


queue = "demo-task-queue"

workflows = [
    WorkflowLog,
    WorkflowNDE,
    WorkflowApplicationError
]


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s  - %(message)s"
    )

    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    worker = Worker(
        client,
        task_queue=queue,
        workflows=workflows,
        activities=[activity_1, activity_2],
        #workflow_failure_exception_types=[WorkflowApplicationError]
    )

    logging.info("Starting worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
