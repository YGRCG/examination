from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from utils.database import get_db
from utils.security import get_current_user
from services import interpretation_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions, CustomException

router = APIRouter(
    prefix="/api/v1/interpretations",
    tags=["报告解读"]
)

@router.post("/create", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def create_report_interpretation(
    report_id: int,
    interpretation_content: str,
    suggestions: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建报告解读接口
    - **report_id**: 报告ID
    - **interpretation_content**: 解读内容
    - **suggestions**: 建议
    """
    # 检查报告是否属于当前用户
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
            message="您无权为此报告创建解读",
            error_type="Forbidden"
        )
    
    # 只有管理员或医生可以创建解读（这里简化处理）
    # 实际应用中应该有角色检查
    
    interpretation = await interpretation_service.create_report_interpretation(
        db, report_id, interpretation_content, suggestions
    )
    
    # 构造响应数据
    response_data = {
        "id": interpretation.id,
        "report_id": interpretation.report_id,
        "user_id": interpretation.user_id,
        "interpretation_content": interpretation.interpretation_content,
        "suggestions": interpretation.suggestions,
        "created_at": interpretation.created_at,
        "updated_at": interpretation.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="报告解读创建成功",
        data=response_data
    )

@router.get("/report/{report_id}", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_report_interpretation(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取报告解读接口
    - **report_id**: 报告ID
    """
    interpretation = await interpretation_service.get_report_interpretation(
        db, report_id, current_user.id
    )
    
    # 构造响应数据
    response_data = {
        "id": interpretation.id,
        "report_id": interpretation.report_id,
        "user_id": interpretation.user_id,
        "interpretation_content": interpretation.interpretation_content,
        "suggestions": interpretation.suggestions,
        "created_at": interpretation.created_at,
        "updated_at": interpretation.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取报告解读成功",
        data=response_data
    )

@router.put("/{interpretation_id}", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def update_report_interpretation(
    interpretation_id: int,
    interpretation_content: Optional[str] = None,
    suggestions: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新报告解读接口
    - **interpretation_id**: 解读ID
    - **interpretation_content**: 新的解读内容（可选）
    - **suggestions**: 新的建议（可选）
    """
    # 检查解读是否属于当前用户
    interpretation = db.query(ReportInterpretation).filter(
        ReportInterpretation.id == interpretation_id
    ).first()
    if not interpretation:
        raise CustomException(
            status_code=404,
            message="报告解读不存在",
            error_type="InterpretationNotFound"
        )
    
    if interpretation.user_id != current_user.id:
        raise CustomException(
            status_code=403,
            message="您无权修改此报告解读",
            error_type="Forbidden"
        )
    
    # 只有管理员或医生可以更新解读（这里简化处理）
    # 实际应用中应该有角色检查
    
    updated_interpretation = await interpretation_service.update_report_interpretation(
        db, interpretation_id, interpretation_content, suggestions
    )
    
    # 构造响应数据
    response_data = {
        "id": updated_interpretation.id,
        "report_id": updated_interpretation.report_id,
        "interpretation_content": updated_interpretation.interpretation_content,
        "suggestions": updated_interpretation.suggestions,
        "updated_at": updated_interpretation.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="报告解读更新成功",
        data=response_data
    )

@router.get("/list", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_interpretations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户的所有报告解读接口
    - **limit**: 返回的记录数量，默认50
    - **offset**: 偏移量，默认0
    """
    interpretations = await interpretation_service.get_user_interpretations(
        db, current_user.id, limit, offset
    )
    
    # 构造响应数据
    response_data = []
    for interpretation in interpretations:
        # 获取关联的报告信息
        report = db.query(ExaminationReport).filter(
            ExaminationReport.id == interpretation.report_id
        ).first()
        
        report_info = None
        if report:
            report_info = {
                "id": report.id,
                "appointment_id": report.appointment_id,
                "created_at": report.created_at
            }
        
        response_data.append({
            "id": interpretation.id,
            "report_id": interpretation.report_id,
            "report_info": report_info,
            "interpretation_content": interpretation.interpretation_content,
            "suggestions": interpretation.suggestions,
            "created_at": interpretation.created_at,
            "updated_at": interpretation.updated_at
        })
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取报告解读列表成功",
        data={
            "interpretations": response_data,
            "total": len(response_data),
            "limit": limit,
            "offset": offset
        }
    )