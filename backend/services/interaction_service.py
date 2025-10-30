from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models import Interaction, User
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.interaction")

async def send_text_message(
    db: Session,
    user_id: int,
    message_content: str
) -> Interaction:
    """
    发送文字消息
    :param db: 数据库会话
    :param user_id: 用户ID
    :param message_content: 消息内容
    :return: 创建的交互记录
    """
    try:
        async with db_transaction(db):
            # 检查用户是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 创建交互记录
            interaction = Interaction(
                user_id=user_id,
                message_type="text",
                message_content=message_content,
                is_user_message=True,
                timestamp=datetime.now()
            )
            
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            logger.info(f"用户发送文字消息: 用户ID={user_id}")
            return interaction
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("SendTextMessageError", f"发送文字消息失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="发送消息失败，请稍后重试",
            error_type="MessageSendingError"
        )

async def send_voice_message(
    db: Session,
    user_id: int,
    voice_url: str,
    duration: float
) -> Interaction:
    """
    发送语音消息
    :param db: 数据库会话
    :param user_id: 用户ID
    :param voice_url: 语音文件URL
    :param duration: 语音时长（秒）
    :return: 创建的交互记录
    """
    try:
        async with db_transaction(db):
            # 检查用户是否存在
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 创建交互记录
            interaction = Interaction(
                user_id=user_id,
                message_type="voice",
                message_content=voice_url,
                voice_duration=duration,
                is_user_message=True,
                timestamp=datetime.now()
            )
            
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            logger.info(f"用户发送语音消息: 用户ID={user_id}")
            return interaction
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("SendVoiceMessageError", f"发送语音消息失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="发送语音消息失败，请稍后重试",
            error_type="VoiceMessageSendingError"
        )

async def get_conversation_history(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> list[Interaction]:
    """
    获取会话历史
    :param db: 数据库会话
    :param user_id: 用户ID
    :param limit: 返回的记录数量
    :param offset: 偏移量
    :return: 会话历史记录列表
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
        
        # 查询会话历史
        interactions = (
            db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .order_by(Interaction.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # 按时间升序返回
        interactions.reverse()
        
        logger.info(f"获取用户会话历史: 用户ID={user_id}, 数量={len(interactions)}")
        return interactions
        
    except CustomException as e:
        raise
    except Exception as e:
        log_error("GetConversationHistoryError", f"获取会话历史失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取会话历史失败，请稍后重试",
            error_type="ConversationHistoryError"
        )