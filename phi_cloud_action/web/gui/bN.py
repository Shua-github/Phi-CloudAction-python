from copy import deepcopy
from typing import List, Optional
from datetime import datetime
import jinja2
from fastapi import Query, Response, Request
from fastapi.responses import JSONResponse, HTMLResponse
from phi_cloud_action import getB30, rate, readSaveHistory,add_game_record,logger
from phi_cloud_action._utils import (
    get_web_dir,
    BNTemplate,
    Song,
    GameUser,
    Version,
    PhiScore,
    b30,
    route_safe_execution,
)
from .example import example

# 配置 Jinja2 模板目录
web_dir = get_web_dir()
templates_dir = str(web_dir / "resources")

# 创建Jinja2环境
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_dir),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)


def get_songs(
    bn_list: list, info, rks: float, rks_tap_num: int, prefix: str = ""
) -> tuple[List[Song], float]:
    songs_list = []

    for i, song in enumerate(bn_list):
        # 深度拷贝,防止修改原数据
        song_temp = deepcopy(song)

        # 生成真实id
        song_temp["id"] = song["name"]

        # 替换为真实名字
        song_temp["name"] = info[song["name"]][0]

        # 排序生成
        num = f"{prefix}{i + 1}"

        # 构造歌曲信息
        songs_list.append(
            Song(
                num=num,
                song=song_temp["name"],
                illustration=f"/static/ill/ill/{song_temp['id']}.png",
                rank=song_temp["level"],
                difficulty=song_temp["difficulty"],
                rks=song_temp["rks"],
                Rating=rate(song_temp["score"], 1000000, bool(song_temp["fc"])),
                score=song_temp["score"],
                acc=song_temp["acc"],
                suggest="?",
            )
        )

        # 限制rks的累加次数
        if i < rks_tap_num:
            rks += song_temp["rks"]

    return songs_list, rks


def get_b3(b30: b30, info, rks: float) -> List[Optional[Song]]:
    songs, rks = get_songs(b30.p3, info, rks, 3, "P")

    # 如果返回的歌曲数少于3个，补充None
    while len(songs) < 3:
        songs.append(None)

    return songs, rks


def get_b27(b30: b30, info, rks: float):
    return get_songs(b30.b27, info, rks, 27, "#")


class gui_bN(example):
    def __init__(self):
        self.route_path = "/gui/bN"
        self.methods = ["GET"]

    @route_safe_execution
    async def route(
        self, request: Request, b_num: int = 3, p_num: int = 27
    ) -> HTMLResponse:
        # 获取定数和info
        difficulty = self.get_difficulty()
        info = self.get_info("info.csv")

        # 读取存档
        saves = readSaveHistory("")
        record = saves.record
        save_dict = saves.save_dict
        user_name = saves.user["nickname"]

        # 将字典的键按时间排序
        record_time = max(
            record.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S")
        )

        # 获取b30和其它一些信息
        b30 = getB30(record[record_time], difficulty, b_num=b_num, p_num=p_num)
        gameProgress: dict = save_dict["gameProgress"]
        money: list = gameProgress["money"]
        challengeModeRank = str(gameProgress["challengeModeRank"])

        # 获取b30喵
        b30 = getB30(save_dict["gameRecord"], difficulty)

        # 输出并计算玩家rks喵
        b3, rks = get_b3(b30, info, 0.0)
        b27, rks = get_b27(b30, info, rks)

        # 拼接b3和b27的歌曲信息喵
        songs_list = b3 + b27

        # 计算用户rks喵
        user_rks = rks / 30

        # 构造模板上下文
        context = {
            "request": request,
            **BNTemplate(
                username=user_name,
                userrks=round(user_rks, 2),
                challenge=challengeModeRank,
                avatar_name="cycats_1",
                songs=songs_list,
            ).model_dump(),
        }

        # 渲染模板并返回HTML响应
        template = env.get_template("bN.html")
        html_content = template.render(context)
        return HTMLResponse(content=html_content)


class gui_bN_1(example):
    def __init__(self):
        self.route_path = "/gui/bN_1"
        self.methods = ["GET"]

    @route_safe_execution
    async def route(
        self, request: Request, p_num: int = 3, b_num: int = 27
    ) -> Response:
        # 获取定数和info
        difficulty = self.get_difficulty("difficulty.csv")
        info = self.get_info("info.csv")

        # 读取存档
        saves = readSaveHistory("")
        record = saves.record
        save_dict = saves.save_dict
        save_dict["gameRecord"] = add_game_record(records=save_dict["gameRecord"],difficult=difficulty,mode_list=["IN","AT"],force_replace=True)
        user_name = saves.user["nickname"]
        logger.debug(save_dict)

        # 将字典的键按时间排序
        record_time = max(
            record.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S")
        )

        # 获取b30和其它一些信息
        b30 = getB30(save_dict["gameRecord"], difficulty, b_num=b_num, p_num=p_num)
        gameProgress: dict = save_dict["gameProgress"]
        money: list = gameProgress["money"]
        challengeModeRank = str(gameProgress["challengeModeRank"])

        # 版本信息
        version = Version(
            ver="""v1.14.514,仅供娱乐""",
            phi_plugin="phi-plugin<del>-python-api</del><br>由Playwright和Jinja2强力驱动</br>",
        )

        # 计算rks和b30列表
        songs_phi, rks = get_b3(b30, info, 0.0)
        songs_b19, rks = get_b27(b30, info, rks)
        rks = rks / 30

        # 定义单位列表，从小到大的顺序
        units = ["KIB", "MIB", "GIB", "TIB", "PIB"]

        # 将单位和数值组成一个元组列表
        unit_value_pairs = [(money[i], units[i]) for i in range(len(money))]

        # 过滤掉值为0的项并按照从大到小的顺序排序
        filtered_units = sorted(
            [f"{value}{unit}" for value, unit in unit_value_pairs if value > 0],
            key=lambda x: units.index(x[-3:]),  # 按照单位顺序排序
            reverse=True,  # 使用reverse=True使其从大到小排序
        )

        # 用户信息
        gameuser = GameUser(
            PlayerId=user_name,
            rks=rks,
            ChallengeMode=challengeModeRank[0],
            ChallengeModeRank=challengeModeRank[1:3],
            data=" ".join(filtered_units),
        )

        # 成绩
        phi_score = PhiScore(
            gameuser=gameuser,
            phi=songs_phi,
            b19_list=songs_b19,
            Date=record_time,
            Version=version,
        )

        # 模板
        context = {
            "request": request,
            **phi_score.model_dump(),
            "_res_path": f"/static/resources/",
        }

        # 渲染模板并返回HTML响应
        template = env.get_template("test.html")
        html_content = template.render(context)
        return HTMLResponse(content=html_content)
