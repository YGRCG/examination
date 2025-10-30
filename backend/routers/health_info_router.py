from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from typing import Optional

from utils.database import get_db
from utils.security import get_current_user
from services import health_info_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions

router = APIRouter(
    prefix="/api/v1/health-info",
    tags=["信息收集"]
)

# 体检报告文件存储路径
REPORT_STORAGE_PATH = "medical_reports"

# 确保存储目录存在
if not os.path.exists(REPORT_STORAGE_PATH):
    os.makedirs(REPORT_STORAGE_PATH)

@router.post("/submit", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def submit_health_information(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    提交健康信息接口
    - **age**: 年龄
    - **gender**: 性别
    - **height**: 身高
    - **weight**: 体重
    - **blood_type**: 血型
    - **allergies**: 过敏史
    - **chronic_diseases**: 慢性疾病
    - **family_medical_history**: 家族病史
    - **lifestyle**: 生活方式
    - **last_examination_date**: 上次体检日期
    """
    health_info = await health_info_service.submit_health_info(db, current_user.id, data)
    
    # 构造响应数据
    response_data = {
        "id": health_info.id,
        "user_id": health_info.user_id,
        "age": health_info.age,
        "gender": health_info.gender,
        "height": health_info.height,
        "weight": health_info.weight,
        "blood_type": health_info.blood_type,
        "allergies": health_info.allergies,
        "chronic_diseases": health_info.chronic_diseases,
        "family_medical_history": health_info.family_medical_history,
        "lifestyle": health_info.lifestyle,
        "last_examination_date": health_info.last_examination_date,
        "updated_at": health_info.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="健康信息提交成功",
        data=response_data
    )

@router.post("/upload-report", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def upload_medical_report(
    file: UploadFile = File(...),
    report_date: Optional[str] = None,
    report_type: Optional[str] = "体检报告",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    上传历史体检报告接口
    - **file**: 体检报告文件
    - **report_date**: 报告日期 (YYYY-MM-DD)
    - **report_type**: 报告类型，默认"体检报告"
    """
    # 保存报告文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(REPORT_STORAGE_PATH, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 存储文件URL（实际应用中应该是可访问的URL）
        report_url = f"/static/reports/{filename}"
        
        # 解析报告日期
        report_date_obj = None
        if report_date:
            report_date_obj = datetime.strptime(report_date, "%Y-%m-%d")
        
        # 创建体检报告记录
        medical_report = await health_info_service.upload_medical_report(
            db, current_user.id, report_url, report_date_obj, report_type
        )
        
        # 构造响应数据
        response_data = {
            "id": medical_report.id,
            "user_id": medical_report.user_id,
            "report_url": medical_report.report_url,
            "report_date": medical_report.report_date,
            "report_type": medical_report.report_type,
            "uploaded_at": medical_report.uploaded_at
        }
        
        return user_schemas.ApiResponse(
            status="success",
            message="体检报告上传成功",
            data=response_data
        )
    finally:
        # 关闭文件
        file.file.close()

@router.post("/update", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def update_health_information(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新健康信息接口
    - **age**: 年龄
    - **gender**: 性别
    - **height**: 身高
    - **weight**: 体重
    - **blood_type**: 血型
    - **allergies**: 过敏史
    - **chronic_diseases**: 慢性疾病
    - **family_medical_history**: 家族病史
    - **lifestyle**: 生活方式
    - **last_examination_date**: 上次体检日期
    """
    health_info = await health_info_service.update_health_info(db, current_user.id, data)
    
    # 构造响应数据
    response_data = {
        "id": health_info.id,
        "user_id": health_info.user_id,
        "age": health_info.age,
        "gender": health_info.gender,
        "height": health_info.height,
        "weight": health_info.weight,
        "blood_type": health_info.blood_type,
        "allergies": health_info.allergies,
        "chronic_diseases": health_info.chronic_diseases,
        "family_medical_history": health_info.family_medical_history,
        "lifestyle": health_info.lifestyle,
        "last_examination_date": health_info.last_examination_date,
        "updated_at": health_info.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="健康信息更新成功",
        data=response_data
    )

@router.get("/user/{user_id}", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_health_info(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户健康信息接口
    """
    health_info = await health_info_service.get_user_health_info(db, user_id)
    
    # 构造响应数据
    response_data = {
        "id": health_info.id,
        "user_id": health_info.user_id,
        "age": health_info.age,
        "gender": health_info.gender,
        "height": health_info.height,
        "weight": health_info.weight,
        "blood_type": health_info.blood_type,
        "allergies": health_info.allergies,
        "chronic_diseases": health_info.chronic_diseases,
        "family_medical_history": health_info.family_medical_history,
        "lifestyle": health_info.lifestyle,
        "last_examination_date": health_info.last_examination_date,
        "updated_at": health_info.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取用户健康信息成功",
        data=response_data
    )

@router.get("/generate-portrait", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def generate_user_portrait(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    生成用户画像接口
    """
    user_portrait = await health_info_service.generate_user_portrait(db, current_user.id)
    
    # 构造响应数据
    response_data = {
        "id": user_portrait.id,
        "user_id": user_portrait.user_id,
        "health_risk": user_portrait.health_risk,
        "recommended_frequency": user_portrait.recommended_frequency,
        "generated_at": user_portrait.generated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="用户画像生成成功",
        data=response_data
    )