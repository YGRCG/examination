from sqlalchemy.orm import Session
from datetime import datetime
import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any

from models import User, UserProfile, HealthInfo, MedicalReport, UserPortrait, UserSymptom, QuestionnaireProgress
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.user_portrait")

# 主流程步骤定义
MAIN_FLOW_STEPS = [
    "basic_info",      # 基本信息（必填）
    "health_history",  # 健康史（重要可选）
    "lifestyle",       # 生活习惯（可选）
    "symptoms",        # 不适症状（可选）
    "medical_reports", # 历史体检报告（可选）
    "concerns"         # 重点关注（可选）
]

# 症状知识包 - 用于动态追问
SYMPTOM_QUESTIONNAIRES = {
    "头晕": [
        "请问是眩晕（感觉天旋地转）还是昏沉（感觉头重脚轻）？",
        "这种情况持续多久了？",
        "在什么情况下容易诱发（比如起床、转头时）？"
    ],
    "头痛": [
        "是胀痛、刺痛还是搏动性疼痛？",
        "通常在什么部位疼痛？",
        "疼痛程度如何（轻微、中等、严重）？"
    ],
    "胃痛": [
        "是胀痛、刺痛还是反酸？",
        "通常是在饭前还是饭后出现？",
        "是否伴有恶心、没胃口？"
    ],
    "胸闷": [
        "是持续性的还是阵发性的？",
        "是否伴有呼吸困难或心悸？",
        "在什么情况下会加重？"
    ],
    "乏力": [
        "是全身乏力还是某个部位？",
        "早晨起床时更严重还是全天都一样？",
        "最近是否有过度劳累或压力过大？"
    ],
    "失眠": [
        "入睡困难还是容易醒？",
        "通常几点上床，几点能入睡？",
        "是否有焦虑或压力大的情况？"
    ]
}

# 默认的通用症状追问
DEFAULT_SYMPTOM_QUESTIONS = [
    "这种症状持续多久了？",
    "频率如何（偶尔、经常、每天）？",
    "有什么加重或缓解的因素吗？"
]

class UserPortraitFlowService:
    """用户画像生成流程服务"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.progress = self._get_or_create_progress()
    
    def _get_or_create_progress(self) -> QuestionnaireProgress:
        """获取或创建问卷进度"""
        progress = self.db.query(QuestionnaireProgress).filter(
            QuestionnaireProgress.user_id == self.user_id
        ).first()
        
        if not progress:
            progress = QuestionnaireProgress(
                user_id=self.user_id,
                current_step=MAIN_FLOW_STEPS[0],
                completed_steps=[],
                session_data={}
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        
        return progress
    
    def _update_progress(self, **kwargs) -> None:
        """更新进度信息"""
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        
        self.progress.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(self.progress)
    
    def get_current_step(self) -> str:
        """获取当前步骤"""
        return self.progress.current_step
    
    def get_completed_steps(self) -> List[str]:
        """获取已完成步骤"""
        return self.progress.completed_steps or []
    
    def _extract_symptom_entities(self, text: str) -> Dict[str, str]:
        """
        NLU - 从用户文本中提取症状实体
        简单实现：基于关键词匹配和规则提取
        """
        entities = {}
        
        # 提取症状名称（简化版，实际应用需要更复杂的NLP模型）
        symptom_keywords = list(SYMPTOM_QUESTIONNAIRES.keys())
        matched_symptom = None
        
        for symptom in symptom_keywords:
            if symptom in text:
                matched_symptom = symptom
                break
        
        if not matched_symptom:
            # 尝试从文本中提取可能的症状
            symptom_pattern = re.compile(r'最近\w*(头晕|头痛|胃痛|胸闷|乏力|失眠|不适|难受|疼痛|异常)\w*')
            match = symptom_pattern.search(text)
            if match:
                matched_symptom = match.group(1)
        
        entities["symptom"] = matched_symptom
        
        # 提取频率
        frequency_patterns = {
            "经常": re.compile(r'经常|频繁|总是|常常'),
            "偶尔": re.compile(r'偶尔|有时|时不时'),
            "持续": re.compile(r'持续|一直|不断'),
            "最近": re.compile(r'最近|近\w*天|这几天')
        }
        
        for freq, pattern in frequency_patterns.items():
            if pattern.search(text):
                entities["frequency"] = freq
                break
        
        # 提取严重程度
        severity_patterns = {
            "严重": re.compile(r'严重|很|非常|厉害'),
            "中等": re.compile(r'一般|中等|有点'),
            "轻微": re.compile(r'轻微|稍微|不太')
        }
        
        for severity, pattern in severity_patterns.items():
            if pattern.search(text):
                entities["severity"] = severity
                break
        
        return entities
    
    def _get_symptom_questions(self, symptom: str) -> List[str]:
        """获取特定症状的追问问题"""
        return SYMPTOM_QUESTIONNAIRES.get(symptom, DEFAULT_SYMPTOM_QUESTIONS)
    
    def process_main_flow_step(self, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理主流程步骤"""
        # 保存当前步骤的数据
        session_data = self.progress.session_data or {}
        session_data[step] = data
        
        # 检查是否是症状步骤，需要特殊处理
        if step == "symptoms" and data.get("has_symptoms", False):
            # 进入AI动态子流程
            self._update_progress(
                current_state="symptom_dynamic",
                session_data=session_data
            )
            
            # 提取症状实体
            user_description = data.get("description", "")
            entities = self._extract_symptom_entities(user_description)
            
            # 如果识别到症状，初始化动态追问
            if entities.get("symptom"):
                symptom_data = {
                    "symptom": entities["symptom"],
                    "frequency": entities.get("frequency"),
                    "severity": entities.get("severity"),
                    "questions": self._get_symptom_questions(entities["symptom"]),
                    "current_question_index": 0,
                    "answers": {}
                }
                session_data["symptom_dynamic"] = symptom_data
                self._update_progress(session_data=session_data)
                
                return {
                    "next_action": "dynamic_question",
                    "question": symptom_data["questions"][0],
                    "step": "symptoms"
                }
        
        # 更新完成步骤
        completed_steps = self.get_completed_steps()
        if step not in completed_steps:
            completed_steps.append(step)
        
        # 确定下一步
        current_index = MAIN_FLOW_STEPS.index(step)
        if current_index < len(MAIN_FLOW_STEPS) - 1:
            next_step = MAIN_FLOW_STEPS[current_index + 1]
        else:
            next_step = "complete"
        
        self._update_progress(
            current_step=next_step,
            completed_steps=completed_steps,
            current_state="normal",
            session_data=session_data
        )
        
        if next_step == "complete":
            # 生成最终用户画像
            user_portrait = self.generate_final_user_portrait(session_data)
            return {
                "next_action": "complete",
                "message": "用户画像生成完成",
                "portrait_id": user_portrait.id
            }
        else:
            return {
                "next_action": "next_step",
                "next_step": next_step,
                "completed_steps": completed_steps
            }
    
    def process_dynamic_question(self, answer: str) -> Dict[str, Any]:
        """处理动态追问"""
        session_data = self.progress.session_data or {}
        symptom_dynamic = session_data.get("symptom_dynamic")
        
        if not symptom_dynamic:
            raise CustomException(
                status_code=400,
                message="未找到动态追问状态",
                error_type="DynamicQuestionError"
            )
        
        # 保存当前问题的答案
        current_index = symptom_dynamic["current_question_index"]
        current_question = symptom_dynamic["questions"][current_index]
        symptom_dynamic["answers"][current_question] = answer
        
        # 检查是否还有下一个问题
        if current_index < len(symptom_dynamic["questions"]) - 1:
            # 继续追问
            symptom_dynamic["current_question_index"] += 1
            next_question = symptom_dynamic["questions"][symptom_dynamic["current_question_index"]]
            self._update_progress(session_data=session_data)
            
            return {
                "next_action": "dynamic_question",
                "question": next_question,
                "step": "symptoms"
            }
        else:
            # 动态追问结束，保存症状信息到数据库
            self._save_symptom_data(symptom_dynamic)
            
            # 退出动态流程，继续主流程
            step = "symptoms"
            completed_steps = self.get_completed_steps()
            if step not in completed_steps:
                completed_steps.append(step)
            
            # 确定下一步
            current_index = MAIN_FLOW_STEPS.index(step)
            next_step = MAIN_FLOW_STEPS[current_index + 1]
            
            self._update_progress(
                current_step=next_step,
                completed_steps=completed_steps,
                current_state="normal",
                session_data=session_data
            )
            
            return {
                "next_action": "next_step",
                "next_step": next_step,
                "completed_steps": completed_steps
            }
    
    def _save_symptom_data(self, symptom_data: Dict[str, Any]) -> None:
        """保存症状数据到数据库"""
        # 从追问答案中提取结构化信息
        answers = symptom_data["answers"]
        additional_info = {}
        
        # 基于问题提取信息
        for question, answer in answers.items():
            if "类型" in question or "哪种" in question:
                symptom_data["symptom_type"] = answer
            elif "持续" in question or "多久" in question:
                symptom_data["duration"] = answer
            elif "诱发" in question or "情况" in question:
                symptom_data["triggers"] = answer
            else:
                additional_info[question] = answer
        
        # 创建用户症状记录
        user_symptom = UserSymptom(
            user_id=self.user_id,
            symptom_name=symptom_data["symptom"],
            frequency=symptom_data.get("frequency"),
            symptom_type=symptom_data.get("symptom_type"),
            duration=symptom_data.get("duration"),
            triggers=symptom_data.get("triggers"),
            severity=symptom_data.get("severity"),
            additional_info=additional_info if additional_info else None
        )
        
        self.db.add(user_symptom)
        self.db.commit()
    
    def generate_final_user_portrait(self, session_data: Dict[str, Any]) -> UserPortrait:
        """基于收集的所有信息生成最终用户画像"""
        # 获取所有收集的数据，确保符合数据库表结构
        basic_info = session_data.get("basic_info", {})
        health_history = session_data.get("health_history", {})
        lifestyle = session_data.get("lifestyle", {})
        symptoms = session_data.get("symptoms", [])
        medical_reports = session_data.get("medical_reports", [])
        
        # 分析健康风险
        health_risk = "低风险"
        risk_factors = []
        
        # 年龄因素
        age = basic_info.get("age")
        if age and age >= 40:
            risk_factors.append("年龄大于40岁")
        
        # 慢性疾病因素
        if health_history.get("chronic_diseases"):
            risk_factors.append("有慢性疾病史")
        
        # 家族病史因素
        if health_history.get("family_medical_history"):
            risk_factors.append("有家族病史")
        
        # 生活方式因素
        if lifestyle.get("smoking", False):
            risk_factors.append("吸烟")
        if lifestyle.get("alcohol", False):
            risk_factors.append("饮酒")
        if lifestyle.get("exercise_frequency") == "很少":
            risk_factors.append("缺乏运动")
        
        # 症状因素
        if symptoms and len(symptoms) > 0:
            risk_factors.append(f"有{len(symptoms)}个不适症状")
        
        # 体检报告因素
        if medical_reports and len(medical_reports) > 0:
            risk_factors.append("有历史体检报告")
        
        # 根据风险因素确定风险等级
        if len(risk_factors) >= 3:
            health_risk = "高风险"
        elif len(risk_factors) >= 1:
            health_risk = "中风险"
        
        # 确定推荐体检频率
        recommended_frequency = "每年一次"
        if health_risk == "高风险" or (age and age >= 50):
            recommended_frequency = "每半年一次"
        
        # 生成重点关注领域
        focus_areas = self._generate_focus_areas(basic_info, health_history, lifestyle, symptoms, medical_reports)
        
        # 创建或更新用户画像
        user_portrait = self.db.query(UserPortrait).filter(
            UserPortrait.user_id == self.user_id
        ).first()
        
        if user_portrait:
            user_portrait.basic_info = basic_info
            user_portrait.health_history = health_history
            user_portrait.lifestyle = lifestyle
            user_portrait.symptoms = symptoms
            user_portrait.medical_reports = medical_reports
            user_portrait.focus_areas = focus_areas
            user_portrait.health_risk = health_risk
            user_portrait.recommended_frequency = recommended_frequency
            user_portrait.generated_at = datetime.now()
        else:
            user_portrait = UserPortrait(
                user_id=self.user_id,
                basic_info=basic_info,
                health_history=health_history,
                lifestyle=lifestyle,
                symptoms=symptoms,
                medical_reports=medical_reports,
                focus_areas=focus_areas,
                health_risk=health_risk,
                recommended_frequency=recommended_frequency,
                generated_at=datetime.now()
            )
            self.db.add(user_portrait)
        
        self.db.commit()
        self.db.refresh(user_portrait)
        
        logger.info(f"生成用户画像: 用户ID={self.user_id}, 健康风险={health_risk}, 关注领域={len(focus_areas)}个")
        return user_portrait
    
    def _generate_focus_areas(self, basic_info: Dict[str, Any], health_history: Dict[str, Any], 
                            lifestyle: Dict[str, Any], symptoms: List[Dict[str, Any]], 
                            medical_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成用户重点关注领域"""
        focus_areas = []
        
        # 基于基本信息生成关注领域
        age = basic_info.get("age")
        if age and age >= 40:
            focus_areas.append({
                "area_name": "中年健康管理",
                "reason": "年龄超过40岁，需要关注中年期健康问题",
                "priority": "high"
            })
        
        # 基于健康史生成关注领域
        if health_history.get("chronic_diseases"):
            focus_areas.append({
                "area_name": "慢性病管理",
                "reason": "有慢性疾病史，需要定期监测和管理",
                "priority": "high"
            })
        
        if health_history.get("family_medical_history"):
            focus_areas.append({
                "area_name": "遗传风险监测",
                "reason": "有家族病史，需要关注相关疾病风险",
                "priority": "medium"
            })
        
        # 基于生活习惯生成关注领域
        if lifestyle.get("smoking", False):
            focus_areas.append({
                "area_name": "戒烟指导",
                "reason": "吸烟习惯对健康有显著影响",
                "priority": "high"
            })
        
        if lifestyle.get("alcohol", False):
            focus_areas.append({
                "area_name": "饮酒管理",
                "reason": "饮酒习惯需要合理控制",
                "priority": "medium"
            })
        
        if lifestyle.get("exercise_frequency") == "很少":
            focus_areas.append({
                "area_name": "运动指导",
                "reason": "缺乏运动，需要建立运动习惯",
                "priority": "medium"
            })
        
        # 基于症状生成关注领域
        if symptoms and len(symptoms) > 0:
            focus_areas.append({
                "area_name": "症状管理",
                "reason": f"有{len(symptoms)}个不适症状需要关注",
                "priority": "high"
            })
        
        # 基于体检报告生成关注领域
        if medical_reports and len(medical_reports) > 0:
            focus_areas.append({
                "area_name": "体检报告解读",
                "reason": "有历史体检报告需要专业解读",
                "priority": "medium"
            })
        
        # 如果没有特定关注领域，添加基础健康管理
        if not focus_areas:
            focus_areas.append({
                "area_name": "基础健康管理",
                "reason": "保持良好生活习惯，定期体检",
                "priority": "low"
            })
        
        return focus_areas
    
    def skip_step(self, step: str) -> Dict[str, Any]:
        """跳过当前步骤"""
        if step not in MAIN_FLOW_STEPS:
            raise CustomException(
                status_code=400,
                message="无效的步骤",
                error_type="InvalidStepError"
            )
        
        # 更新完成步骤
        completed_steps = self.get_completed_steps()
        if step not in completed_steps:
            completed_steps.append(step)
        
        # 确定下一步
        current_index = MAIN_FLOW_STEPS.index(step)
        if current_index < len(MAIN_FLOW_STEPS) - 1:
            next_step = MAIN_FLOW_STEPS[current_index + 1]
        else:
            next_step = "complete"
        
        self._update_progress(
            current_step=next_step,
            completed_steps=completed_steps
        )
        
        if next_step == "complete":
            # 生成最终用户画像
            user_portrait = self.generate_final_user_portrait(self.progress.session_data or {})
            return {
                "next_action": "complete",
                "message": "用户画像生成完成",
                "portrait_id": user_portrait.id
            }
        else:
            return {
                "next_action": "next_step",
                "next_step": next_step,
                "completed_steps": completed_steps
            }
    
    def reset_flow(self) -> Dict[str, Any]:
        """重置流程"""
        self._update_progress(
            current_step=MAIN_FLOW_STEPS[0],
            completed_steps=[],
            current_state="normal",
            session_data={}
        )
        
        return {
            "next_action": "reset",
            "message": "流程已重置",
            "next_step": MAIN_FLOW_STEPS[0]
        }


async def get_questionnaire_progress(db: Session, user_id: int) -> Dict[str, Any]:
    """
    获取用户问卷进度
    """
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(
                status_code=404,
                message="用户不存在",
                error_type="UserNotFound"
            )
        
        # 获取或创建进度
        service = UserPortraitFlowService(db, user_id)
        
        return {
            "current_step": service.get_current_step(),
            "completed_steps": service.get_completed_steps(),
            "current_state": service.progress.current_state or "normal"
        }
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GetQuestionnaireProgressError", f"获取问卷进度失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取问卷进度失败，请稍后重试",
            error_type="ProgressRetrievalError"
        )


async def process_questionnaire_step(
    db: Session, 
    user_id: int,
    step: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理问卷步骤
    """
    try:
        service = UserPortraitFlowService(db, user_id)
        
        # 检查步骤是否有效
        if step not in MAIN_FLOW_STEPS:
            raise CustomException(
                status_code=400,
                message="无效的步骤",
                error_type="InvalidStepError"
            )
        
        # 检查是否是当前应该处理的步骤
        if step != service.get_current_step() and service.progress.current_state != "symptom_dynamic":
            raise CustomException(
                status_code=400,
                message=f"当前应该处理的步骤是: {service.get_current_step()}",
                error_type="StepOrderError"
            )
        
        # 处理步骤
        result = service.process_main_flow_step(step, data)
        return result
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("ProcessQuestionnaireStepError", f"处理问卷步骤失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="处理问卷步骤失败，请稍后重试",
            error_type="StepProcessingError"
        )


async def process_dynamic_question_answer(
    db: Session,
    user_id: int,
    answer: str
) -> Dict[str, Any]:
    """
    处理动态追问的回答
    """
    try:
        service = UserPortraitFlowService(db, user_id)
        
        # 检查是否处于动态追问状态
        if service.progress.current_state != "symptom_dynamic":
            raise CustomException(
                status_code=400,
                message="当前未处于动态追问状态",
                error_type="NotInDynamicStateError"
            )
        
        # 处理回答
        result = service.process_dynamic_question(answer)
        return result
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("ProcessDynamicAnswerError", f"处理动态追问回答失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="处理动态追问回答失败，请稍后重试",
            error_type="DynamicProcessingError"
        )


async def skip_questionnaire_step(db: Session, user_id: int) -> Dict[str, Any]:
    """
    跳过当前问卷步骤
    """
    try:
        service = UserPortraitFlowService(db, user_id)
        current_step = service.get_current_step()
        
        # 不能跳过基本信息步骤
        if current_step == "basic_info":
            raise CustomException(
                status_code=400,
                message="基本信息步骤不能跳过",
                error_type="CannotSkipBasicInfoError"
            )
        
        # 处理跳过
        result = service.skip_step(current_step)
        return result
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("SkipQuestionnaireStepError", f"跳过问卷步骤失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="跳过问卷步骤失败，请稍后重试",
            error_type="SkipProcessingError"
        )


async def reset_questionnaire(db: Session, user_id: int) -> Dict[str, Any]:
    """
    重置问卷
    """
    try:
        service = UserPortraitFlowService(db, user_id)
        result = service.reset_flow()
        return result
        
    except Exception as e:
        log_error("ResetQuestionnaireError", f"重置问卷失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="重置问卷失败，请稍后重试",
            error_type="ResetProcessingError"
        )