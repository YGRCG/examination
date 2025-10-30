from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models import User, Appointment, ExaminationReport, ReportInterpretation
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.report")

async def create_examination_report(
    db: Session,
    appointment_id: int,
    report_data: dict,
    report_url: str
) -> ExaminationReport:
    """
    创建体检报告
    :param db: 数据库会话
    :param appointment_id: 预约ID
    :param report_data: 报告数据
    :param report_url: 报告文件URL
    :return: 创建的体检报告记录
    """
    try:
        async with db_transaction(db):
            # 检查预约是否存在
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                raise CustomException(
                    status_code=404,
                    message="预约不存在",
                    error_type="AppointmentNotFound"
                )
            
            # 检查预约是否已完成
            if appointment.status != "completed":
                raise CustomException(
                    status_code=400,
                    message="预约尚未完成，无法生成报告",
                    error_type="AppointmentNotCompleted"
                )
            
            # 检查是否已存在报告
            existing_report = db.query(ExaminationReport).filter(
                ExaminationReport.appointment_id == appointment_id
            ).first()
            if existing_report:
                raise CustomException(
                    status_code=400,
                    message="报告已存在",
                    error_type="ReportAlreadyExists"
                )
            
            # 创建体检报告
            examination_report = ExaminationReport(
                appointment_id=appointment_id,
                user_id=appointment.user_id,
                report_url=report_url,
                report_data=report_data,
                status="generated",
                created_at=datetime.now()
            )
            
            db.add(examination_report)
            db.commit()
            db.refresh(examination_report)
            
            logger.info(f"创建体检报告: 预约ID={appointment_id}, 报告ID={examination_report.id}")
            return examination_report
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("CreateExaminationReportError", f"创建体检报告失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="创建体检报告失败，请稍后重试",
            error_type="ReportCreationError"
        )

async def get_user_reports(
    db: Session,
    user_id: int,
    status: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[ExaminationReport]:
    """
    获取用户报告列表
    :param db: 数据库会话
    :param user_id: 用户ID
    :param status: 报告状态（可选）
    :param limit: 返回的记录数量
    :param offset: 偏移量
    :return: 报告列表
    """
    try:
        # 构建查询
        query = db.query(ExaminationReport).filter(ExaminationReport.user_id == user_id)
        
        # 按状态筛选
        if status:
            query = query.filter(ExaminationReport.status == status)
        
        # 按创建时间倒序排序
        reports = query.order_by(ExaminationReport.created_at.desc()).offset(offset).limit(limit).all()
        
        logger.info(f"获取用户报告列表: 用户ID={user_id}, 数量={len(reports)}")
        return reports
        
    except Exception as e:
        log_error("GetUserReportsError", f"获取用户报告列表失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取报告列表失败，请稍后重试",
            error_type="ReportsListError"
        )

async def get_report_detail(
    db: Session,
    report_id: int,
    user_id: int
) -> ExaminationReport:
    """
    获取报告详情
    :param db: 数据库会话
    :param report_id: 报告ID
    :param user_id: 用户ID（用于验证）
    :return: 报告详情
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
                message="您无权查看此报告",
                error_type="Forbidden"
            )
            
        return report
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GetReportDetailError", f"获取报告详情失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取报告详情失败，请稍后重试",
            error_type="ReportDetailError"
        )

async def update_report_status(
    db: Session,
    report_id: int,
    new_status: str
) -> ExaminationReport:
    """
    更新报告状态
    :param db: 数据库会话
    :param report_id: 报告ID
    :param new_status: 新状态
    :return: 更新后的报告记录
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
            
            # 检查状态是否合法
            valid_statuses = ["generated", "interpreted", "archived"]
            if new_status not in valid_statuses:
                raise CustomException(
                    status_code=400,
                    message="无效的报告状态",
                    error_type="InvalidStatus"
                )
            
            # 更新状态
            report.status = new_status
            report.updated_at = datetime.now()
            
            db.commit()
            db.refresh(report)
            
            logger.info(f"更新报告状态: 报告ID={report_id}, 新状态={new_status}")
            return report
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("UpdateReportStatusError", f"更新报告状态失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="更新报告状态失败，请稍后重试",
            error_type="StatusUpdateError"
        )