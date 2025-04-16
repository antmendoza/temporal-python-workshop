import asyncio
from dataclasses import dataclass
from random import uniform

from temporalio import activity
from temporalio.exceptions import ApplicationError


@dataclass
class ActivityInput:
    input_1: str
    input_2: str
    raise_error: bool = False


@activity.defn
async def activity_1(activity_input: ActivityInput) -> str:
    activity.logger.info("Executing activity_1 with input: %s", activity_input)
    await asyncio.sleep(uniform(0.1, 0.5))

    if (activity_input.raise_error and
            activity.info().attempt < 3):
        raise Exception("Any error")


    return "result_1_" + str(uniform(0.1, 0.5))


@activity.defn
async def activity_2(activity_input: ActivityInput) -> str:
    activity.logger.info("Executing activity_2 with input: %s", activity_input)
    await asyncio.sleep(uniform(0.1, 0.5))

    if  activity_input.raise_error:
        raise ApplicationError("my error", "my error details",
                               non_retryable=True)

    return "result_2_" + str(uniform(0.1, 0.5))
