from sqlalchemy.orm import Session
from datetime import datetime, date, time
import logging

from models import User, Appointment, ExaminationItem
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.appointment")

async def create_appointment(
    db: Session,
    user_id: int,
    hospital_id: int,
    department_id: int,
    appointment_date: date,
    appointment_time: time,
    examination_items: list[int]
) -> Appointment:
    """
    创建体检预约
    :param db: 数据库会话
    :param user_id: 用户ID
    :param hospital_id: 医院ID
    :param department_id: 科室ID
    :param appointment_date: 预约日期
    :param appointment_time: 预约时间
    :param examination_items: 体检项目ID列表
    :return: 创建的预约记录
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
            
            # 检查预约日期是否合法
            if appointment_date < date.today():
                raise CustomException(
                    status_code=400,
                    message="预约日期不能小于今天",
                    error_type="InvalidAppointmentDate"
                )
            
            # 检查体检项目是否存在
            items = db.query(ExaminationItem).filter(ExaminationItem.id.in_(examination_items)).all()
            if len(items) != len(examination_items):
                raise CustomException(
                    status_code=404,
                    message="部分体检项目不存在",
                    error_type="ItemsNotFound"
                )
            
            # 计算总费用
            total_cost = sum(item.price for item in items)
            
            # 创建预约记录
            appointment = Appointment(
                user_id=user_id,
                hospital_id=hospital_id,
                department_id=department_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                examination_items=",".join(map(str, examination_items)),
                total_cost=total_cost,
                status="pending",
                created_at=datetime.now()
            )
            
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            
            logger.info(f"用户创建体检预约: 用户ID={user_id}, 预约ID={appointment.id}")
            return appointment
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("CreateAppointmentError", f"创建预约失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="创建预约失败，请稍后重试",
            error_type="AppointmentCreationError"
        )

async def get_user_appointments(
    db: Session,
    user_id: int,
    status: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[Appointment]:
    """
    获取用户预约列表
    :param db: 数据库会话
    :param user_id: 用户ID
    :param status: 预约状态（可选）
    :param limit: 返回的记录数量
    :param offset: 偏移量
    :return: 预约列表
    """
    try:
        # 构建查询
        query = db.query(Appointment).filter(Appointment.user_id == user_id)
        
        # 按状态筛选
        if status:
            query = query.filter(Appointment.status == status)
        
        # 按创建时间倒序排序
        appointments = query.order_by(Appointment.created_at.desc()).offset(offset).limit(limit).all()
        
        logger.info(f"获取用户预约列表: 用户ID={user_id}, 数量={len(appointments)}")
        return appointments
        
    except Exception as e:
        log_error("GetUserAppointmentsError", f"获取用户预约列表失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取预约列表失败，请稍后重试",
            error_type="AppointmentsListError"
        )

async def update_appointment_status(
    db: Session,
    appointment_id: int,
    new_status: str
) -> Appointment:
    """
    更新预约状态
    :param db: 数据库会话
    :param appointment_id: 预约ID
    :param new_status: 新状态
    :return: 更新后的预约记录
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
            
            # 检查状态是否合法
            valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
            if new_status not in valid_statuses:
                raise CustomException(
                    status_code=400,
                    message="无效的预约状态",
                    error_type="InvalidStatus"
                )
            
            # 更新状态
            appointment.status = new_status
            appointment.updated_at = datetime.now()
            
            db.commit()
            db.refresh(appointment)
            
            logger.info(f"更新预约状态: 预约ID={appointment_id}, 新状态={new_status}")
            return appointment
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("UpdateAppointmentStatusError", f"更新预约状态失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="更新预约状态失败，请稍后重试",
            error_type="StatusUpdateError"
        )

async def cancel_appointment(
    db: Session,
    appointment_id: int,
    user_id: int
) -> Appointment:
    """
    取消预约
    :param db: 数据库会话
    :param appointment_id: 预约ID
    :param user_id: 用户ID（用于验证）
    :return: 取消后的预约记录
    """
    try:
        # 检查预约是否存在
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise CustomException(
                status_code=404,
                message="预约不存在",
                error_type="AppointmentNotFound"
            )
            
        # 检查预约是否属于当前用户
        if appointment.user_id != user_id:
            raise CustomException(
                status_code=403,
                message="您无权取消此预约",
                error_type="Forbidden"
            )
            
        # 检查预约是否可以取消
        if appointment.status == "cancelled" or appointment.status == "completed":
            raise CustomException(
                status_code=400,
                message="此预约无法取消",
                error_type="CannotCancel"
            )
            
        # 取消预约
        appointment = await update_appointment_status(db, appointment_id, "cancelled")
        
        return appointment
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("CancelAppointmentError", f"取消预约失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="取消预约失败，请稍后重试",
            error_type="CancelError"
        )