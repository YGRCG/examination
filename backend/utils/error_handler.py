import logging
import traceback
from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("app")


class CustomException(Exception):
    """自定义异常类"""
    def __init__(self, status_code: int, message: str, error_type: str = "CustomError"):
        self.status_code = status_code
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


def log_error(error_type: str, error_message: str, exc_info=None):
    """
    记录错误日志
    :param error_type: 错误类型
    :param error_message: 错误消息
    :param exc_info: 异常信息
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if exc_info:
        # 如果提供了异常信息，记录完整的堆栈跟踪
        logger.error(f"[{timestamp}] [{error_type}] {error_message}", exc_info=exc_info)
    else:
        logger.error(f"[{timestamp}] [{error_type}] {error_message}")


def handle_database_error(db_session, exception: Exception) -> None:
    """
    处理数据库错误并执行回滚
    :param db_session: 数据库会话对象
    :param exception: 捕获的异常
    """
    try:
        # 尝试回滚事务
        if db_session and hasattr(db_session, 'rollback'):
            db_session.rollback()
            log_error("DatabaseError", f"事务已回滚: {str(exception)}")
    except Exception as rollback_error:
        log_error("RollbackError", f"回滚失败: {str(rollback_error)}")
    
    # 记录原始数据库错误
    log_error("DatabaseError", str(exception), exc_info=True)


def create_error_response(error_type: str, message: str, status_code: int = 500) -> dict:
    """
    创建统一的错误响应格式
    :param error_type: 错误类型
    :param message: 错误消息
    :param status_code: HTTP状态码
    :return: 错误响应字典
    """
    return {
        "status": "error",
        "code": status_code,
        "message": message,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat()
    }


def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理函数
    用于FastAPI的app.exception_handler装饰器
    """
    if isinstance(exc, CustomException):
        # 处理自定义异常
        log_error(exc.error_type, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(exc.error_type, exc.message, exc.status_code)
        )
    elif isinstance(exc, SQLAlchemyError):
        # 处理数据库异常
        log_error("DatabaseError", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content=create_error_response("DatabaseError", "数据库操作失败，请稍后重试", 500)
        )
    elif isinstance(exc, HTTPException):
        # 处理FastAPI的HTTP异常
        log_error("HTTPError", exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response("HTTPError", exc.detail, exc.status_code)
        )
    else:
        # 处理其他所有未捕获的异常
        log_error("UnexpectedError", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content=create_error_response("UnexpectedError", "服务器内部错误，请稍后重试", 500)
        )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """\全局异常处理中间件"""
    async def dispatch(self, request: Request, call_next):
        try:
            # 处理请求
            response = await call_next(request)
            return response
        except CustomException as e:
            # 处理自定义异常
            log_error(e.error_type, e.message)
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(e.error_type, e.message, e.status_code)
            )
        except SQLAlchemyError as e:
            # 处理数据库异常
            log_error("DatabaseError", str(e), exc_info=True)
            return JSONResponse(
                status_code=500,
                content=create_error_response("DatabaseError", "数据库操作失败，请稍后重试", 500)
            )
        except HTTPException as e:
            # 处理FastAPI内置HTTP异常
            log_error(f"HTTPException_{e.status_code}", e.detail)
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(f"HTTPException_{e.status_code}", e.detail, e.status_code)
            )
        except Exception as e:
            # 处理其他未预期的异常
            log_error("UnexpectedError", str(e), exc_info=True)
            return JSONResponse(
                status_code=500,
                content=create_error_response("UnexpectedError", "服务器内部错误，请稍后重试")
            )


# 异常处理装饰器，用于FastAPI路由函数
def handle_exceptions(func):
    """\n    异常处理装饰器，用于FastAPI路由函数
    自动处理异常并返回统一格式的错误响应
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except CustomException as e:
            log_error(e.error_type, e.message)
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(e.error_type, e.message, e.status_code)
            )
        except SQLAlchemyError as e:
            log_error("DatabaseError", str(e), exc_info=True)
            # 尝试获取数据库会话并回滚
            for arg in args:
                if hasattr(arg, 'db'):
                    handle_database_error(arg.db, e)
                    break
            return JSONResponse(
                status_code=500,
                content=create_error_response("DatabaseError", "数据库操作失败，请稍后重试")
            )
        except HTTPException as e:
            log_error(f"HTTPException_{e.status_code}", e.detail)
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(f"HTTPException_{e.status_code}", e.detail, e.status_code)
            )
        except Exception as e:
            log_error("UnexpectedError", str(e), exc_info=True)
            return JSONResponse(
                status_code=500,
                content=create_error_response("UnexpectedError", "服务器内部错误，请稍后重试")
            )
    
    return wrapper


# 数据库事务上下文管理器，确保事务的原子性
class db_transaction:
    """
    数据库事务上下文管理器
    确保数据库操作的原子性，自动提交或回滚
    """
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def __aenter__(self):
        return self.db_session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                # 发生异常，执行回滚
                handle_database_error(self.db_session, exc_val)
                return False  # 不抑制异常，让上层处理
            else:
                # 没有异常，提交事务
                self.db_session.commit()
                return True
        except Exception as e:
            # 提交或回滚过程中发生错误
            log_error("TransactionError", f"事务处理失败: {str(e)}")
            # 再次尝试回滚
            if hasattr(self.db_session, 'rollback'):
                try:
                    self.db_session.rollback()
                except:
                    pass
            return False