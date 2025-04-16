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
class WorkflowApplicationError:

    @workflow.run
    async def run(self, wf_input: WorkflowInput) -> str:
        workflow.logger.info("[workflow.logger.info]Workflow starts " + workflow.info().workflow_id)

        activity_result = await workflow.execute_activity(
            activity=activity_1,
            arg=ActivityInput(wf_input.input_1,
                              wf_input.input_2,
                              raise_error=True
                              ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                non_retryable_error_types=[
                    # EntityNotFoundError,
                ]
            )
        )

        workflow.logger.info("[workflow.logger.info] Scheduling timer")

        await asyncio.sleep(5)

        #    if activity_result:
        #        raise Exception("activity_result is not empty")
        #        raise ApplicationError("my error", "my error details", )

        activity_result = await workflow.execute_activity(
            activity=activity_2,
            arg=ActivityInput(wf_input.input_1,
                              wf_input.input_2,
                              raise_error=True
                              ),
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(
                #  maximum_attempts=3,
                non_retryable_error_types=[
                    # EntityNotFoundError,
                ]
            )
        )

        workflow.logger.info("[workflow.logger.info]Workflow about to complete " + activity_result)

        return "done"
