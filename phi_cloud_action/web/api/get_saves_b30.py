from phi_cloud_action import getB30
from fastapi.responses import JSONResponse
from .request_models import SavesRequest, BNumRequest
from .example import example
from phi_cloud_action._utils import route_safe_execution


class BNumAndSavesRequest(SavesRequest, BNumRequest):
    pass


class get_saves_b30(example):
    def __init__(self):
        self.route_path = "/get/saves/b30"
        self.methods = ["POST"]

    @route_safe_execution
    async def route(self, request: BNumAndSavesRequest) -> JSONResponse:
        # 获取存档
        save_dict = request.saves

        # 获取难度定数
        difficulty = self.get_difficulty()

        # 获取b30喵
        b30 = getB30(save_dict["gameRecord"], difficulty, request.b_num, request.p_num)

        # 计算玩家rks喵
        rks = 0.0
        for song in b30():
            rks += song["rks"]
        rks = rks / 30

        return JSONResponse(
            content={
                "code": 200,
                "status": "ok",
                "data": {"rks": rks, "b30": {"p3": b30.p3, "b27": b30.b27}},
            },
            status_code=200,
        )
