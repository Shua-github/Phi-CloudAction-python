# 萌新写的代码，可能不是很好，但是已经尽可能注释了，希望各位大佬谅解喵=v=
# ----------------------- 导包区喵 -----------------------

from typing import Dict, Literal, Optional, List, Any
from .logger import logger
import os
import pyqrcode
import httpx
from pydantic import BaseModel
from .._utils import get_info_dir
import subprocess
import importlib.metadata
import sys
from packaging import version
import re
from github import Github, RateLimitExceededException
import time
from datetime import datetime
import asyncio
from tqdm.asyncio import tqdm
from .._utils import DownloadTask

# ---------------------- 定义赋值区喵 ----------------------


# 补全存档喵
def complete_game_record(
    records: Dict[str, Dict[str, Dict[str, int]]],  # 打歌成绩数据喵
    difficult: Dict[str, Dict[str, Dict[str, int]]],  # 每首歌的各个难度的难度系数喵
    add_record: bool = False,  # 是否添加成绩，默认为 False 喵
    add_record_mode_list: list[str] = [
        "EZ",
        "HD",
    ],  # 需要添加成绩的难度列表，默认为 ["EZ", "HD"] 喵
    score: int = 1000000,  # 默认分数喵
    acc: float = 100.0,  # 默认准确度喵
    fc: bool = True,  # 是否全连，默认为 True 喵
) -> Dict[str, Dict[str, Dict[str, int]]]:  # 返回值类型
    """
    补全存档数据喵~如果某个歌曲记录缺失，默认添加空的成绩喵

    参数：
        records (dict): 打歌成绩数据喵~
        difficult (dict): 每首歌的各个难度的难度系数喵~
        add_record (bool): 是否添加成绩，默认为 False 喵~
        add_record_mode_list (list): 需要添加成绩的难度列表，默认为 ["EZ", "HD"] 喵~
        score (int): 分数，默认为 1000000 喵~
        acc (float): 准确度，默认为 100.0 喵~
        fc (bool): 是否全连，默认为 True 喵~

    返回：
        dict: 更新后的打歌成绩数据喵~
    """
    for game_name, values in difficult.items():
        if game_name not in records:  # 如果该游戏还不存在，就添加
            records[game_name] = {}

        if add_record:
            for mode in add_record_mode_list:
                if mode not in records[game_name]:
                    records[game_name][mode] = {
                        "score": score,
                        "acc": acc,
                        "fc": int(fc),
                    }  # 给没记录的模式添加成绩喵～

    return records


# 更新存档数据喵
def add_game_record(
    records: Dict[str, Dict[str, Dict[str, int]]],  # 打歌成绩数据喵~
    difficult: Dict[str, Dict[str, Dict[str, int]]],  # 每首歌的各个难度的难度系数喵~
    mode_list: list[str] = ["EZ", "HD"],  # 需要更新的模式列表，默认为 ["EZ", "HD"] 喵~
    score: int = 1000000,  # 默认分数喵~
    acc: float = 100.0,  # 默认准确度喵~
    fc: bool = True,  # 是否全连，默认为 True 喵~
    force_replace: bool = False,  # 是否强制替换已有记录，默认为 False 喵~
) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    更新存档数据喵~

    参数：
        records (dict): 打歌成绩数据喵~
        difficult (dict): 每首歌的各个难度的难度系数喵~
        mode_list (list): 需要更新的模式列表，默认为 ["EZ", "HD"] 喵~
        score (int): 游戏得分，默认为 1000000 喵~
        acc (float): 准确度，默认为 100.0 喵~
        fc (bool): 是否全连，默认为 True 喵~
        force_replace (bool): 是否强制替换已有记录，默认为 False 喵~

    返回：
        dict: 更新后的打歌成绩数据喵~
    """
    for game_name, values in difficult.items():
        if game_name in records:  # 如果该游戏已存在，就更新
            for mode in mode_list:
                if mode in records[game_name]:
                    if force_replace:  # 如果需要强制替换，直接更新喵～
                        records[game_name][mode].update(
                            {"score": score, "acc": acc, "fc": int(fc)}
                        )
                else:
                    # 如果该模式没有成绩数据，就直接替换喵~
                    records[game_name][mode] = {
                        "score": score,
                        "acc": acc,
                        "fc": int(fc),
                    }

            # 按照 EZ, HD, IN, AT 顺序重新排序，只保留存在的难度喵~
            records[game_name] = {
                k: records[game_name][k]
                for k in ["EZ", "HD", "IN", "AT"]
                if k in records[game_name]
            }

    return records


# ? 你用不到.jpg
async def download_file(
    download_task: DownloadTask, folder_path: str, max_retries: int = 3
):
    # 确保目标文件夹存在
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    # 提取任务参数
    urls = download_task.download_urls
    filename = download_task.save_name

    # 构造文件保存路径
    file_path = os.path.join(folder_path, filename)

    async def download_url(url):
        async with httpx.AsyncClient(follow_redirects=True) as client:  # 确保跟随重定向
            try:
                # 使用 GET 请求来处理重定向
                response = await client.get(url)
                response.raise_for_status()  # 检查请求是否成功

                # 获取文件大小（通常在响应头中）
                file_size = int(response.headers.get("content-length", 0))

                # 保存文件
                with (
                    open(file_path, "wb") as file,
                    tqdm(
                        desc=filename, total=file_size, unit="B", unit_scale=True
                    ) as bar,
                ):
                    async for chunk in response.aiter_bytes(1024):
                        file.write(chunk)
                        bar.update(len(chunk))  # 更新进度条

                return True  # 下载成功
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 错误：{e.response.status_code} - {e.response.text}")
            except Exception as e:
                logger.error(f"下载失败，尝试 URL: {url}, 错误: {e}")
            return False

    for attempt in range(max_retries):
        tasks = []
        # 创建任务列表
        for url in urls:
            tasks.append(download_url(url))

        # 并发执行下载任务
        results = await asyncio.gather(*tasks)

        # 如果任意一个下载成功，则返回 True
        if any(results):
            return True

        if attempt < max_retries - 1:
            logger.warning(f"第 {attempt + 1} 次尝试失败，正在重试...")
        else:
            logger.error(f"所有 URL 都下载失败，最大尝试次数为 {max_retries} 次。")
            return False  # 如果所有尝试都失败，返回 False

    return False


# 更新函数
async def update(
    tasks: list[DownloadTask], save_dir: str = "./info", max_retries: int = 3
) -> bool:
    """
    更新文件

    参数：
        tasks (set): 存储多个下载任务的集合，每个任务是一个字典，包含 "download_urls" 和 "save_name"。
        save_dir (str): 文件目录，默认为 info 目录。
        max_retries (int): 重试次数。

    返回：
        bool: 是否成功下载至少一个任务。
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for task in tasks:
        download_urls = task.download_urls
        save_name = task.save_name
        save_path = os.path.join(save_dir, save_name)

        logger.info(f"尝试下载任务: {save_name}，保存路径: {save_path}")

        # 尝试下载源直到某个源成功
        for attempt in range(max_retries):
            success = await download_file(task, save_dir, max_retries)

            if success:
                logger.info(f"更新 {save_name} 完成!")
                break  # 成功后跳出循环，进行下一个任务
            else:
                logger.warning(f"第 {attempt + 1} 次尝试下载失败，换源...")
                # 试着使用下一个下载 URL
                if len(download_urls) > 1:
                    download_urls = download_urls[1:]  # 删除当前URL，尝试下一个
                    task.download_urls = download_urls  # 更新任务中的URLs
                else:
                    logger.error(f"所有URL下载失败，更新 {save_name} 失败!")
                    raise RuntimeError(f"更新 {save_name} 失败!")

    return True


def extract_whl_urls(repo_url: str, github_token: str = None) -> List[str]:
    """
    爬取 Github 仓库的 Releases 下载地址

    参数：
        repo_url(str) 仓库地址
        token(str) GitHub API Token, 可选
    返回：
        (list) 文件url列表
    """
    # 从 GitHub API 获取仓库名和拥有者
    repo_path = repo_url.rstrip("/").split("/")[-2:]
    owner, repo = repo_path[0], repo_path[1]

    # 使用 GitHub token 初始化 PyGithub 客户端
    if github_token:
        g = Github(github_token)
    else:
        g = Github()

    # 获取 GitHub 仓库对象
    repository = g.get_repo(f"{owner}/{repo}")

    # 获取所有发布版本
    try:
        releases = repository.get_releases()

        # 存储所有 .whl 文件的下载链接
        whl_links = []

        # 遍历所有发布版本，查找 .whl 文件
        for release in releases:
            for asset in release.get_assets():
                if asset.name.endswith(".whl"):
                    whl_links.append(asset.browser_download_url)

    except RateLimitExceededException:
        # 捕获速率限制异常，获取重置时间（Unix 时间戳）
        reset_time = g.get_rate_limit().core
        minutes_remaining = (reset_time - time.time()) / 60  # 转换为分钟
        reset_day_time = datetime.fromtimestamp(reset_time)
        # 提示用户剩余时间
        raise RuntimeError(
            f"""
            GitHub API 请求速率过快:
            恢复时间:{reset_day_time}
            您需要等待约:{minutes_remaining:.2f}分钟
            """
        )

    # 关闭对象
    g.close()

    return whl_links


def extract_version_from_url(url: str):
    """
    从whl文件的url中提取版本号
    假设文件名格式为：phi_cloud_action-1.5.1.1b0-whl
    """
    # 去掉前后空格和换行符
    url = url.strip()

    logger.debug(f"处理的URL: {url}")

    # 使用正则提取版本号，支持带有后缀（如b、rc等）的版本号
    match = re.search(r"[-v]?(\d+\.\d+\.\d+(\.\d+)?[a-zA-Z0-9]*)(?=-|$)", url)
    logger.debug(f"match: {match}")

    if match:
        return match.group(1).strip()

    return None


# 下载源
SOURCE_INFO = {
    "Catrong": [
        DownloadTask(
            download_urls=[
                "https://github.com/Catrong/phi-plugin-resources/raw/refs/heads/main/info/difficulty.csv"
            ],
            save_name="difficulty.csv",
        ),
        DownloadTask(
            download_urls=[
                "https://github.com/Catrong/phi-plugin-resources/raw/refs/heads/main/info/info.csv"
            ],
            save_name="info.csv",
        ),
    ],
    "7aGiven": [
        DownloadTask(
            download_urls=[
                "https://github.com/7aGiven/Phigros_Resource/raw/refs/heads/info/difficulty.tsv"
            ],
            save_name="difficulty.tsv",
        ),
        DownloadTask(
            download_urls=[
                "https://github.com/7aGiven/Phigros_Resource/raw/refs/heads/info/info.tsv"
            ],
            save_name="info.tsv",
        ),
    ],
}


class Update:
    @staticmethod
    async def info(source: str, max_retries: int = 3, source_info: dict = SOURCE_INFO):
        source_data = source_info.get(source)
        logger.debug(f"下载源: {source_data}")
        if not source_data:
            raise ValueError(f"未知来源: {source}")
        await update(source_data, str(get_info_dir()), max_retries)

    # 更新 本体
    @staticmethod
    def pca(
        github_token: str = None,
        repo_url: str = "https://github.com/Shua-github/Phi-CloudAction-python/",
        package_name="phi_cloud_action",
    ):
        """
        更新phi_cloud_action本体

        参数：
            github_token(str) Github Token 用于突破 Github API 速率限制
            repo_url(str) github的仓库地址
            package_name(str) 要检查更新的包名称
        返回：
            (bool) 是否成功
        """

        # 获取当前安装的版本
        try:
            current_version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            current_version = None  # 如果没有安装该包，设置为 None

        release_links = extract_whl_urls(repo_url, github_token)
        logger.debug(f"文件url列表:{release_links}")

        if not release_links:
            raise RuntimeError(f"找不到文件url喵!")

        # 假设获取第一个发布的链接
        download_url = release_links[0]
        logger.debug(f"文件url:{download_url}")

        # 从下载链接中提取发布版本
        release_version = extract_version_from_url(download_url)
        if release_version == None:
            raise ValueError("没有发布版本喵!")

        logger.debug(f"当前版本: {current_version}, 发布版本: {release_version}")

        # 判断版本是否需要更新
        if current_version and version.parse(current_version) >= version.parse(
            release_version
        ):
            logger.info(f"当前版本 ({current_version}) 已是最新，无需更新。")
            return False

        # 使用 pip 安装 .whl 文件
        logger.info(f"开始更新,当前版本:{current_version},目标版本:{release_version}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", download_url])
        logger.info("更新完成!")
        return True


def get_qr_text(data: str):
    """
    获取二维码文本

    参数：
        data(str) 需要生成二维码的字符串
    返回：
        (str) 二维码字符串
    """
    qr = pyqrcode.create(data, error="L")

    # 获取二维码的文本图案
    qr_str = qr.text(quiet_zone=1)  # 生成二维码文本

    # 手动替换字符，使每个像素宽度为 2，高度为 1
    expanded_qr_str = ""
    for line in qr_str.splitlines():
        expanded_line = ""
        for char in line:
            if char == "0":  # 黑色模块
                expanded_line += "██"  # 每个黑色模块用两个“█”表示
            else:  # 白色模块
                expanded_line += "  "  # 每个白色模块用两个空格表示
        expanded_qr_str += expanded_line + "\n"
    return expanded_qr_str
