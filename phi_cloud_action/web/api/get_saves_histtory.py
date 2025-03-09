from phi_cloud_action import readSaveHistory, logger
from fastapi.responses import JSONResponse
from .request_models import TokenRequest
from .example import example
from phi_cloud_action._utils import route_safe_execution


class get_saves_histtory(example):
    def __init__(self):
        self.route_path = "/get/saves/histtory"
        self.methods = ["POST"]

    @route_safe_execution
    async def route(self, request: TokenRequest) -> JSONResponse:
        # 使用 request.token 来获取传递的 token 值
        data = readSaveHistory(request.token)
        return JSONResponse(
            content={
                "code": 200,
                "status": "ok",
                "data": {
                    "histtory": {
                        "summary": data.summary,
                        "save_dict": data.save_dict,
                        "user": data.user,
                    }
                },
            },
            status_code=200,
        )
