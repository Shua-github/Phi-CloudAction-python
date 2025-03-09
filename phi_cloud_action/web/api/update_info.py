from phi_cloud_action import Update, logger
from typing import Optional
from phi_cloud_action.PhiCloudLib.other import SOURCE_INFO
from phi_cloud_action import DownloadTask
from phi_cloud_action._utils import route_safe_execution
from fastapi.responses import JSONResponse
from fastapi import Body, Query
from pydantic import BaseModel
from .example import example


# 定义 body 的 Pydantic 模型，source_info 字段可选
class boby(BaseModel):
    download_urls: Optional[list] = None  # download_urls 字段可选，默认值为 None
    save_name: Optional[str] = None  # save_name 字段可选，默认值为 None


# 更新信息的处理类
class update_info(example):
    def __init__(self):
        # 路由路径和请求方法
        self.route_path = "/update/info"
        self.methods = ["GET", "POST"]

    @route_safe_execution
    async def route(
        self,
        source: str = Query(...),
        body: Optional[boby] = Body(None),
        max_retries: int = 3,
    ):
        if body and (body.download_urls is not None and body.save_name is not None):
            # 如果 download_urls 和 save_name 都不为 None
            task = {
                source: DownloadTask(
                    download_urls=body.download_urls, save_name=body.save_name
                )
            }
            source_info = task
        else:
            # 如果有任意一个字段为 None，则使用默认的 SOURCE_INFO
            source_info = SOURCE_INFO

        # 执行更新操作
        await Update.info(
            source=source, max_retries=max_retries, source_info=source_info
        )

        return JSONResponse(
            content={"code": 200, "status": "ok", "data": {}}, status_code=200
        )
