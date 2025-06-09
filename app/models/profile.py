"""
프로필 관리 시스템의 Pydantic 모델 정의
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# 프로필 기본 모델
class ProfileBase(BaseModel):
    name: str = Field(..., max_length=100, description="이름")
    address: Optional[str] = Field(None, description="주소")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    email: EmailStr = Field(..., description="이메일")
    bio: Optional[str] = Field(None, description="자기소개")


class ProfileCreate(ProfileBase):
    """프로필 생성용 모델"""
    pass


class ProfileUpdate(BaseModel):
    """프로필 수정용 모델 (모든 필드 선택사항)"""
    name: Optional[str] = Field(None, max_length=100, description="이름")
    address: Optional[str] = Field(None, description="주소")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    email: Optional[EmailStr] = Field(None, description="이메일")
    bio: Optional[str] = Field(None, description="자기소개")


class Profile(ProfileBase):
    """프로필 응답 모델"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 경력사항 모델
class CareerBase(BaseModel):
    company_name: str = Field(..., max_length=200, description="회사명")
    start_date: date = Field(..., description="입사일")
    end_date: Optional[date] = Field(None, description="퇴사일 (현재 재직중이면 null)")
    job_description: Optional[str] = Field(None, description="업무내용")
    position: Optional[str] = Field(None, max_length=100, description="직책")


class CareerCreate(CareerBase):
    """경력사항 생성용 모델"""
    profile_id: UUID = Field(..., description="프로필 ID")


class CareerUpdate(BaseModel):
    """경력사항 수정용 모델"""
    company_name: Optional[str] = Field(None, max_length=200, description="회사명")
    start_date: Optional[date] = Field(None, description="입사일")
    end_date: Optional[date] = Field(None, description="퇴사일")
    job_description: Optional[str] = Field(None, description="업무내용")
    position: Optional[str] = Field(None, max_length=100, description="직책")


class Career(CareerBase):
    """경력사항 응답 모델"""
    id: UUID
    profile_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 프로젝트 모델
class ProjectBase(BaseModel):
    project_name: str = Field(..., max_length=200, description="프로젝트명")
    start_date: Optional[date] = Field(None, description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    description: Optional[str] = Field(None, description="프로젝트 내용")
    technologies: Optional[List[str]] = Field(default=[], description="사용 기술 스택")


class ProjectCreate(ProjectBase):
    """프로젝트 생성용 모델"""
    career_id: UUID = Field(..., description="경력사항 ID")


class ProjectUpdate(BaseModel):
    """프로젝트 수정용 모델"""
    project_name: Optional[str] = Field(None, max_length=200, description="프로젝트명")
    start_date: Optional[date] = Field(None, description="시작일")
    end_date: Optional[date] = Field(None, description="종료일")
    description: Optional[str] = Field(None, description="프로젝트 내용")
    technologies: Optional[List[str]] = Field(None, description="사용 기술 스택")


class Project(ProjectBase):
    """프로젝트 응답 모델"""
    id: UUID
    career_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 전체 프로필 정보 (경력사항과 프로젝트 포함)
class CareerWithProjects(Career):
    """프로젝트가 포함된 경력사항 모델"""
    projects: List[Project] = []


class ProfileWithDetails(Profile):
    """경력사항과 프로젝트가 모두 포함된 전체 프로필 모델"""
    careers: List[CareerWithProjects] = []


# 응답 모델
class ProfileResponse(BaseModel):
    """API 응답용 프로필 모델"""
    success: bool = True
    message: str = "성공"
    data: Optional[Profile] = None


class ProfileListResponse(BaseModel):
    """프로필 목록 응답 모델"""
    success: bool = True
    message: str = "성공"
    data: List[Profile] = []
    total: int = 0


class CareerResponse(BaseModel):
    """경력사항 응답 모델"""
    success: bool = True
    message: str = "성공"
    data: Optional[Career] = None


class ProjectResponse(BaseModel):
    """프로젝트 응답 모델"""
    success: bool = True
    message: str = "성공"
    data: Optional[Project] = None 