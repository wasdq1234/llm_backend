# AI Assistant Chat System

FastAPI, LangChain을 사용한 AI 어시스턴트 채팅 시스템입니다.

## 주요 기능

- 🤖 **AI 어시스턴트**: OpenAI GPT 및 Anthropic Claude 모델 지원
- 💬 **실시간 채팅**: 스트리밍 응답으로 실시간 대화
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
│   │       └── chat.py          # 채팅 API 엔드포인트
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # 애플리케이션 설정
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py              # 데이터 모델
│   ├── services/
│   │   ├── __init__.py
│   │   └── chat_service.py      # 채팅 서비스
│   └── utils/
│       ├── __init__.py
│       └── logging.py           # 로깅 유틸리티
├── tests/                       # 테스트 파일
├── main.py                      # FastAPI 애플리케이션 진입점
├── pyproject.toml              # 프로젝트 설정 및 의존성
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

# .env 파일을 편집하여 API 키 설정
# 최소한 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY 중 하나는 필요합니다
```

### 3. 애플리케이션 실행

```bash
# 개발 모드로 실행
uv run python main.py

# 또는 uvicorn 직접 사용
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 사용법

### 기본 채팅

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요!",
    "stream": false
  }'
```

### 스트리밍 채팅

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "긴 답변이 필요한 질문을 해주세요",
    "conversation_id": "test-conversation"
  }'
```



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
| `DEFAULT_MODEL` | 기본 모델 | `gpt-3.5-turbo` |
| `MAX_TOKENS` | 최대 토큰 수 | `1000` |
| `TEMPERATURE` | 모델 온도 | `0.7` |
| `CORS_ORIGINS` | CORS 허용 오리진 | `http://localhost:3000,http://localhost:8080` |

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

## 기술 스택

- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **LangChain**: LLM 애플리케이션 개발 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **uvicorn**: ASGI 서버
- **uv**: 빠른 Python 패키지 관리자

## 라이선스

MIT License
