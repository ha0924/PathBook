"""跨域共享 - 统一日志系统.

基于 Python 标准库 logging，JSON 结构化输出到 stdout。
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON 格式化器，方便后续对接日志平台."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 附加 request_id（如果有）
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_data["request_id"] = request_id

        # 异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """应用启动时调用一次，初始化日志配置.

    Args:
        level: 日志级别，从环境变量 LOG_LEVEL 读取。
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.root
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # 降低第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """业务模块获取 logger 的统一入口.

    用法：
        from app.shared.logger import get_logger
        logger = get_logger(__name__)
        logger.info("用户注册成功")
    """
    return logging.getLogger(name)
