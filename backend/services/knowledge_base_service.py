"""
知识库/规则库服务
用于支持用户画像智能交互模块的AI动态子流程
"""
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from models.user_profile import SymptomKnowledge
from schemas.user_profile_schemas import SymptomExtraction, SymptomFollowUp
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KnowledgeBaseService:
    """知识库服务类，提供症状知识查询和规则处理"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_symptom_knowledge(self, symptom: str) -> Optional[Dict]:
        """获取症状相关知识"""
        try:
            # 查询症状知识库
            knowledge = self.db.query(SymptomKnowledge).filter(
                SymptomKnowledge.symptom.ilike(f"%{symptom}%")
            ).first()
            
            if not knowledge:
                logger.warning(f"未找到症状知识: {symptom}")
                return None
            
            # 解析JSON字段
            follow_up_questions = json.loads(knowledge.follow_up_questions) if knowledge.follow_up_questions else []
            related_symptoms = json.loads(knowledge.related_symptoms) if knowledge.related_symptoms else []
            
            return {
                "symptom": knowledge.symptom,
                "description": knowledge.description,
                "follow_up_questions": follow_up_questions,
                "related_symptoms": related_symptoms
            }
        except Exception as e:
            logger.error(f"获取症状知识失败: {str(e)}")
            return None
    
    def extract_symptom_entities(self, user_input: str) -> List[SymptomExtraction]:
        """从用户输入中提取症状实体"""
        try:
            # 获取所有症状关键词
            all_symptoms = self.db.query(SymptomKnowledge.symptom).all()
            symptom_keywords = [item[0] for item in all_symptoms]
            
            # 构建正则表达式模式
            pattern = r'(' + '|'.join(symptom_keywords) + r')'
            
            # 查找所有匹配的症状
            matches = re.finditer(pattern, user_input, re.IGNORECASE)
            
            extractions = []
            for match in matches:
                symptom = match.group(0)
                
                # 提取频率信息
                frequency = self._extract_frequency(user_input, match.start(), match.end())
                
                # 提取持续时间
                duration = self._extract_duration(user_input)
                
                # 提取程度
                severity = self._extract_severity(user_input)
                
                extractions.append(SymptomExtraction(
                    symptom=symptom,
                    frequency=frequency,
                    duration=duration,
                    severity=severity,
                    context=user_input
                ))
            
            return extractions
        except Exception as e:
            logger.error(f"提取症状实体失败: {str(e)}")
            return []
    
    def _extract_frequency(self, text: str, start: int, end: int) -> Optional[str]:
        """提取症状频率"""
        # 常见频率关键词
        frequency_keywords = ["经常", "总是", "偶尔", "有时", "很少", "从不", "每天", "每周", "每月"]
        
        # 在症状前后查找频率关键词
        context_start = max(0, start - 10)
        context_end = min(len(text), end + 10)
        context = text[context_start:context_end]
        
        for keyword in frequency_keywords:
            if keyword in context:
                return keyword
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """提取症状持续时间"""
        # 常见时间模式
        duration_patterns = [
            r'(\d+天)',
            r'(\d+周)',
            r'(\d+月)',
            r'(\d+年)',
            r'(几天)',
            r'(几周)',
            r'(几个月)',
            r'(几年)',
            r'(最近)',
            r'(这段时间)',
            r'(一直)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_severity(self, text: str) -> Optional[str]:
        """提取症状程度"""
        # 常见程度关键词
        severity_keywords = ["轻微", "轻度", "中度", "严重", "剧烈", "非常", "特别", "有点"]
        
        for keyword in severity_keywords:
            if keyword in text:
                return keyword
        
        return None
    
    def generate_follow_up_questions(self, symptom: str, user_input: str) -> List[SymptomFollowUp]:
        """根据症状生成追问"""
        try:
            # 获取症状知识
            knowledge = self.get_symptom_knowledge(symptom)
            if not knowledge or not knowledge.get("follow_up_questions"):
                return []
            
            # 提取用户已回答的信息
            extractions = self.extract_symptom_entities(user_input)
            answered_keys = set()
            
            for extraction in extractions:
                if extraction.symptom == symptom:
                    if extraction.frequency:
                        answered_keys.add("frequency")
                    if extraction.duration:
                        answered_keys.add("duration")
                    if extraction.severity:
                        answered_keys.add("severity")
            
            # 生成未回答的追问
            follow_ups = []
            for question_data in knowledge["follow_up_questions"]:
                key = question_data.get("key")
                if key and key not in answered_keys:
                    follow_ups.append(SymptomFollowUp(
                        question=question_data.get("question"),
                        key=key,
                        options=question_data.get("options")
                    ))
            
            return follow_ups
        except Exception as e:
            logger.error(f"生成追问失败: {str(e)}")
            return []
    
    def should_continue_ai_subflow(self, symptom: str, collected_info: Dict) -> bool:
        """判断是否应该继续AI动态子流程"""
        try:
            # 获取症状知识
            knowledge = self.get_symptom_knowledge(symptom)
            if not knowledge:
                return False
            
            # 获取所有需要收集的关键信息
            required_keys = set()
            for question_data in knowledge.get("follow_up_questions", []):
                key = question_data.get("key")
                if key:
                    required_keys.add(key)
            
            # 检查是否已收集所有关键信息
            collected_keys = set(collected_info.keys())
            
            # 如果已收集所有关键信息，则结束子流程
            if required_keys.issubset(collected_keys):
                return False
            
            # 如果用户明确表示没有其他补充，则结束子流程
            if "no_more" in collected_info or "没有其他补充" in str(collected_info):
                return False
            
            # 否则继续子流程
            return True
        except Exception as e:
            logger.error(f"判断子流程状态失败: {str(e)}")
            return False
    
    def get_related_symptoms(self, symptom: str) -> List[str]:
        """获取相关症状"""
        try:
            knowledge = self.get_symptom_knowledge(symptom)
            if not knowledge:
                return []
            
            return knowledge.get("related_symptoms", [])
        except Exception as e:
            logger.error(f"获取相关症状失败: {str(e)}")
            return []
    
    def process_symptom_response(self, symptom: str, user_response: str, current_collected: Dict) -> Dict:
        """处理用户对症状追问的响应"""
        try:
            # 更新收集的信息
            updated_collected = current_collected.copy()
            
            # 提取频率
            frequency = self._extract_frequency(user_response, 0, len(user_response))
            if frequency:
                updated_collected["frequency"] = frequency
            
            # 提取持续时间
            duration = self._extract_duration(user_response)
            if duration:
                updated_collected["duration"] = duration
            
            # 提取程度
            severity = self._extract_severity(user_response)
            if severity:
                updated_collected["severity"] = severity
            
            # 检查是否表示没有其他补充
            if any(keyword in user_response for keyword in ["没有", "没有了", "没有了", "没有了", "no more", "no more"]):
                updated_collected["no_more"] = True
            
            return updated_collected
        except Exception as e:
            logger.error(f"处理症状响应失败: {str(e)}")
            return current_collected