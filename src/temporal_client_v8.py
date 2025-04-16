import asyncio

from temporalio.client import Client

from src.temporal_worker import queue
from src.temporal_worker_v8 import init_runtime_with_prometheus
from src.workflow.system_patch_workflow_v7 import SystemPatchWorkflow_V7
from src.workflow.types import SystemPatchWorkflowInput

SystemPatchWorkflow = SystemPatchWorkflow_V7


async def start_workflow(client, i):
    workflow_id = "my-business-id-SystemPatchWorkflow_" + str(i)
    workflow_handle = await client.start_workflow(
        SystemPatchWorkflow.run,
        SystemPatchWorkflowInput(
            targetClusters=["cluster1", "cluster2", "cluster3"],
            pilotHostCount=3
        ),
        id=workflow_id,
        task_queue=queue,

    )

    # asyncio.create_task(query_workflow(workflow_handle))

    await asyncio.sleep(3)  # revisar
    await workflow_handle.signal(SystemPatchWorkflow.approve_request)  # revisar

    print("Workflow started with workflow_id:", workflow_handle.id)
    print("Result:", await workflow_handle.result())



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
    

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

