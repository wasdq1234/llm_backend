"""
프로필 관리 API 엔드포인트
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.models.profile import (
    ProfileCreate, ProfileUpdate, Profile, ProfileResponse, ProfileListResponse,
    CareerCreate, CareerUpdate, Career, CareerResponse,
    ProjectCreate, ProjectUpdate, Project, ProjectResponse,
    ProfileWithDetails
)
from app.services.profile_service import profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


# 프로필 엔드포인트
@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_data: ProfileCreate):
    """새 프로필을 생성합니다."""
    try:
        profile = await profile_service.create_profile(profile_data)
        return ProfileResponse(
            success=True,
            message="프로필이 성공적으로 생성되었습니다.",
            data=profile
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=ProfileListResponse)
async def get_profiles(
    limit: int = Query(100, ge=1, le=1000, description="조회할 프로필 수"),
    offset: int = Query(0, ge=0, description="건너뛸 프로필 수")
):
    """프로필 목록을 조회합니다."""
    try:
        profiles = await profile_service.get_all_profiles(limit=limit, offset=offset)
        return ProfileListResponse(
            success=True,
            message="프로필 목록을 성공적으로 조회했습니다.",
            data=profiles,
            total=len(profiles)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: UUID):
    """ID로 프로필을 조회합니다."""
    try:
        profile = await profile_service.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필을 찾을 수 없습니다."
            )
        return ProfileResponse(
            success=True,
            message="프로필을 성공적으로 조회했습니다.",
            data=profile
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{profile_id}/details")
async def get_profile_with_details(profile_id: UUID):
    """프로필과 관련된 모든 정보(경력사항, 프로젝트)를 조회합니다."""
    try:
        profile_details = await profile_service.get_profile_with_details(profile_id)
        if not profile_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필을 찾을 수 없습니다."
            )
        return {
            "success": True,
            "message": "전체 프로필 정보를 성공적으로 조회했습니다.",
            "data": profile_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: UUID, profile_data: ProfileUpdate):
    """프로필을 수정합니다."""
    try:
        profile = await profile_service.update_profile(profile_id, profile_data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필을 찾을 수 없습니다."
            )
        return ProfileResponse(
            success=True,
            message="프로필이 성공적으로 수정되었습니다.",
            data=profile
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{profile_id}")
async def delete_profile(profile_id: UUID):
    """프로필을 삭제합니다."""
    try:
        success = await profile_service.delete_profile(profile_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필을 찾을 수 없습니다."
            )
        return {
            "success": True,
            "message": "프로필이 성공적으로 삭제되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 경력사항 엔드포인트
@router.post("/{profile_id}/careers", response_model=CareerResponse, status_code=status.HTTP_201_CREATED)
async def create_career(profile_id: UUID, career_data: CareerCreate):
    """새 경력사항을 생성합니다."""
    try:
        # 프로필 존재 확인
        profile = await profile_service.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필을 찾을 수 없습니다."
            )
        
        # 경력사항의 profile_id 설정
        career_data.profile_id = profile_id
        career = await profile_service.create_career(career_data)
        return CareerResponse(
            success=True,
            message="경력사항이 성공적으로 생성되었습니다.",
            data=career
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{profile_id}/careers")
async def get_careers_by_profile(profile_id: UUID):
    """프로필의 경력사항 목록을 조회합니다."""
    try:
        careers = await profile_service.get_careers_by_profile_id(profile_id)
        return {
            "success": True,
            "message": "경력사항 목록을 성공적으로 조회했습니다.",
            "data": careers
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/careers/{career_id}", response_model=CareerResponse)
async def update_career(career_id: UUID, career_data: CareerUpdate):
    """경력사항을 수정합니다."""
    try:
        career = await profile_service.update_career(career_id, career_data)
        if not career:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="경력사항을 찾을 수 없습니다."
            )
        return CareerResponse(
            success=True,
            message="경력사항이 성공적으로 수정되었습니다.",
            data=career
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/careers/{career_id}")
async def delete_career(career_id: UUID):
    """경력사항을 삭제합니다."""
    try:
        success = await profile_service.delete_career(career_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="경력사항을 찾을 수 없습니다."
            )
        return {
            "success": True,
            "message": "경력사항이 성공적으로 삭제되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 프로젝트 엔드포인트
@router.post("/careers/{career_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(career_id: UUID, project_data: ProjectCreate):
    """새 프로젝트를 생성합니다."""
    try:
        # 경력사항 존재 확인
        career = await profile_service.get_career_by_id(career_id)
        if not career:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="경력사항을 찾을 수 없습니다."
            )
        
        # 프로젝트의 career_id 설정
        project_data.career_id = career_id
        project = await profile_service.create_project(project_data)
        return ProjectResponse(
            success=True,
            message="프로젝트가 성공적으로 생성되었습니다.",
            data=project
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/careers/{career_id}/projects")
async def get_projects_by_career(career_id: UUID):
    """경력사항의 프로젝트 목록을 조회합니다."""
    try:
        projects = await profile_service.get_projects_by_career_id(career_id)
        return {
            "success": True,
            "message": "프로젝트 목록을 성공적으로 조회했습니다.",
            "data": projects
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project_data: ProjectUpdate):
    """프로젝트를 수정합니다."""
    try:
        project = await profile_service.update_project(project_id, project_data)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        return ProjectResponse(
            success=True,
            message="프로젝트가 성공적으로 수정되었습니다.",
            data=project
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/projects/{project_id}")
async def delete_project(project_id: UUID):
    """프로젝트를 삭제합니다."""
    try:
        success = await profile_service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        return {
            "success": True,
            "message": "프로젝트가 성공적으로 삭제되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 