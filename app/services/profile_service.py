"""
프로필 관리 Supabase 서비스
"""
from typing import List, Optional
from uuid import UUID

from app.core.database import get_supabase_client
from app.models.profile import (
    ProfileCreate, ProfileUpdate, Profile,
    CareerCreate, CareerUpdate, Career,
    ProjectCreate, ProjectUpdate, Project,
    ProfileWithDetails, CareerWithProjects
)


class ProfileService:
    """프로필 관련 데이터베이스 서비스"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    # 프로필 CRUD
    async def create_profile(self, profile_data: ProfileCreate) -> Profile:
        """새 프로필을 생성합니다."""
        try:
            result = self.client.table('profiles').insert(profile_data.model_dump()).execute()
            if result.data:
                return Profile(**result.data[0])
            raise Exception("프로필 생성에 실패했습니다.")
        except Exception as e:
            raise Exception(f"프로필 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_profile_by_id(self, profile_id: UUID) -> Optional[Profile]:
        """ID로 프로필을 조회합니다."""
        try:
            result = self.client.table('profiles').select('*').eq('id', str(profile_id)).execute()
            if result.data:
                return Profile(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"프로필 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_profile_by_email(self, email: str) -> Optional[Profile]:
        """이메일로 프로필을 조회합니다."""
        try:
            result = self.client.table('profiles').select('*').eq('email', email).execute()
            if result.data:
                return Profile(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"프로필 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_all_profiles(self, limit: int = 100, offset: int = 0) -> List[Profile]:
        """모든 프로필을 조회합니다."""
        try:
            result = self.client.table('profiles').select('*').range(offset, offset + limit - 1).execute()
            return [Profile(**profile) for profile in result.data]
        except Exception as e:
            raise Exception(f"프로필 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_profile(self, profile_id: UUID, profile_data: ProfileUpdate) -> Optional[Profile]:
        """프로필을 수정합니다."""
        try:
            # 빈 값 제외하고 업데이트할 데이터만 추출
            update_data = {k: v for k, v in profile_data.model_dump().items() if v is not None}
            if not update_data:
                return await self.get_profile_by_id(profile_id)
            
            result = self.client.table('profiles').update(update_data).eq('id', str(profile_id)).execute()
            if result.data:
                return Profile(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"프로필 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_profile(self, profile_id: UUID) -> bool:
        """프로필을 삭제합니다."""
        try:
            result = self.client.table('profiles').delete().eq('id', str(profile_id)).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"프로필 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # 경력사항 CRUD
    async def create_career(self, career_data: CareerCreate) -> Career:
        """새 경력사항을 생성합니다."""
        try:
            data = career_data.model_dump()
            data['profile_id'] = str(data['profile_id'])
            result = self.client.table('careers').insert(data).execute()
            if result.data:
                return Career(**result.data[0])
            raise Exception("경력사항 생성에 실패했습니다.")
        except Exception as e:
            raise Exception(f"경력사항 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_career_by_id(self, career_id: UUID) -> Optional[Career]:
        """ID로 경력사항을 조회합니다."""
        try:
            result = self.client.table('careers').select('*').eq('id', str(career_id)).execute()
            if result.data:
                return Career(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"경력사항 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_careers_by_profile_id(self, profile_id: UUID) -> List[Career]:
        """프로필 ID로 경력사항 목록을 조회합니다."""
        try:
            result = self.client.table('careers').select('*').eq('profile_id', str(profile_id)).order('start_date', desc=True).execute()
            return [Career(**career) for career in result.data]
        except Exception as e:
            raise Exception(f"경력사항 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_career(self, career_id: UUID, career_data: CareerUpdate) -> Optional[Career]:
        """경력사항을 수정합니다."""
        try:
            update_data = {k: v for k, v in career_data.model_dump().items() if v is not None}
            if not update_data:
                return await self.get_career_by_id(career_id)
            
            result = self.client.table('careers').update(update_data).eq('id', str(career_id)).execute()
            if result.data:
                return Career(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"경력사항 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_career(self, career_id: UUID) -> bool:
        """경력사항을 삭제합니다."""
        try:
            result = self.client.table('careers').delete().eq('id', str(career_id)).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"경력사항 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # 프로젝트 CRUD
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """새 프로젝트를 생성합니다."""
        try:
            data = project_data.model_dump()
            data['career_id'] = str(data['career_id'])
            result = self.client.table('projects').insert(data).execute()
            if result.data:
                return Project(**result.data[0])
            raise Exception("프로젝트 생성에 실패했습니다.")
        except Exception as e:
            raise Exception(f"프로젝트 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """ID로 프로젝트를 조회합니다."""
        try:
            result = self.client.table('projects').select('*').eq('id', str(project_id)).execute()
            if result.data:
                return Project(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_projects_by_career_id(self, career_id: UUID) -> List[Project]:
        """경력사항 ID로 프로젝트 목록을 조회합니다."""
        try:
            result = self.client.table('projects').select('*').eq('career_id', str(career_id)).order('start_date', desc=True).execute()
            return [Project(**project) for project in result.data]
        except Exception as e:
            raise Exception(f"프로젝트 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_project(self, project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]:
        """프로젝트를 수정합니다."""
        try:
            update_data = {k: v for k, v in project_data.model_dump().items() if v is not None}
            if not update_data:
                return await self.get_project_by_id(project_id)
            
            result = self.client.table('projects').update(update_data).eq('id', str(project_id)).execute()
            if result.data:
                return Project(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"프로젝트 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_project(self, project_id: UUID) -> bool:
        """프로젝트를 삭제합니다."""
        try:
            result = self.client.table('projects').delete().eq('id', str(project_id)).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"프로젝트 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # 전체 프로필 정보 조회
    async def get_profile_with_details(self, profile_id: UUID) -> Optional[ProfileWithDetails]:
        """프로필과 관련된 모든 정보(경력사항, 프로젝트)를 조회합니다."""
        try:
            # 프로필 정보 조회
            profile = await self.get_profile_by_id(profile_id)
            if not profile:
                return None
            
            # 경력사항 조회
            careers = await self.get_careers_by_profile_id(profile_id)
            
            # 각 경력사항별 프로젝트 조회
            careers_with_projects = []
            for career in careers:
                projects = await self.get_projects_by_career_id(career.id)
                career_with_projects = CareerWithProjects(**career.model_dump())
                career_with_projects.projects = projects
                careers_with_projects.append(career_with_projects)
            
            # 전체 프로필 정보 구성
            profile_with_details = ProfileWithDetails(**profile.model_dump())
            profile_with_details.careers = careers_with_projects
            
            return profile_with_details
        except Exception as e:
            raise Exception(f"전체 프로필 정보 조회 중 오류가 발생했습니다: {str(e)}")


# 서비스 인스턴스
profile_service = ProfileService() 