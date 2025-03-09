from pathlib import Path
from ..PhiCloudLib.logger import logger
from .get_dev_mode import get_dev_mode
from importlib.resources import files
import phi_cloud_action


def get_info_dir() -> Path:
    # 根据 DEV 环境变量的值返回不同的目录路径
    if get_dev_mode():
        return Path.cwd() / "phi_cloud_action" / "data" / "info"
    else:
        return Path.cwd() / "info"


def get_web_dir() -> Path:
    # 获取包内资源路径
    if get_dev_mode():
        return Path.cwd() / "phi_cloud_action" / "data" / "web"
    else:
        return Path.cwd() / "web"
