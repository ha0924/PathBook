"""跨域共享 - 统一异常定义."""


class AppBaseException(Exception):
    """应用基础异常."""

    def __init__(self, code: int = 500, message: str = "Internal Server Error") -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class BadRequestError(AppBaseException):
    """客户端请求错误."""

    def __init__(self, message: str = "Bad Request") -> None:
        super().__init__(code=400, message=message)


class NotFoundError(AppBaseException):
    """资源不存在."""

    def __init__(self, message: str = "Not Found") -> None:
        super().__init__(code=404, message=message)
