from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
from sqlalchemy.orm import Session

from models.user_profile import UserPortrait, SymptomKnowledge, ConversationHistory, UserFlowState
from schemas.user_profile_schemas import (
    UserProfileProcessRequest, UserProfileProcessResponse, 
    UserProfileInitializeResponse, NLUResponse, NLUExtractedEntity
)
from services.knowledge_base_service import KnowledgeBaseService
from utils.logger import setup_logger
from utils.database import get_db

logger = setup_logger(__name__)


class UserProfileService:
    """
    用户画像服务类，实现主流程状态机和AI动态子流程逻辑
    """
    
    def __init__(self, db: Session):
        self.db = db
        # 初始化知识库服务
        self.knowledge_base = KnowledgeBaseService(db)
        
        # 主流程步骤定义
        self.main_steps = [
            {"id": "basic_info", "title": "基本信息", "required": True},
            {"id": "health_history", "title": "健康史", "required": False},
            {"id": "lifestyle", "title": "生活习惯", "required": False},
            {"id": "symptoms", "title": "不适症状", "required": False},
            {"id": "medical_reports", "title": "历史体检报告", "required": False},
            {"id": "focus_areas", "title": "重点关注", "required": False}
        ]
        
        # 基本信息字段定义
        self.basic_info_fields = [
            {"key": "name", "question": "请问您的姓名是？", "type": "text"},
            {"key": "age", "question": "请问您的年龄是？", "type": "number"},
            {"key": "gender", "question": "请问您的性别是？", "type": "choice", "options": ["男", "女"]},
            {"key": "height", "question": "请问您的身高是多少厘米？", "type": "number"},
            {"key": "weight", "question": "请问您的体重是多少公斤？", "type": "number"},
            {"key": "occupation", "question": "请问您的职业是？", "type": "text"},
            {"key": "phone", "question": "请问您的联系电话是？", "type": "text"},
            {"key": "email", "question": "请问您的邮箱是？", "type": "email"}
        ]
        
        # 健康史问题
        self.health_history_questions = [
            "您是否有既往病史？如果有，请告诉我是什么疾病，何时诊断的，目前治疗情况如何？",
            "您是否有长期服药的情况？如果有，请告诉我是什么药物，服用多久了？",
            "您是否有过敏史？如果有，请告诉我对什么过敏？"
        ]
        
        # 生活习惯问题
        self.lifestyle_questions = [
            {"key": "smoking", "question": "请问您有吸烟的习惯吗？", "type": "choice", "options": ["从不吸烟", "已戒烟", "偶尔吸烟", "经常吸烟"]},
            {"key": "drinking", "question": "请问您有饮酒的习惯吗？", "type": "choice", "options": ["从不饮酒", "偶尔饮酒", "经常饮酒", "每天饮酒"]},
            {"key": "exercise", "question": "请问您每周运动几次？", "type": "choice", "options": ["几乎不运动", "1-2次", "3-4次", "5次以上"]},
            {"key": "diet", "question": "请问您的饮食习惯如何？", "type": "choice", "options": ["非常规律健康", "比较规律", "不太规律", "很不规律"]},
            {"key": "sleep", "question": "请问您的睡眠质量如何？", "type": "choice", "options": ["很好", "较好", "一般", "较差", "很差"]},
            {"key": "stress", "question": "请问您的工作压力如何？", "type": "choice", "options": ["很小", "较小", "一般", "较大", "很大"]}
        ]
        
        # 症状关键词列表
        self.symptom_keywords = [
            "头痛", "头晕", "失眠", "疲劳", "乏力", "发热", "咳嗽", "咳痰", 
            "胸闷", "心悸", "气短", "腹痛", "腹胀", "恶心", "呕吐", "腹泻",
            "便秘", "尿频", "尿急", "尿痛", "关节痛", "肌肉痛", "皮肤瘙痒",
            "皮疹", "视力模糊", "耳鸣", "鼻塞", "流涕", "咽痛", "声音嘶哑"
        ]
    
    async def initialize_profile(self, user_id: int) -> UserProfileInitializeResponse:
        """
        初始化用户画像收集流程
        """
        # 获取或创建用户流程状态
        db = next(get_db())
        try:
            # 检查是否已有流程状态
            flow_state = db.query(UserFlowState).filter(UserFlowState.user_id == user_id).first()
            
            if flow_state:
                # 如果已有流程状态，重置到开始
                flow_state.current_main_step = "basic_info"
                flow_state.current_sub_step = 0
                flow_state.is_ai_sub_process = False
                flow_state.temp_data = {}
                flow_state.updated_at = datetime.utcnow()
                db.commit()
            else:
                # 创建新的流程状态
                flow_state = UserFlowState(
                    user_id=user_id,
                    current_main_step="basic_info",
                    current_sub_step=0,
                    is_ai_sub_process=False,
                    temp_data={}
                )
                db.add(flow_state)
                db.commit()
            
            # 返回初始欢迎消息
            return UserProfileInitializeResponse(
                message="您好！我是您的健康助手，接下来我将通过几个步骤了解您的基本情况，以便为您提供更精准的健康建议。我们先从基本信息开始，请问您的姓名是？",
                step_type="text"
            )
        finally:
            db.close()
    
    async def process_user_input(self, request: UserProfileProcessRequest, user_id: int) -> UserProfileProcessResponse:
        """
        处理用户输入，根据当前流程状态返回响应
        """
        db = next(get_db())
        try:
            # 获取用户流程状态
            flow_state = db.query(UserFlowState).filter(UserFlowState.user_id == user_id).first()
            if not flow_state:
                # 如果没有流程状态，初始化一个
                return await self.initialize_profile(user_id)
            
            # 保存对话历史
            conversation = ConversationHistory(
                user_id=user_id,
                message=request.user_input,
                sender="user",
                main_step=request.main_step,
                sub_step=request.sub_step,
                is_ai_sub_process=request.is_ai_sub_process
            )
            db.add(conversation)
            
            # 根据当前流程状态处理用户输入
            if request.is_ai_sub_process:
                # AI动态子流程处理
                response = await self._process_ai_sub_process(request, flow_state, db)
            else:
                # 主流程处理
                response = await self._process_main_flow(request, flow_state, db)
            
            # 更新流程状态
            db.commit()
            
            # 保存AI回复到对话历史
            ai_conversation = ConversationHistory(
                user_id=user_id,
                message=response.message,
                sender="ai",
                main_step=flow_state.current_main_step,
                sub_step=flow_state.current_sub_step,
                is_ai_sub_process=flow_state.is_ai_sub_process,
                extracted_entities=response.extracted_entities,
                response_data=response.dict()
            )
            db.add(ai_conversation)
            db.commit()
            
            return response
        except Exception as e:
            logger.error(f"处理用户输入失败: {str(e)}")
            db.rollback()
            return UserProfileProcessResponse(
                message="抱歉，处理您的输入时出现了问题，请稍后再试。",
                step_type="text",
                next_step=request.sub_step
            )
        finally:
            db.close()
    
    async def _process_main_flow(self, request: UserProfileProcessRequest, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理主流程
        """
        current_step = request.main_step
        sub_step = request.sub_step
        user_input = request.user_input
        
        # 根据当前步骤处理
        if current_step == "basic_info":
            return await self._process_basic_info(user_input, sub_step, flow_state, db)
        elif current_step == "health_history":
            return await self._process_health_history(user_input, sub_step, flow_state, db)
        elif current_step == "lifestyle":
            return await self._process_lifestyle(user_input, sub_step, flow_state, db)
        elif current_step == "symptoms":
            return await self._process_symptoms(user_input, sub_step, flow_state, db)
        elif current_step == "medical_reports":
            return await self._process_medical_reports(user_input, sub_step, flow_state, db)
        elif current_step == "focus_areas":
            return await self._process_focus_areas(user_input, sub_step, flow_state, db)
        else:
            # 未知步骤，完成流程
            return await self._complete_profile(flow_state, db)
    
    async def _process_basic_info(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理基本信息步骤
        """
        # 获取当前字段
        if sub_step < len(self.basic_info_fields):
            current_field = self.basic_info_fields[sub_step]
            field_key = current_field["key"]
            
            # 验证并保存用户输入
            validated_value = await self._validate_field_input(user_input, current_field)
            
            # 更新临时数据
            if not flow_state.temp_data:
                flow_state.temp_data = {}
            if "basic_info" not in flow_state.temp_data:
                flow_state.temp_data["basic_info"] = {}
            
            flow_state.temp_data["basic_info"][field_key] = validated_value
            
            # 准备下一个问题
            next_sub_step = sub_step + 1
            if next_sub_step < len(self.basic_info_fields):
                next_field = self.basic_info_fields[next_sub_step]
                next_question = next_field["question"]
                
                # 更新流程状态
                flow_state.current_sub_step = next_sub_step
                
                # 返回下一个问题
                if next_field["type"] == "choice":
                    return UserProfileProcessResponse(
                        message=next_question,
                        step_type="multiple-choice",
                        options=[{"text": option, "value": option} for option in next_field["options"]],
                        next_step=next_sub_step,
                        profile_update={"basic_info": flow_state.temp_data.get("basic_info", {})}
                    )
                else:
                    return UserProfileProcessResponse(
                        message=next_question,
                        step_type="text",
                        next_step=next_sub_step,
                        profile_update={"basic_info": flow_state.temp_data.get("basic_info", {})}
                    )
            else:
                # 基本信息收集完成，进入下一步
                flow_state.current_main_step = "health_history"
                flow_state.current_sub_step = 0
                
                return UserProfileProcessResponse(
                    message="基本信息已收集完成。接下来，我想了解一下您的健康史。您是否有既往病史？如果有，请告诉我是什么疾病，何时诊断的，目前治疗情况如何？",
                    step_type="text",
                    next_step="next_main",
                    profile_update={"basic_info": flow_state.temp_data.get("basic_info", {})}
                )
        else:
            # 基本信息已收集完成，进入下一步
            flow_state.current_main_step = "health_history"
            flow_state.current_sub_step = 0
            
            return UserProfileProcessResponse(
                message="基本信息已收集完成。接下来，我想了解一下您的健康史。您是否有既往病史？如果有，请告诉我是什么疾病，何时诊断的，目前治疗情况如何？",
                step_type="text",
                next_step="next_main",
                profile_update={"basic_info": flow_state.temp_data.get("basic_info", {})}
            )
    
    async def _process_health_history(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理健康史步骤
        """
        # 保存用户输入
        if not flow_state.temp_data:
            flow_state.temp_data = {}
        if "health_history" not in flow_state.temp_data:
            flow_state.temp_data["health_history"] = []
        
        # 如果用户提供了健康史信息，添加到列表中
        if user_input.strip() and not user_input.lower() in ["没有", "无", "没有病史", "无病史"]:
            flow_state.temp_data["health_history"].append(user_input)
        
        # 准备下一个问题
        next_sub_step = sub_step + 1
        if next_sub_step < len(self.health_history_questions):
            next_question = self.health_history_questions[next_sub_step]
            
            # 更新流程状态
            flow_state.current_sub_step = next_sub_step
            
            return UserProfileProcessResponse(
                message=next_question,
                step_type="text",
                next_step=next_sub_step,
                profile_update={"health_history": flow_state.temp_data.get("health_history", [])}
            )
        else:
            # 健康史收集完成，进入下一步
            flow_state.current_main_step = "lifestyle"
            flow_state.current_sub_step = 0
            
            return UserProfileProcessResponse(
                message="感谢您的分享。接下来，我想了解一下您的生活习惯。请问您有吸烟的习惯吗？",
                step_type="multiple-choice",
                options=[{"text": "从不吸烟", "value": "从不吸烟"}, 
                         {"text": "已戒烟", "value": "已戒烟"},
                         {"text": "偶尔吸烟", "value": "偶尔吸烟"},
                         {"text": "经常吸烟", "value": "经常吸烟"}],
                next_step="next_main",
                profile_update={"health_history": flow_state.temp_data.get("health_history", [])}
            )
    
    async def _process_lifestyle(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理生活习惯步骤
        """
        # 获取当前问题
        if sub_step < len(self.lifestyle_questions):
            current_question = self.lifestyle_questions[sub_step]
            field_key = current_question["key"]
            
            # 验证并保存用户输入
            validated_value = await self._validate_field_input(user_input, current_question)
            
            # 更新临时数据
            if not flow_state.temp_data:
                flow_state.temp_data = {}
            if "lifestyle" not in flow_state.temp_data:
                flow_state.temp_data["lifestyle"] = {}
            
            flow_state.temp_data["lifestyle"][field_key] = validated_value
            
            # 准备下一个问题
            next_sub_step = sub_step + 1
            if next_sub_step < len(self.lifestyle_questions):
                next_question = self.lifestyle_questions[next_sub_step]
                next_question_text = next_question["question"]
                
                # 更新流程状态
                flow_state.current_sub_step = next_sub_step
                
                # 返回下一个问题
                if next_question["type"] == "choice":
                    return UserProfileProcessResponse(
                        message=next_question_text,
                        step_type="multiple-choice",
                        options=[{"text": option, "value": option} for option in next_question["options"]],
                        next_step=next_sub_step,
                        profile_update={"lifestyle": flow_state.temp_data.get("lifestyle", {})}
                    )
                else:
                    return UserProfileProcessResponse(
                        message=next_question_text,
                        step_type="text",
                        next_step=next_sub_step,
                        profile_update={"lifestyle": flow_state.temp_data.get("lifestyle", {})}
                    )
            else:
                # 生活习惯收集完成，进入下一步
                flow_state.current_main_step = "symptoms"
                flow_state.current_sub_step = 0
                
                return UserProfileProcessResponse(
                    message="生活习惯信息已收集完成。接下来，我想了解一下您是否有任何不适症状？请告诉我您最近是否有感到不舒服的地方，比如头痛、头晕、胃痛等？",
                    step_type="text",
                    next_step="next_main",
                    profile_update={"lifestyle": flow_state.temp_data.get("lifestyle", {})}
                )
        else:
            # 生活习惯已收集完成，进入下一步
            flow_state.current_main_step = "symptoms"
            flow_state.current_sub_step = 0
            
            return UserProfileProcessResponse(
                message="生活习惯信息已收集完成。接下来，我想了解一下您是否有任何不适症状？请告诉我您最近是否有感到不舒服的地方，比如头痛、头晕、胃痛等？",
                step_type="text",
                next_step="next_main",
                profile_update={"lifestyle": flow_state.temp_data.get("lifestyle", {})}
            )
    
    async def _process_symptoms(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理不适症状步骤
        """
        # 检查用户是否提到了症状
        symptoms_found = await self._extract_symptoms(user_input)
        
        if symptoms_found:
            # 有症状，进入AI动态子流程
            flow_state.is_ai_sub_process = True
            flow_state.temp_data = flow_state.temp_data or {}
            flow_state.temp_data["current_symptom"] = symptoms_found[0]  # 取第一个症状进行深入询问
            
            # 获取症状的追问问题
            symptom = symptoms_found[0]
            follow_up_questions = await self._get_symptom_follow_up_questions(symptom, db)
            
            if follow_up_questions:
                # 返回第一个追问问题
                first_question = follow_up_questions[0]["question"]
                flow_state.temp_data["current_question_index"] = 0
                flow_state.temp_data["symptom_data"] = {"symptom_name": symptom}
                
                return UserProfileProcessResponse(
                    message=f"您提到了{symptom}，{first_question}",
                    step_type="text",
                    next_step="ai_sub_process",
                    profile_update={},
                    extracted_entities={"symptom": symptom}
                )
            else:
                # 没有找到追问问题，使用默认问题
                flow_state.temp_data["symptom_data"] = {"symptom_name": symptom}
                
                return UserProfileProcessResponse(
                    message=f"您提到了{symptom}，请问这种情况持续多久了？",
                    step_type="text",
                    next_step="ai_sub_process",
                    profile_update={},
                    extracted_entities={"symptom": symptom}
                )
        else:
            # 没有症状，询问是否还有其他症状
            if sub_step == 0:
                return UserProfileProcessResponse(
                    message="好的，请问您还有其他不适症状吗？如果没有，请告诉我\"没有\"。",
                    step_type="text",
                    next_step=sub_step + 1
                )
            elif user_input.lower() in ["没有", "无", "没有其他症状", "没有不适"]:
                # 没有其他症状，进入下一步
                flow_state.current_main_step = "medical_reports"
                flow_state.current_sub_step = 0
                
                return UserProfileProcessResponse(
                    message="好的，了解了。接下来，我想了解一下您的历史体检报告情况。您最近一次体检是什么时候？有没有异常指标？",
                    step_type="text",
                    next_step="next_main"
                )
            else:
                # 用户可能提到了症状，再次尝试提取
                symptoms_found = await self._extract_symptoms(user_input)
                if symptoms_found:
                    # 有症状，进入AI动态子流程
                    flow_state.is_ai_sub_process = True
                    flow_state.temp_data = flow_state.temp_data or {}
                    flow_state.temp_data["current_symptom"] = symptoms_found[0]
                    
                    return UserProfileProcessResponse(
                        message=f"您提到了{symptoms_found[0]}，请问这种情况持续多久了？",
                        step_type="text",
                        next_step="ai_sub_process",
                        profile_update={},
                        extracted_entities={"symptom": symptoms_found[0]}
                    )
                else:
                    # 仍然没有检测到症状，继续询问
                    return UserProfileProcessResponse(
                        message="抱歉，我没有理解您的症状。请用更简单的方式描述您的不适，比如\"头痛\"、\"胃痛\"等，或者告诉我\"没有\"。",
                        step_type="text",
                        next_step=sub_step
                    )
    
    async def _process_medical_reports(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理历史体检报告步骤
        """
        # 保存用户输入
        if not flow_state.temp_data:
            flow_state.temp_data = {}
        if "medical_reports" not in flow_state.temp_data:
            flow_state.temp_data["medical_reports"] = []
        
        # 如果用户提供了体检报告信息，添加到列表中
        if user_input.strip() and not user_input.lower() in ["没有", "无", "没有体检报告", "无体检报告"]:
            flow_state.temp_data["medical_reports"].append(user_input)
        
        # 询问是否还有其他体检报告
        if sub_step == 0:
            return UserProfileProcessResponse(
                message="好的，请问还有其他体检报告需要分享吗？如果没有，请告诉我\"没有\"。",
                step_type="text",
                next_step=sub_step + 1,
                profile_update={"medical_reports": flow_state.temp_data.get("medical_reports", [])}
            )
        elif user_input.lower() in ["没有", "无", "没有其他报告", "没有其他体检报告"]:
            # 没有其他报告，进入下一步
            flow_state.current_main_step = "focus_areas"
            flow_state.current_sub_step = 0
            
            return UserProfileProcessResponse(
                message="好的，了解了。最后，我想了解一下您特别关注的健康领域。比如您是否特别关注心脏健康、血糖、血压或者其他方面？",
                step_type="text",
                next_step="next_main",
                profile_update={"medical_reports": flow_state.temp_data.get("medical_reports", [])}
            )
        else:
            # 用户提供了更多报告信息
            flow_state.temp_data["medical_reports"].append(user_input)
            
            return UserProfileProcessResponse(
                message="好的，已记录。请问还有其他体检报告需要分享吗？如果没有，请告诉我\"没有\"。",
                step_type="text",
                next_step=sub_step,
                profile_update={"medical_reports": flow_state.temp_data.get("medical_reports", [])}
            )
    
    async def _process_focus_areas(self, user_input: str, sub_step: int, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理重点关注步骤
        """
        # 保存用户输入
        if not flow_state.temp_data:
            flow_state.temp_data = {}
        if "focus_areas" not in flow_state.temp_data:
            flow_state.temp_data["focus_areas"] = []
        
        # 如果用户提供了关注领域，添加到列表中
        if user_input.strip() and not user_input.lower() in ["没有", "无", "没有特别关注", "无特别关注"]:
            flow_state.temp_data["focus_areas"].append(user_input)
        
        # 询问是否还有其他关注领域
        if sub_step == 0:
            return UserProfileProcessResponse(
                message="好的，请问还有其他您特别关注的健康领域吗？如果没有，请告诉我\"没有\"。",
                step_type="text",
                next_step=sub_step + 1,
                profile_update={"focus_areas": flow_state.temp_data.get("focus_areas", [])}
            )
        elif user_input.lower() in ["没有", "无", "没有其他关注", "没有其他关注领域"]:
            # 没有其他关注领域，完成流程
            return await self._complete_profile(flow_state, db)
        else:
            # 用户提供了更多关注领域
            flow_state.temp_data["focus_areas"].append(user_input)
            
            return UserProfileProcessResponse(
                message="好的，已记录。请问还有其他您特别关注的健康领域吗？如果没有，请告诉我\"没有\"。",
                step_type="text",
                next_step=sub_step,
                profile_update={"focus_areas": flow_state.temp_data.get("focus_areas", [])}
            )
    
    async def _process_ai_sub_process(self, request: UserProfileProcessRequest, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        处理AI动态子流程
        """
        user_input = request.user_input
        current_symptom = flow_state.temp_data.get("current_symptom")
        current_question_index = flow_state.temp_data.get("current_question_index", 0)
        symptom_data = flow_state.temp_data.get("symptom_data", {})
        
        # 使用知识库服务处理用户回答
        if symptom_data:
            symptom_data = self.knowledge_base.process_symptom_response(
                current_symptom, user_input, symptom_data
            )
        
        flow_state.temp_data["symptom_data"] = symptom_data
        
        # 使用知识库服务获取下一个问题
        follow_up_questions = self.knowledge_base.generate_follow_up_questions(current_symptom, user_input)
        
        if follow_up_questions and current_question_index < len(follow_up_questions):
            # 还有更多问题
            next_question = follow_up_questions[current_question_index].question
            flow_state.temp_data["current_question_index"] = current_question_index + 1
            
            return UserProfileProcessResponse(
                message=next_question,
                step_type="text",
                next_step="ai_sub_process",
                profile_update={}
            )
        else:
            # 没有更多问题，完成症状收集
            # 将症状数据添加到用户画像中
            if not flow_state.temp_data.get("symptoms"):
                flow_state.temp_data["symptoms"] = []
            
            flow_state.temp_data["symptoms"].append(symptom_data)
            
            # 重置AI子流程状态
            flow_state.is_ai_sub_process = False
            flow_state.temp_data["current_symptom"] = None
            flow_state.temp_data["current_question_index"] = 0
            flow_state.temp_data["symptom_data"] = {}
            
            # 返回主流程
            return UserProfileProcessResponse(
                message=f"好的，已了解您的{current_symptom}情况。请问您还有其他不适症状吗？如果没有，请告诉我\"没有\"。",
                step_type="text",
                next_step="next_main",
                profile_update={"symptoms": flow_state.temp_data.get("symptoms", [])}
            )
    
    async def _complete_profile(self, flow_state: UserFlowState, db) -> UserProfileProcessResponse:
        """
        完成用户画像收集
        """
        # 保存用户画像到数据库
        user_id = flow_state.user_id
        profile_data = {}
        
        # 从临时数据中提取各部分数据
        temp_data = flow_state.temp_data or {}
        if "basic_info" in temp_data:
            profile_data["basic_info"] = temp_data["basic_info"]
        if "health_history" in temp_data:
            profile_data["health_history"] = temp_data["health_history"]
        if "lifestyle" in temp_data:
            profile_data["lifestyle"] = temp_data["lifestyle"]
        if "symptoms" in temp_data:
            profile_data["symptoms"] = temp_data["symptoms"]
        if "medical_reports" in temp_data:
            profile_data["medical_reports"] = temp_data["medical_reports"]
        if "focus_areas" in temp_data:
            profile_data["focus_areas"] = temp_data["focus_areas"]
        
        # 检查是否已有用户画像
        existing_profile = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        if existing_profile:
            # 更新现有画像
            existing_profile.basic_info = profile_data.get("basic_info")
            existing_profile.health_history = profile_data.get("health_history")
            existing_profile.lifestyle = profile_data.get("lifestyle")
            existing_profile.symptoms = profile_data.get("symptoms")
            existing_profile.medical_reports = profile_data.get("medical_reports")
            existing_profile.focus_areas = profile_data.get("focus_areas")
            existing_profile.updated_at = datetime.utcnow()
        else:
            # 创建新画像
            new_profile = UserPortrait(
                user_id=user_id,
                basic_info=profile_data.get("basic_info"),
                health_history=profile_data.get("health_history"),
                lifestyle=profile_data.get("lifestyle"),
                symptoms=profile_data.get("symptoms"),
                medical_reports=profile_data.get("medical_reports"),
                focus_areas=profile_data.get("focus_areas")
            )
            db.add(new_profile)
        
        # 重置流程状态
        flow_state.current_main_step = "basic_info"
        flow_state.current_sub_step = 0
        flow_state.is_ai_sub_process = False
        flow_state.temp_data = {}
        flow_state.updated_at = datetime.utcnow()
        
        db.commit()
        
        return UserProfileProcessResponse(
            message="感谢您的配合，您的用户画像已收集完成！这些信息将帮助我们为您提供更精准的健康建议。",
            step_type="text",
            next_step="complete",
            profile_update=profile_data
        )
    
    async def _validate_field_input(self, user_input: str, field_config: dict) -> str:
        """
        验证字段输入
        """
        field_type = field_config.get("type", "text")
        
        if field_type == "number":
            # 尝试转换为数字
            try:
                return str(float(user_input))
            except ValueError:
                return user_input  # 如果转换失败，返回原始输入
        elif field_type == "email":
            # 简单的邮箱验证
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, user_input):
                return user_input
            else:
                return user_input  # 如果验证失败，返回原始输入
        else:
            # 文本类型，直接返回
            return user_input
    
    async def _extract_symptoms(self, text: str) -> List[str]:
        """
        从文本中提取症状
        """
        # 使用知识库服务提取症状实体
        symptom_entities = self.knowledge_base.extract_symptom_entities(text)
        
        # 提取症状名称
        symptoms_found = [entity.symptom for entity in symptom_entities]
        
        return symptoms_found
    
    async def _get_symptom_follow_up_questions(self, symptom: str, db) -> List[dict]:
        """
        获取症状的追问问题
        """
        # 从数据库中查询症状知识
        symptom_knowledge = db.query(SymptomKnowledge).filter(SymptomKnowledge.symptom == symptom).first()
        
        if symptom_knowledge and symptom_knowledge.follow_up_questions:
            return symptom_knowledge.follow_up_questions
        
        # 如果数据库中没有，返回默认问题
        default_questions = [
            {"question": f"请问您的{symptom}是什么性质的？比如是刺痛、胀痛还是其他感觉？"},
            {"question": f"请问您的{symptom}多久出现一次？"},
            {"question": f"请问您的{symptom}持续多久了？"},
            {"question": f"请问在什么情况下容易出现{symptom}？"}
        ]
        
        return default_questions