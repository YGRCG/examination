from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from typing import Optional

from utils.database import get_db
from utils.security import get_current_user
from services import report_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions, CustomException

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["报告管理"]
)

# 报告文件存储路径
EXAMINATION_REPORT_STORAGE_PATH = "examination_reports"

# 确保存储目录存在
if not os.path.exists(EXAMINATION_REPORT_STORAGE_PATH):
    os.makedirs(EXAMINATION_REPORT_STORAGE_PATH)

@router.post("/create", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def create_examination_report(
    appointment_id: int,
    report_data: dict,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建体检报告接口
    - **appointment_id**: 预约ID
    - **report_data**: 报告数据
    - **file**: 报告文件
    """
    # 检查预约是否属于当前用户
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
            message="您无权为此预约创建报告",
            error_type="Forbidden"
        )
    
    # 保存报告文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{appointment_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(EXAMINATION_REPORT_STORAGE_PATH, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 存储文件URL（实际应用中应该是可访问的URL）
        report_url = f"/static/examination_reports/{filename}"
        
        # 创建体检报告记录
        examination_report = await report_service.create_examination_report(
            db, appointment_id, report_data, report_url
        )
        
        # 构造响应数据
        response_data = {
            "id": examination_report.id,
            "appointment_id": examination_report.appointment_id,
            "user_id": examination_report.user_id,
            "report_url": examination_report.report_url,
            "report_data": examination_report.report_data,
            "status": examination_report.status,
            "created_at": examination_report.created_at,
            "updated_at": examination_report.updated_at
        }
        
        return user_schemas.ApiResponse(
            status="success",
            message="报告创建成功",
            data=response_data
        )
    finally:
        # 关闭文件
        file.file.close()

@router.get("/list", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_reports(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户报告列表接口
    - **status**: 报告状态（可选）：generated, interpreted, archived
    - **limit**: 返回的记录数量，默认50
    - **offset**: 偏移量，默认0
    """
    reports = await report_service.get_user_reports(
        db, current_user.id, status, limit, offset
    )
    
    # 构造响应数据
    response_data = []
    for report in reports:
        response_data.append({
            "id": report.id,
            "appointment_id": report.appointment_id,
            "report_url": report.report_url,
            "status": report.status,
            "created_at": report.created_at,
            "updated_at": report.updated_at
        })
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取报告列表成功",
        data={
            "reports": response_data,
            "total": len(response_data),
            "limit": limit,
            "offset": offset
        }
    )

@router.get("/{report_id}", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取报告详情接口
    - **report_id**: 报告ID
    """
    report = await report_service.get_report_detail(db, report_id, current_user.id)
    
    # 构造响应数据
    response_data = {
        "id": report.id,
        "appointment_id": report.appointment_id,
        "user_id": report.user_id,
        "report_url": report.report_url,
        "report_data": report.report_data,
        "status": report.status,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取报告详情成功",
        data=response_data
    )

@router.put("/{report_id}/status", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def update_report_status(
    report_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新报告状态接口
    - **report_id**: 报告ID
    - **new_status**: 新状态：generated, interpreted, archived
    """
    # 先检查报告是否属于当前用户
    report = db.query(ExaminationReport).filter(ExaminationReport.id == report_id).first()
    if not report:
        raise CustomException(
            status_code=404,
            message="报告不存在",
            error_type="ReportNotFound"
        )
    
    if report.user_id != current_user.id:
        raise CustomException(
            status_code=403,
            message="您无权修改此报告",
            error_type="Forbidden"
        )
    
    # 普通用户只能将状态改为archived（这里简化处理）
    if new_status != "archived":
        raise CustomException(
            status_code=403,
            message="只有管理员可以设置此状态",
            error_type="Forbidden"
        )
    
    updated_report = await report_service.update_report_status(db, report_id, new_status)
    
    # 构造响应数据
    response_data = {
        "id": updated_report.id,
        "status": updated_report.status,
        "updated_at": updated_report.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="报告状态更新成功",
        data=response_data
    )