import asyncio
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from activities import activity_1, ActivityInput, activity_2


@dataclass
class WorkflowInput:
    input_1: str
    input_2: str


@workflow.defn
class WorkflowNDE:

    @workflow.run
    async def run(self, wf_input: WorkflowInput) -> str:
        workflow.logger.info("[workflow.logger.info]Workflow starts " + workflow.info().workflow_id)
        print("[print]Workflow starts " + workflow.info().workflow_id)

        # https://docs.temporal.io/develop/python/versioning

        # if workflow.patched("my-patch"):
        #     await workflow.execute_activity(
        #         activity=activity_2,
        #         arg=ActivityInput(wf_input.input_1,
        #                           wf_input.input_2
        #                           ),
        #         start_to_close_timeout=timedelta(seconds=5),
        #         retry_policy=RetryPolicy(
        #             maximum_attempts=3,
        #             non_retryable_error_types=[]
        #         )
        #     )

        # https://docs.temporal.io/develop/python/testing-suite#replay

        activity_result = await workflow.execute_activity(
            activity=activity_1,
            arg=ActivityInput(wf_input.input_1,
                              wf_input.input_2
                              ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                non_retryable_error_types=[]
            )
        )

        workflow.logger.info("[workflow.logger.info] Scheduling timer")

        await asyncio.sleep(20)

        workflow.logger.info("[workflow.logger.info]Workflow about to complete " + activity_result)

        return "done"
