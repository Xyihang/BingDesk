"""
课程表服务 (重构版)
只分单周、双周、全周，彻底删除1-30周冗余！
"""
from typing import Optional, List
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from loguru import logger

from app.models.course import Course


class CourseService:
    """课程表管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[int, List[Course]]:
        """获取所有课程"""
        result = await self.db.execute(
            select(Course).order_by(Course.day_of_week, Course.start_time).offset(skip).limit(limit)
        )
        courses = result.scalars().all()
        
        count_result = await self.db.execute(select(Course))
        total = len(count_result.scalars().all())
        
        return total, courses
    
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        """根据 ID 获取课程"""
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_day(self, day_of_week: int) -> List[Course]:
        """获取指定星期几的课程"""
        result = await self.db.execute(
            select(Course)
            .where(Course.day_of_week == day_of_week)
            .order_by(Course.start_time)
        )
        return list(result.scalars().all())
    
    async def get_today(self) -> List[Course]:
        """获取今日课程"""
        today = date.today().weekday() + 1  # Python weekday: 0=Monday, 转换为 1=Monday
        return await self.get_by_day(today)
    
    async def get_by_week_type(self, week_type: str) -> List[Course]:
        """获取指定周类型的课程: odd(单周), even(双周), all(全周)"""
        result = await self.db.execute(
            select(Course)
            .where(
                or_(
                    Course.week_type == week_type,
                    Course.week_type == "all",
                )
            )
            .order_by(Course.day_of_week, Course.start_time)
        )
        return list(result.scalars().all())
    
    async def get_for_week_number(self, week_number: int) -> List[Course]:
        """根据周号获取对应的课程（自动识别单双周）"""
        week_type = "odd" if week_number % 2 == 1 else "even"
        return await self.get_by_week_type(week_type)
    
    async def create(
        self,
        course_name: str,
        day_of_week: int,
        start_time: time,
        end_time: time,
        teacher: Optional[str] = None,
        classroom: Optional[str] = None,
        week_type: str = "all",
        color: str = "#1890ff",
        notes: Optional[str] = None,
    ) -> Course:
        """创建课程"""
        course = Course(
            course_name=course_name,
            teacher=teacher,
            classroom=classroom,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            week_type=week_type,
            color=color,
            notes=notes,
        )
        
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        
        logger.info(f"课程创建成功: {course.id} - {course.course_name}")
        return course
    
    async def update(
        self,
        course_id: int,
        **kwargs,
    ) -> Course:
        """更新课程"""
        course = await self.get_by_id(course_id)
        if not course:
            raise ValueError(f"课程不存在: {course_id}")
        
        for key, value in kwargs.items():
            if hasattr(course, key) and value is not None:
                setattr(course, key, value)
        
        await self.db.commit()
        await self.db.refresh(course)
        
        logger.info(f"课程更新成功: {course.id}")
        return course
    
    async def delete(self, course_id: int) -> bool:
        """删除课程"""
        course = await self.get_by_id(course_id)
        if not course:
            raise ValueError(f"课程不存在: {course_id}")
        
        await self.db.delete(course)
        await self.db.commit()
        
        logger.info(f"课程删除成功: {course_id}")
        return True
    
    async def batch_delete(self, course_ids: List[int]) -> int:
        """批量删除课程"""
        count = 0
        for course_id in course_ids:
            try:
                await self.delete(course_id)
                count += 1
            except Exception as e:
                logger.warning(f"删除课程 {course_id} 失败: {e}")
        
        return count
