import asyncio
import logging

from temporalio.client import Client
from temporalio.runtime import Runtime, TelemetryConfig, PrometheusConfig
from temporalio.worker import Worker

# from src.workflow.activities import activities
# from src.workflow.activities_v4 import activities
from src.workflow.activities_v7 import activities
from src.workflow.system_patch_workflow_v7 import SystemPatchWorkflow_Host_V7, SystemPatchWorkflow_Cluster_V7, \
    SystemPatchWorkflow_V7
from src.workflow.types import MyVaultClient

queue = "system_patch-task-queue"

workflows = [
    SystemPatchWorkflow_V7,
    SystemPatchWorkflow_Cluster_V7,  # revisar
    SystemPatchWorkflow_Host_V7,  # revisar
]


def init_runtime_with_prometheus(port: int) -> Runtime:
    # Create runtime for use with Prometheus metrics
    return Runtime(
        telemetry=TelemetryConfig(
            metrics=PrometheusConfig(
                bind_address=f"127.0.0.1:{port}",
            )
        )
    )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s  - %(message)s"
    )

    runtime = init_runtime_with_prometheus(8086)

    client = await Client.connect(
        "localhost:7233",
        runtime=runtime)

    # Run a worker for the workflow
    worker = Worker(
        client,
        task_queue=queue,
        workflows=workflows,
        activities=activities(MyVaultClient()),
        max_concurrent_activities=5,
    )

    logging.info("Starting worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
