from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
import json

router = APIRouter(
    prefix="/ai",
    tags=["AI智能交互"]
)

# 定义请求和响应模型
class ChatMessage(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: str
    query: str
    context: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    status: str
    answer: str
    suggestions: Optional[List[str]] = []

# 预设的常见问题和回答
PRESET_ANSWERS = {
    "体检项目": [
        "根据您的年龄和健康状况，我建议您进行以下体检项目：\n1. 基础体检套餐（血常规、尿常规、肝功能等）\n2. 心电图检查\n3. 胸部X光检查\n\n这些项目可以帮助全面了解您的健康状况。",
        "针对您的年龄段，推荐以下体检项目：\n- 血常规：检查血液基本状况\n- 尿常规：评估肾脏功能\n- 肝功能：检查肝脏健康状况\n- 血脂：评估心血管疾病风险\n- 血糖：筛查糖尿病风险"
    ],
    "体检报告": [
        "体检报告中的异常指标需要结合具体情况分析。一般来说，轻微偏离正常范围的指标可能是暂时的，建议您：\n1. 注意生活习惯调整\n2. 1-3个月后复查\n3. 如有明显异常，请及时就医",
        "解读体检报告时，请注意以下几点：\n1. 参考范围：每个指标都有正常参考范围\n2. 趋势分析：对比往年报告看变化趋势\n3. 综合评估：单项指标异常不一定代表有疾病\n4. 专业咨询：如有疑问，建议咨询专业医生"
    ],
    "高血压": [
        "高血压患者体检需要注意：\n1. 定期监测血压，记录变化\n2. 检查项目应包括：血压测量、心电图、尿常规、肾功能、血脂、血糖\n3. 避免剧烈运动和情绪激动\n4. 体检前正常服用降压药",
        "高血压患者体检建议：\n- 增加心脏彩超检查\n- 检查眼底血管\n- 24小时动态血压监测\n- 肾动脉超声检查\n- 同型半胱氨酸检测"
    ],
    "体检准备": [
        "体检前准备事项：\n1. 空腹8-12小时（可少量饮水）\n2. 体检前3天避免高脂饮食和饮酒\n3. 体检前1天避免剧烈运动\n4. 女性避开月经期\n5. 服用药物请咨询医生是否需要停药",
        "体检前注意事项：\n- 穿宽松舒适的衣物\n- 不要佩戴金属饰品\n- 早上可少量饮水服药\n- 体检当天不要化妆\n- 如有晕血史请提前告知医护人员"
    ]
}

# 默认回答
DEFAULT_ANSWERS = [
    "感谢您的提问。作为您的健康助手，我建议您根据个人情况选择合适的体检项目。如有具体健康问题，建议咨询专业医生。",
    "每个人的健康状况不同，建议的体检项目也会有所差异。您可以先完成基础体检，然后根据结果进行针对性检查。",
    "健康体检是预防疾病的重要手段。建议您每年进行一次全面体检，及时发现潜在健康问题。",
    "您的健康问题很重要。如果您有具体的症状或担忧，建议及时就医，不要延误诊断和治疗。"
]

# 健康建议
HEALTH_SUGGESTIONS = [
    "保持规律作息，每天睡眠7-8小时",
    "均衡饮食，多吃蔬菜水果，少油少盐",
    "适量运动，每周至少150分钟中等强度运动",
    "戒烟限酒，减少有害物质摄入",
    "定期体检，早发现早治疗",
    "保持心理健康，学会释放压力"
]

@router.post("/interaction")
async def ai_interaction(request: ChatRequest):
    """
    AI智能交互接口
    - **user_id**: 用户ID
    - **query**: 用户查询
    - **context**: 对话上下文（可选）
    """
    try:
        # 简单的关键词匹配回复
        query_lower = request.query.lower()
        answer = None
        
        # 根据关键词匹配预设回答
        for keyword, answers in PRESET_ANSWERS.items():
            if keyword in query_lower:
                answer = random.choice(answers)
                break
        
        # 如果没有匹配的关键词，使用默认回答
        if not answer:
            answer = random.choice(DEFAULT_ANSWERS)
        
        # 随机添加健康建议
        if random.random() > 0.5:  # 50%概率添加建议
            suggestion = random.choice(HEALTH_SUGGESTIONS)
            answer += f"\n\n健康小贴士：{suggestion}"
        
        # 生成相关问题建议
        suggestions = [
            "我这个年龄段应该做哪些体检项目？",
            "如何解读体检报告中的异常指标？",
            "有高血压病史的人体检需要注意什么？",
            "体检前需要做哪些准备？"
        ]
        
        # 随机选择2-3个建议
        selected_suggestions = random.sample(suggestions, k=random.randint(2, 3))
        
        return {
            "status": "success",
            "data": {
                "answer": answer,
                "suggestions": selected_suggestions
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI交互处理失败: {str(e)}"
        )