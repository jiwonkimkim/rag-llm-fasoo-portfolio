# RAG Pipeline Visualizer 빠른 시작 가이드

팀원들이 프로젝트를 쉽게 설정하고 실행할 수 있도록 작성된 가이드입니다.

## 실행 방법 선택

| 방법 | 장점 | 단점 |
|------|------|------|
| **Docker (권장)** | 한 줄 명령어로 실행 | Docker 설치 필요 |
| 로컬 설치 | 개발/디버깅 용이 | 의존성 설치 필요 |

---

# 방법 1: Docker로 실행 (권장)

## 사전 요구사항

- Docker Desktop 설치: https://www.docker.com/products/docker-desktop

## 실행

```bash
# 1. 저장소 클론
git clone https://github.com/TripleC-org/Triple_c_rag.git
cd Triple_c_rag

# 2. 환경 변수 설정 (선택)
echo "OPENAI_API_KEY=your_key" > .env

# 3. Docker Compose로 실행 (한 줄!)
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

## 접속

| 서비스 | URL |
|--------|-----|
| **웹 UI** | http://localhost |
| FastAPI Docs | http://localhost:8000/docs |

## Docker 명령어

```bash
# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f

# n8n도 함께 실행
docker-compose --profile n8n up --build
```

---

# 방법 2: 로컬 설치

## 사전 요구사항

| 도구 | 버전 | 설치 확인 |
|------|------|----------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | 최신 | `git --version` |

---

## 1. 저장소 클론/풀

```bash
# 최초 클론
git clone https://github.com/TripleC-org/Triple_c_rag.git
cd Triple_c_rag

# 이미 클론했다면 최신 버전 풀
git pull origin main
```

---

## 2. 의존성 설치 (최초 1회)

터미널 3개를 열어서 각각 실행합니다.

### 터미널 1: Python 의존성
```bash
pip install -r requirements.txt
pip install -r visualizer/requirements.txt
```

### 터미널 2: NestJS 백엔드
```bash
cd web-visualizer/backend
npm install
```

### 터미널 3: React 프론트엔드
```bash
cd web-visualizer/frontend
npm install
```

---

## 3. 서버 실행 (매번)

터미널 3개에서 각각 실행합니다.

### 터미널 1: FastAPI (포트 8000)
```bash
uvicorn visualizer.api.main:app --reload --port 8000
```

### 터미널 2: NestJS (포트 3001)
```bash
cd web-visualizer/backend
npm run start:dev
```

### 터미널 3: React (포트 5173)
```bash
cd web-visualizer/frontend
npm run dev
```

---

## 4. 접속

| 서비스 | URL | 설명 |
|--------|-----|------|
| **웹 UI** | http://localhost:5173 | 메인 인터페이스 |
| FastAPI Docs | http://localhost:8000/docs | API 문서 (Swagger) |
| NestJS Gateway | http://localhost:3001 | API Gateway |

---

## 시스템 아키텍처

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  React + Vite    │────▶│     NestJS       │────▶│     FastAPI      │────▶│   RAG Modules    │
│   (Frontend)     │◀────│    (Gateway)     │◀────│    (Backend)     │◀────│   (src/)         │
│   Port: 5173     │     │   Port: 3001     │     │   Port: 8000     │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 문제 해결

### 포트 충돌 시

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /F /PID <PID번호>
```

**Mac/Linux:**
```bash
lsof -i :8000
kill -9 <PID번호>
```

### 모듈 에러 시
```bash
pip install -e ".[all]"  # 모든 RAG 모듈 설치
```

### API 연결 실패 시
```bash
# FastAPI 서버 상태 확인
curl http://localhost:8000/health
```

---

## 프로젝트 구조

```
Triple_c_rag/
├── src/                    # RAG 핵심 모듈
│   ├── crawler/           # 데이터 수집
│   ├── preprocessor/      # 텍스트 전처리
│   ├── chunker/           # 텍스트 청킹
│   ├── embedder/          # 임베딩 생성
│   ├── vectorstore/       # 벡터 DB
│   ├── retriever/         # 문서 검색
│   └── generator/         # LLM 응답 생성
├── visualizer/
│   └── api/               # FastAPI 백엔드
└── web-visualizer/
    ├── backend/           # NestJS API Gateway
    └── frontend/          # React UI
```

---

## 환경 변수 (선택)

`.env` 파일을 프로젝트 루트에 생성:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Pinecone 사용 시
HUGGINGFACE_API_KEY=your_hf_api_key     # HuggingFace 사용 시
```

---

## 추가 자료

- [상세 문서](visualizer/README.md)
- [API 엔드포인트 목록](http://localhost:8000/docs)
- [프로젝트 설정](CLAUDE.md)
