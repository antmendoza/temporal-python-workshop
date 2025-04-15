import asyncio
import math
import numbers
from dataclasses import dataclass
from random import uniform

from temporalio import activity


@dataclass
class ActivityInput:
    input_1:str
    input_2:str


@activity.defn
async def activity_1(activity_input: ActivityInput) -> str:

    activity.logger.info("Executing activity_1 with input: %s", activity_input)
    await asyncio.sleep(uniform(0.1, 0.5))

    return "result_1_" + str(uniform(0.1, 0.5))



@activity.defn
async def activity_2(activity_input: ActivityInput) -> str:
    activity.logger.info("Executing activity_2 with input: %s", activity_input)
    await asyncio.sleep(uniform(0.1, 0.5))

    return "result_2_" + str(uniform(0.1, 0.5))
