import asyncio
import random

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy

from src.temporal_worker import queue
from src.temporal_worker_v8 import init_runtime_with_prometheus
from src.workflow.system_patch_workflow_v7 import SystemPatchWorkflow_V7
from src.workflow.types import SystemPatchWorkflowInput

SystemPatchWorkflow = SystemPatchWorkflow_V7



async def main():
    runtime = init_runtime_with_prometheus(8085)

    # Connect client
    client = await Client.connect(
        "localhost:7233",
        runtime=runtime,
    )

    tasks = [asyncio.create_task(
        start_workflow(client, i)
    ) for i in range(1,6)]


    await asyncio.sleep(3)  # revisar


    for task in tasks:
        workflow_id = await task
        print("Workflow started with workflow_id:", workflow_id)
        await client.get_workflow_handle(workflow_id).signal(SystemPatchWorkflow.approve_request)  # revisar


# revisar
async def query_workflow(workflow_handle):
    while True:
        state = await workflow_handle.query(SystemPatchWorkflow.get_completed_steps)
        print("Querying workflow state:", state)
        await asyncio.sleep(3)


async def start_workflow(client, i):

    workflow_id = "my-business-id-SystemPatchWorkflow_" + str(i)
    await client.start_workflow(
        SystemPatchWorkflow.run,
        SystemPatchWorkflowInput(
            targetClusters=["cluster1", "cluster2", "cluster3"],
            pilotHostCount=3
        ),
        id=workflow_id,
        task_queue=queue,

        # Terminate the workflow if it is already running.
        id_reuse_policy=WorkflowIDReusePolicy.TERMINATE_IF_RUNNING
    )

    return workflow_id



if __name__ == "__main__":
    asyncio.run(main())
