from abc import ABC, abstractmethod
import os
from typing import List, Literal, Dict
from phi_cloud_action import (
    readDifficultyFile,
    logger,
    PhigrosCloud,
    unzipSave,
    decryptSave,
    formatSaveDict,
    checkSaveHistory,
    readInfoFile,
)
from phi_cloud_action._utils import get_info_dir, Saves

# 获取info目录
info_dir = get_info_dir()


class route_example(ABC):
    # 读取定数文件名
    difficulty_name = os.getenv("PHI_DIF_NAME", "difficulty.tsv")
    logger.debug(f"当前环境PHI_DIF_NAME:{difficulty_name}")

    # 声明路由路径和方法(?)
    def __init__(self):
        self.route_path: str
        self.methods: List[
            Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        ]

    # 获取云存档
    @staticmethod
    async def get_saves(token: str) -> Saves:
        """
        获取云存档并记录到历史记录

        参数:
            token(str): 玩家的token

        返回:
            (Saves) 玩家存档,包含save_dict、save_data、user和summary
        """
        async with PhigrosCloud(token) as cloud:
            # 获取玩家summary和用户名喵
            summary = await cloud.getSummary()
            nick_name = await cloud.getNickname()

            # 获取并解析存档喵
            save_data = await cloud.getSave(summary["url"], summary["checksum"])
            save_dict = unzipSave(save_data)
            save_dict = decryptSave(save_dict)
            save_dict = formatSaveDict(save_dict)

        data = Saves(save_dict=save_dict, summary=summary, save_data=save_data)
        checkSaveHistory(
            token,
            summary,
            save_data,
            route_example.get_difficulty(),
            {"nickname": nick_name},
        )
        return data

    # 获取定数
    @staticmethod
    def get_difficulty(
        file_name: Literal["difficulty.tsv", "difficulty.csv"] = difficulty_name,
    ) -> Dict[str, List[float]]:
        """
        获取定数

        参数:
            file_name(str): 定数文件名

        返回:
            (dict) 定数,key是曲名,内容是列表,包含定数
        """
        # 获取路径
        difficulty_path = info_dir / file_name

        # 读取难度文件
        difficulty = readDifficultyFile(str(difficulty_path))
        return difficulty

    # 获取info文件
    @staticmethod
    def get_info(
        file_name: Literal["info.tsv", "info.csv"] = "info.csv",
    ) -> Dict[str, List[float]]:
        """
        获取info

        参数:
            file_name(str): info文件名

        返回:
            (dict) ?
        """
        # 获取路径
        info_path = info_dir / file_name

        # 读取文件
        info = readInfoFile(str(info_path))
        return info

    # 路由部分
    @abstractmethod
    async def route(self):
        pass
