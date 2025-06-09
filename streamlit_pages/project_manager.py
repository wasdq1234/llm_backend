"""
프로젝트 관리 시스템 Streamlit UI
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid


class ProjectManager:
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
    
    def get_profiles(self) -> Dict:
        """프로필 목록을 조회합니다."""
        return self._make_request("GET", "/profiles/")
    
    def get_careers(self, profile_id: str) -> Dict:
        """경력사항 목록을 조회합니다."""
        return self._make_request("GET", f"/profiles/{profile_id}/careers")
    
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


def render_project_manager(base_url: str):
    """프로젝트 관리 UI를 렌더링합니다."""
    st.header("📁 프로젝트 관리 시스템")
    
    pm = ProjectManager(base_url)
    
    # 프로필 선택
    st.subheader("1️⃣ 프로필 선택")
    profile_response = pm.get_profiles()
    
    if not profile_response.get("success"):
        st.error(f"프로필 목록 조회 실패: {profile_response.get('error')}")
        return
    
    profiles = profile_response.get("data", [])
    if not profiles:
        st.warning("등록된 프로필이 없습니다. 먼저 프로필을 생성해주세요.")
        return
    
    # 프로필 선택 드롭다운
    profile_options = {f"{p['name']} ({p['email']})": p['id'] for p in profiles}
    selected_profile_name = st.selectbox(
        "프로필을 선택하세요:",
        options=list(profile_options.keys()),
        key="project_profile_select"
    )
    
    if not selected_profile_name:
        st.info("프로필을 선택해주세요.")
        return
    
    selected_profile_id = profile_options[selected_profile_name]
    
    # 경력사항 선택
    st.subheader("2️⃣ 경력사항 선택")
    career_response = pm.get_careers(selected_profile_id)
    
    if not career_response.get("success"):
        st.error(f"경력사항 목록 조회 실패: {career_response.get('error')}")
        return
    
    careers = career_response.get("data", [])
    if not careers:
        st.warning("등록된 경력사항이 없습니다. 먼저 경력사항을 생성해주세요.")
        return
    
    # 경력사항 선택 드롭다운
    career_options = {f"{c['company_name']} - {c.get('position', '직책없음')} ({c['start_date']}~{c.get('end_date', '현재')})": c['id'] for c in careers}
    selected_career_name = st.selectbox(
        "경력사항을 선택하세요:",
        options=list(career_options.keys()),
        key="project_career_select"
    )
    
    if not selected_career_name:
        st.info("경력사항을 선택해주세요.")
        return
    
    selected_career_id = career_options[selected_career_name]
    
    # 선택된 경력사항 정보 표시
    selected_career = next(c for c in careers if c['id'] == selected_career_id)
    with st.expander("📋 선택된 경력사항 정보", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**회사명:** {selected_career['company_name']}")
            st.write(f"**직책:** {selected_career.get('position', 'N/A')}")
        with col2:
            st.write(f"**근무기간:** {selected_career['start_date']} ~ {selected_career.get('end_date', '현재')}")
            if selected_career.get('job_description'):
                st.write(f"**업무내용:** {selected_career['job_description'][:100]}...")
    
    st.divider()
    
    # 프로젝트 관리 탭
    tab1, tab2, tab3 = st.tabs(["📋 프로젝트 목록", "➕ 프로젝트 추가", "✏️ 프로젝트 편집"])
    
    with tab1:
        render_project_list(pm, selected_career_id)
    
    with tab2:
        render_project_create(pm, selected_career_id)
    
    with tab3:
        render_project_edit(pm, selected_career_id)


def render_project_list(pm: ProjectManager, career_id: str):
    """프로젝트 목록을 렌더링합니다."""
    st.subheader("📋 프로젝트 목록")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 새로고침", key="refresh_projects"):
            st.rerun()
    
    # 프로젝트 목록 조회
    response = pm.get_projects(career_id)
    
    if response.get("success"):
        projects = response.get("data", [])
        
        if projects:
            st.write(f"**총 {len(projects)}개의 프로젝트가 있습니다.**")
            
            for i, project in enumerate(projects):
                with st.expander(f"📁 {project['project_name']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**프로젝트명:** {project['project_name']}")
                        
                        if project.get('start_date'):
                            st.write(f"**시작일:** {project['start_date']}")
                        else:
                            st.write(f"**시작일:** 정보 없음")
                            
                        if project.get('end_date'):
                            st.write(f"**종료일:** {project['end_date']}")
                            # 프로젝트 기간 계산
                            if project.get('start_date'):
                                start_date = datetime.strptime(project['start_date'], '%Y-%m-%d').date()
                                end_date = datetime.strptime(project['end_date'], '%Y-%m-%d').date()
                                duration = end_date - start_date
                                months = duration.days // 30
                                days = duration.days % 30
                                st.write(f"**프로젝트 기간:** 약 {months}개월 {days}일")
                        else:
                            st.write(f"**종료일:** 진행중")
                            if project.get('start_date'):
                                start_date = datetime.strptime(project['start_date'], '%Y-%m-%d').date()
                                current_date = date.today()
                                duration = current_date - start_date
                                months = duration.days // 30
                                days = duration.days % 30
                                st.write(f"**프로젝트 기간:** 약 {months}개월 {days}일 (진행중)")
                    
                    with col2:
                        if project.get('description'):
                            st.write(f"**프로젝트 설명:**")
                            st.write(project['description'])
                        else:
                            st.write("**프로젝트 설명:** 정보 없음")
                        
                        if project.get('technologies'):
                            st.write(f"**사용 기술:**")
                            # 기술 스택을 태그 형태로 표시
                            tech_tags = " ".join([f"`{tech}`" for tech in project['technologies']])
                            st.markdown(tech_tags)
                        else:
                            st.write("**사용 기술:** 정보 없음")
                    
                    with col3:
                        st.write(f"**생성일:** {project['created_at'][:10]}")
                        
                        # 삭제 버튼
                        if st.button("🗑️ 삭제", key=f"delete_project_{project['id']}"):
                            if st.session_state.get(f"confirm_delete_project_{project['id']}", False):
                                delete_response = pm.delete_project(project['id'])
                                if delete_response.get("success"):
                                    st.success("프로젝트가 삭제되었습니다!")
                                    st.rerun()
                                else:
                                    st.error(f"삭제 실패: {delete_response.get('error')}")
                            else:
                                st.session_state[f"confirm_delete_project_{project['id']}"] = True
                                st.warning("한 번 더 클릭하면 삭제됩니다.")
        else:
            st.info("등록된 프로젝트가 없습니다.")
    else:
        st.error(f"프로젝트 목록 조회 실패: {response.get('error')}")


def render_project_create(pm: ProjectManager, career_id: str):
    """프로젝트 생성 폼을 렌더링합니다."""
    st.subheader("➕ 새 프로젝트 추가")
    
    with st.form("create_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "프로젝트명 *", 
                placeholder="예: 온라인 쇼핑몰 개발",
                help="프로젝트 이름을 입력하세요"
            )
            
            # 시작일 (년도, 월만 입력)
            st.write("**시작일**")
            start_col1, start_col2 = st.columns(2)
            with start_col1:
                start_year = st.number_input("시작년도", min_value=1980, max_value=2030, value=date.today().year, step=1)
            with start_col2:
                start_month = st.number_input("시작월", min_value=1, max_value=12, value=date.today().month, step=1)
            start_date = date(start_year, start_month, 1)
            
        with col2:
            is_ongoing = st.checkbox("진행중", value=False)
            end_date = None
            if not is_ongoing:
                # 종료일 (년도, 월만 입력)
                st.write("**종료일**")
                end_col1, end_col2 = st.columns(2)
                with end_col1:
                    end_year = st.number_input("종료년도", min_value=1980, max_value=2030, value=date.today().year, step=1)
                with end_col2:
                    end_month = st.number_input("종료월", min_value=1, max_value=12, value=date.today().month, step=1)
                end_date = date(end_year, end_month, 1)
            else:
                st.info("진행중인 경우 종료일을 비워둡니다.")
        
        description = st.text_area(
            "프로젝트 설명",
            placeholder="프로젝트의 주요 내용과 역할을 설명하세요",
            height=100,
            help="프로젝트에 대한 상세한 설명을 입력하세요"
        )
        
        # 기술 스택 입력
        st.write("**사용 기술 스택**")
        tech_input = st.text_input(
            "기술들을 쉼표로 구분해서 입력하세요",
            placeholder="예: Python, FastAPI, PostgreSQL, React, Docker",
            help="사용한 기술들을 쉼표(,)로 구분하여 입력하세요"
        )
        
        # 미리보기
        if tech_input:
            technologies = [tech.strip() for tech in tech_input.split(',') if tech.strip()]
            if technologies:
                st.write("**기술 스택 미리보기:**")
                tech_preview = " ".join([f"`{tech}`" for tech in technologies])
                st.markdown(tech_preview)
        
        submitted = st.form_submit_button("✅ 프로젝트 생성", type="primary")
        
        if submitted:
            # 필수 필드 검증
            if not project_name.strip():
                st.error("프로젝트명은 필수 입력사항입니다.")
                return
            
            # 날짜 검증
            if not is_ongoing and end_date and start_date > end_date:
                st.error("시작년월이 종료년월보다 늦을 수 없습니다.")
                return
            
            # 기술 스택 처리
            technologies = []
            if tech_input:
                technologies = [tech.strip() for tech in tech_input.split(',') if tech.strip()]
            
            # 프로젝트 데이터 구성
            project_data = {
                "project_name": project_name.strip(),
                "description": description.strip() if description.strip() else None,
                "technologies": technologies,
                "career_id": career_id  # career_id 추가
            }
            
            # 날짜 추가
            project_data["start_date"] = start_date.isoformat()
            if not is_ongoing and end_date:
                project_data["end_date"] = end_date.isoformat()
            
            # API 호출
            with st.spinner("프로젝트를 생성하는 중..."):
                response = pm.create_project(career_id, project_data)
                
                if response.get("success"):
                    st.success("✅ 프로젝트가 성공적으로 생성되었습니다!")
                    st.balloons()
                    
                    # 생성된 프로젝트 정보 표시
                    with st.expander("생성된 프로젝트 정보", expanded=True):
                        project = response.get("data")
                        if project:
                            st.json(project)
                    
                    # 페이지 새로고침을 위한 버튼
                    if st.button("🔄 목록으로 돌아가기"):
                        st.rerun()
                else:
                    st.error(f"❌ 프로젝트 생성 실패: {response.get('error', '알 수 없는 오류')}")


def render_project_edit(pm: ProjectManager, career_id: str):
    """프로젝트 편집 폼을 렌더링합니다."""
    st.subheader("✏️ 프로젝트 편집")
    
    # 먼저 편집할 프로젝트 선택
    response = pm.get_projects(career_id)
    
    if not response.get("success"):
        st.error(f"프로젝트 목록 조회 실패: {response.get('error')}")
        return
    
    projects = response.get("data", [])
    if not projects:
        st.info("편집할 프로젝트가 없습니다. 먼저 프로젝트를 생성해주세요.")
        return
    
    # 프로젝트 선택
    project_options = {f"{p['project_name']} ({p.get('start_date', 'N/A')} ~ {p.get('end_date', '진행중')})": p for p in projects}
    selected_project_name = st.selectbox(
        "편집할 프로젝트를 선택하세요:",
        options=list(project_options.keys()),
        key="edit_project_select"
    )
    
    if not selected_project_name:
        return
    
    selected_project = project_options[selected_project_name]
    
    # 선택된 프로젝트 정보 표시
    with st.expander("현재 프로젝트 정보", expanded=False):
        st.json(selected_project)
    
    # 편집 폼
    with st.form("edit_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "프로젝트명",
                value=selected_project.get('project_name', ''),
                help="프로젝트 이름을 수정하세요"
            )
            
            # 기존 시작일이 있으면 파싱, 없으면 현재 날짜
            current_start_date = None
            if selected_project.get('start_date'):
                try:
                    current_start_date = datetime.strptime(selected_project['start_date'], '%Y-%m-%d').date()
                except:
                    current_start_date = date.today()
            else:
                current_start_date = date.today()
            
            # 시작일 (년도, 월만 입력)
            st.write("**시작일**")
            start_col1, start_col2 = st.columns(2)
            with start_col1:
                start_year = st.number_input("시작년도", min_value=1980, max_value=2030, value=current_start_date.year, step=1, key="edit_start_year")
            with start_col2:
                start_month = st.number_input("시작월", min_value=1, max_value=12, value=current_start_date.month, step=1, key="edit_start_month")
            start_date = date(start_year, start_month, 1)
            
        with col2:
            is_ongoing = st.checkbox("진행중", value=selected_project.get('end_date') is None)
            end_date = None
            if not is_ongoing:
                # 기존 종료일이 있으면 파싱, 없으면 현재 날짜
                current_end_date = None
                if selected_project.get('end_date'):
                    try:
                        current_end_date = datetime.strptime(selected_project['end_date'], '%Y-%m-%d').date()
                    except:
                        current_end_date = date.today()
                else:
                    current_end_date = date.today()
                
                # 종료일 (년도, 월만 입력)
                st.write("**종료일**")
                end_col1, end_col2 = st.columns(2)
                with end_col1:
                    end_year = st.number_input("종료년도", min_value=1980, max_value=2030, value=current_end_date.year, step=1, key="edit_end_year")
                with end_col2:
                    end_month = st.number_input("종료월", min_value=1, max_value=12, value=current_end_date.month, step=1, key="edit_end_month")
                end_date = date(end_year, end_month, 1)
            else:
                st.info("진행중인 경우 종료일을 비워둡니다.")
        
        description = st.text_area(
            "프로젝트 설명",
            value=selected_project.get('description', ''),
            height=100,
            help="프로젝트에 대한 상세한 설명을 수정하세요"
        )
        
        # 기술 스택 수정
        st.write("**사용 기술 스택**")
        current_tech = selected_project.get('technologies', [])
        tech_input = st.text_input(
            "기술들을 쉼표로 구분해서 입력하세요",
            value=', '.join(current_tech) if current_tech else '',
            help="사용한 기술들을 쉼표(,)로 구분하여 입력하세요"
        )
        
        # 미리보기
        if tech_input:
            technologies = [tech.strip() for tech in tech_input.split(',') if tech.strip()]
            if technologies:
                st.write("**기술 스택 미리보기:**")
                tech_preview = " ".join([f"`{tech}`" for tech in technologies])
                st.markdown(tech_preview)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ 프로젝트 수정", type="primary")
        with col2:
            clear_dates = st.form_submit_button("📅 날짜 지우기", help="시작일과 종료일을 모두 지웁니다")
        
        if clear_dates:
            st.info("날짜를 지우려면 위의 날짜 입력란을 직접 수정하세요.")
        
        if submitted:
            # 필수 필드 검증
            if not project_name.strip():
                st.error("프로젝트명은 필수 입력사항입니다.")
                return
            
            # 날짜 검증
            if not is_ongoing and end_date and start_date > end_date:
                st.error("시작년월이 종료년월보다 늦을 수 없습니다.")
                return
            
            # 기술 스택 처리
            technologies = []
            if tech_input:
                technologies = [tech.strip() for tech in tech_input.split(',') if tech.strip()]
            
            # 프로젝트 데이터 구성
            project_data = {
                "project_name": project_name.strip(),
                "description": description.strip() if description.strip() else None,
                "technologies": technologies
            }
            
            # 날짜 추가
            project_data["start_date"] = start_date.isoformat()
            if not is_ongoing and end_date:
                project_data["end_date"] = end_date.isoformat()
            
            # API 호출
            with st.spinner("프로젝트를 수정하는 중..."):
                update_response = pm.update_project(selected_project['id'], project_data)
                
                if update_response.get("success"):
                    st.success("✅ 프로젝트가 성공적으로 수정되었습니다!")
                    
                    # 수정된 프로젝트 정보 표시
                    with st.expander("수정된 프로젝트 정보", expanded=True):
                        project = update_response.get("data")
                        if project:
                            st.json(project)
                    
                    # 페이지 새로고침을 위한 버튼
                    if st.button("🔄 목록으로 돌아가기"):
                        st.rerun()
                else:
                    st.error(f"❌ 프로젝트 수정 실패: {update_response.get('error', '알 수 없는 오류')}")


def main():
    """메인 실행 함수"""
    st.set_page_config(
        page_title="프로젝트 관리 시스템",
        page_icon="📁",
        layout="wide"
    )
    
    render_project_manager("http://localhost:8000")


if __name__ == "__main__":
    main() 