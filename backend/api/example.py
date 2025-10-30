from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from utils.database import get_db
# from models import User  # 暂时注释掉，因为我们还没有定义User模型
from utils.error_handler import (
    CustomException,
    handle_exceptions,
    db_transaction,
    log_error
)

router = APIRouter(
    prefix="/api/v1/example",
    tags=["示例接口"],
    responses={404: {"description": "未找到"}}
)


# 请求模型示例
class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


# 响应模型示例
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        orm_mode = True


@router.post("/users", response_model=UserResponse, summary="创建用户")
@handle_exceptions  # 使用异常处理装饰器
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    """
    创建新用户
    
    - **username**: 用户名
    - **email**: 电子邮箱
    - **password**: 密码
    
    返回创建的用户信息
    """
    # 使用数据库事务上下文管理器
    async with db_transaction(db):
        # 检查用户是否已存在
        existing_user = db.query(User).filter(
            (User.username == request.username) | (User.email == request.email)
        ).first()
        
        if existing_user:
            # 抛出自定义异常
            raise CustomException(
                status_code=400,
                message="用户名或邮箱已被使用",
                error_type="UserAlreadyExists"
            )
        
        try:
            # 创建新用户
            new_user = User(
                username=request.username,
                email=request.email,
                # 在实际应用中，应该对密码进行哈希处理
                password_hash=request.password  # 示例中简化处理
            )
            
            # 添加到数据库
            db.add(new_user)
            
            # 手动提交，因为db_transaction会处理事务
            # 这里也可以不调用commit，让上下文管理器处理
            # db.commit()
            
            # 刷新以获取数据库生成的ID
            db.refresh(new_user)
            
            return new_user
        except Exception as e:
            # 记录详细错误信息
            log_error("CreateUserError", f"创建用户失败: {str(e)}", exc_info=True)
            # 重新抛出，让装饰器处理
            raise


@router.get("/users/{user_id}", response_model=UserResponse, summary="获取用户信息")
@handle_exceptions
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    根据用户ID获取用户信息
    
    - **user_id**: 用户ID
    
    返回用户详细信息
    """
    try:
        # 查询用户
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            # 使用FastAPI内置的HTTPException
            raise HTTPException(status_code=404, detail="用户不存在")
            
            # 或者使用我们的自定义异常
            # raise CustomException(
            #     status_code=404,
            #     message="用户不存在",
            #     error_type="UserNotFound"
            # )
        
        return user
    except Exception as e:
        log_error("GetUserError", f"获取用户信息失败: {str(e)}", exc_info=True)
        raise


@router.get("/simulate-error", summary="模拟错误")
@handle_exceptions
async def simulate_error(error_type: str = "general"):
    """
    模拟不同类型的错误（用于测试异常处理）
    
    - **error_type**: 错误类型 (general, database, custom, http)
    """
    if error_type == "general":
        # 模拟一般错误
        raise Exception("这是一个模拟的一般错误")
    elif error_type == "database":
        # 模拟数据库错误
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("这是一个模拟的数据库错误")
    elif error_type == "custom":
        # 模拟自定义错误
        raise CustomException(
            status_code=400,
            message="这是一个模拟的自定义错误",
            error_type="SimulatedCustomError"
        )
    elif error_type == "http":
        # 模拟HTTP错误
        raise HTTPException(status_code=401, detail="这是一个模拟的HTTP错误")
    else:
        return {"status": "success", "message": "没有触发任何错误"}


@router.get("/test-transaction", summary="测试事务")
@handle_exceptions
async def test_transaction(
    should_fail: bool = False,
    db: Session = Depends(get_db)
):
    """
    测试事务的提交和回滚
    
    - **should_fail**: 是否故意触发失败以测试回滚
    """
    try:
        async with db_transaction(db):
            # 模拟一些数据库操作
            test_user = User(
                username="test_transaction",
                email="test_transaction@example.com",
                password_hash="test_password"
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            if should_fail:
                # 故意触发错误以测试回滚
                raise Exception("故意触发错误以测试事务回滚")
            
            return {"status": "success", "message": "事务测试成功"}
    except Exception as e:
        # 这个异常会被db_transaction捕获并处理回滚
        # 然后会被handle_exceptions装饰器捕获并返回统一错误响应
        # 所以这里实际上不需要额外的处理
        raise