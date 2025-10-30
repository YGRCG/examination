import logging
import os
from datetime import datetime

# 确保日志目录存在
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'backend')
os.makedirs(LOG_DIR, exist_ok=True)

# 获取当前日期作为日志文件名的一部分
current_date = datetime.now().strftime('%Y-%m-%d')
LOG_FILE = os.path.join(LOG_DIR, f'app_{current_date}.log')

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_logger(name=None):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器的名称，如果为None，则返回根日志记录器
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 获取或创建日志记录器
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT)
    
    # 设置处理器的格式化器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 创建默认的日志记录器
default_logger = setup_logger('app')

# 导出常用方法
info = default_logger.info
debug = default_logger.debug
warning = default_logger.warning
error = default_logger.error
exception = default_logger.exception
critical = default_logger.critical