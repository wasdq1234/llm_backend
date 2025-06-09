"""
프로필 관리 시스템 Streamlit UI
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid


class ProfileManager:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """API 요청을 보내고 응답을 반환합니다."""
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url)
            
            if response.status_code >= 400:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_profile(self, profile_data: Dict) -> Dict:
        """프로필을 생성합니다."""
        return self._make_request("POST", "/profiles/", profile_data)
    
    def get_profiles(self) -> Dict:
        """프로필 목록을 조회합니다."""
        return self._make_request("GET", "/profiles/")
    
    def get_profile(self, profile_id: str) -> Dict:
        """프로필을 조회합니다."""
        return self._make_request("GET", f"/profiles/{profile_id}")
    
    def get_profile_details(self, profile_id: str) -> Dict:
        """프로필 전체 정보를 조회합니다."""
        return self._make_request("GET", f"/profiles/{profile_id}/details")
    
    def update_profile(self, profile_id: str, profile_data: Dict) -> Dict:
        """프로필을 수정합니다."""
        return self._make_request("PUT", f"/profiles/{profile_id}", profile_data)
    
    def delete_profile(self, profile_id: str) -> Dict:
        """프로필을 삭제합니다."""
        return self._make_request("DELETE", f"/profiles/{profile_id}")
    
    def create_career(self, profile_id: str, career_data: Dict) -> Dict:
        """경력사항을 생성합니다."""
        return self._make_request("POST", f"/profiles/{profile_id}/careers", career_data)
    
    def get_careers(self, profile_id: str) -> Dict:
        """경력사항 목록을 조회합니다."""
        return self._make_request("GET", f"/profiles/{profile_id}/careers")
    
    def update_career(self, career_id: str, career_data: Dict) -> Dict:
        """경력사항을 수정합니다."""
        return self._make_request("PUT", f"/profiles/careers/{career_id}", career_data)
    
    def delete_career(self, career_id: str) -> Dict:
        """경력사항을 삭제합니다."""
        return self._make_request("DELETE", f"/profiles/careers/{career_id}")
    
    def create_project(self, career_id: str, project_data: Dict) -> Dict:
        """프로젝트를 생성합니다."""
        return self._make_request("POST", f"/profiles/careers/{career_id}/projects", project_data)
    
    def get_projects(self, career_id: str) -> Dict:
        """프로젝트 목록을 조회합니다."""
        return self._make_request("GET", f"/profiles/careers/{career_id}/projects")
    
    def update_project(self, project_id: str, project_data: Dict) -> Dict:
        """프로젝트를 수정합니다."""
        return self._make_request("PUT", f"/profiles/projects/{project_id}", project_data)
    
    def delete_project(self, project_id: str) -> Dict:
        """프로젝트를 삭제합니다."""
        return self._make_request("DELETE", f"/profiles/projects/{project_id}")


def render_profile_manager(base_url: str):
    """프로필 관리 UI를 렌더링합니다."""
    st.header("👤 프로필 관리 시스템")
    
    pm = ProfileManager(base_url)
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 프로필 목록", "➕ 프로필 생성", "✏️ 프로필 편집", "📊 전체 정보"])
    
    with tab1:
        render_profile_list(pm)
    
    with tab2:
        render_profile_create(pm)
    
    with tab3:
        render_profile_edit(pm)
    
    with tab4:
        render_profile_details(pm)


def render_profile_list(pm: ProfileManager):
    """프로필 목록을 렌더링합니다."""
    st.subheader("📋 프로필 목록")
    
    if st.button("🔄 새로고침", key="refresh_profiles"):
        st.rerun()
    
    # 프로필 목록 조회
    response = pm.get_profiles()
    
    if response.get("success"):
        profiles = response.get("data", [])
        
        if profiles:
            for profile in profiles:
                with st.expander(f"👤 {profile['name']} ({profile['email']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**이메일:** {profile['email']}")
                        st.write(f"**전화번호:** {profile.get('phone', 'N/A')}")
                        st.write(f"**주소:** {profile.get('address', 'N/A')}")
                        if profile.get('bio'):
                            st.write(f"**자기소개:** {profile['bio'][:100]}...")
                        st.write(f"**생성일:** {profile['created_at'][:10]}")
                    
                    with col2:
                        if st.button("🗑️ 삭제", key=f"delete_{profile['id']}"):
                            delete_response = pm.delete_profile(profile['id'])
                            if delete_response.get("success"):
                                st.success("프로필이 삭제되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"삭제 실패: {delete_response.get('error')}")
        else:
            st.info("등록된 프로필이 없습니다.")
    else:
        st.error(f"프로필 목록 조회 실패: {response.get('error')}")


def render_profile_create(pm: ProfileManager):
    """프로필 생성 폼을 렌더링합니다."""
    st.subheader("➕ 새 프로필 생성")
    
    with st.form("create_profile_form"):
        name = st.text_input("이름 *", placeholder="홍길동")
        email = st.text_input("이메일 *", placeholder="hong@example.com")
        phone = st.text_input("전화번호", placeholder="010-1234-5678")
        address = st.text_area("주소", placeholder="서울시 강남구...")
        bio = st.text_area("자기소개", placeholder="안녕하세요! 저는...")
        
        submitted = st.form_submit_button("✅ 프로필 생성")
        
        if submitted:
            if not name or not email:
                st.error("이름과 이메일은 필수 입력 항목입니다.")
            else:
                profile_data = {
                    "name": name,
                    "email": email,
                    "phone": phone if phone else None,
                    "address": address if address else None,
                    "bio": bio if bio else None
                }
                
                response = pm.create_profile(profile_data)
                
                if response.get("success"):
                    st.success("프로필이 성공적으로 생성되었습니다!")
                    st.json(response.get("data"))
                else:
                    st.error(f"프로필 생성 실패: {response.get('error')}")


def render_profile_edit(pm: ProfileManager):
    """프로필 편집 UI를 렌더링합니다."""
    st.subheader("✏️ 프로필 편집")
    
    # 프로필 선택
    profiles_response = pm.get_profiles()
    
    if not profiles_response.get("success"):
        st.error(f"프로필 목록 조회 실패: {profiles_response.get('error')}")
        return
    
    profiles = profiles_response.get("data", [])
    
    if not profiles:
        st.info("편집할 프로필이 없습니다. 먼저 프로필을 생성해주세요.")
        return
    
    # 프로필 선택 드롭다운
    profile_options = {f"{p['name']} ({p['email']})": p['id'] for p in profiles}
    selected_profile_name = st.selectbox("편집할 프로필 선택", list(profile_options.keys()))
    
    if selected_profile_name:
        profile_id = profile_options[selected_profile_name]
        
        # 선택된 프로필 정보 조회
        profile_response = pm.get_profile(profile_id)
        
        if profile_response.get("success"):
            profile = profile_response["data"]
            
            # 편집 탭
            edit_tab1, edit_tab2, edit_tab3 = st.tabs(["📝 기본정보", "💼 경력사항", "🚀 프로젝트"])
            
            with edit_tab1:
                render_profile_basic_edit(pm, profile)
            
            with edit_tab2:
                render_career_management(pm, profile_id)
            
            with edit_tab3:
                render_project_management(pm, profile_id)


def render_profile_basic_edit(pm: ProfileManager, profile: Dict):
    """프로필 기본정보 편집 폼을 렌더링합니다."""
    st.write("**기본 정보 수정**")
    
    with st.form(f"edit_profile_{profile['id']}"):
        name = st.text_input("이름", value=profile['name'])
        email = st.text_input("이메일", value=profile['email'])
        phone = st.text_input("전화번호", value=profile.get('phone', ''))
        address = st.text_area("주소", value=profile.get('address', ''))
        bio = st.text_area("자기소개", value=profile.get('bio', ''))
        
        submitted = st.form_submit_button("💾 수정 저장")
        
        if submitted:
            update_data = {}
            if name != profile['name']:
                update_data["name"] = name
            if email != profile['email']:
                update_data["email"] = email
            if phone != profile.get('phone', ''):
                update_data["phone"] = phone if phone else None
            if address != profile.get('address', ''):
                update_data["address"] = address if address else None
            if bio != profile.get('bio', ''):
                update_data["bio"] = bio if bio else None
            
            if update_data:
                response = pm.update_profile(profile['id'], update_data)
                
                if response.get("success"):
                    st.success("프로필이 성공적으로 수정되었습니다!")
                    st.rerun()
                else:
                    st.error(f"프로필 수정 실패: {response.get('error')}")
            else:
                st.info("변경된 내용이 없습니다.")


def render_career_management(pm: ProfileManager, profile_id: str):
    """경력사항 관리 UI를 렌더링합니다."""
    st.write("**경력사항 관리**")
    
    # 경력사항 목록 조회
    careers_response = pm.get_careers(profile_id)
    
    if careers_response.get("success"):
        careers = careers_response.get("data", [])
        
        # 새 경력사항 추가
        with st.expander("➕ 새 경력사항 추가"):
            with st.form(f"add_career_{profile_id}"):
                company_name = st.text_input("회사명 *")
                position = st.text_input("직책")
                start_date = st.date_input("입사일 *", value=date.today())
                
                # 현재 재직중 체크박스
                is_current = st.checkbox("현재 재직중")
                end_date = None if is_current else st.date_input("퇴사일", value=None)
                
                job_description = st.text_area("업무내용")
                
                submitted = st.form_submit_button("➕ 경력사항 추가")
                
                if submitted:
                    if not company_name:
                        st.error("회사명은 필수 입력 항목입니다.")
                    else:
                        career_data = {
                            "company_name": company_name,
                            "position": position if position else None,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat() if end_date else None,
                            "job_description": job_description if job_description else None
                        }
                        
                        response = pm.create_career(profile_id, career_data)
                        
                        if response.get("success"):
                            st.success("경력사항이 추가되었습니다!")
                            st.rerun()
                        else:
                            st.error(f"경력사항 추가 실패: {response.get('error')}")
        
        # 기존 경력사항 목록
        if careers:
            st.write("**기존 경력사항**")
            for career in careers:
                with st.expander(f"🏢 {career['company_name']} ({career['start_date']} ~ {career.get('end_date', '현재')})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**직책:** {career.get('position', 'N/A')}")
                        st.write(f"**기간:** {career['start_date']} ~ {career.get('end_date', '현재')}")
                        if career.get('job_description'):
                            st.write(f"**업무내용:** {career['job_description']}")
                    
                    with col2:
                        if st.button("🗑️ 삭제", key=f"delete_career_{career['id']}"):
                            delete_response = pm.delete_career(career['id'])
                            if delete_response.get("success"):
                                st.success("경력사항이 삭제되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"삭제 실패: {delete_response.get('error')}")
        else:
            st.info("등록된 경력사항이 없습니다.")
    else:
        st.error(f"경력사항 조회 실패: {careers_response.get('error')}")


def render_project_management(pm: ProfileManager, profile_id: str):
    """프로젝트 관리 UI를 렌더링합니다."""
    st.write("**프로젝트 관리**")
    
    # 경력사항 목록 조회 (프로젝트는 경력사항에 속함)
    careers_response = pm.get_careers(profile_id)
    
    if not careers_response.get("success"):
        st.error(f"경력사항 조회 실패: {careers_response.get('error')}")
        return
    
    careers = careers_response.get("data", [])
    
    if not careers:
        st.info("프로젝트를 추가하려면 먼저 경력사항을 등록해주세요.")
        return
    
    # 경력사항 선택
    career_options = {f"{c['company_name']} ({c['start_date']} ~ {c.get('end_date', '현재')})": c['id'] for c in careers}
    selected_career_name = st.selectbox("경력사항 선택", list(career_options.keys()))
    
    if selected_career_name:
        career_id = career_options[selected_career_name]
        
        # 프로젝트 목록 조회
        projects_response = pm.get_projects(career_id)
        
        if projects_response.get("success"):
            projects = projects_response.get("data", [])
            
            # 새 프로젝트 추가
            with st.expander("➕ 새 프로젝트 추가"):
                with st.form(f"add_project_{career_id}"):
                    project_name = st.text_input("프로젝트명 *")
                    start_date = st.date_input("시작일", value=None)
                    end_date = st.date_input("종료일", value=None)
                    description = st.text_area("프로젝트 내용")
                    technologies = st.text_area("사용 기술 (쉼표로 구분)", placeholder="Python, FastAPI, PostgreSQL")
                    
                    submitted = st.form_submit_button("➕ 프로젝트 추가")
                    
                    if submitted:
                        if not project_name:
                            st.error("프로젝트명은 필수 입력 항목입니다.")
                        else:
                            tech_list = [tech.strip() for tech in technologies.split(",")] if technologies else []
                            
                            project_data = {
                                "project_name": project_name,
                                "start_date": start_date.isoformat() if start_date else None,
                                "end_date": end_date.isoformat() if end_date else None,
                                "description": description if description else None,
                                "technologies": tech_list
                            }
                            
                            response = pm.create_project(career_id, project_data)
                            
                            if response.get("success"):
                                st.success("프로젝트가 추가되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"프로젝트 추가 실패: {response.get('error')}")
            
            # 기존 프로젝트 목록
            if projects:
                st.write("**기존 프로젝트**")
                for project in projects:
                    with st.expander(f"🚀 {project['project_name']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if project.get('start_date') or project.get('end_date'):
                                st.write(f"**기간:** {project.get('start_date', 'N/A')} ~ {project.get('end_date', 'N/A')}")
                            if project.get('description'):
                                st.write(f"**내용:** {project['description']}")
                            if project.get('technologies'):
                                st.write(f"**기술스택:** {', '.join(project['technologies'])}")
                        
                        with col2:
                            if st.button("🗑️ 삭제", key=f"delete_project_{project['id']}"):
                                delete_response = pm.delete_project(project['id'])
                                if delete_response.get("success"):
                                    st.success("프로젝트가 삭제되었습니다!")
                                    st.rerun()
                                else:
                                    st.error(f"삭제 실패: {delete_response.get('error')}")
            else:
                st.info("등록된 프로젝트가 없습니다.")
        else:
            st.error(f"프로젝트 조회 실패: {projects_response.get('error')}")


def render_profile_details(pm: ProfileManager):
    """프로필 전체 정보를 렌더링합니다."""
    st.subheader("📊 전체 정보 조회")
    
    # 프로필 선택
    profiles_response = pm.get_profiles()
    
    if not profiles_response.get("success"):
        st.error(f"프로필 목록 조회 실패: {profiles_response.get('error')}")
        return
    
    profiles = profiles_response.get("data", [])
    
    if not profiles:
        st.info("조회할 프로필이 없습니다.")
        return
    
    profile_options = {f"{p['name']} ({p['email']})": p['id'] for p in profiles}
    selected_profile_name = st.selectbox("조회할 프로필 선택", list(profile_options.keys()), key="details_select")
    
    if selected_profile_name:
        profile_id = profile_options[selected_profile_name]
        
        # 전체 정보 조회
        details_response = pm.get_profile_details(profile_id)
        
        if details_response.get("success"):
            profile_details = details_response["data"]
            
            # 기본 정보
            st.write("### 👤 기본 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**이름:** {profile_details['name']}")
                st.write(f"**이메일:** {profile_details['email']}")
                st.write(f"**전화번호:** {profile_details.get('phone', 'N/A')}")
            
            with col2:
                st.write(f"**주소:** {profile_details.get('address', 'N/A')}")
                st.write(f"**생성일:** {profile_details['created_at'][:10]}")
                st.write(f"**수정일:** {profile_details['updated_at'][:10]}")
            
            if profile_details.get('bio'):
                st.write("**자기소개:**")
                st.write(profile_details['bio'])
            
            # 경력사항 및 프로젝트
            careers = profile_details.get('careers', [])
            
            if careers:
                st.write("### 💼 경력사항 및 프로젝트")
                
                for i, career in enumerate(careers):
                    st.write(f"#### 🏢 {career['company_name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**직책:** {career.get('position', 'N/A')}")
                        st.write(f"**기간:** {career['start_date']} ~ {career.get('end_date', '현재')}")
                    
                    with col2:
                        if career.get('job_description'):
                            st.write(f"**업무내용:** {career['job_description']}")
                    
                    # 프로젝트
                    projects = career.get('projects', [])
                    if projects:
                        st.write("**프로젝트:**")
                        for project in projects:
                            with st.expander(f"🚀 {project['project_name']}"):
                                if project.get('start_date') or project.get('end_date'):
                                    st.write(f"**기간:** {project.get('start_date', 'N/A')} ~ {project.get('end_date', 'N/A')}")
                                if project.get('description'):
                                    st.write(f"**내용:** {project['description']}")
                                if project.get('technologies'):
                                    st.write(f"**기술스택:** {', '.join(project['technologies'])}")
                    
                    if i < len(careers) - 1:  # 마지막이 아니면 구분선 추가
                        st.markdown("---")
            else:
                st.info("등록된 경력사항이 없습니다.")
        else:
            st.error(f"프로필 정보 조회 실패: {details_response.get('error')}") 