import argparse
import os
import platform
import shutil
import re
import inspect
from pathlib import Path
from typing import List, Type, Optional
from pydantic import BaseModel, Field, ValidationError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import run
from importlib.resources import files
from yaml import safe_load

from phi_cloud_action import logger
from phi_cloud_action._utils import get_dev_mode, get_web_dir


# 重写 argparse.ArgumentParser 类，修改帮助信息的显示格式喵~
class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self, *args, **kwargs):
        # 获取格式化的帮助信息
        help_text = self.format_help()

        # 去除短选项和长选项之间的空格
        help_text = help_text.replace("-c ,", "-c,").replace("--config", "--config ")

        # 输出修改后的帮助信息
        self._print_message(help_text, *args, **kwargs)


# 配置类 (使用 Pydantic)
class RoutesConfig(BaseModel):
    allow_routes: set[str] = set([])
    ban_routes: set[str] = set([])


class CORSConfig(BaseModel):
    switch: bool = Field(..., alias="CORS_switch")
    allow_origins: List[str] = Field(..., alias="CORS_allow_origins")
    allow_credentials: bool = Field(..., alias="CORS_allow_credentials")
    allow_methods: List[str] = Field(..., alias="CORS_allow_methods")
    allow_headers: List[str] = Field(..., alias="CORS_allow_headers")


class ServerConfig(BaseModel):
    host: str
    port: int
    cors: CORSConfig
    routes: RoutesConfig = RoutesConfig()


class Config(BaseModel):
    net: ServerConfig


# 配置管理器
class ConfigManager:
    @staticmethod
    def get_default_dir() -> Path:
        """获取默认配置文件目录喵~"""
        package_name = "phi_cloud_action"
        system: str = platform.system()

        if get_dev_mode():
            return Path.cwd() / package_name / "data"

        if system == "Windows":
            appdata: Optional[str] = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / package_name
            else:
                return Path.home() / "AppData" / "Roaming" / package_name
        else:
            return Path.home() / ".config" / package_name

    def __init__(self) -> None:
        self.args: argparse.Namespace = self._parse_args()
        self.config_path: Path = self._get_config_path()
        self.config: Config = self._read_config()

    DEFAULT_DIR: Path = get_default_dir()
    CONFIG_FILE: str = "RunConfig.yml"

    def _parse_args(self) -> argparse.Namespace:
        """解析命令行参数喵~"""
        parser = CustomArgumentParser(
            description="phi_cloud_action.webapi 配置管理器喵~",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "-c", "--config", type=str, help="自定义配置文件路径喵~", metavar=""
        )
        return parser.parse_args()

    def _get_config_path(self) -> Path:
        """获取配置文件路径喵~"""
        if self.args.config:
            return Path(self.args.config)
        return self.DEFAULT_DIR / self.CONFIG_FILE

    def _read_config(self) -> Config:
        """读取并返回配置对象喵~"""
        try:
            # 打开配置文件并读取
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_dict = safe_load(f)

            # 使用 model_validate 来解析配置文件
            return Config.model_validate(config_dict)

        except ValidationError as e:
            logger.error("配置文件解析失败，错误信息如下：")
            for error in e.errors():
                logger.error(f"字段: {error['loc']}, 错误: {error['msg']}")
            exit(1)

        except FileNotFoundError:
            # 配置文件不存在，创建默认配置文件
            self._ensure_config_file_exists()
            return self._read_config()

        except Exception as e:
            # 捕获其他异常并抛出更清晰的错误信息
            raise RuntimeError(f"读取配置文件失败喵~: {str(e)}")

    def _ensure_config_file_exists(self) -> None:
        if not self.config_path.exists():
            try:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"配置文件 {self.config_path} 不存在，正在从包内复制喵~...")

                package_config_path = (
                    files("phi_cloud_action") / "data" / self.CONFIG_FILE
                )
                logger.info(f"从包内获取配置文件路径喵: {package_config_path}")

                if package_config_path.is_file():
                    shutil.copy(package_config_path, self.config_path)
                    logger.info(
                        f"配置文件已从 {package_config_path} 拷贝到 {self.config_path} 喵~"
                    )
                else:
                    logger.error("包内默认配置文件未找到喵~！")
                    raise FileNotFoundError(f"包内默认配置文件未找到喵~！")

            except Exception as e:
                logger.error(f"配置文件初始化失败喵~: {str(e)}")
                raise RuntimeError(f"配置文件初始化失败喵~: {str(e)}")


# 路由分类
def routes_classification(name: str) -> List[str]:
    group_list: list = []

    if name.startswith("/get/cloud"):
        group_list.append("cloud")
    elif name.startswith("/get/saves"):
        group_list.append("saves")
    elif name.startswith("/update"):
        group_list.append("update")
    elif name.startswith("/get/token"):
        group_list.append("token")
    elif name.startswith("/gui"):
        group_list.append("gui")
    else:
        group_list.append("other")

    return group_list


def should_register_route(route_path: str, routes_config: RoutesConfig) -> bool:
    """
    判断是否应该注册路由。
    """
    ban_route = (
        set(routes_config.ban_routes)
        if routes_config and routes_config.ban_routes
        else None
    )
    allow_route = (
        set(routes_config.allow_routes)
        if routes_config and routes_config.allow_routes
        else None
    )

    if ban_route and any(route_path.startswith(route) for route in ban_route):
        logger.info(f"跳过路由: {route_path}, 在黑名单中")
        return False

    if allow_route and not any(route_path.startswith(route) for route in allow_route):
        logger.info(f"跳过路由: {route_path}, 不在允许列表中")
        return False

    return True


# 路由注册
from .web.route_example import route_example as example


def register_routes(
    app: FastAPI, interface_class: Type[example], routes_config: RoutesConfig
):
    route_classes = []

    # 获取路由对象
    for name, obj in inspect.getmembers(interface_class):
        if inspect.isclass(obj):
            for method_name, method_obj in inspect.getmembers(obj):
                if method_name == "route" and inspect.isfunction(method_obj):
                    try:
                        instance: example = obj()
                    except TypeError as e:
                        logger.error(f"{obj.__class__.__name__}无法实例化")
                        logger.debug(repr(e))
                    except Exception as e:
                        logger.error(f"注册路由失败: {repr(e)}")
                    if hasattr(instance, "route_path") and hasattr(instance, "methods"):
                        route_classes.append(instance)

    # 辅助排序
    def sort_key(route_class: example):
        return (route_class.route_path.find("{") != -1, len(route_class.route_path))

    # 排序
    route_classes.sort(key=sort_key)

    # 挂载静态资源
    resources_dir = get_web_dir() / "resources"
    ill_dir = resources_dir / "ill"
    logger.info(f"资源目录: {resources_dir}, 曲绘目录: {ill_dir}")
    if ill_dir.exists():
        app.mount("/static/", StaticFiles(directory=str(resources_dir)), name="static")
    else:
        logger.warning("资源目录不存在, 一些路由路由将无法使用")
        routes_config.ban_routes.add("/gui")  # 添加到黑名单

    for instance in route_classes:
        route_path = instance.route_path

        # 判断是否注册该路由
        if not should_register_route(route_path, routes_config):
            continue

        logger.info(f"注册路由: {route_path}")

        # 获取名称
        name: str = route_path

        # 分类
        group: list = routes_classification(name)

        # summary名称
        title_name = re.sub(r"\{.*?\}", "", name)  # 清除{和}之间的内容
        title_name = title_name.replace("/", " ").title()

        # 注册路由
        app.add_api_route(
            route_path,
            instance.route,
            methods=instance.methods,
            summary=title_name,
            tags=group,
        )


# 启动程序
def main():
    manager: ConfigManager = ConfigManager()
    config = manager.config.net  # 获取配置中的 net 部分
    app = FastAPI(debug=get_dev_mode())

    if config.cors.switch:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors.allow_origins,
            allow_credentials=config.cors.allow_credentials,
            allow_methods=config.cors.allow_methods,
            allow_headers=config.cors.allow_headers,
        )

    # 注册路由
    from . import web

    register_routes(app, web, config.routes)

    logger.info(f"监听主机: {config.host}, 端口: {config.port} 喵~")
    logger.info(f"配置文件路径喵~: {manager.config_path}")

    run(app, host=config.host, port=config.port)


# 主程序入口喵~
if __name__ == "__main__":
    main()
