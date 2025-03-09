from typing import List, Literal, Optional, Union
from pydantic import BaseModel


# 定义歌曲信息的数据结构
class Song(BaseModel):
    """
    num(str): 曲目编号
    song(str): 曲目名称
    illustration(str): 曲目插图
    rank(str): 难度等级
    difficulty(float): 难度定数
    rks(float): 玩家单曲rks
    Rating(str): 玩家单曲评级,关连显示的图标
    score(int): 玩家分数
    acc(float): 玩家acc
    suggest(str): 推分建议
    """

    num: str = "P1"
    song: str = "Rrharil"
    illustration: str = "/static/ill/illLow/Rrharil.TeamGrimoire.png"
    rank: Literal["AT", "IN", "HD", "EZ"] = "AT"
    difficulty: float = 17.6
    rks: float = 11.4514
    Rating: Literal["phi", "FC", "V", "S", "A", "B", "C", "F"]
    score: int = 100000
    acc: float = 98.1145
    suggest: str = "无法推分"


# 定义 bN 页面的数据结构
class BNTemplate(BaseModel):
    # 用户名
    username: str
    # 用户rks
    userrks: float
    # 课题分(比如551,448)
    challenge: str
    # 头像名称
    avatar_name: str
    # 成绩列表
    songs: List[Song]


class GameUser(BaseModel):
    PlayerId: str
    rks: float
    ChallengeMode: str
    ChallengeModeRank: str
    data: Optional[str] = None
    dan: Optional[dict] = None


class Version(BaseModel):
    ver: str
    phi_plugin: str


class PhiScore(BaseModel):
    gameuser: GameUser
    phi: List[Union[Song, None]]
    b19_list: List[Song]
    Date: str
    Version: Version


class b30:
    def __init__(self, p3: list, b27: list):
        self.p3: list = p3
        self.b27: list = b27
        self.b30: list = p3 + b27

    def __call__(self):
        return self.b30


class savesHistory:
    def __init__(self, summary: dict, record: dict, user: dict, save_dict: dict):
        self.summary: dict = summary
        self.record: dict = record
        self.user: dict = user
        self.save_dict: dict = save_dict
        self.saves: dict = {
            "summary": summary,
            "record": record,
            "user": user,
            "save_dict": save_dict,
        }

    def __call__(self):
        return self.saves


# 下载任务模型
class DownloadTask(BaseModel):
    download_urls: List[str]
    save_name: str


class Saves(BaseModel):
    save_dict: dict
    summary: dict
    save_data: bytes
