"""接入层 - 全局异常处理器.

将 BizError、校验异常、未预期异常统一捕获并格式化为标准响应。
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.shared.exceptions import BizError, ErrorCode
from app.shared.i18n import t
from app.shared.logger import get_logger
from app.shared.response import fail

logger = get_logger(__name__)


def _get_locale(request: Request) -> str:
    """从 request.state 获取语言偏好（由中间件设置）."""
    return getattr(request.state, "locale", "zh_CN")


def _code_to_http_status(code: int) -> int:
    """错误码 → HTTP 状态码映射."""
    # 特殊映射
    if code == ErrorCode.USER_ALREADY_EXISTS:
        return 409
    if code == ErrorCode.PROFILE_ALREADY_INITIALIZED:
        return 409
    if code == ErrorCode.PROFILE_NOT_FOUND:
        return 404
    if 40100 <= code <= 40199:
        return 401
    elif 40300 <= code <= 40399:
        return 403
    elif 40000 <= code <= 40099:
        return 400
    elif code == ErrorCode.VALIDATION_ERROR:
        return 422
    return 500


async def _biz_error_handler(request: Request, exc: BizError) -> JSONResponse:
    """处理业务异常."""
    locale = _get_locale(request)
    message = t(f"errors.{exc.code.value}", locale=locale)
    status = _code_to_http_status(exc.code.value)

    logger.warning(
        f"BizError: [{exc.code.value}] {exc.code.name}",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )

    body = fail(code=exc.code.value, message=message, detail=exc.detail)
    return JSONResponse(status_code=status, content=body)


async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理 Pydantic 参数校验异常."""
    locale = _get_locale(request)
    message = t(f"errors.{ErrorCode.VALIDATION_ERROR.value}", locale=locale)

    logger.warning(
        f"ValidationError: {exc.errors()}",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )

    return JSONResponse(
        status_code=422,
        content=fail(
            code=ErrorCode.VALIDATION_ERROR.value,
            message=message,
            detail=str(exc.errors()),
        ),
    )


async def _global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底：未预期的异常."""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={"request_id": getattr(request.state, "request_id", None)},
    )

    locale = _get_locale(request)
    message = t(f"errors.{ErrorCode.UNKNOWN.value}", locale=locale)

    return JSONResponse(
        status_code=500,
        content=fail(code=ErrorCode.UNKNOWN.value, message=message),
    )


def register_error_handlers(app: FastAPI) -> None:
    """注册所有异常处理器到 FastAPI app."""
    app.add_exception_handler(BizError, _biz_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _global_error_handler)  # type: ignore[arg-type]
