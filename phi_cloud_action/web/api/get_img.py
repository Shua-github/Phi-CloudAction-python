from playwright.async_api import async_playwright
from io import BytesIO
from fastapi import Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List
import time
from phi_cloud_action._utils import route_safe_execution


class get_img:
    def __init__(self):
        self.route_path = "/get/img"
        self.methods = ["GET"]

    @route_safe_execution
    async def route(
        self,
        request: Request,
        route_path: str = Query(...),
        args: List[str] = Query(None),
    ) -> StreamingResponse:
        # 记录开始时间
        start_time = time.time()

        # 将传入的args（列表）转换为字典
        args_dict = {}
        if args:
            for arg in args:
                # 判断arg是否包含 "=" 符号
                if "=" in arg:
                    key, value = arg.split("=", 1)  # 防止出现多个"="导致错误
                    args_dict[key] = value
                else:
                    return JSONResponse(
                        content={
                            "code": 400,
                            "status": "error",
                            "message": """没有包含=""",
                        },
                        status_code=400,
                    )

        # 删除开头的/
        if route_path.startswith("/"):
            route_path = route_path[1:]

        # 判断是否为外部http链接
        if route_path.startswith("http"):
            url = route_path
        else:
            # 拼接url
            url = str(request.base_url._url) + route_path

        # 如果有其他动态查询参数，则追加到url
        if args_dict:
            query_params = "&".join(
                f"{key}={value}" for key, value in args_dict.items()
            )
            url = f"{url}?{query_params}"

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)

            # 获取页面高度
            body_handle = await page.query_selector("body")
            bounding_box = await body_handle.bounding_box()
            height = int(bounding_box["height"])

            # 设置动态视口大小
            await page.set_viewport_size(
                {"width": 1200, "height": height}
            )  # 设置视口大小
            image_bytes = await page.screenshot(full_page=True)  # 获取完整页面截图
            await browser.close()

        # 计算渲染时间
        render_time = time.time() - start_time

        # 将渲染时间添加到响应头
        headers = {"X-Render-Time": str(round(render_time, 4))}

        return StreamingResponse(
            BytesIO(image_bytes), media_type="image/png", headers=headers
        )
