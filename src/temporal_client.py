import asyncio

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy

from src.temporal_worker import queue
from src.workflow.system_patch_workflow_v1 import SystemPatchWorkflow_V1
from src.workflow.system_patch_workflow_v3 import SystemPatchWorkflow_V3
from src.workflow.system_patch_workflow_v7 import SystemPatchWorkflow_V7
from src.workflow.types import SystemPatchWorkflowInput

SystemPatchWorkflow = SystemPatchWorkflow_V1


async def main():
    client = await Client.connect("localhost:7233")

    workflow_handle = await client.start_workflow(
        SystemPatchWorkflow.run,
        SystemPatchWorkflowInput(
            targetClusters=["cluster1", "cluster2", "cluster3"],
            pilotHostCount=3
        ),
        id="my-business-id-",  # str(uuid.uuid4()),
        task_queue=queue,

        # Terminate the workflow if it is already running.
        id_reuse_policy=WorkflowIDReusePolicy.TERMINATE_IF_RUNNING
    )

    #asyncio.create_task(query_workflow(workflow_handle))

    await asyncio.sleep(3)  # revisar
    await workflow_handle.signal(SystemPatchWorkflow.approve_request)  # revisar

    print("Workflow started with workflow_id:", workflow_handle.id)
    print("Result:", await workflow_handle.result())


# revisar
async def query_workflow(workflow_handle):
    while True:
        state = await workflow_handle.query(SystemPatchWorkflow.get_completed_steps)
        print("Querying workflow state:", state)
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
