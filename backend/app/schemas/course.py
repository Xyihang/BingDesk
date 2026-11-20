"""
Pydantic 模式 - 课程表 (重构版)
只分单周、双周、全周
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import time, datetime


class CourseBase(BaseModel):
    """课程基础模式"""
    course_name: str = Field(..., min_length=1, max_length=100, description="课程名称")
    teacher: Optional[str] = Field(None, max_length=50, description="教师姓名")
    classroom: Optional[str] = Field(None, max_length=50, description="教室位置")
    day_of_week: int = Field(..., ge=1, le=7, description="星期几 (1-7)")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    week_type: str = Field("all", description="周类型: odd(单周), even(双周), all(全周)")
    color: Optional[str] = Field("#1890ff", max_length=20, description="显示颜色")
    notes: Optional[str] = Field(None, description="备注")


class CourseCreate(CourseBase):
    """创建课程模式"""
    pass


class CourseUpdate(BaseModel):
    """更新课程模式（所有字段可选）"""
    course_name: Optional[str] = Field(None, min_length=1, max_length=100)
    teacher: Optional[str] = Field(None, max_length=50)
    classroom: Optional[str] = Field(None, max_length=50)
    day_of_week: Optional[int] = Field(None, ge=1, le=7)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    week_type: Optional[str] = Field(None, description="周类型: odd, even, all")
    color: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class CourseResponse(CourseBase):
    """课程响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """课程列表响应"""
    total: int
    items: list[CourseResponse]
