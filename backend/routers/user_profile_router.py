from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from models.user_profile import UserPortrait, SymptomKnowledge, ConversationHistory, UserFlowState
from schemas.user_profile_schemas import (
    UserProfileInitializeRequest, UserProfileInitializeResponse,
    UserProfileProcessRequest, UserProfileProcessResponse,
    UserProfileSaveRequest, UserProfileSaveResponse,
    UserProfileResponse, SymptomKnowledgeResponse
)
from services.user_profile_service import UserProfileService
from services.knowledge_base_service import KnowledgeBaseService
from utils.database import get_db
from utils.security import get_current_user
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/user-profile", tags=["用户画像"])

# 移除全局初始化的用户画像服务，改为在每个路由中初始化


@router.post("/initialize", response_model=UserProfileInitializeResponse)
async def initialize_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    初始化用户画像收集流程
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 初始化用户画像服务
        user_profile_service = UserProfileService(db)
        response = await user_profile_service.initialize_profile(user_id)
        return response
    except Exception as e:
        logger.error(f"初始化用户画像失败: {str(e)}")
        raise HTTPException(status_code=500, detail="初始化用户画像失败")


@router.post("/process", response_model=UserProfileProcessResponse)
async def process_user_input(
    request: UserProfileProcessRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理用户输入，根据当前流程状态返回响应
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 初始化用户画像服务
        user_profile_service = UserProfileService(db)
        response = await user_profile_service.process_user_input(request, user_id)
        return response
    except Exception as e:
        logger.error(f"处理用户输入失败: {str(e)}")
        raise HTTPException(status_code=500, detail="处理用户输入失败")


@router.get("/", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户画像
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 查询用户画像
        profile = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="用户画像不存在")
        
        return UserProfileResponse(
            user_id=profile.user_id,
            basic_info=profile.basic_info,
            health_history=profile.health_history,
            lifestyle=profile.lifestyle,
            symptoms=profile.symptoms,
            medical_reports=profile.medical_reports,
            focus_areas=profile.focus_areas,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户画像失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户画像失败")


@router.post("/", response_model=UserProfileSaveResponse)
async def save_user_profile(
    request: UserProfileSaveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存用户画像
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 检查是否已有用户画像
        existing_profile = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        
        if existing_profile:
            # 更新现有画像
            existing_profile.basic_info = request.basic_info
            existing_profile.health_history = request.health_history
            existing_profile.lifestyle = request.lifestyle
            existing_profile.symptoms = request.symptoms
            existing_profile.medical_reports = request.medical_reports
            existing_profile.focus_areas = request.focus_areas
            existing_profile.updated_at = datetime.utcnow()
            db.commit()
            
            return UserProfileSaveResponse(
                success=True,
                message="用户画像更新成功",
                user_id=user_id
            )
        else:
            # 创建新画像
            new_profile = UserPortrait(
                user_id=user_id,
                basic_info=request.basic_info,
                health_history=request.health_history,
                lifestyle=request.lifestyle,
                symptoms=request.symptoms,
                medical_reports=request.medical_reports,
                focus_areas=request.focus_areas
            )
            db.add(new_profile)
            db.commit()
            
            return UserProfileSaveResponse(
                success=True,
                message="用户画像创建成功",
                user_id=user_id
            )
    except Exception as e:
        logger.error(f"保存用户画像失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="保存用户画像失败")


@router.get("/conversation-history")
async def get_conversation_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取对话历史
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 查询对话历史
        conversations = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id
        ).order_by(ConversationHistory.created_at).all()
        
        # 转换为字典列表
        history = []
        for conv in conversations:
            history.append({
                "id": conv.id,
                "message": conv.message,
                "sender": conv.sender,
                "main_step": conv.main_step,
                "sub_step": conv.sub_step,
                "is_ai_sub_process": conv.is_ai_sub_process,
                "extracted_entities": conv.extracted_entities,
                "response_data": conv.response_data,
                "created_at": conv.created_at
            })
        
        return {"history": history}
    except Exception as e:
        logger.error(f"获取对话历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取对话历史失败")


@router.delete("/conversation-history")
async def clear_conversation_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清除对话历史
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 删除对话历史
        db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id
        ).delete()
        
        # 重置用户流程状态
        flow_state = db.query(UserFlowState).filter(UserFlowState.user_id == user_id).first()
        if flow_state:
            flow_state.current_main_step = "basic_info"
            flow_state.current_sub_step = 0
            flow_state.is_ai_sub_process = False
            flow_state.temp_data = {}
            flow_state.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "对话历史已清除"}
    except Exception as e:
        logger.error(f"清除对话历史失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="清除对话历史失败")


@router.get("/symptom-knowledge")
async def get_symptom_knowledge(
    symptom: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取症状知识库
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        if symptom:
            # 查询特定症状
            symptom_info = db.query(SymptomKnowledge).filter(SymptomKnowledge.symptom == symptom).first()
            if not symptom_info:
                raise HTTPException(status_code=404, detail=f"症状 {symptom} 的知识不存在")
            
            return {
                "symptom": symptom_info.symptom,
                "description": symptom_info.description,
                "follow_up_questions": symptom_info.follow_up_questions,
                "related_symptoms": symptom_info.related_symptoms,
                "created_at": symptom_info.created_at,
                "updated_at": symptom_info.updated_at
            }
        else:
            # 查询所有症状
            symptoms = db.query(SymptomKnowledge).all()
            
            result = []
            for s in symptoms:
                result.append({
                    "symptom": s.symptom,
                    "description": s.description,
                    "follow_up_questions": s.follow_up_questions,
                    "related_symptoms": s.related_symptoms,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at
                })
            
            return {"symptoms": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取症状知识库失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取症状知识库失败")


@router.post("/symptom-knowledge")
async def create_symptom_knowledge(
    symptom: str,
    description: str,
    follow_up_questions: List[Dict[str, Any]],
    related_symptoms: List[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建症状知识库
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 检查症状是否已存在
        existing_symptom = db.query(SymptomKnowledge).filter(SymptomKnowledge.symptom == symptom).first()
        if existing_symptom:
            raise HTTPException(status_code=400, detail=f"症状 {symptom} 已存在")
        
        # 创建新症状知识
        new_symptom = SymptomKnowledge(
            symptom=symptom,
            description=description,
            follow_up_questions=follow_up_questions,
            related_symptoms=related_symptoms or []
        )
        db.add(new_symptom)
        db.commit()
        
        return {"message": f"症状 {symptom} 知识创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建症状知识库失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="创建症状知识库失败")


@router.put("/symptom-knowledge/{symptom}")
async def update_symptom_knowledge(
    symptom: str,
    description: str = None,
    follow_up_questions: List[Dict[str, Any]] = None,
    related_symptoms: List[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新症状知识库
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 查询症状
        symptom_info = db.query(SymptomKnowledge).filter(SymptomKnowledge.symptom == symptom).first()
        if not symptom_info:
            raise HTTPException(status_code=404, detail=f"症状 {symptom} 不存在")
        
        # 更新症状信息
        if description is not None:
            symptom_info.description = description
        if follow_up_questions is not None:
            symptom_info.follow_up_questions = follow_up_questions
        if related_symptoms is not None:
            symptom_info.related_symptoms = related_symptoms
        
        symptom_info.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"症状 {symptom} 知识更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新症状知识库失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="更新症状知识库失败")


@router.delete("/symptom-knowledge/{symptom}")
async def delete_symptom_knowledge(
    symptom: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除症状知识库
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 查询症状
        symptom_info = db.query(SymptomKnowledge).filter(SymptomKnowledge.symptom == symptom).first()
        if not symptom_info:
            raise HTTPException(status_code=404, detail=f"症状 {symptom} 不存在")
        
        # 删除症状
        db.delete(symptom_info)
        db.commit()
        
        return {"message": f"症状 {symptom} 知识删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除症状知识库失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="删除症状知识库失败")