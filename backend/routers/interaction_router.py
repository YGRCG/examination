from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from utils.database import get_db
from utils.security import get_current_user
from services import interaction_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions

router = APIRouter(
    prefix="/api/v1/interactions",
    tags=["智能交互"]
)

# 语音文件存储路径
VOICE_STORAGE_PATH = "voice_files"

# 确保存储目录存在
if not os.path.exists(VOICE_STORAGE_PATH):
    os.makedirs(VOICE_STORAGE_PATH)

@router.post("/text", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def send_text(
    content: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    发送文字消息接口
    - **content**: 文字消息内容
    """
    interaction = await interaction_service.send_text_message(db, current_user.id, content)
    
    # 构造响应数据
    response_data = {
        "id": interaction.id,
        "message_type": interaction.message_type,
        "content": interaction.message_content,
        "timestamp": interaction.timestamp
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="文字消息发送成功",
        data=response_data
    )

@router.post("/voice", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def send_voice(
    file: UploadFile = File(...),
    duration: float = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    发送语音消息接口
    - **file**: 语音文件
    - **duration**: 语音时长（秒）
    """
    # 保存语音文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(VOICE_STORAGE_PATH, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 存储文件URL（实际应用中应该是可访问的URL）
        voice_url = f"/static/voice/{filename}"
        
        # 创建交互记录
        interaction = await interaction_service.send_voice_message(
            db, current_user.id, voice_url, duration
        )
        
        # 构造响应数据
        response_data = {
            "id": interaction.id,
            "message_type": interaction.message_type,
            "voice_url": interaction.message_content,
            "duration": interaction.voice_duration,
            "timestamp": interaction.timestamp
        }
        
        return user_schemas.ApiResponse(
            status="success",
            message="语音消息发送成功",
            data=response_data
        )
    finally:
        # 关闭文件
        file.file.close()

@router.get("/history", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取会话历史接口
    - **limit**: 返回的记录数量，默认50
    - **offset**: 偏移量，默认0
    """
    interactions = await interaction_service.get_conversation_history(
        db, current_user.id, limit, offset
    )
    
    # 构造响应数据
    response_data = []
    for interaction in interactions:
        message_data = {
            "id": interaction.id,
            "message_type": interaction.message_type,
            "timestamp": interaction.timestamp,
            "is_user_message": interaction.is_user_message
        }
        
        if interaction.message_type == "text":
            message_data["content"] = interaction.message_content
        else:
            message_data["voice_url"] = interaction.message_content
            message_data["duration"] = interaction.voice_duration
        
        response_data.append(message_data)
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取会话历史成功",
        data=response_data
    )