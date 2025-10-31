from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import logging
import os
from dotenv import load_dotenv

# 导入自定义模块
from utils.error_handler import global_exception_handler, CustomException
from utils.database import get_db, init_db
from utils.logger import setup_logger
from api.example import router as example_router
from middleware import auth_middleware, cors_middleware, log_middleware

# 导入路由模块
from routers.auth_router import router as auth_router
from routers.user_router import router as user_router
from routers.interaction_router import router as interaction_router
from routers.health_info_router import router as health_info_router
from routers.recommendation_router import router as recommendation_router
from routers.appointment_router import router as appointment_router
from routers.report_router import router as report_router
from routers.interpretation_router import router as interpretation_router
from routers.admin_router import router as admin_router
from routers.user_profile_router import router as user_profile_router
from routers.ai_router import router as ai_router
from api.v1.user_portrait_router import router as user_portrait_router

# 加载环境变量
load_dotenv()

# 设置日志
logger = setup_logger("app.main")

# 创建FastAPI应用
app = FastAPI(
    title="医院体检项目智能推荐系统",
    description="基于用户健康数据和体检记录的智能体检项目推荐系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加全局异常处理中间件
app.exception_handler(Exception)(global_exception_handler)

# 挂载静态文件目录
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# API版本前缀
API_V1_PREFIX = "/api/v1"

# 注册路由
app.include_router(example_router, prefix="/api", tags=["示例接口"])
# 注册认证路由
app.include_router(auth_router, prefix=API_V1_PREFIX, tags=["认证管理"])
# 注册用户管理路由
app.include_router(user_router, prefix=API_V1_PREFIX, tags=["用户管理"])
# 注册智能交互路由
app.include_router(interaction_router, prefix=API_V1_PREFIX, tags=["智能交互"])
# 注册信息收集路由
app.include_router(health_info_router, prefix=API_V1_PREFIX, tags=["健康信息"])
# 注册智能推荐路由
app.include_router(recommendation_router, prefix=API_V1_PREFIX, tags=["智能推荐"])
# 注册预约管理路由
app.include_router(appointment_router, prefix=API_V1_PREFIX, tags=["预约管理"])
# 注册报告管理路由
app.include_router(report_router, prefix=API_V1_PREFIX, tags=["报告管理"])
# 注册报告解读路由
app.include_router(interpretation_router, prefix=API_V1_PREFIX, tags=["报告解读"])
# 注册管理路由
app.include_router(admin_router, prefix=API_V1_PREFIX, tags=["系统管理"])
# 注册用户画像路由
app.include_router(user_profile_router, prefix=API_V1_PREFIX, tags=["用户画像"])
# 注册用户画像路由
app.include_router(user_portrait_router, prefix=API_V1_PREFIX, tags=["用户画像"])
# 注册AI智能交互路由
app.include_router(ai_router, prefix=API_V1_PREFIX, tags=["AI智能交互"])


@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件
    初始化数据库连接、创建表结构等
    """
    try:
        logger.info("应用启动中...")
        
        # 尝试初始化数据库，但在失败时不阻止应用启动
        try:
            init_db()
            logger.info("数据库初始化成功")
        except Exception as db_error:
            logger.error(f"数据库初始化失败: {str(db_error)}", exc_info=True)
            logger.warning("应用将继续运行，但部分功能可能不可用")
        
        logger.info("应用启动成功")
    except Exception as e:
        logger.error(f"应用启动过程中发生错误: {str(e)}", exc_info=True)
        # 不再直接抛出异常，允许应用继续运行
        logger.warning("应用尝试继续运行，但可能存在问题")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行的事件
    清理资源、关闭连接等
    """
    try:
        logger.info("应用关闭中...")
        # 在这里可以添加资源清理代码
        logger.info("应用关闭成功")
    except Exception as e:
        logger.error(f"应用关闭过程中发生错误: {str(e)}")


@app.get("/")
def read_root():
    """
    根路径接口
    返回应用基本信息
    """
    return {
        "status": "success",
        "message": "医院体检项目智能推荐系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    健康检查接口
    检查应用和数据库连接是否正常
    """
    try:
        # 执行简单的数据库查询来验证连接
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "success",
            "message": "应用健康运行中",
            "database": "连接正常"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "健康检查失败",
                "database": "连接异常"
            }
        )


# 启动应用的入口点
if __name__ == "__main__":
    # 获取端口号，默认为8000
    port = int(os.getenv("PORT", "8000"))
    # 获取主机地址，默认为0.0.0.0
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"启动服务器: {host}:{port}")
    # 启动应用
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)