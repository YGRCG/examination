"""
用户画像相关数据库表创建脚本
"""

from sqlalchemy import create_engine, text
from utils.database import DATABASE_URL
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_user_profile_tables():
    """
    创建用户画像相关的数据库表
    """
    engine = create_engine(DATABASE_URL)
    
    # 创建用户画像表
    create_user_profile_table = """
    CREATE TABLE IF NOT EXISTS user_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        basic_info JSONB,
        health_history JSONB,
        lifestyle JSONB,
        symptoms JSONB,
        medical_reports JSONB,
        focus_areas JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建症状知识库表
    create_symptom_knowledge_table = """
    CREATE TABLE IF NOT EXISTS symptom_knowledge (
        id SERIAL PRIMARY KEY,
        symptom VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        follow_up_questions JSONB,
        related_symptoms JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建对话历史表
    create_conversation_history_table = """
    CREATE TABLE IF NOT EXISTS conversation_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        sender VARCHAR(20) NOT NULL,
        main_step VARCHAR(50),
        sub_step INTEGER,
        is_ai_sub_process BOOLEAN DEFAULT FALSE,
        extracted_entities JSONB,
        response_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建用户流程状态表
    create_user_flow_state_table = """
    CREATE TABLE IF NOT EXISTS user_flow_state (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        current_main_step VARCHAR(50) DEFAULT 'basic_info',
        current_sub_step INTEGER DEFAULT 0,
        is_ai_sub_process BOOLEAN DEFAULT FALSE,
        temp_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建索引
    create_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_symptom_knowledge_symptom ON symptom_knowledge(symptom);",
        "CREATE INDEX IF NOT EXISTS idx_conversation_history_user_id ON conversation_history(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_conversation_history_created_at ON conversation_history(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_user_flow_state_user_id ON user_flow_state(user_id);"
    ]
    
    try:
        with engine.connect() as connection:
            # 创建表
            connection.execute(text(create_user_profile_table))
            connection.execute(text(create_symptom_knowledge_table))
            connection.execute(text(create_conversation_history_table))
            connection.execute(text(create_user_flow_state_table))
            
            # 创建索引
            for index_sql in create_indexes:
                connection.execute(text(index_sql))
            
            connection.commit()
            logger.info("用户画像相关数据库表创建成功")
            
            # 初始化症状知识库数据
            init_symptom_knowledge(connection)
            
    except Exception as e:
        logger.error(f"创建用户画像相关数据库表失败: {str(e)}")
        raise

def init_symptom_knowledge(connection):
    """
    初始化症状知识库数据
    """
    # 头晕症状知识
    dizziness_data = {
        "symptom": "头晕",
        "description": "头晕是指感觉自身或周围环境旋转、摇晃或不稳定的症状",
        "follow_up_questions": [
            {"question": "请问是眩晕（感觉天旋地转）还是昏沉（感觉头重脚轻）？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "在什么情况下容易诱发（比如起床、转头时）？", "key": "triggers"},
            {"question": "是否伴有恶心、呕吐？", "key": "accompanying_symptoms"}
        ],
        "related_symptoms": ["头痛", "恶心", "耳鸣", "视力模糊"]
    }
    
    # 胃不适症状知识
    stomach_discomfort_data = {
        "symptom": "胃不适",
        "description": "胃部不适是指胃部区域出现的不舒服感觉，包括疼痛、胀气、反酸等",
        "follow_up_questions": [
            {"question": "是胀痛、刺痛还是反酸？", "key": "type"},
            {"question": "通常是在饭前还是饭后出现？", "key": "timing"},
            {"question": "是否伴有恶心、没胃口？", "key": "accompanying_symptoms"},
            {"question": "这种情况持续多久了？", "key": "duration"}
        ],
        "related_symptoms": ["恶心", "呕吐", "食欲不振", "反酸"]
    }
    
    # 头痛症状知识
    headache_data = {
        "symptom": "头痛",
        "description": "头痛是指头部任何部位出现的疼痛感",
        "follow_up_questions": [
            {"question": "是搏动性疼痛、压迫性疼痛还是刺痛？", "key": "type"},
            {"question": "疼痛部位是在前额、太阳穴还是后脑？", "key": "location"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "在什么情况下会加重或缓解？", "key": "triggers"}
        ],
        "related_symptoms": ["头晕", "恶心", "视力模糊", "畏光"]
    }
    
    # 失眠症状知识
    insomnia_data = {
        "symptom": "失眠",
        "description": "失眠是指难以入睡、睡眠浅或早醒等睡眠质量问题",
        "follow_up_questions": [
            {"question": "是难以入睡、容易醒还是早醒？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "是否与压力、焦虑有关？", "key": "causes"},
            {"question": "白天是否感到疲劳、注意力不集中？", "key": "daytime_impact"}
        ],
        "related_symptoms": ["疲劳", "焦虑", "注意力不集中", "情绪波动"]
    }
    
    # 疲劳症状知识
    fatigue_data = {
        "symptom": "疲劳",
        "description": "疲劳是指感到身体或精神上的疲惫、乏力",
        "follow_up_questions": [
            {"question": "是身体疲劳还是精神疲劳？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "是否与睡眠质量有关？", "key": "related_factors"},
            {"question": "是否伴有注意力不集中、记忆力下降？", "key": "accompanying_symptoms"}
        ],
        "related_symptoms": ["失眠", "注意力不集中", "记忆力下降", "情绪低落"]
    }
    
    # 胸闷症状知识
    chest_tightness_data = {
        "symptom": "胸闷",
        "description": "胸闷是指胸部感到压迫、憋闷或呼吸不畅",
        "follow_up_questions": [
            {"question": "是压迫感、憋闷感还是疼痛？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "在什么情况下会出现（如运动、情绪激动时）？", "key": "triggers"},
            {"question": "是否伴有心悸、气短？", "key": "accompanying_symptoms"}
        ],
        "related_symptoms": ["心悸", "气短", "胸痛", "呼吸困难"]
    }
    
    # 心悸症状知识
    palpitations_data = {
        "symptom": "心悸",
        "description": "心悸是指感觉到心跳过快、过慢或不规律",
        "follow_up_questions": [
            {"question": "是心跳过快、过慢还是不规律？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "在什么情况下会出现（如运动、情绪激动时）？", "key": "triggers"},
            {"question": "是否伴有头晕、胸闷？", "key": "accompanying_symptoms"}
        ],
        "related_symptoms": ["胸闷", "头晕", "气短", "焦虑"]
    }
    
    # 关节痛症状知识
    joint_pain_data = {
        "symptom": "关节痛",
        "description": "关节痛是指关节部位出现的疼痛感",
        "follow_up_questions": [
            {"question": "是哪个关节疼痛（如膝盖、手肘、手腕等）？", "key": "location"},
            {"question": "是刺痛、胀痛还是酸痛？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "是否伴有肿胀、活动受限？", "key": "accompanying_symptoms"}
        ],
        "related_symptoms": ["肿胀", "活动受限", "僵硬", "红肿"]
    }
    
    # 肌肉痛症状知识
    muscle_pain_data = {
        "symptom": "肌肉痛",
        "description": "肌肉痛是指肌肉组织出现的疼痛感",
        "follow_up_questions": [
            {"question": "是哪个部位的肌肉疼痛？", "key": "location"},
            {"question": "是酸痛、刺痛还是胀痛？", "key": "type"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "是否与运动、劳累有关？", "key": "triggers"}
        ],
        "related_symptoms": ["疲劳", "僵硬", "肿胀", "活动受限"]
    }
    
    # 皮肤瘙痒症状知识
    skin_itching_data = {
        "symptom": "皮肤瘙痒",
        "description": "皮肤瘙痒是指皮肤感到痒，想要抓挠",
        "follow_up_questions": [
            {"question": "是哪个部位的皮肤瘙痒？", "key": "location"},
            {"question": "是否有皮疹、红肿？", "key": "skin_changes"},
            {"question": "这种情况持续多久了？", "key": "duration"},
            {"question": "是否与过敏、干燥有关？", "key": "triggers"}
        ],
        "related_symptoms": ["皮疹", "红肿", "干燥", "过敏"]
    }
    
    # 插入症状知识数据
    symptom_data_list = [
        dizziness_data, stomach_discomfort_data, headache_data, insomnia_data,
        fatigue_data, chest_tightness_data, palpitations_data, joint_pain_data,
        muscle_pain_data, skin_itching_data
    ]
    
    for data in symptom_data_list:
        # 检查是否已存在
        check_sql = "SELECT id FROM symptom_knowledge WHERE symptom = :symptom"
        result = connection.execute(text(check_sql), {"symptom": data["symptom"]}).fetchone()
        
        if not result:
            # 插入新数据
            import json
            insert_sql = """
            INSERT INTO symptom_knowledge (symptom, description, follow_up_questions, related_symptoms)
            VALUES (:symptom, :description, :follow_up_questions, :related_symptoms)
            """
            # 将字典转换为JSON字符串
            insert_data = {
                "symptom": data["symptom"],
                "description": data["description"],
                "follow_up_questions": json.dumps(data["follow_up_questions"]),
                "related_symptoms": json.dumps(data["related_symptoms"])
            }
            connection.execute(text(insert_sql), insert_data)
            logger.info(f"初始化症状知识: {data['symptom']}")
    
    connection.commit()
    logger.info("症状知识库初始化完成")

if __name__ == "__main__":
    create_user_profile_tables()