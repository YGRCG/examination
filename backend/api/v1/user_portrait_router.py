from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from utils.database import get_db
from utils.security import get_current_user
from models import User
from services.user_portrait_service import (
    get_questionnaire_progress,
    process_questionnaire_step,
    process_dynamic_question_answer,
    skip_questionnaire_step,
    reset_questionnaire,
    MAIN_FLOW_STEPS
)
from utils.schemas import (
    QuestionnaireProgressResponse,
    StepRequest,
    StepResponse,
    DynamicQuestionRequest,
    DynamicQuestionResponse,
    SkipResponse,
    ResetResponse
)

logger = logging.getLogger("app.api.user_portrait")

router = APIRouter(
    prefix="/user-portrait",
    tags=["user-portrait"]
)


@router.get("/progress", response_model=QuestionnaireProgressResponse)
def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户画像问卷进度
    返回当前步骤、已完成步骤和当前状态
    """
    try:
        progress = get_questionnaire_progress(db, current_user.id)
        return progress
    except Exception as e:
        logger.error(f"获取问卷进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取问卷进度失败")


@router.post("/step", response_model=StepResponse)
def process_step(
    step_data: StepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理问卷步骤数据
    根据当前步骤和用户输入处理信息，并返回下一步指示
    """
    try:
        result = process_questionnaire_step(
            db, 
            current_user.id, 
            step_data.step,
            step_data.data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理问卷步骤失败: {str(e)}")
        raise HTTPException(status_code=500, detail="处理问卷步骤失败")


@router.post("/dynamic-question", response_model=DynamicQuestionResponse)
def process_dynamic_answer(
    answer_data: DynamicQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理动态追问的回答
    用户回答症状相关的动态追问，系统继续追问或返回主流程
    """
    try:
        result = process_dynamic_question_answer(
            db,
            current_user.id,
            answer_data.answer
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理动态追问回答失败: {str(e)}")
        raise HTTPException(status_code=500, detail="处理动态追问回答失败")


@router.post("/skip", response_model=SkipResponse)
def skip_step(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    跳过当前问卷步骤
    注意：基本信息步骤无法跳过
    """
    try:
        result = skip_questionnaire_step(db, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"跳过问卷步骤失败: {str(e)}")
        raise HTTPException(status_code=500, detail="跳过问卷步骤失败")


@router.post("/reset", response_model=ResetResponse)
def reset_flow(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重置用户画像问卷流程
    清空所有已填写的数据，重新开始问卷
    """
    try:
        result = reset_questionnaire(db, current_user.id)
        return result
    except Exception as e:
        logger.error(f"重置问卷失败: {str(e)}")
        raise HTTPException(status_code=500, detail="重置问卷失败")


@router.get("/steps", response_model=List[str])
def get_all_steps():
    """
    获取所有问卷步骤定义
    返回主流程的所有步骤列表
    """
    return MAIN_FLOW_STEPS


@router.get("/status")
def get_flow_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户画像流程的详细状态
    返回包括进度、已收集数据等完整信息
    """
    try:
        # 获取基础进度
        progress = get_questionnaire_progress(db, current_user.id)
        
        # 这里可以扩展返回更多详细信息
        # 例如已收集的数据概要、预计剩余时间等
        
        # 计算完成百分比
        completed_count = len(progress.get("completed_steps", []))
        total_steps = len(MAIN_FLOW_STEPS)
        completion_percentage = (completed_count / total_steps) * 100
        
        detailed_status = {
            **progress,
            "completion_percentage": completion_percentage,
            "total_steps": total_steps,
            "completed_count": completed_count,
            "remaining_steps": total_steps - completed_count
        }
        
        return detailed_status
    except Exception as e:
        logger.error(f"获取流程状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取流程状态失败")