from uuid import UUID
from datetime import date
from langchain_core.tools import tool
from app.services.profile_service import ProfileService

# Profile 관련 도구들 정의
@tool
async def get_profile_info(profile_id: str) -> str:
    """Profile UUID로 프로필 기본 정보를 조회합니다."""
    try:
        service = ProfileService()
        profile = await service.get_profile_by_id(UUID(profile_id))
        
        if not profile:
            return f"프로필 ID {profile_id}에 해당하는 정보를 찾을 수 없습니다."
        
        result = f"""프로필 정보:
이름: {profile.name}
이메일: {profile.email}
전화번호: {profile.phone or '정보 없음'}
주소: {profile.address or '정보 없음'}
자기소개: {profile.bio or '자기소개 없음'}"""
        
        return result
    
    except Exception as e:
        return f"프로필 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_careers_by_profile(profile_id: str) -> str:
    """Profile UUID로 해당 프로필의 모든 경력사항을 조회합니다."""
    try:
        service = ProfileService()
        careers = await service.get_careers_by_profile_id(UUID(profile_id))
        
        if not careers:
            return f"프로필 ID {profile_id}에 해당하는 경력사항을 찾을 수 없습니다."
        
        result = f"경력사항 ({len(careers)}개):\n\n"
        
        for i, career in enumerate(careers, 1):
            result += f"{i}. {career.company_name}\n"
            result += f"   직책: {career.position or '정보 없음'}\n"
            result += f"   근무기간: {career.start_date}"
            if career.end_date:
                result += f" ~ {career.end_date}\n"
            else:
                result += f" ~ 현재\n"
            if career.job_description:
                result += f"   업무내용: {career.job_description}\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"경력사항 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_projects_by_profile(profile_id: str) -> str:
    """Profile UUID로 해당 프로필의 모든 프로젝트를 조회합니다."""
    try:
        service = ProfileService()
        # 먼저 경력사항을 조회하고 각 경력의 프로젝트를 가져옴
        careers = await service.get_careers_by_profile_id(UUID(profile_id))
        
        if not careers:
            return f"프로필 ID {profile_id}에 해당하는 경력사항을 찾을 수 없어 프로젝트를 조회할 수 없습니다."
        
        all_projects = []
        for career in careers:
            projects = await service.get_projects_by_career_id(career.id)
            for project in projects:
                # 프로젝트에 회사 정보 추가
                project_info = {
                    "project": project,
                    "company": career.company_name
                }
                all_projects.append(project_info)
        
        if not all_projects:
            return f"프로필 ID {profile_id}에 해당하는 프로젝트를 찾을 수 없습니다."
        
        # 시작일자 기준으로 최신순 정렬
        all_projects.sort(key=lambda x: x["project"].start_date or date(1900, 1, 1), reverse=True)
        
        result = f"프로젝트 ({len(all_projects)}개):\n\n"
        
        for i, project_info in enumerate(all_projects, 1):
            project = project_info["project"]
            company = project_info["company"]
            
            result += f"{i}. {project.project_name}\n"
            result += f"   회사: {company}\n"
            if project.start_date:
                result += f"   기간: {project.start_date}"
                if project.end_date:
                    result += f" ~ {project.end_date}\n"
                else:
                    result += f" ~ 현재\n"
            else:
                result += f"   기간: 정보 없음\n"
            if project.description:
                result += f"   설명: {project.description}\n"
            if project.technologies:
                result += f"   사용기술: {', '.join(project.technologies)}\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_profile_with_full_details(profile_id: str) -> str:
    """Profile UUID로 프로필의 모든 정보(기본정보, 경력, 프로젝트)를 한번에 조회합니다."""
    try:
        service = ProfileService()
        profile_details = await service.get_profile_with_details(UUID(profile_id))
        
        if not profile_details:
            return f"프로필 ID {profile_id}에 해당하는 정보를 찾을 수 없습니다."
        
        result = f"""=== {profile_details.name}님의 상세 프로필 ===

기본 정보:
이름: {profile_details.name}
이메일: {profile_details.email}
전화번호: {profile_details.phone or '정보 없음'}
주소: {profile_details.address or '정보 없음'}
자기소개: {profile_details.bio or '자기소개 없음'}

"""
        
        if profile_details.careers:
            result += f"경력사항 ({len(profile_details.careers)}개):\n"
            for i, career in enumerate(profile_details.careers, 1):
                result += f"\n{i}. {career.company_name} - {career.position or '정보 없음'}\n"
                result += f"   기간: {career.start_date}"
                if career.end_date:
                    result += f" ~ {career.end_date}\n"
                else:
                    result += f" ~ 현재\n"
                if career.job_description:
                    result += f"   업무: {career.job_description}\n"
                
                # 해당 경력의 프로젝트들
                if hasattr(career, 'projects') and career.projects:
                    result += f"프로젝트 ({len(career.projects)}개):\n"
                    for j, project in enumerate(career.projects, 1):
                        result += f"   {i}-{j}. {project.project_name}\n"
                        if project.start_date:
                            result += f"        기간: {project.start_date}"
                            if project.end_date:
                                result += f" ~ {project.end_date}\n"
                            else:
                                result += f" ~ 현재\n"
                        else:
                            result += f"        기간: 정보 없음\n"
                        if project.description:
                            result += f"        설명: {project.description}\n"
                        if project.technologies:
                            result += f"        기술: {', '.join(project.technologies)}\n"
        else:
            result += "등록된 경력사항이 없습니다.\n"
        
        return result
    
    except Exception as e:
        return f"상세 프로필 조회 중 오류가 발생했습니다: {str(e)}"