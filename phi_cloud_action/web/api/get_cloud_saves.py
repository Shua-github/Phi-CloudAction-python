from fastapi.responses import JSONResponse
from .request_models import TokenRequest
from .example import example
from phi_cloud_action._utils import route_safe_execution


class get_cloud_saves(example):
    def __init__(self):
        self.route_path = "/get/cloud/saves"
        self.methods = ["POST"]

    @route_safe_execution
    async def route(self, request: TokenRequest) -> JSONResponse:
        # 获取存档
        temp = await self.get_saves(request.token)
        summary = temp.summary
        save_dict = temp.save_dict

        # 返回
        return JSONResponse(
            content={
                "code": 200,
                "status": "ok",
                "data": {"saves": save_dict, "summary": summary},
            },
            status_code=200,
        )
