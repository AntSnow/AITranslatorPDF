from loguru import logger
import os
import sys

# 定义输出日志的文件名
LOG_FILE = "translation.log"

#
ROTATION_TIME = "02:00"


class Logger:
    # 构造方法
    def __init__(self, name: str = "translation", log_dir: str = "logs", debug: bool = False):
        # 如果文件夹的路径不存在，就创建
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 文件夹 + 文件名，组合成文件路径
        log_file_path = os.path.join(log_dir, name + '.log')

        # 移除`logger`默认的日志处理器，避免输出到标准输出，方便自定义日志处理器
        logger.remove()

        # 声明日志等级，目前仅支持`DEBUG`和`INFO`两种
        level = "DEBUG" if debug else "INFO"

        # 将日志信息输出到标准输出
        logger.add(sys.stdout, level=level)

        # 将日志输出到文件（`DEBUG`级别以上）
        logger.add(log_file_path, rotation=ROTATION_TIME, level="DEBUG")

        # 声明`logger`
        self.logger = logger


# 声明全局变量
LOG = Logger(debug=True).logger

if __name__ == "__main__":
    log = Logger().logger

    log.debug("This is a debug message")
    log.info("This is a info message")
    log.warning("This is a warning message")
    log.error("This is a error message")
