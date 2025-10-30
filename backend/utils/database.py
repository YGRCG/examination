from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv
import logging
from models import Base

# 加载环境变量
load_dotenv()

# 获取数据库URL，如果环境变量中不存在，则使用默认值
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://exam_admin:admin123456@localhost:5433/hospital_examination"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    # 对于异步操作，可以添加以下参数
    # echo=True,  # 打印SQL语句
    # pool_size=5,  # 连接池大小
    # max_overflow=10,  # 超出连接池大小的最大连接数
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 从backend.models导入Base，确保所有模型使用同一个基础类

logger = logging.getLogger("app.database")


def get_db() -> Generator:
    """
    数据库会话依赖项
    提供数据库会话，用于FastAPI路由中依赖注入
    :return: 数据库会话生成器
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # 记录错误日志
        logger.error(f"数据库会话错误: {str(e)}")
        # 发生错误时回滚事务
        db.rollback()
        # 重新抛出异常，让上层处理
        raise
    finally:
        # 无论如何都关闭会话
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
        raise


def drop_db():
    """
    删除数据库中所有表
    注意：仅在开发和测试环境中使用
    """
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库表已删除")
    except Exception as e:
        logger.error(f"删除数据库表失败: {str(e)}", exc_info=True)
        raise


def get_db_connection():
    """
    获取原始数据库连接
    直接返回数据库引擎的连接，用于需要执行原始SQL的场景
    :return: 数据库连接对象
    """
    conn = engine.connect()
    try:
        yield conn
    except Exception as e:
        logger.error(f"数据库连接错误: {str(e)}")
        # 发生错误时关闭连接
        conn.close()
        raise
    finally:
        # 无论如何都关闭连接
        conn.close()


# 添加表的索引创建函数
def create_indexes():
    """
    创建数据库索引
    优化查询性能
    """
    from sqlalchemy import Index
    from models import User, UserProfile, ExaminationItem, UserExaminationItem, \
                        ExaminationRecord, ExaminationResult, Recommendation, HealthMetric
    
    try:
        # 用户表索引
        Index('idx_users_username', User.username).create(bind=engine)
        Index('idx_users_email', User.email).create(bind=engine)
        
        # 用户资料表索引
        Index('idx_user_profiles_user_id', UserProfile.user_id).create(bind=engine)
        
        # 体检项目表索引
        Index('idx_examination_items_category', ExaminationItem.category).create(bind=engine)
        Index('idx_examination_items_name', ExaminationItem.name).create(bind=engine)
        
        # 用户体检项目表索引
        Index('idx_user_examination_items_user_id', UserExaminationItem.user_id).create(bind=engine)
        Index('idx_user_examination_items_item_id', UserExaminationItem.examination_item_id).create(bind=engine)
        Index('idx_user_examination_items_status', UserExaminationItem.status).create(bind=engine)
        
        # 体检记录表索引
        Index('idx_examination_records_user_id', ExaminationRecord.user_id).create(bind=engine)
        Index('idx_examination_records_record_date', ExaminationRecord.record_date).create(bind=engine)
        Index('idx_examination_records_status', ExaminationRecord.status).create(bind=engine)
        
        # 体检结果表索引
        Index('idx_examination_results_record_id', ExaminationResult.record_id).create(bind=engine)
        Index('idx_examination_results_item_id', ExaminationResult.examination_item_id).create(bind=engine)
        Index('idx_examination_results_is_abnormal', ExaminationResult.is_abnormal).create(bind=engine)
        
        # 推荐表索引
        Index('idx_recommendations_user_id', Recommendation.user_id).create(bind=engine)
        Index('idx_recommendations_based_on_record_id', Recommendation.based_on_record_id).create(bind=engine)
        
        # 健康指标表索引
        Index('idx_health_metrics_user_id', HealthMetric.user_id).create(bind=engine)
        Index('idx_health_metrics_metric_name', HealthMetric.metric_name).create(bind=engine)
        Index('idx_health_metrics_recorded_at', HealthMetric.recorded_at).create(bind=engine)
        
        logger.info("数据库索引创建成功")
    except Exception as e:
        logger.error(f"创建数据库索引失败: {str(e)}", exc_info=True)
        raise