from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models import User, UserProfile, HealthInfo, MedicalReport, UserPortrait
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.health_info")

async def submit_health_info(
    db: Session,
    user_id: int,
    health_data: dict
) -> HealthInfo:
    """
    提交健康信息
    :param db: 数据库会话
    :param user_id: 用户ID
    :param health_data: 健康信息数据
    :return: 创建的健康信息记录
    """
    try:
        async with db_transaction(db):
            # 检查用户是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 创建健康信息记录
            health_info = HealthInfo(
                user_id=user_id,
                age=health_data.get("age"),
                gender=health_data.get("gender"),
                height=health_data.get("height"),
                weight=health_data.get("weight"),
                blood_type=health_data.get("blood_type"),
                allergies=health_data.get("allergies"),
                chronic_diseases=health_data.get("chronic_diseases"),
                family_medical_history=health_data.get("family_medical_history"),
                lifestyle=health_data.get("lifestyle"),
                last_examination_date=health_data.get("last_examination_date"),
                updated_at=datetime.now()
            )
            
            # 检查是否已存在健康信息，如果有则更新，没有则创建
            existing_health_info = db.query(HealthInfo).filter(HealthInfo.user_id == user_id).first()
            if existing_health_info:
                for key, value in health_info.__dict__.items():
                    if key != "id" and value is not None:
                        setattr(existing_health_info, key, value)
                db.commit()
                db.refresh(existing_health_info)
                health_info = existing_health_info
            else:
                db.add(health_info)
                db.commit()
                db.refresh(health_info)
            
            logger.info(f"用户提交健康信息: 用户ID={user_id}")
            return health_info
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("SubmitHealthInfoError", f"提交健康信息失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="提交健康信息失败，请稍后重试",
            error_type="HealthInfoSubmissionError"
        )

async def upload_medical_report(
    db: Session,
    user_id: int,
    report_url: str,
    report_date: datetime,
    report_type: str
) -> MedicalReport:
    """
    上传历史体检报告
    :param db: 数据库会话
    :param user_id: 用户ID
    :param report_url: 报告文件URL
    :param report_date: 报告日期
    :param report_type: 报告类型
    :return: 创建的体检报告记录
    """
    try:
        async with db_transaction(db):
            # 检查用户是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 创建体检报告记录
            medical_report = MedicalReport(
                user_id=user_id,
                report_url=report_url,
                report_date=report_date,
                report_type=report_type,
                uploaded_at=datetime.now()
            )
            
            db.add(medical_report)
            db.commit()
            db.refresh(medical_report)
            
            logger.info(f"用户上传体检报告: 用户ID={user_id}, 报告ID={medical_report.id}")
            return medical_report
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("UploadMedicalReportError", f"上传体检报告失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="上传体检报告失败，请稍后重试",
            error_type="MedicalReportUploadError"
        )

async def update_health_info(
    db: Session,
    user_id: int,
    health_data: dict
) -> HealthInfo:
    """
    更新健康信息
    :param db: 数据库会话
    :param user_id: 用户ID
    :param health_data: 健康信息数据
    :return: 更新的健康信息记录
    """
    try:
        async with db_transaction(db):
            # 检查用户是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 查找现有的健康信息记录
            existing_health_info = db.query(HealthInfo).filter(HealthInfo.user_id == user_id).first()
            
            if existing_health_info:
                # 更新现有记录
                for key, value in health_data.items():
                    if hasattr(existing_health_info, key) and value is not None:
                        setattr(existing_health_info, key, value)
                existing_health_info.updated_at = datetime.now()
                db.commit()
                db.refresh(existing_health_info)
                health_info = existing_health_info
            else:
                # 创建新的健康信息记录
                health_info = HealthInfo(
                    user_id=user_id,
                    age=health_data.get("age"),
                    gender=health_data.get("gender"),
                    height=health_data.get("height"),
                    weight=health_data.get("weight"),
                    blood_type=health_data.get("blood_type"),
                    allergies=health_data.get("allergies"),
                    chronic_diseases=health_data.get("chronic_diseases"),
                    family_medical_history=health_data.get("family_medical_history"),
                    lifestyle=health_data.get("lifestyle"),
                    last_examination_date=health_data.get("last_examination_date"),
                    updated_at=datetime.now()
                )
                db.add(health_info)
                db.commit()
                db.refresh(health_info)
            
            logger.info(f"用户更新健康信息: 用户ID={user_id}")
            return health_info
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("UpdateHealthInfoError", f"更新健康信息失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="更新健康信息失败，请稍后重试",
            error_type="HealthInfoUpdateError"
        )

async def get_user_health_info(
    db: Session,
    user_id: int
) -> HealthInfo:
    """
    获取用户健康信息
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 健康信息记录
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(
                status_code=404,
                message="用户不存在",
                error_type="UserNotFound"
            )
        
        # 获取用户健康信息
        health_info = db.query(HealthInfo).filter(HealthInfo.user_id == user_id).first()
        
        if not health_info:
            raise CustomException(
                status_code=404,
                message="用户健康信息不存在",
                error_type="HealthInfoNotFound"
            )
        
        return health_info
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GetUserHealthInfoError", f"获取用户健康信息失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="获取用户健康信息失败，请稍后重试",
            error_type="GetUserHealthInfoError"
        )

async def generate_user_portrait(
    db: Session,
    user_id: int
) -> UserPortrait:
    """
    生成用户画像
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 创建的用户画像记录
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(
                status_code=404,
                message="用户不存在",
                error_type="UserNotFound"
            )
            
        # 获取用户健康信息和体检报告
        health_info = db.query(HealthInfo).filter(HealthInfo.user_id == user_id).first()
        medical_reports = db.query(MedicalReport).filter(MedicalReport.user_id == user_id).all()
        
        # 这里应该有更复杂的用户画像生成逻辑
        # 为了演示，我们简单地创建一个用户画像
        health_risk = "低风险"
        recommended_frequency = "每年一次"
        
        # 检查是否已存在用户画像，如果有则更新，没有则创建
        user_portrait = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        
        if user_portrait:
            # 更新用户画像
            user_portrait.health_risk = health_risk
            user_portrait.recommended_frequency = recommended_frequency
            user_portrait.generated_at = datetime.now()
        else:
            # 创建用户画像
            user_portrait = UserPortrait(
                user_id=user_id,
                health_risk=health_risk,
                recommended_frequency=recommended_frequency,
                generated_at=datetime.now()
            )
            db.add(user_portrait)
        
        db.commit()
        db.refresh(user_portrait)
        
        logger.info(f"生成用户画像: 用户ID={user_id}")
        return user_portrait
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GenerateUserPortraitError", f"生成用户画像失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="生成用户画像失败，请稍后重试",
            error_type="UserPortraitGenerationError"
        )