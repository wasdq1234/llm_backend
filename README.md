# AI Assistant Chat System

FastAPI, LangChain, Supabase를 사용한 AI 어시스턴트 채팅 시스템 및 프로필 관리 시스템입니다.

## 주요 기능

- 🤖 **AI 어시스턴트**: OpenAI GPT 및 Anthropic Claude 모델 지원
- 💬 **실시간 채팅**: 스트리밍 응답으로 실시간 대화
- 👤 **프로필 관리**: 개인 프로필, 경력사항, 프로젝트 관리
- 🗄️ **Supabase 통합**: PostgreSQL 기반 데이터베이스
- 🔄 **RESTful API**: FastAPI 기반의 현대적인 API
- 🎛️ **설정 가능**: 모델, 온도, 토큰 수 등 유연한 설정

## 프로젝트 구조

```
llm_backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # 채팅 서비스 의존성
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── chat.py          # 채팅 API 엔드포인트
│   │       └── profile.py       # 프로필 관리 API 엔드포인트
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # 애플리케이션 설정
│   │   └── database.py          # Supabase 데이터베이스 연결
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py              # 채팅 데이터 모델
│   │   └── profile.py           # 프로필 관련 데이터 모델
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py      # 채팅 서비스
│   │   └── profile_service.py   # 프로필 관리 서비스
│   └── utils/
│       ├── __init__.py
│       └── logging.py           # 로깅 유틸리티
├── tests/                       # 테스트 파일
├── main.py                      # FastAPI 애플리케이션 진입점
├── pyproject.toml              # 프로젝트 설정 및 의존성
├── supabase_schema.sql         # Supabase 데이터베이스 스키마
├── .env.example                # 환경 변수 예시
└── README.md                   # 프로젝트 문서
```

## 설치 및 실행

### 1. 의존성 설치 (uv 사용)

```bash
# uv가 설치되어 있지 않다면
pip install uv

# 의존성 설치
uv sync
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 편집하여 필요한 설정 추가
# 1. AI 모델: 최소한 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY 중 하나는 필요
# 2. Supabase: SUPABASE_URL과 SUPABASE_KEY 설정 (프로필 관리 기능 사용 시)
```

### 3. Supabase 데이터베이스 설정 (선택사항)

프로필 관리 기능을 사용하려면 Supabase 데이터베이스를 설정해야 합니다:

```bash
# 1. Supabase 프로젝트 생성 (https://supabase.com)
# 2. SQL Editor에서 supabase_schema.sql 파일 실행
# 3. .env 파일에 SUPABASE_URL과 SUPABASE_KEY 추가
```

### 4. 애플리케이션 실행

```bash
# 개발 모드로 실행
uv run python main.py

# 또는 uvicorn 직접 사용
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 사용법

### 채팅 API

#### 기본 채팅

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요!",
    "stream": false
  }'
```

#### 스트리밍 채팅

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "긴 답변이 필요한 질문을 해주세요",
    "conversation_id": "test-conversation"
  }'
```

### 프로필 관리 API

#### 프로필 생성

```bash
curl -X POST "http://localhost:8000/api/v1/profiles/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김개발",
    "email": "kim@example.com",
    "phone": "010-1234-5678",
    "address": "서울시 강남구",
    "bio": "5년차 백엔드 개발자입니다."
  }'
```

#### 프로필 조회

```bash
# 프로필 목록 조회
curl "http://localhost:8000/api/v1/profiles/"

# 특정 프로필 조회
curl "http://localhost:8000/api/v1/profiles/{profile_id}"

# 전체 프로필 정보 조회 (경력사항, 프로젝트 포함)
curl "http://localhost:8000/api/v1/profiles/{profile_id}/details"
```

#### 경력사항 추가

```bash
curl -X POST "http://localhost:8000/api/v1/profiles/{profile_id}/careers" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "테크스타트업",
    "position": "시니어 백엔드 개발자",
    "start_date": "2022-01-01",
    "job_description": "FastAPI를 활용한 백엔드 API 개발"
  }'
```

#### 프로젝트 추가

```bash
curl -X POST "http://localhost:8000/api/v1/profiles/careers/{career_id}/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "AI 챗봇 시스템",
    "start_date": "2023-06-01",
    "end_date": "2024-02-01",
    "description": "LLM을 활용한 고객 서비스 챗봇 시스템 개발",
    "technologies": ["Python", "FastAPI", "LangChain", "PostgreSQL"]
  }'
```



## 테스트 UI

프로필 관리 시스템을 쉽게 테스트할 수 있는 Streamlit 기반 UI를 제공합니다.

### UI 실행

```bash
# Streamlit UI 실행
python run_profile_ui.py

# 또는 직접 실행
uv run streamlit run test_ui.py
```

### UI 기능

- **📡 API 테스터**: 기존 채팅 API 테스트
- **👤 프로필 관리**: 
  - 📋 프로필 목록 조회 및 삭제
  - ➕ 새 프로필 생성
  - ✏️ 프로필 편집 (기본정보, 경력사항, 프로젝트)
  - 📊 전체 정보 조회 (이력서 형태)

### 사용법

1. **서버 시작**: `python main.py`로 FastAPI 서버 실행
2. **UI 시작**: `python run_profile_ui.py`로 Streamlit UI 실행
3. **브라우저 접속**: http://localhost:8501
4. **메뉴 선택**: 사이드바에서 "👤 프로필 관리" 선택
5. **데이터 관리**: 직관적인 UI로 프로필 데이터 관리

## API 문서

애플리케이션 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 지원 모델

### OpenAI 모델
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo

### Anthropic 모델
- claude-3-haiku
- claude-3-sonnet
- claude-3-opus

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DEBUG` | 디버그 모드 | `false` |
| `HOST` | 서버 호스트 | `0.0.0.0` |
| `PORT` | 서버 포트 | `8000` |
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | - |
| `DEFAULT_MODEL` | 기본 모델 | `gpt-4o-mini` |
| `MAX_TOKENS` | 최대 토큰 수 | `1000` |
| `TEMPERATURE` | 모델 온도 | `0.7` |
| `CORS_ORIGINS` | CORS 허용 오리진 | `http://localhost:3000,http://localhost:8080` |
| `SUPABASE_URL` | Supabase 프로젝트 URL | - |
| `SUPABASE_KEY` | Supabase Anon 키 | - |

## 개발

### 테스트 실행

```bash
uv run pytest
```

### 코드 포맷팅

```bash
uv run black .
uv run isort .
```

### 타입 체크

```bash
uv run mypy .
```

## 프로필 관리 시스템

### 데이터 구조

```
프로필 (Profile)
├── 기본 정보: 이름, 이메일, 전화번호, 주소, 자기소개
└── 경력사항 (Career) [1:N]
    ├── 회사명, 직책, 입사일, 퇴사일, 업무내용
    └── 프로젝트 (Project) [1:N]
        └── 프로젝트명, 기간, 내용, 사용기술
```

### 주요 엔드포인트

- **프로필**: `/api/v1/profiles/`
  - `GET /` - 프로필 목록 조회
  - `POST /` - 프로필 생성
  - `GET /{id}` - 프로필 상세 조회
  - `PUT /{id}` - 프로필 수정
  - `DELETE /{id}` - 프로필 삭제
  - `GET /{id}/details` - 전체 정보 조회

- **경력사항**: `/api/v1/profiles/{profile_id}/careers`
  - `GET /` - 경력사항 목록 조회
  - `POST /` - 경력사항 생성
  - `PUT /careers/{id}` - 경력사항 수정
  - `DELETE /careers/{id}` - 경력사항 삭제

- **프로젝트**: `/api/v1/profiles/careers/{career_id}/projects`
  - `GET /` - 프로젝트 목록 조회
  - `POST /` - 프로젝트 생성
  - `PUT /projects/{id}` - 프로젝트 수정
  - `DELETE /projects/{id}` - 프로젝트 삭제

## 기술 스택

- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **LangChain**: LLM 애플리케이션 개발 프레임워크
- **Supabase**: PostgreSQL 기반 클라우드 데이터베이스
- **Pydantic**: 데이터 검증 및 설정 관리
- **uvicorn**: ASGI 서버
- **uv**: 빠른 Python 패키지 관리자

## 라이선스

MIT License
