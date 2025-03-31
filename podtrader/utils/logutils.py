import logging
from logging import handlers

__all__ = ['get_logger']


# 日志级别关系映射
LEVEL_RELATIONS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'crit': logging.CRITICAL
}


def get_logger(name=None, level='info', fmt='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s: %(message)s',
               stream=False, path='logs', filename=None, when='D', back_count=3, disabled=False):
    import os

    logger = logging.getLogger(name)
    if stream:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if filename:
            filename = os.path.join(log_dir, filename)
        else:
            filename = os.path.join(log_dir, 'default.log')
        logger = logging.getLogger()
        handler = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=back_count,
            encoding='utf-8'
        )
    else:
        handler = logging.StreamHandler()
    # 设置是否禁用日志
    logger.disabled = disabled
    # 设置日志级别
    level = LEVEL_RELATIONS.get(level)
    logger.setLevel(level)
    handler.setLevel(level)
    # 设置日志格式
    format_str = logging.Formatter(fmt)
    handler.setFormatter(format_str)
    logger.addHandler(handler)
    return logger
