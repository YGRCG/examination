from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from models.user import User
from models.user_profile import UserPortrait, SymptomKnowledge, ConversationHistory, UserFlowState
from schemas.user_profile_schemas import (
    UserProfileInitializeRequest, UserProfileInitializeResponse,
    UserProfileProcessRequest, UserProfileProcessResponse,
    UserProfileSaveRequest, UserProfileSaveResponse,
    UserProfileResponse, SymptomKnowledgeResponse
)
from schemas.user_schemas import ApiResponse
from services.user_profile_service import UserProfileService
from services.knowledge_base_service import KnowledgeBaseService
from utils.database import get_db
from utils.security import get_current_user
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/user-profile", tags=["用户画像"])

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


@router.get("/")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户画像
    """
    try:
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 首先尝试从user_portraits表获取数据
        from models.user_profile import UserPortrait
        portrait = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        
        if portrait:
            # 如果有画像数据，直接返回
            user_profile = UserProfileResponse(
                user_id=user_id,
                basic_info=portrait.basic_info,
                health_history=portrait.health_history,
                lifestyle=portrait.lifestyle,
                symptoms=portrait.symptoms,
                medical_reports=portrait.medical_reports,
                focus_areas=portrait.focus_areas
            )
            return ApiResponse.success(data=user_profile.model_dump(), message="获取用户画像成功")
        
        # 如果没有画像数据，尝试从其他表聚合数据
        from models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 尝试从user_profiles表获取数据
        profile = None
        try:
            from models.user import UserProfile
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        except:
            pass
        
        # 构造basic_info
        basic_info = {
            "name": user.username,
            "age": profile.age if profile else None,
            "gender": profile.gender if profile else None,
            "marital_status": profile.marital_status if profile else None,
            "height": float(profile.height) if profile and profile.height else None,
            "weight": float(profile.weight) if profile and profile.weight else None
        }
        
        # 构造health_history - 改为列表格式以符合模型定义
        health_history = []
        if profile:
            if profile.allergies:
                health_history.append({"type": "allergies", "value": profile.allergies})
            if profile.chronic_diseases:
                health_history.append({"type": "chronic_diseases", "value": profile.chronic_diseases})
            if profile.surgeries:
                health_history.append({"type": "surgeries", "value": profile.surgeries})
            if profile.family_medical_history:
                health_history.append({"type": "family_medical_history", "value": profile.family_medical_history})
        
        # 构造lifestyle
        lifestyle = {
            "smoking_status": profile.smoking_status if profile else None,
            "drinking_status": profile.drinking_status if profile else None,
            "exercise_habits": profile.exercise_habits if profile else None,
            "sleep_quality": profile.sleep_quality if profile else None
        }
        
        # 尝试从user_symptoms表获取症状数据
        symptoms = []
        try:
            from models.user_symptom import UserSymptom
            user_symptoms = db.query(UserSymptom).filter(UserSymptom.user_id == user_id).all()
            for symptom in user_symptoms:
                symptoms.append({
                    "symptom": symptom.symptom,
                    "description": symptom.description,
                    "duration": symptom.duration,
                    "severity": symptom.severity
                })
        except:
            pass
        
        # 尝试从medical_reports表获取体检报告数据
        medical_reports = []
        try:
            from models.medical_report import MedicalReport
            reports = db.query(MedicalReport).filter(MedicalReport.user_id == user_id).all()
            for report in reports:
                medical_reports.append({
                    "report_type": report.report_type,
                    "report_date": report.report_date,
                    "hospital": report.hospital,
                    "summary": report.summary,
                    "details": report.details
                })
        except:
            pass
        
        # 构造focus_areas
        focus_areas = []
        if symptoms:
            focus_areas.append("症状管理")
        if medical_reports:
            focus_areas.append("体检报告解读")
        
        # 检查health_history列表中是否有慢性病
        has_chronic_diseases = False
        for item in health_history:
            if item.get("type") == "chronic_diseases" and item.get("value"):
                has_chronic_diseases = True
                break
        
        if has_chronic_diseases:
            focus_areas.append("慢性病管理")
            
        if lifestyle.get("smoking_status") == "吸烟" or lifestyle.get("drinking_status") == "饮酒":
            focus_areas.append("生活习惯改善")
        
        user_profile = UserProfileResponse(
            user_id=user_id,
            basic_info=basic_info,
            health_history=health_history,
            lifestyle=lifestyle,
            symptoms=symptoms,
            medical_reports=medical_reports,
            focus_areas=focus_areas
        )
        
        return ApiResponse.success(data=user_profile.model_dump(), message="获取用户画像成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户画像失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户画像失败")


@router.post("/")
async def save_user_profile(
    request: UserProfileSaveRequest,
    current_user: User = Depends(get_current_user),
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
            
            return ApiResponse.success(data={"user_id": user_id}, message="用户画像更新成功")
        else:
            # 创建新画像
            new_profile = UserPortrait(
                user_id=user_id,
                basic_info=request.basic_info,
                health_history=request.health_history,
                lifestyle=request.lifestyle,
                symptoms=request.symptoms,
                medical_reports=request.medical_reports,
                focus_areas=request.focus_areas,
                health_risk="未评估",
                recommended_frequency="每年一次",
                generated_at=datetime.utcnow()
            )
            db.add(new_profile)
            db.commit()
            
            return ApiResponse.success(data={"user_id": user_id}, message="用户画像创建成功")
    except Exception as e:
        logger.error(f"保存用户画像失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="保存用户画像失败")


@router.get("/conversation-history")
async def get_conversation_history(
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清除对话历史
    """
    try:
        user_id = current_user.id
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取症状知识库
    """
    try:
        user_id = current_user.id
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建症状知识库
    """
    try:
        user_id = current_user.id
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新症状知识库
    """
    try:
        user_id = current_user.id
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除症状知识库
    """
    try:
        user_id = current_user.id
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