#!/bin/bash

# 数据库初始化脚本

# 从.env文件加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 提取数据库连接信息
DB_URL="$DATABASE_URL"

# 如果环境变量未设置，使用默认值
if [ -z "$DB_URL" ]; then
    echo "警告: 未找到DATABASE_URL环境变量，使用默认值"
    DB_URL="postgresql://postgres:postgres@localhost:5432/hospital_examination"
fi

# 显示正在执行的操作
echo "开始初始化数据库..."
echo "使用数据库连接: $DB_URL"

# 使用psql导入schema文件
psql "$DB_URL" -f "$(pwd)/database_schema.sql" 2>/dev/null

# 检查导入是否成功
if [ $? -eq 0 ]; then
    echo "数据库schema导入成功!"
    
    # 可选：导入初始数据
    if [ -f "$(pwd)/data/initial/data.sql" ]; then
        echo "正在导入初始数据..."
        psql "$DB_URL" -f "$(pwd)/data/initial/data.sql"
        if [ $? -eq 0 ]; then
            echo "初始数据导入成功!"
        else
            echo "警告: 初始数据导入失败"
        fi
    fi
else
    echo "错误: 数据库schema导入失败"
    echo "尝试创建数据库后重试..."
    
    # 提取数据库名称和连接信息
    DB_NAME=$(echo "$DB_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_CONN=$(echo "$DB_URL" | sed 's/\/[^\/]*$/\/postgres/')
    
    # 尝试创建数据库
    psql "$DB_CONN" -c "CREATE DATABASE $DB_NAME" 2>/dev/null
    
    # 再次尝试导入
    if [ $? -eq 0 ]; then
        echo "数据库创建成功，再次尝试导入schema..."
        psql "$DB_URL" -f "$(pwd)/database_schema.sql"
        if [ $? -eq 0 ]; then
            echo "数据库schema导入成功!"
        else
            echo "错误: 再次导入schema失败"
            exit 1
        fi
    else
        echo "错误: 创建数据库失败，请手动创建数据库"
        exit 1
    fi
fi

echo "数据库初始化完成!"
exit 0