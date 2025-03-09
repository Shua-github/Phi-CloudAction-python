from functools import wraps
from fastapi.responses import JSONResponse


def route_safe_execution(func):
    from phi_cloud_action import logger

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(repr(e))
            return JSONResponse(
                content={"code": 400, "status": "error", "message": str(e)},
                status_code=400,
            )

    return wrapper
