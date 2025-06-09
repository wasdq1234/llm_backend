"""
FastAPI 엔드포인트 테스트용 Streamlit UI
"""

import streamlit as st
import requests
import json
from datetime import datetime
import asyncio
import httpx
from streamlit_pages.profile_manager import render_profile_manager

# 페이지 설정
st.set_page_config(
    page_title="FastAPI 시스템 관리",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 FastAPI 시스템 관리")

# 서버 설정
st.sidebar.header("서버 설정")
base_url = st.sidebar.text_input("Base URL", "http://localhost:8000")

# 페이지 선택
st.sidebar.header("메뉴")
page = st.sidebar.selectbox(
    "선택하세요",
    ["📡 API 테스터", "👤 프로필 관리"]
)

if page == "👤 프로필 관리":
    render_profile_manager(base_url)
    st.stop()

# API 테스터 페이지
st.header("📡 API 엔드포인트 테스터")

# 엔드포인트 선택
st.sidebar.header("엔드포인트 선택")
endpoint = st.sidebar.selectbox(
    "테스트할 엔드포인트",
    [
        "GET /",
        "GET /health", 
        "GET /api/v1/chat/health",
        "POST /api/v1/chat/",
        "POST /api/v1/chat/stream"
    ]
)

# 메인 화면
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📨 요청")
    
    if endpoint in ["POST /api/v1/chat/", "POST /api/v1/chat/stream"]:
        st.subheader("채팅 요청 파라미터")
        
        message = st.text_area("메시지", "안녕하세요! 테스트 메시지입니다.")
        conversation_id = st.text_input("대화 ID (선택사항)", "")
        model = st.text_input("모델 (선택사항)", "")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.number_input("최대 토큰수", 1, 4000, 1000)
        
        if endpoint == "POST /api/v1/chat/stream":
            stream = True
        else:
            stream = st.checkbox("스트림 모드", False)
        
        # 요청 데이터 구성
        request_data = {
            "message": message,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if conversation_id:
            request_data["conversation_id"] = conversation_id
        if model:
            request_data["model"] = model
        
        st.subheader("요청 JSON")
        st.json(request_data)
    
    # 테스트 버튼
    if st.button("🚀 테스트 실행"):
        with st.spinner("요청 처리 중..."):
            try:
                if endpoint == "GET /":
                    url = f"{base_url}/"
                    response = requests.get(url)
                    
                elif endpoint == "GET /health":
                    url = f"{base_url}/health"
                    response = requests.get(url)
                    
                elif endpoint == "GET /api/v1/chat/health":
                    url = f"{base_url}/api/v1/chat/health"
                    response = requests.get(url)
                    
                elif endpoint == "POST /api/v1/chat/":
                    url = f"{base_url}/api/v1/chat/"
                    response = requests.post(
                        url,
                        json=request_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                elif endpoint == "POST /api/v1/chat/stream":
                    url = f"{base_url}/api/v1/chat/stream"
                    response = requests.post(
                        url,
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        stream=True
                    )
                
                # 세션 스테이트에 응답 저장
                st.session_state.last_response = response
                st.session_state.last_endpoint = endpoint
                st.session_state.last_url = url
                st.session_state.request_time = datetime.now()
                
            except Exception as e:
                st.error(f"요청 중 오류 발생: {str(e)}")

with col2:
    st.header("📬 응답")
    
    if hasattr(st.session_state, 'last_response'):
        response = st.session_state.last_response
        
        # 응답 정보
        st.subheader("응답 정보")
        st.write(f"**URL:** {st.session_state.last_url}")
        st.write(f"**상태 코드:** {response.status_code}")
        st.write(f"**요청 시간:** {st.session_state.request_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 응답 헤더
        with st.expander("응답 헤더"):
            for key, value in response.headers.items():
                st.write(f"**{key}:** {value}")
        
        # 응답 본문
        st.subheader("응답 본문")
        
        if st.session_state.last_endpoint == "POST /api/v1/chat/stream":
            # 스트림 응답 처리
            st.write("**스트림 응답:**")
            stream_container = st.empty()
            
            try:
                content = ""
                for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk:
                        content += chunk
                        # 실시간으로 스트림 내용 표시
                        stream_container.text_area("스트림 내용", content, height=400)
                        
            except Exception as e:
                st.error(f"스트림 읽기 오류: {str(e)}")
        else:
            # 일반 응답 처리
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    json_response = response.json()
                    st.json(json_response)
                else:
                    st.text(response.text)
            except Exception as e:
                st.error(f"응답 파싱 오류: {str(e)}")
                st.text(response.text)
    else:
        st.info("위의 '테스트 실행' 버튼을 눌러 API를 테스트해보세요.")

# 하단 정보
st.markdown("---")
st.markdown("### 📌 사용 가능한 엔드포인트")
st.markdown("""
- **GET /** - 루트 엔드포인트 (앱 정보)
- **GET /health** - 헬스 체크
- **GET /api/v1/chat/health** - 채팅 서비스 헬스 체크  
- **POST /api/v1/chat/** - 일반 채팅 (논스트림)
- **POST /api/v1/chat/stream** - 스트림 채팅
""")

st.markdown("### 💡 사용법")
st.markdown("""
1. 왼쪽 사이드바에서 서버 URL을 설정하세요 (기본: http://localhost:8000)
2. 테스트하고 싶은 엔드포인트를 선택하세요
3. POST 요청의 경우 필요한 파라미터를 입력하세요
4. '테스트 실행' 버튼을 클릭하여 API를 호출하세요
5. 오른쪽에서 응답 결과를 확인하세요
""") 