# RAG Pipeline Visualizer

RAG (Retrieval-Augmented Generation) 파이프라인을 시각적으로 테스트하고 디버깅할 수 있는 도구입니다.

## 아키텍처

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  React + Vite    │────▶│     NestJS       │────▶│     FastAPI      │────▶│   RAG Modules    │
│   (Frontend)     │◀────│    (Gateway)     │◀────│    (Backend)     │◀────│   (src/)         │
│   Port: 5173     │     │   Port: 3001     │     │   Port: 8000     │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────────┐
                                                  │       n8n        │
                                                  │  (Automation)    │
                                                  │   Port: 5678     │
                                                  └──────────────────┘
```

## 주요 기능

### 1. Step-by-Step 모드
- 각 파이프라인 단계별 입력/출력 확인
- 파라미터 실시간 조정
- 이전 단계 결과를 다음 단계로 자동 전달

### 2. Module Test 모드
- 개별 모듈 독립 테스트
- 다양한 옵션 실험
- 결과 비교 분석

### 3. n8n Integration
- Webhook 엔드포인트 제공
- 워크플로우 자동화
- 외부 시스템 연동

## 빠른 시작

### 로컬 실행

```bash
# 1. FastAPI 서버 시작 (터미널 1)
cd Triple_c_rag
pip install -r visualizer/requirements.txt
uvicorn visualizer.api.main:app --reload --host 0.0.0.0 --port 8000

# 2. NestJS 서버 시작 (터미널 2)
cd Triple_c_rag/web-visualizer/backend
npm install
npm run start:dev

# 3. React 앱 시작 (터미널 3)
cd Triple_c_rag/web-visualizer/frontend
npm install
npm run dev
```

### 접속 URL
- React Frontend: http://localhost:5173
- NestJS Gateway: http://localhost:3001
- FastAPI Docs: http://localhost:8000/docs
- n8n: http://localhost:5678 (`N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`)

## API 엔드포인트

### 파이프라인 모듈

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/preprocess` | POST | 텍스트 전처리 |
| `/api/v1/chunk` | POST | 텍스트 청킹 |
| `/api/v1/embed` | POST | 임베딩 생성 |
| `/api/v1/retrieve` | POST | 문서 검색 |
| `/api/v1/generate` | POST | 응답 생성 |

### n8n Webhook

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/n8n/query` | POST | RAG 쿼리 실행 |
| `/webhook/n8n/ingest` | POST | 문서 인제스트 |
| `/api/v1/pipeline/full` | POST | 전체 파이프라인 |

### 시스템

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | 헬스 체크 |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

## n8n 워크플로우 설정

### 1. n8n 접속
- URL: http://localhost:5678
- 계정: `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`

### 2. 워크플로우 임포트
1. n8n 대시보드에서 "Import from File" 클릭
2. `visualizer/n8n/workflow_rag_query.json` 선택
3. 워크플로우 활성화

### 3. 웹훅 테스트
```bash
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "RAG 시스템이란?",
    "settings": {
      "retriever_type": "dense",
      "top_k": 5
    }
  }'
```

## API 요청 예시

### Preprocess

```bash
curl -X POST http://localhost:8000/api/v1/preprocess \
  -H "Content-Type: application/json" \
  -d '{
    "text": "  Hello,   World!  <br>  ",
    "use_cleaner": true,
    "use_normalizer": true
  }'
```

### Chunk

```bash
curl -X POST http://localhost:8000/api/v1/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "text": "긴 문서 내용...",
    "chunker_type": "fixed",
    "chunk_size": 512,
    "chunk_overlap": 50
  }'
```

### Full Pipeline

```bash
curl -X POST http://localhost:8000/api/v1/pipeline/full \
  -H "Content-Type: application/json" \
  -d '{
    "query": "인공지능이란 무엇인가요?",
    "retriever_type": "hybrid",
    "top_k": 5,
    "model": "gpt-3.5-turbo"
  }'
```

## 프로젝트 구조

```
visualizer/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI 애플리케이션
│   └── models.py        # Pydantic 모델
├── n8n/
│   ├── workflow_rag_query.json
│   └── workflow_document_ingest.json
├── requirements.txt
└── README.md

web-visualizer/
├── frontend/            # React + Vite 프론트엔드
│   ├── src/
│   │   ├── App.tsx
│   │   └── api.ts
│   └── package.json
└── backend/             # NestJS API Gateway
    ├── src/
    │   └── pipeline/
    └── package.json
```

## 환경 변수

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `API_BASE_URL` | FastAPI 서버 URL | http://localhost:8000 |
| `N8N_BASIC_AUTH_USER` | n8n 사용자명 | n8n_admin |
| `N8N_BASIC_AUTH_PASSWORD` | n8n 비밀번호 | (필수, 기본값 없음) |

## 문제 해결

### API 연결 실패
```bash
# FastAPI 서버 상태 확인
curl http://localhost:8000/health
```

### 모듈 로드 실패
- `src/` 디렉토리가 Python 경로에 포함되어 있는지 확인
- 필요한 의존성이 설치되어 있는지 확인

### n8n 웹훅 실패
- n8n이 실행 중인지 확인
- 워크플로우가 활성화되어 있는지 확인
- FastAPI URL이 올바른지 확인 (Docker 내부: `http://api:8000`)

## 라이선스

MIT License
