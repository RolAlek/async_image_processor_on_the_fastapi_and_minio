import asyncio
from http import HTTPStatus

from celery.result import AsyncResult, states
from fastapi import HTTPException

# TODO: реализация сообщения для websocketa!
async def wait_task(task: AsyncResult, timeout=10, duration=0.5):
    for _ in range(int(timeout / duration)):
        if task.state in (states.SUCCESS, states.FAILURE):
            break
        await asyncio.sleep(duration)
    if task.state != states.SUCCESS:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Task {task.id} did not succeed.'
        )
    return task.result
