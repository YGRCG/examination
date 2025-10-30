from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models import User, ExaminationReport, ReportInterpretation
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.interpretation")

async def create_report_interpretation(
    db: Session,
    report_id: int,
    interpretation_content: str,
    suggestions: str
) -> ReportInterpretation:
    """
    创建报告解读
    :param db: 数据库会话
    :param report_id: 报告ID
    :param interpretation_content: 解读内容
    :param suggestions: 建议
    :return: 创建的报告解读记录
    """
    try:
        async with db_transaction(db):
            # 检查报告是否存在
            report = db.query(ExaminationReport).filter(ExaminationReport.id == report_id).first()
            if not report:
                raise CustomException(
                    status_code=404,
                    message="报告不存在",
                    error_type="ReportNotFound"
                )
            
            # 检查报告是否已完成
            if report.status not in ["generated", "interpreted"]:
                raise CustomException(
                    status_code=400,
                    message="报告状态不允许解读",
                    error_type="InvalidReportStatus"
                )
            
            # 检查是否已存在解读
            existing_interpretation = db.query(ReportInterpretation).filter(
                ReportInterpretation.report_id == report_id
            ).first()
            if existing_interpretation:
                raise CustomException(
                    status_code=400,
                    message="报告已解读",
                    error_type="InterpretationAlreadyExists"
                )
            
            # 创建报告解读
            interpretation = ReportInterpretation(
                report_id=report_id,
                user_id=report.user_id,
                interpretation_content=interpretation_content,
                suggestions=suggestions,
                created_at=datetime.now()
            )
            
            db.add(interpretation)
            
            # 更新报告状态为已解读
            report.status = "interpreted"
            report.updated_at = datetime.now()
            
            db.commit()
            db.refresh(interpretation)
            
            logger.info(f"创建报告解读: 报告ID={report_id}, 解读ID={interpretation.id}")
            return interpretation
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("CreateReportInterpretationError", f"创建报告解读失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="创建报告解读失败，请稍后重试",
            error_type="InterpretationCreationError"
        )

async def get_report_interpretation(
    db: Session,
    report_id: int,
    user_id: int
) -> ReportInterpretation:
    """
    获取报告解读
    :param db: 数据库会话
    :param report_id: 报告ID
    :param user_id: 用户ID（用于验证）
    :return: 报告解读记录
    """
    try:
        # 检查报告是否存在
        report = db.query(ExaminationReport).filter(ExaminationReport.id == report_id).first()
        if not report:
            raise CustomException(
                status_code=404,
                message="报告不存在",
                error_type="ReportNotFound"
            )
            
        # 检查报告是否属于当前用户
        if report.user_id != user_id:
            raise CustomException(
                status_code=403,
                message="您无权查看此报告的解读",
                error_type="Forbidden"
            )
            
        # 获取报告解读
        interpretation = db.query(ReportInterpretation).filter(
            ReportInterpretation.report_id == report_id
        ).first()
        
        if not interpretation:
            raise CustomException(
                status_code=404,
                message="报告尚未解读",
                error_type="InterpretationNotFound"
            )
            
        return interpretation
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GetReportInterpretationError", f"获取报告解读失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取报告解读失败，请稍后重试",
            error_type="InterpretationRetrievalError"
        )

async def update_report_interpretation(
    db: Session,
    interpretation_id: int,
    interpretation_content: str = None,
    suggestions: str = None
) -> ReportInterpretation:
    """
    更新报告解读
    :param db: 数据库会话
    :param interpretation_id: 解读ID
    :param interpretation_content: 新的解读内容（可选）
    :param suggestions: 新的建议（可选）
    :return: 更新后的报告解读记录
    """
    try:
        async with db_transaction(db):
            # 检查解读是否存在
            interpretation = db.query(ReportInterpretation).filter(
                ReportInterpretation.id == interpretation_id
            ).first()
            if not interpretation:
                raise CustomException(
                    status_code=404,
                    message="报告解读不存在",
                    error_type="InterpretationNotFound"
                )
            
            # 更新解读内容
            if interpretation_content:
                interpretation.interpretation_content = interpretation_content
            
            if suggestions:
                interpretation.suggestions = suggestions
            
            # 更新时间
            interpretation.updated_at = datetime.now()
            
            db.commit()
            db.refresh(interpretation)
            
            logger.info(f"更新报告解读: 解读ID={interpretation_id}")
            return interpretation
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("UpdateReportInterpretationError", f"更新报告解读失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="更新报告解读失败，请稍后重试",
            error_type="InterpretationUpdateError"
        )

async def get_user_interpretations(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> list[ReportInterpretation]:
    """
    获取用户的所有报告解读
    :param db: 数据库会话
    :param user_id: 用户ID
    :param limit: 返回的记录数量
    :param offset: 偏移量
    :return: 报告解读列表
    """
    try:
        # 查询用户的所有报告解读
        interpretations = db.query(ReportInterpretation)
        interpretations = interpretations.filter(ReportInterpretation.user_id == user_id)
        interpretations = interpretations.order_by(ReportInterpretation.created_at.desc())
        interpretations = interpretations.offset(offset)
        interpretations = interpretations.limit(limit)
        interpretations = interpretations.all()
        
        logger.info(f"获取用户报告解读列表: 用户ID={user_id}, 数量={len(interpretations)}")
        return interpretations
        
    except Exception as e:
        log_error("GetUserInterpretationsError", f"获取用户报告解读列表失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取报告解读列表失败，请稍后重试",
            error_type="InterpretationsListError"
        )