"""
Career 관리 시스템 Streamlit UI
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid


class CareerManager:
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
    
    def get_profile(self, profile_id: str) -> Dict:
        """프로필을 조회합니다."""
        return self._make_request("GET", f"/profiles/{profile_id}")
    
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


def render_career_manager(base_url: str):
    """Career 관리 UI를 렌더링합니다."""
    st.header("💼 Career 관리 시스템")
    
    cm = CareerManager(base_url)
    
    # 프로필 선택
    st.subheader("1️⃣ 프로필 선택")
    profile_response = cm.get_profiles()
    
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
        key="career_profile_select"
    )
    
    if not selected_profile_name:
        st.info("프로필을 선택해주세요.")
        return
    
    selected_profile_id = profile_options[selected_profile_name]
    
    # 선택된 프로필 정보 표시
    selected_profile = next(p for p in profiles if p['id'] == selected_profile_id)
    with st.expander("📋 선택된 프로필 정보", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**이름:** {selected_profile['name']}")
            st.write(f"**이메일:** {selected_profile['email']}")
        with col2:
            st.write(f"**전화번호:** {selected_profile.get('phone', 'N/A')}")
            st.write(f"**생성일:** {selected_profile['created_at'][:10]}")
    
    st.divider()
    
    # Career 관리 탭
    tab1, tab2, tab3 = st.tabs(["📋 Career 목록", "➕ Career 추가", "✏️ Career 편집"])
    
    with tab1:
        render_career_list(cm, selected_profile_id)
    
    with tab2:
        render_career_create(cm, selected_profile_id)
    
    with tab3:
        render_career_edit(cm, selected_profile_id)


def render_career_list(cm: CareerManager, profile_id: str):
    """Career 목록을 렌더링합니다."""
    st.subheader("📋 Career 목록")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 새로고침", key="refresh_careers"):
            st.rerun()
    
    # Career 목록 조회
    response = cm.get_careers(profile_id)
    
    if response.get("success"):
        careers = response.get("data", [])
        
        if careers:
            st.write(f"**총 {len(careers)}개의 경력사항이 있습니다.**")
            
            for i, career in enumerate(careers):
                with st.expander(f"💼 {career['company_name']} - {career.get('position', '직책 정보 없음')}", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**회사명:** {career['company_name']}")
                        st.write(f"**직책:** {career.get('position', 'N/A')}")
                        st.write(f"**입사일:** {career['start_date']}")
                        
                        if career.get('end_date'):
                            st.write(f"**퇴사일:** {career['end_date']}")
                            # 근무 기간 계산
                            start_date = datetime.strptime(career['start_date'], '%Y-%m-%d').date()
                            end_date = datetime.strptime(career['end_date'], '%Y-%m-%d').date()
                            duration = end_date - start_date
                            years = duration.days // 365
                            months = (duration.days % 365) // 30
                            st.write(f"**근무 기간:** 약 {years}년 {months}개월")
                        else:
                            st.write(f"**퇴사일:** 현재 재직중")
                            # 현재까지 근무 기간
                            start_date = datetime.strptime(career['start_date'], '%Y-%m-%d').date()
                            current_date = date.today()
                            duration = current_date - start_date
                            years = duration.days // 365
                            months = (duration.days % 365) // 30
                            st.write(f"**근무 기간:** 약 {years}년 {months}개월 (현재)")
                    
                    with col2:
                        if career.get('job_description'):
                            st.write(f"**업무 내용:**")
                            st.write(career['job_description'])
                        else:
                            st.write("**업무 내용:** 정보 없음")
                    
                    with col3:
                        st.write(f"**생성일:** {career['created_at'][:10]}")
                        
                        # 삭제 버튼
                        if st.button("🗑️ 삭제", key=f"delete_career_{career['id']}"):
                            if st.session_state.get(f"confirm_delete_{career['id']}", False):
                                delete_response = cm.delete_career(career['id'])
                                if delete_response.get("success"):
                                    st.success("경력사항이 삭제되었습니다!")
                                    st.rerun()
                                else:
                                    st.error(f"삭제 실패: {delete_response.get('error')}")
                            else:
                                st.session_state[f"confirm_delete_{career['id']}"] = True
                                st.warning("한 번 더 클릭하면 삭제됩니다.")
        else:
            st.info("등록된 경력사항이 없습니다.")
    else:
        st.error(f"경력사항 목록 조회 실패: {response.get('error')}")


def render_career_create(cm: CareerManager, profile_id: str):
    """Career 생성 폼을 렌더링합니다."""
    st.subheader("➕ 새 Career 추가")
    
    with st.form("create_career_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("회사명 *", placeholder="예: 구글코리아")
            position = st.text_input("직책", placeholder="예: 시니어 소프트웨어 엔지니어")
            
            # 입사일 (년도, 월만 입력)
            st.write("**입사일 ***")
            start_col1, start_col2 = st.columns(2)
            with start_col1:
                start_year = st.number_input("입사년도", min_value=1980, max_value=2030, value=date.today().year, step=1)
            with start_col2:
                start_month = st.number_input("입사월", min_value=1, max_value=12, value=date.today().month, step=1)
            start_date = date(start_year, start_month, 1)
        
        with col2:
            is_current = st.checkbox("현재 재직중", value=False)
            end_date = None
            if not is_current:
                # 퇴사일 (년도, 월만 입력)
                st.write("**퇴사일**")
                end_col1, end_col2 = st.columns(2)
                with end_col1:
                    end_year = st.number_input("퇴사년도", min_value=1980, max_value=2030, value=date.today().year, step=1)
                with end_col2:
                    end_month = st.number_input("퇴사월", min_value=1, max_value=12, value=date.today().month, step=1)
                end_date = date(end_year, end_month, 1)
            else:
                st.info("현재 재직중인 경우 퇴사일을 비워둡니다.")
        
        job_description = st.text_area(
            "업무 내용", 
            placeholder="주요 업무와 성과를 상세히 입력해주세요...",
            height=150
        )
        
        submitted = st.form_submit_button("✅ Career 추가")
        
        if submitted:
            if not company_name:
                st.error("회사명은 필수 입력 항목입니다.")
            elif not is_current and end_date and start_date > end_date:
                st.error("입사년월이 퇴사년월보다 늦을 수 없습니다.")
            else:
                career_data = {
                    "profile_id": profile_id,
                    "company_name": company_name,
                    "position": position if position else None,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat() if end_date and not is_current else None,
                    "job_description": job_description if job_description else None
                }
                
                response = cm.create_career(profile_id, career_data)
                
                if response.get("success"):
                    st.success("경력사항이 성공적으로 추가되었습니다!")
                    st.balloons()
                    # 폼 초기화를 위해 rerun
                    st.rerun()
                else:
                    st.error(f"경력사항 추가 실패: {response.get('error')}")


def render_career_edit(cm: CareerManager, profile_id: str):
    """Career 편집 UI를 렌더링합니다."""
    st.subheader("✏️ Career 편집")
    
    # 기존 경력사항 목록 조회
    response = cm.get_careers(profile_id)
    
    if not response.get("success"):
        st.error(f"경력사항 목록 조회 실패: {response.get('error')}")
        return
    
    careers = response.get("data", [])
    if not careers:
        st.info("편집할 경력사항이 없습니다. 먼저 경력사항을 추가해주세요.")
        return
    
    # 편집할 경력사항 선택
    career_options = {
        f"{c['company_name']} - {c.get('position', '직책 없음')} ({c['start_date']})": c 
        for c in careers
    }
    
    selected_career_name = st.selectbox(
        "편집할 경력사항을 선택하세요:",
        options=list(career_options.keys()),
        key="edit_career_select"
    )
    
    if not selected_career_name:
        return
    
    selected_career = career_options[selected_career_name]
    
    st.divider()
    
    # 편집 폼
    with st.form("edit_career_form"):
        st.write(f"**편집 중:** {selected_career['company_name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "회사명 *", 
                value=selected_career['company_name']
            )
            position = st.text_input(
                "직책", 
                value=selected_career.get('position', '')
            )
            
            # 입사일 (년도, 월만 입력)
            current_start = datetime.strptime(selected_career['start_date'], '%Y-%m-%d').date()
            st.write("**입사일 ***")
            start_col1, start_col2 = st.columns(2)
            with start_col1:
                start_year = st.number_input("입사년도", min_value=1980, max_value=2030, value=current_start.year, step=1, key="edit_start_year")
            with start_col2:
                start_month = st.number_input("입사월", min_value=1, max_value=12, value=current_start.month, step=1, key="edit_start_month")
            start_date = date(start_year, start_month, 1)
        
        with col2:
            is_current = st.checkbox(
                "현재 재직중", 
                value=selected_career.get('end_date') is None
            )
            end_date = None
            if not is_current:
                current_end = selected_career.get('end_date')
                if current_end:
                    current_end_date = datetime.strptime(current_end, '%Y-%m-%d').date()
                    # 퇴사일 (년도, 월만 입력)
                    st.write("**퇴사일**")
                    end_col1, end_col2 = st.columns(2)
                    with end_col1:
                        end_year = st.number_input("퇴사년도", min_value=1980, max_value=2030, value=current_end_date.year, step=1, key="edit_end_year")
                    with end_col2:
                        end_month = st.number_input("퇴사월", min_value=1, max_value=12, value=current_end_date.month, step=1, key="edit_end_month")
                    end_date = date(end_year, end_month, 1)
                else:
                    # 퇴사일이 없던 경우 (현재 재직중에서 퇴사로 변경)
                    st.write("**퇴사일**")
                    end_col1, end_col2 = st.columns(2)
                    with end_col1:
                        end_year = st.number_input("퇴사년도", min_value=1980, max_value=2030, value=date.today().year, step=1, key="edit_end_year_new")
                    with end_col2:
                        end_month = st.number_input("퇴사월", min_value=1, max_value=12, value=date.today().month, step=1, key="edit_end_month_new")
                    end_date = date(end_year, end_month, 1)
            else:
                st.info("현재 재직중인 경우 퇴사일을 비워둡니다.")
        
        job_description = st.text_area(
            "업무 내용", 
            value=selected_career.get('job_description', ''),
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 수정 저장")
        with col2:
            if st.form_submit_button("🔄 원래대로"):
                st.rerun()
        
        if submitted:
            if not company_name:
                st.error("회사명은 필수 입력 항목입니다.")
            elif not is_current and end_date and start_date > end_date:
                st.error("입사년월이 퇴사년월보다 늦을 수 없습니다.")
            else:
                career_data = {
                    "company_name": company_name,
                    "position": position if position else None,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat() if end_date and not is_current else None,
                    "job_description": job_description if job_description else None
                }
                
                update_response = cm.update_career(selected_career['id'], career_data)
                
                if update_response.get("success"):
                    st.success("경력사항이 성공적으로 수정되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"경력사항 수정 실패: {update_response.get('error')}")


# 메인 함수
def main():
    """Career 관리 페이지 메인 함수"""
    st.set_page_config(
        page_title="Career 관리 시스템",
        page_icon="💼",
        layout="wide"
    )
    
    # API 서버 URL 설정
    base_url = st.sidebar.text_input(
        "API 서버 URL", 
        value="http://localhost:8000",
        help="FastAPI 서버의 URL을 입력하세요"
    )
    
    if base_url:
        render_career_manager(base_url)
    else:
        st.warning("API 서버 URL을 입력해주세요.")


if __name__ == "__main__":
    main()