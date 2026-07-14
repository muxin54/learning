"""
logging_config.py —— 集中日志配置
其他模块用 from app.logging_config import logger 即可
"""
import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)                     # 确保日志目录存在

logging.basicConfig(
    level=logging.INFO,                                 # INFO级别：普通日志看，DEBUG太吵
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                        # 控制台
        logging.FileHandler(                            # 写入文件
            os.path.join(LOG_DIR, "app.log"),
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("card-api")                  # 项目全局日志器
