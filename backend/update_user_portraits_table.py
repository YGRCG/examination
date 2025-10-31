#!/usr/bin/env python3
"""
更新用户画像表结构脚本
"""

from sqlalchemy import create_engine, text
from utils.database import DATABASE_URL
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_user_portraits_table():
    """
    更新user_portraits表结构，使其与模型定义一致
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_portraits'
                )
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                logger.info("表user_portraits不存在，将创建新表")
                # 创建新表
                conn.execute(text("""
                    CREATE TABLE user_portraits (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        basic_info JSONB,
                        health_history JSONB,
                        lifestyle JSONB,
                        symptoms JSONB,
                        medical_reports JSONB,
                        focus_areas JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # 创建索引
                conn.execute(text("""
                    CREATE INDEX idx_user_portraits_user_id ON user_portraits(user_id)
                """))
            else:
                logger.info("表user_portraits已存在，将更新结构")
                
                # 检查并添加缺失的列
                columns_to_add = [
                    ("basic_info", "JSONB"),
                    ("health_history", "JSONB"),
                    ("lifestyle", "JSONB"),
                    ("symptoms", "JSONB"),
                    ("medical_reports", "JSONB"),
                    ("focus_areas", "JSONB")
                ]
                
                for column_name, column_type in columns_to_add:
                    # 检查列是否存在
                    result = conn.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'user_portraits'
                            AND column_name = '{column_name}'
                        )
                    """))
                    column_exists = result.fetchone()[0]
                    
                    if not column_exists:
                        logger.info(f"添加列 {column_name}")
                        conn.execute(text(f"""
                            ALTER TABLE user_portraits 
                            ADD COLUMN {column_name} {column_type}
                        """))
                
                # 检查并创建索引
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename = 'user_portraits'
                        AND indexname = 'idx_user_portraits_user_id'
                    )
                """))
                index_exists = result.fetchone()[0]
                
                if not index_exists:
                    logger.info("创建索引 idx_user_portraits_user_id")
                    conn.execute(text("""
                        CREATE INDEX idx_user_portraits_user_id ON user_portraits(user_id)
                    """))
            
            # 提交事务
            trans.commit()
            logger.info("表结构更新成功")
            
        except Exception as e:
            # 回滚事务
            trans.rollback()
            logger.error(f"更新表结构失败: {str(e)}")
            raise

if __name__ == "__main__":
    update_user_portraits_table()