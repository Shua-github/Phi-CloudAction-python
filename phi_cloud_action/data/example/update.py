# 萌新写的代码喵，可能不是很好喵，但是已经尽可能注释了喵，希望各位大佬谅解喵=v=
# ----------------------- 导包区喵 -----------------------
from sys import argv
import asyncio
from phi_cloud_action import (
    Update,
    DownloadTask
)


# ---------------------- 定义赋值区喵 ----------------------

arguments = argv  # 获取调用脚本时的参数喵

if len(arguments) != 1:
    source = arguments[1]
else:
    source = "7aGiven"  # 填写源

# 自定义下载源(虽然已经内置了一份)
SOURCE_INFO = {
    "Catrong": [
        DownloadTask(
            download_urls=["https://github.com/Catrong/phi-plugin-resources/raw/refs/heads/main/info/difficulty.csv"],
            save_name="difficulty.csv"
        ),
        DownloadTask(
            download_urls=["https://github.com/Catrong/phi-plugin-resources/raw/refs/heads/main/info/info.csv"],
            save_name="info.csv"
        )
    ],
    "7aGiven": [
        DownloadTask(
            download_urls=["https://github.com/7aGiven/Phigros_Resource/raw/refs/heads/info/difficulty.tsv"],
            save_name="difficulty.tsv"
        ),
        DownloadTask(
            download_urls=["https://github.com/7aGiven/Phigros_Resource/raw/refs/heads/info/info.tsv"],
            save_name="info.tsv"
        )
    ]
}

# ----------------------- 运行区喵 -----------------------
if __name__ == "__main__":
    asyncio.run(Update.info(source,3,SOURCE_INFO))
    # 一般情况下不需要填写参数
    Update.pca()
