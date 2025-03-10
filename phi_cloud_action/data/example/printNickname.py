# 萌新写的代码喵，可能不是很好喵，但是已经尽可能注释了喵，希望各位大佬谅解喵=v=
# ----------------------- 导包区喵 -----------------------
from sys import argv
import asyncio
from phi_cloud_action import (
    PhigrosCloud,
    logger,
)


# ---------------------- 定义赋值区喵 ----------------------

arguments = argv  # 获取调用脚本时的参数喵

if len(arguments) != 1:
    sessionToken = arguments[1]
else:
    sessionToken = ""  # 填你的sessionToken喵


# ----------------------- 运行区喵 -----------------------


async def printNickname(token):
    async with PhigrosCloud(token) as cloud:
        # 获取玩家昵称并输出喵
        logger.info(f'玩家昵称："{cloud.getNickname()}"')

if __name__ == "__main__":
    asyncio.run(printNickname(sessionToken))
