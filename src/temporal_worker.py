import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

#from src.workflow.activities import activities
# from src.workflow.activities_v4 import activities
from src.workflow.activities import activities
from src.workflow.system_patch_workflow_v1 import SystemPatchWorkflow_V1
from src.workflow.system_patch_workflow_v2 import SystemPatchWorkflow_V2
from src.workflow.system_patch_workflow_v3 import SystemPatchWorkflow_V3
from src.workflow.system_patch_workflow_v4 import SystemPatchWorkflow_V4
from src.workflow.system_patch_workflow_v5 import SystemPatchWorkflow_V5
from src.workflow.system_patch_workflow_v6 import SystemPatchWorkflow_V6, SystemPatchWorkflow_Cluster_V6, \
    SystemPatchWorkflow_Host_V6
from src.workflow.system_patch_workflow_v7 import SystemPatchWorkflow_Host_V7, SystemPatchWorkflow_Cluster_V7, \
    SystemPatchWorkflow_V7
from src.workflow.types import MyVaultClient

queue = "system_patch-task-queue"

workflows = [
    SystemPatchWorkflow_V1,
    SystemPatchWorkflow_V2,
    SystemPatchWorkflow_V3,
    SystemPatchWorkflow_V4,
    SystemPatchWorkflow_V5,
    SystemPatchWorkflow_V6,
    SystemPatchWorkflow_Cluster_V6,
    SystemPatchWorkflow_Host_V6,
    SystemPatchWorkflow_V7,
    SystemPatchWorkflow_Cluster_V7,
    SystemPatchWorkflow_Host_V7,
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
        activities=activities(MyVaultClient())
    )

    logging.info("Starting worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
