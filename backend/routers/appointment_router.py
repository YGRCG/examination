from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, time
from typing import Optional, List

from utils.database import get_db
from utils.security import get_current_user
from services import appointment_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions, CustomException

router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["预约管理"]
)

@router.post("/create", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def create_appointment(
    hospital_id: int,
    department_id: int,
    appointment_date: date,
    appointment_time: time,
    examination_items: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建体检预约接口
    - **hospital_id**: 医院ID
    - **department_id**: 科室ID
    - **appointment_date**: 预约日期 (YYYY-MM-DD)
    - **appointment_time**: 预约时间 (HH:MM:SS)
    - **examination_items**: 体检项目ID列表
    """
    appointment = await appointment_service.create_appointment(
        db, current_user.id, hospital_id, department_id, 
        appointment_date, appointment_time, examination_items
    )
    
    # 构造响应数据
    response_data = {
        "id": appointment.id,
        "user_id": appointment.user_id,
        "hospital_id": appointment.hospital_id,
        "department_id": appointment.department_id,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "examination_items": appointment.examination_items,
        "total_cost": appointment.total_cost,
        "status": appointment.status,
        "created_at": appointment.created_at,
        "updated_at": appointment.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="预约创建成功",
        data=response_data
    )

@router.get("/list", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_appointments(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户预约列表接口
    - **status**: 预约状态（可选）：pending, confirmed, cancelled, completed
    - **limit**: 返回的记录数量，默认50
    - **offset**: 偏移量，默认0
    """
    appointments = await appointment_service.get_user_appointments(
        db, current_user.id, status, limit, offset
    )
    
    # 构造响应数据
    response_data = []
    for appointment in appointments:
        response_data.append({
            "id": appointment.id,
            "hospital_id": appointment.hospital_id,
            "department_id": appointment.department_id,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "examination_items": appointment.examination_items,
            "total_cost": appointment.total_cost,
            "status": appointment.status,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        })
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取预约列表成功",
        data={
            "appointments": response_data,
            "total": len(response_data),
            "limit": limit,
            "offset": offset
        }
    )

@router.put("/{appointment_id}/status", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def update_appointment_status(
    appointment_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新预约状态接口
    - **appointment_id**: 预约ID
    - **new_status**: 新状态：pending, confirmed, cancelled, completed
    """
    # 先检查预约是否属于当前用户
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise CustomException(
            status_code=404,
            message="预约不存在",
            error_type="AppointmentNotFound"
        )
    
    if appointment.user_id != current_user.id:
        raise CustomException(
            status_code=403,
            message="您无权修改此预约",
            error_type="Forbidden"
        )
    
    # 只有管理员可以将状态改为confirmed或completed（这里简化处理）
    if new_status in ["confirmed", "completed"]:
        raise CustomException(
            status_code=403,
            message="只有管理员可以设置此状态",
            error_type="Forbidden"
        )
    
    updated_appointment = await appointment_service.update_appointment_status(db, appointment_id, new_status)
    
    # 构造响应数据
    response_data = {
        "id": updated_appointment.id,
        "status": updated_appointment.status,
        "updated_at": updated_appointment.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="预约状态更新成功",
        data=response_data
    )

@router.post("/{appointment_id}/cancel", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    取消预约接口
    - **appointment_id**: 预约ID
    """
    cancelled_appointment = await appointment_service.cancel_appointment(
        db, appointment_id, current_user.id
    )
    
    # 构造响应数据
    response_data = {
        "id": cancelled_appointment.id,
        "status": cancelled_appointment.status,
        "updated_at": cancelled_appointment.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="预约已取消",
        data=response_data
    )