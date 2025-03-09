from importlib.resources import files
import shutil
import os
from .PhiCloudLib import logger


def copy_data():
    # 获取包名称和目标工作目录
    package_name = "phi_cloud_action"
    work_dir = os.getcwd()
    copy_num = 0

    # 获取包内 data 文件夹
    try:
        # 使用 files() 来访问包内的 data 文件夹
        data_dir = files(package_name) / "data"

        # 定义一个递归函数来处理文件夹
        def copy_folder_contents(src_folder, dest_folder):
            # 在函数开始时声明 nonlocal
            nonlocal copy_num

            # 如果目标文件夹不存在，创建它
            os.makedirs(dest_folder, exist_ok=True)

            # 遍历文件夹中的所有内容
            for item in src_folder.iterdir():
                if item.is_dir():  # 如果是子文件夹，递归调用
                    dest_subfolder = os.path.join(dest_folder, item.name)
                    copy_folder_contents(item, dest_subfolder)
                elif item.is_file():  # 如果是文件，直接复制
                    dest_file = os.path.join(dest_folder, item.name)
                    shutil.copy(item, dest_file)
                    logger.info(
                        f"已将 {item.name} 从 {src_folder.name} 拷贝到 {dest_folder} 了喵"
                    )
                    copy_num += 1  # 在文件拷贝时就更新计数器

        # 开始复制 data 文件夹中的所有内容
        copy_folder_contents(data_dir, work_dir)

        logger.info(f"所有文件已成功拷贝到当前目录了喵,共拷贝了{copy_num}个文件")
        logger.info(f"可以查看 examples 文件夹中的示例代码了喵")

    except Exception as e:
        logger.error(f"发生错误: {e}")


if __name__ == "__main__":
    # 执行拷贝操作
    copy_data()
