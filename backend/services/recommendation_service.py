from sqlalchemy.orm import Session
from datetime import datetime
import logging
import random

from models import User, UserProfile, HealthInfo, MedicalReport, UserPortrait, \
                     ExaminationItem, RecommendedPackage, PackageItem
from utils.error_handler import CustomException, handle_database_error, log_error, db_transaction

logger = logging.getLogger("app.services.recommendation")

async def get_recommended_packages(
    db: Session,
    user_id: int
) -> list[RecommendedPackage]:
    """
    获取推荐体检套餐
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 推荐套餐列表
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
            
        # 获取用户画像
        user_portrait = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        if not user_portrait:
            # 如果没有用户画像，先生成一个
            user_portrait = await generate_user_portrait(db, user_id)
        
        # 获取所有可用的体检项目
        all_items = db.query(ExaminationItem).filter(ExaminationItem.is_active == True).all()
        
        # 基于用户画像和健康信息生成推荐套餐
        # 这里是简化的推荐逻辑，实际应用中应该有更复杂的算法
        recommended_packages = []
        
        # 创建基础套餐
        basic_package = RecommendedPackage(
            user_id=user_id,
            name="基础体检套餐",
            description="适合健康状况良好的人群",
            total_price=899.0,
            recommended_reason="根据您的健康画像，推荐基础体检项目",
            created_at=datetime.now()
        )
        db.add(basic_package)
        db.flush()  # 为了获取id
        
        # 为基础套餐添加项目
        basic_items = random.sample(all_items, 8)  # 随机选择8个项目
        for item in basic_items:
            package_item = PackageItem(
                package_id=basic_package.id,
                item_id=item.id,
                item_name=item.name,
                item_price=item.price
            )
            db.add(package_item)
        
        # 创建全面套餐
        comprehensive_package = RecommendedPackage(
            user_id=user_id,
            name="全面体检套餐",
            description="适合关注全面健康的人群",
            total_price=1899.0,
            recommended_reason="根据您的健康画像，推荐全面体检项目",
            created_at=datetime.now()
        )
        db.add(comprehensive_package)
        db.flush()  # 为了获取id
        
        # 为全面套餐添加项目
        comprehensive_items = random.sample(all_items, 15)  # 随机选择15个项目
        for item in comprehensive_items:
            package_item = PackageItem(
                package_id=comprehensive_package.id,
                item_id=item.id,
                item_name=item.name,
                item_price=item.price
            )
            db.add(package_item)
        
        db.commit()
        recommended_packages.extend([basic_package, comprehensive_package])
        
        logger.info(f"生成用户推荐套餐: 用户ID={user_id}, 套餐数量={len(recommended_packages)}")
        return recommended_packages
        
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("GetRecommendedPackagesError", f"获取推荐套餐失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="获取推荐套餐失败，请稍后重试",
            error_type="RecommendationError"
        )

async def adjust_recommended_items(
    db: Session,
    package_id: int,
    add_items: list[int] = None,
    remove_items: list[int] = None
) -> RecommendedPackage:
    """
    调整推荐套餐项目
    :param db: 数据库会话
    :param package_id: 套餐ID
    :param add_items: 要添加的项目ID列表
    :param remove_items: 要移除的项目ID列表
    :return: 调整后的套餐
    """
    try:
        async with db_transaction(db):
            # 检查套餐是否存在
            package = db.query(RecommendedPackage).filter(RecommendedPackage.id == package_id).first()
            if not package:
                raise CustomException(
                    status_code=404,
                    message="套餐不存在",
                    error_type="PackageNotFound"
                )
            
            # 移除项目
            if remove_items:
                for item_id in remove_items:
                    package_item = db.query(PackageItem).filter(
                        PackageItem.package_id == package_id,
                        PackageItem.item_id == item_id
                    ).first()
                    if package_item:
                        db.delete(package_item)
            
            # 添加项目
            if add_items:
                for item_id in add_items:
                    # 检查项目是否存在
                    item = db.query(ExaminationItem).filter(ExaminationItem.id == item_id).first()
                    if not item:
                        raise CustomException(
                            status_code=404,
                            message=f"体检项目不存在: {item_id}",
                            error_type="ItemNotFound"
                        )
                    
                    # 检查项目是否已在套餐中
                    existing_item = db.query(PackageItem).filter(
                        PackageItem.package_id == package_id,
                        PackageItem.item_id == item_id
                    ).first()
                    if not existing_item:
                        package_item = PackageItem(
                            package_id=package_id,
                            item_id=item_id,
                            item_name=item.name,
                            item_price=item.price
                        )
                        db.add(package_item)
            
            # 更新套餐总价
            package_items = db.query(PackageItem).filter(PackageItem.package_id == package_id).all()
            package.total_price = sum(item.item_price for item in package_items)
            package.updated_at = datetime.now()
            
            db.commit()
            db.refresh(package)
            
            logger.info(f"调整推荐套餐项目: 套餐ID={package_id}")
            return package
            
    except CustomException as e:
        raise
    except Exception as e:
        handle_database_error(db, e)
        log_error("AdjustRecommendedItemsError", f"调整推荐项目失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="调整推荐项目失败，请稍后重试",
            error_type="AdjustmentError"
        )

async def get_examination_items(
    db: Session,
    category: str = None,
    keyword: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[ExaminationItem]:
    """
    获取体检项目列表
    :param db: 数据库会话
    :param category: 项目分类（可选）
    :param keyword: 关键词搜索（可选）
    :param limit: 返回的记录数量
    :param offset: 偏移量
    :return: 体检项目列表
    """
    try:
        # 构建查询
        query = db.query(ExaminationItem).filter(ExaminationItem.is_active == True)
        
        # 按分类筛选
        if category:
            query = query.filter(ExaminationItem.category == category)
        
        # 按关键词搜索
        if keyword:
            query = query.filter(ExaminationItem.name.ilike(f"%{keyword}%"))
        
        # 排序并分页
        items = query.order_by(ExaminationItem.name).offset(offset).limit(limit).all()
        
        logger.info(f"获取体检项目列表: 数量={len(items)}")
        return items
        
    except Exception as e:
        log_error("GetExaminationItemsError", f"获取体检项目列表失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取体检项目列表失败，请稍后重试",
            error_type="ItemsListError"
        )

# 这个函数在health_info_service.py中也有，为了避免循环导入，这里也定义一下
async def generate_user_portrait(
    db: Session,
    user_id: int
) -> UserPortrait:
    """
    生成用户画像
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 创建的用户画像记录
    """
    try:
        # 获取用户健康信息和体检报告
        health_info = db.query(HealthInfo).filter(HealthInfo.user_id == user_id).first()
        medical_reports = db.query(MedicalReport).filter(MedicalReport.user_id == user_id).all()
        
        # 这里应该有更复杂的用户画像生成逻辑
        # 为了演示，我们简单地创建一个用户画像
        health_risk = "低风险"
        recommended_frequency = "每年一次"
        
        # 检查是否已存在用户画像，如果有则更新，没有则创建
        user_portrait = db.query(UserPortrait).filter(UserPortrait.user_id == user_id).first()
        
        if user_portrait:
            # 更新用户画像
            user_portrait.health_risk = health_risk
            user_portrait.recommended_frequency = recommended_frequency
            user_portrait.generated_at = datetime.now()
        else:
            # 创建用户画像
            user_portrait = UserPortrait(
                user_id=user_id,
                health_risk=health_risk,
                recommended_frequency=recommended_frequency,
                generated_at=datetime.now()
            )
            db.add(user_portrait)
        
        db.commit()
        db.refresh(user_portrait)
        
        return user_portrait
        
    except Exception as e:
        log_error("GenerateUserPortraitError", f"生成用户画像失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="生成用户画像失败，请稍后重试",
            error_type="UserPortraitGenerationError"
        )