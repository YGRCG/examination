-- 医院体检项目智能推荐系统数据库 schema

-- 创建数据库（如果需要）
-- CREATE DATABASE hospital_examination;
-- \c hospital_examination;

-- 1. 用户表 (users)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITHOUT TIME ZONE,
    -- 添加注释
    CONSTRAINT users_username_check CHECK (LENGTH(username) >= 3),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- 为 users 表添加索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone_number ON users(phone_number);

-- 添加注释
COMMENT ON TABLE users IS '存储系统用户的基本信息';
COMMENT ON COLUMN users.id IS '用户唯一标识，主键';
COMMENT ON COLUMN users.username IS '用户名，用于登录';
COMMENT ON COLUMN users.password_hash IS '密码哈希值，存储加密后的密码';
COMMENT ON COLUMN users.phone_number IS '手机号码，用于验证和联系';
COMMENT ON COLUMN users.email IS '电子邮箱，用于验证和联系';
COMMENT ON COLUMN users.created_at IS '用户创建时间';
COMMENT ON COLUMN users.updated_at IS '用户信息最后更新时间';
COMMENT ON COLUMN users.last_login_at IS '用户最后登录时间';

-- 2. 用户信息表 (user_profiles)
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    age INTEGER,
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    allergies TEXT,
    chronic_diseases TEXT,
    surgeries TEXT,
    family_medical_history TEXT,
    smoking_status VARCHAR(20),
    drinking_status VARCHAR(20),
    exercise_habits TEXT,
    sleep_quality VARCHAR(20),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 为 user_profiles 表添加索引
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- 添加注释
COMMENT ON TABLE user_profiles IS '存储用户的详细健康信息和个人资料';
COMMENT ON COLUMN user_profiles.id IS '用户资料唯一标识，主键';
COMMENT ON COLUMN user_profiles.user_id IS '用户ID，外键，关联users表';
COMMENT ON COLUMN user_profiles.age IS '用户年龄';
COMMENT ON COLUMN user_profiles.gender IS '用户性别';
COMMENT ON COLUMN user_profiles.marital_status IS '婚姻状况';
COMMENT ON COLUMN user_profiles.height IS '身高，单位：厘米';
COMMENT ON COLUMN user_profiles.weight IS '体重，单位：公斤';
COMMENT ON COLUMN user_profiles.allergies IS '过敏史';
COMMENT ON COLUMN user_profiles.chronic_diseases IS '慢性病史';
COMMENT ON COLUMN user_profiles.surgeries IS '手术史';
COMMENT ON COLUMN user_profiles.family_medical_history IS '家族病史';
COMMENT ON COLUMN user_profiles.smoking_status IS '吸烟状况';
COMMENT ON COLUMN user_profiles.drinking_status IS '饮酒状况';
COMMENT ON COLUMN user_profiles.exercise_habits IS '运动习惯';
COMMENT ON COLUMN user_profiles.sleep_quality IS '睡眠质量';
COMMENT ON COLUMN user_profiles.created_at IS '资料创建时间';
COMMENT ON COLUMN user_profiles.updated_at IS '资料最后更新时间';

-- 3. 体检项目表 (examination_items)
CREATE TABLE examination_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration INTEGER,
    is_common BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 为 examination_items 表添加索引
CREATE INDEX idx_examination_items_category ON examination_items(category);
CREATE INDEX idx_examination_items_name ON examination_items(name);
CREATE INDEX idx_examination_items_is_common ON examination_items(is_common);

-- 添加注释
COMMENT ON TABLE examination_items IS '存储所有可提供的体检项目信息';
COMMENT ON COLUMN examination_items.id IS '体检项目唯一标识，主键';
COMMENT ON COLUMN examination_items.name IS '项目名称';
COMMENT ON COLUMN examination_items.description IS '项目详细描述';
COMMENT ON COLUMN examination_items.category IS '项目类别，如内科、外科、影像科等';
COMMENT ON COLUMN examination_items.price IS '项目价格';
COMMENT ON COLUMN examination_items.duration IS '预计检查时长，单位：分钟';
COMMENT ON COLUMN examination_items.is_common IS '是否为常规检查项目';
COMMENT ON COLUMN examination_items.created_at IS '项目创建时间';
COMMENT ON COLUMN examination_items.updated_at IS '项目信息最后更新时间';

-- 4. 体检套餐表 (examination_packages)
CREATE TABLE examination_packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    target_group VARCHAR(100),
    recommended_frequency VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 为 examination_packages 表添加索引
CREATE INDEX idx_examination_packages_name ON examination_packages(name);
CREATE INDEX idx_examination_packages_target_group ON examination_packages(target_group);

-- 添加注释
COMMENT ON TABLE examination_packages IS '存储体检套餐信息';
COMMENT ON COLUMN examination_packages.id IS '体检套餐唯一标识，主键';
COMMENT ON COLUMN examination_packages.name IS '套餐名称';
COMMENT ON COLUMN examination_packages.description IS '套餐详细描述';
COMMENT ON COLUMN examination_packages.price IS '套餐价格';
COMMENT ON COLUMN examination_packages.target_group IS '目标人群，如中老年人、职场人士等';
COMMENT ON COLUMN examination_packages.recommended_frequency IS '推荐检查频率，如每年一次';
COMMENT ON COLUMN examination_packages.created_at IS '套餐创建时间';
COMMENT ON COLUMN examination_packages.updated_at IS '套餐信息最后更新时间';

-- 5. 套餐项目关联表 (package_items)
CREATE TABLE package_items (
    id SERIAL PRIMARY KEY,
    package_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (package_id) REFERENCES examination_packages(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES examination_items(id) ON DELETE CASCADE,
    -- 添加唯一约束，确保一个套餐中一个项目只能出现一次
    UNIQUE (package_id, item_id)
);

-- 为 package_items 表添加索引
CREATE INDEX idx_package_items_package_id ON package_items(package_id);
CREATE INDEX idx_package_items_item_id ON package_items(item_id);

-- 添加注释
COMMENT ON TABLE package_items IS '关联体检套餐和体检项目的中间表';
COMMENT ON COLUMN package_items.id IS '关联记录唯一标识，主键';
COMMENT ON COLUMN package_items.package_id IS '套餐ID，外键，关联examination_packages表';
COMMENT ON COLUMN package_items.item_id IS '体检项目ID，外键，关联examination_items表';
COMMENT ON COLUMN package_items.item_quantity IS '项目数量，某些项目可能需要多次检查';
COMMENT ON COLUMN package_items.created_at IS '关联记录创建时间';
COMMENT ON COLUMN package_items.updated_at IS '关联记录最后更新时间';

-- 6. 推荐记录表 (recommendations)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    recommended_package_id INTEGER NOT NULL,
    recommendation_reason TEXT,
    recommended_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_package_id) REFERENCES examination_packages(id) ON DELETE CASCADE
);

-- 为 recommendations 表添加索引
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_profile_id ON recommendations(profile_id);
CREATE INDEX idx_recommendations_package_id ON recommendations(recommended_package_id);
CREATE INDEX idx_recommendations_recommended_at ON recommendations(recommended_at);

-- 添加注释
COMMENT ON TABLE recommendations IS '存储系统为用户推荐的体检套餐记录';
COMMENT ON COLUMN recommendations.id IS '推荐记录唯一标识，主键';
COMMENT ON COLUMN recommendations.user_id IS '用户ID，外键，关联users表';
COMMENT ON COLUMN recommendations.profile_id IS '用户资料ID，外键，关联user_profiles表';
COMMENT ON COLUMN recommendations.recommended_package_id IS '推荐的套餐ID，外键，关联examination_packages表';
COMMENT ON COLUMN recommendations.recommendation_reason IS '推荐理由，说明为什么推荐该套餐';
COMMENT ON COLUMN recommendations.recommended_at IS '推荐时间';
COMMENT ON COLUMN recommendations.created_at IS '记录创建时间';
COMMENT ON COLUMN recommendations.updated_at IS '记录最后更新时间';

-- 7. 预约表 (appointments)
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME WITHOUT TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES examination_packages(id) ON DELETE CASCADE,
    -- 添加检查约束
    CONSTRAINT appointments_status_check CHECK (status IN ('pending', 'confirmed', 'completed', 'canceled'))
);

-- 为 appointments 表添加索引
CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_package_id ON appointments(package_id);
CREATE INDEX idx_appointments_appointment_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- 添加注释
COMMENT ON TABLE appointments IS '存储用户的体检预约信息';
COMMENT ON COLUMN appointments.id IS '预约记录唯一标识，主键';
COMMENT ON COLUMN appointments.user_id IS '用户ID，外键，关联users表';
COMMENT ON COLUMN appointments.package_id IS '套餐ID，外键，关联examination_packages表';
COMMENT ON COLUMN appointments.appointment_date IS '预约日期';
COMMENT ON COLUMN appointments.appointment_time IS '预约时间';
COMMENT ON COLUMN appointments.status IS '预约状态：待确认(pending)、已确认(confirmed)、已完成(completed)、已取消(canceled)';
COMMENT ON COLUMN appointments.created_at IS '预约创建时间';
COMMENT ON COLUMN appointments.updated_at IS '预约信息最后更新时间';

-- 8. 体检报告表 (examination_reports)
CREATE TABLE examination_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    appointment_id INTEGER,
    report_url VARCHAR(255) NOT NULL,
    report_date DATE NOT NULL,
    summary TEXT,
    abnormal_items JSONB,
    doctor_comments TEXT,
    is_interpreted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
);

-- 为 examination_reports 表添加索引
CREATE INDEX idx_examination_reports_user_id ON examination_reports(user_id);
CREATE INDEX idx_examination_reports_appointment_id ON examination_reports(appointment_id);
CREATE INDEX idx_examination_reports_report_date ON examination_reports(report_date);
CREATE INDEX idx_examination_reports_is_interpreted ON examination_reports(is_interpreted);

-- 添加注释
COMMENT ON TABLE examination_reports IS '存储用户的体检报告信息';
COMMENT ON COLUMN examination_reports.id IS '报告唯一标识，主键';
COMMENT ON COLUMN examination_reports.user_id IS '用户ID，外键，关联users表';
COMMENT ON COLUMN examination_reports.appointment_id IS '预约ID，外键，关联appointments表，可为空（如上传历史报告）';
COMMENT ON COLUMN examination_reports.report_url IS '报告文件存储路径';
COMMENT ON COLUMN examination_reports.report_date IS '报告生成日期';
COMMENT ON COLUMN examination_reports.summary IS '报告摘要';
COMMENT ON COLUMN examination_reports.abnormal_items IS '异常项目，JSON格式存储';
COMMENT ON COLUMN examination_reports.doctor_comments IS '医生评语';
COMMENT ON COLUMN examination_reports.is_interpreted IS '报告是否已解读';
COMMENT ON COLUMN examination_reports.created_at IS '报告创建/上传时间';
COMMENT ON COLUMN examination_reports.updated_at IS '报告信息最后更新时间';

-- 9. 对话记录表 (conversations)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message_content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    sender VARCHAR(20) NOT NULL,
    sent_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 添加外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- 添加检查约束
    CONSTRAINT conversations_message_type_check CHECK (message_type IN ('text', 'voice')),
    CONSTRAINT conversations_sender_check CHECK (sender IN ('user', 'system'))
);

-- 为 conversations 表添加索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_sent_at ON conversations(sent_at);

-- 添加注释
COMMENT ON TABLE conversations IS '存储用户与系统的对话记录';
COMMENT ON COLUMN conversations.id IS '对话记录唯一标识，主键';
COMMENT ON COLUMN conversations.user_id IS '用户ID，外键，关联users表';
COMMENT ON COLUMN conversations.message_content IS '消息内容';
COMMENT ON COLUMN conversations.message_type IS '消息类型：text(文本)、voice(语音)';
COMMENT ON COLUMN conversations.sender IS '发送者：user(用户)、system(系统)';
COMMENT ON COLUMN conversations.sent_at IS '发送时间';
COMMENT ON COLUMN conversations.session_id IS '会话ID，用于多轮对话上下文管理';
COMMENT ON COLUMN conversations.created_at IS '记录创建时间';
COMMENT ON COLUMN conversations.updated_at IS '记录最后更新时间';

-- 创建更新时间的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加更新时间触发器
DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN (
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'users', 'user_profiles', 'examination_items', 
            'examination_packages', 'package_items', 'recommendations', 
            'appointments', 'examination_reports', 'conversations'
        )
    ) LOOP
        EXECUTE format('CREATE TRIGGER update_%I_updated_at
                        BEFORE UPDATE ON %I
                        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();',
                       table_name, table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 初始化一些基础数据（可选）
-- INSERT INTO examination_items (name, description, category, price, duration, is_common) VALUES
-- ('血常规', '检查血液中的红细胞、白细胞、血小板等指标', '检验科', 50.00, 15, TRUE),
-- ('尿常规', '检查尿液中的各项指标', '检验科', 30.00, 10, TRUE),
-- ('肝功能检查', '检查肝脏功能相关指标', '检验科', 120.00, 20, TRUE);

-- 提交所有更改
-- COMMIT;