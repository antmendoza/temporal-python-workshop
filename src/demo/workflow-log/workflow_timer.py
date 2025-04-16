import asyncio
from asyncio import create_task
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from activities import activity_1, ActivityInput


@dataclass
class WorkflowInput:
    input_1: str
    input_2: str


@workflow.defn
class WorkflowLog:

    @workflow.run
    async def run(self, wf_input: WorkflowInput) -> str:
        workflow.logger.info("[workflow.logger.info]Workflow starts " + workflow.info().workflow_id)

        print("[print]Workflow starts " + workflow.info().workflow_id)

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


        done, pending = await workflow.wait([
            create_task(asyncio.sleep(10), name="timer_task"),
            create_task(asyncio.sleep(20), name="timer_task2")

        ], return_when=asyncio.FIRST_COMPLETED);


        workflow.logger.info("[workflow.logger.info] Scheduling timer")

        await asyncio.sleep(20)

        workflow.logger.info("[workflow.logger.info]Workflow about to complete " + activity_result)

        return "done"
