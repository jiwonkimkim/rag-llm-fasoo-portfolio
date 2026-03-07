### 생성된 프로젝트 구조

RAG (Retrieval-Augmented Generation) 시스템 웹/문서에서 데이터를 수집하고, 사용자 질문에 대해 관련 문서를 검색한 후    
   LLM이 답변을 생성하는 파이프라인

  핵심 흐름

  [데이터 수집]                    [질의 응답]
       │                              │
   Crawler (웹/PDF/DOCX)          사용자 질문
       │                              │
   Preprocessor (정제)            Retriever (검색)
       │                              │
   Chunker (분할)                 LLM Client
       │                              │
   Embedder (벡터화)              PromptBuilder
       │                              │
   VectorStore (저장)             응답 생성

  ### Python 모듈 (50개 파일)

  **모듈별 역할**

  | 모듈            | 역할     | 주요 구현체                                 |
  |---------------|--------|----------------------------------------|
  | crawler/      | 데이터 수집 | WebCrawler, FileLoader                 |
  | preprocessor/ | 텍스트 정제 | TextCleaner, TextNormalizer            |
  | chunker/      | 텍스트 분할 | RecursiveChunker, SemanticChunker      |
  | embedder/     | 벡터 변환  | OpenAIEmbedder, HuggingFaceEmbedder    |
  | vectorstore/  | 벡터 DB  | ChromaStore, FAISSStore, PineconeStore |
  | retriever/    | 문서 검색  | DenseRetriever, HybridRetriever        |
  | generator/    | 답변 생성  | LLMClient, PromptBuilder               |
  | pipeline/     | 전체 조율  | IngestionPipeline, RAGPipeline         |

  **설계 특징**

  1. 추상 베이스 클래스 패턴: 각 모듈에 Base* 클래스가 있어 구현체 교체가 쉬움
  2. 데이터 클래스: Document, Chunk, RetrievalResult 등 타입이 명확한 데이터 객체
  3. 의존성 주입: 컴포넌트들이 __init__에서 의존성을 받아 테스트/교체 용이

  config/          - 3개 파일 (settings, logging)
  src/
    ├── crawler/       - 4개 파일 (web_crawler, file_loader)
    ├── preprocessor/  - 3개 파일 (cleaner, normalizer)
    ├── chunker/       - 5개 파일 (fixed, semantic, recursive)
    ├── embedder/      - 4개 파일 (openai, huggingface)
    ├── vectorstore/   - 5개 파일 (chroma, faiss, pinecone)
    ├── retriever/     - 5개 파일 (dense, sparse, hybrid)
    ├── generator/     - 4개 파일 (prompt, llm_client, parser)
    └── pipeline/      - 3개 파일 (ingestion, rag)
  tests/           - 12개 파일 (기본 테스트 포함)
  scripts/         - 2개 파일 (run_ingestion, run_rag)

  설정 파일

  - README.md - 프로젝트 문서 (팀원 역할, 사용법 포함)
  - requirements.txt - 의존성 목록
  - pyproject.toml - 프로젝트 설정
  - .env.example - 환경변수 예시
  - .gitignore - Git 제외 파일

  데이터 폴더

  - data/raw/ - 원본 데이터
  - data/processed/ - 전처리된 데이터
  - data/chunks/ - 청킹된 데이터
  - data/vectordb/ - 벡터 DB

  ---
  시작하기

  # 1. 가상환경 생성
  python -m venv venv
  venv\Scripts\activate

  # 2. 의존성 설치
  pip install -r requirements.txt

  # 3. 환경변수 설정
  copy .env.example .env
  # .env 파일에서 OPENAI_API_KEY 설정

  # 4. 테스트 실행
  pytest tests/

----

# Triple C RAG - RAG 테스트 모듈

RAG(Retrieval-Augmented Generation) 파이프라인 테스트 모듈 프로젝트입니다.

## 팀원

- **지원** - 크롤링, 전처리
- **지윤** - 청킹, 임베딩
- **동훈** - 벡터DB, 리트리버

---

## 프로젝트 구조

```
Triple_c_rag/
│
├── config/                          # 설정 파일
│   ├── __init__.py
│   ├── settings.py                  # 전역 설정 (API 키, 경로 등)
│   └── logging_config.py            # 로깅 설정
│
├── src/                             # 메인 소스 코드
│   ├── __init__.py
│   │
│   ├── crawler/                     # 크롤링 모듈 (담당: 지원)
│   │   ├── __init__.py
│   │   ├── base_crawler.py          # 크롤러 베이스 클래스
│   │   ├── web_crawler.py           # 웹 크롤러
│   │   └── file_loader.py           # 로컬 파일 로더 (PDF, DOCX 등)
│   │
│   ├── preprocessor/                # 전처리 모듈 (담당: 지원)
│   │   ├── __init__.py
│   │   ├── cleaner.py               # 텍스트 정제 (HTML 태그, 특수문자 제거)
│   │   └── normalizer.py            # 정규화 (인코딩, 공백 처리)
│   │
│   ├── chunker/                     # 청킹 모듈 (담당: 지윤)
│   │   ├── __init__.py
│   │   ├── base_chunker.py          # 청커 베이스 클래스
│   │   ├── fixed_chunker.py         # 고정 크기 청킹
│   │   ├── semantic_chunker.py      # 의미 기반 청킹
│   │   └── recursive_chunker.py     # 재귀적 청킹
│   │
│   ├── embedder/                    # 임베딩 모듈 (담당: 지윤)
│   │   ├── __init__.py
│   │   ├── base_embedder.py         # 임베더 베이스 클래스
│   │   ├── openai_embedder.py       # OpenAI 임베딩
│   │   └── huggingface_embedder.py  # HuggingFace 임베딩
│   │
│   ├── vectorstore/                 # 벡터 DB 모듈 (담당: 동훈)
│   │   ├── __init__.py
│   │   ├── base_store.py            # 벡터스토어 베이스 클래스
│   │   ├── chroma_store.py          # ChromaDB
│   │   ├── faiss_store.py           # FAISS
│   │   └── pinecone_store.py        # Pinecone
│   │
│   ├── retriever/                   # 리트리버 모듈 (담당: 동훈)
│   │   ├── __init__.py
│   │   ├── base_retriever.py        # 리트리버 베이스 클래스
│   │   ├── dense_retriever.py       # Dense 검색
│   │   ├── sparse_retriever.py      # Sparse 검색 (BM25)
│   │   └── hybrid_retriever.py      # 하이브리드 검색
│   │
│   ├── generator/                   # RAG 생성 모듈 (공동)
│   │   ├── __init__.py
│   │   ├── prompt_builder.py        # 프롬프트 구성
│   │   ├── llm_client.py            # LLM API 클라이언트
│   │   └── response_parser.py       # 응답 파싱
│   │
│   └── pipeline/                    # 파이프라인 통합 (공동)
│       ├── __init__.py
│       ├── ingestion_pipeline.py    # 데이터 수집 파이프라인
│       └── rag_pipeline.py          # RAG 전체 파이프라인
│
├── tests/                           # 테스트 코드
│   ├── __init__.py
│   ├── test_crawler/
│   ├── test_preprocessor/
│   ├── test_chunker/
│   ├── test_embedder/
│   ├── test_vectorstore/
│   ├── test_retriever/
│   └── test_pipeline/
│
├── data/                            # 데이터 저장소
│   ├── raw/                         # 크롤링 원본 데이터
│   ├── processed/                   # 전처리된 데이터
│   ├── chunks/                      # 청킹된 데이터
│   └── vectordb/                    # 벡터 DB 저장소
│
├── notebooks/                       # 실험용 주피터 노트북
│
├── scripts/                         # 실행 스크립트
│   ├── run_ingestion.py             # 데이터 수집 실행
│   └── run_rag.py                   # RAG 실행
│
├── .env.example                     # 환경변수 예시
├── .gitignore
├── requirements.txt                 # 의존성
├── pyproject.toml                   # 프로젝트 설정
└── README.md                        # 프로젝트 문서
```

---

## 팀원별 담당 영역

| 담당자 | 모듈 | 역할 |
|--------|------|------|
| **지원** | `crawler/`, `preprocessor/` | 데이터 수집 및 정제 |
| **지윤** | `chunker/`, `embedder/` | 텍스트 분할 및 벡터화 |
| **동훈** | `vectorstore/`, `retriever/` | 저장 및 검색 |
| **공동** | `generator/`, `pipeline/`, `tests/` | 통합 및 테스트 |

---

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd Triple_c_rag
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 API 키 설정
```

---

## 사용 방법

### 데이터 수집 (Ingestion)

```bash
# 로컬 파일 수집
python scripts/run_ingestion.py --sources data/raw/document.pdf --source-type file

# 웹 페이지 수집
python scripts/run_ingestion.py --sources https://example.com --source-type web

# 여러 소스 수집
python scripts/run_ingestion.py --sources file1.pdf file2.txt --source-type file
```

### RAG 질의

```bash
# 단일 질문
python scripts/run_rag.py --query "질문 내용"

# 대화형 모드
python scripts/run_rag.py --interactive
```

---

## 모듈별 사용 예시

### 크롤링

```python
from src.crawler import WebCrawler, FileLoader

# 웹 크롤링
crawler = WebCrawler()
documents = crawler.crawl("https://example.com")

# 파일 로딩
loader = FileLoader()
documents = loader.crawl("data/raw/document.pdf")
```

### 전처리

```python
from src.preprocessor import TextCleaner, TextNormalizer

cleaner = TextCleaner(remove_html=True, remove_urls=True)
normalizer = TextNormalizer(normalize_unicode=True)

text = cleaner.clean(raw_text)
text = normalizer.normalize(text)
```

### 청킹

```python
from src.chunker import RecursiveChunker

chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk(text, source="document.pdf")
```

### 임베딩

```python
from src.embedder import OpenAIEmbedder

embedder = OpenAIEmbedder(model_name="text-embedding-3-small")
embedding = embedder.embed("텍스트")
embeddings = embedder.embed_batch(["텍스트1", "텍스트2"])
```

### 벡터 저장소

```python
from src.vectorstore import ChromaStore

store = ChromaStore(collection_name="my_collection", persist_directory="data/vectordb")
store.add(ids=["id1"], embeddings=[embedding], documents=["텍스트"])
results = store.search(query_embedding, top_k=5)
```

### 리트리버

```python
from src.retriever import DenseRetriever

retriever = DenseRetriever(embedder=embedder, vectorstore=store, top_k=5)
results = retriever.retrieve("검색 질문")
```

### RAG 파이프라인

```python
from src.pipeline import RAGPipeline

pipeline = RAGPipeline(retriever=retriever)
response = pipeline.query("질문")
print(response.answer)
```

---

## 테스트 실행

```bash
# 전체 테스트
pytest tests/

# 특정 모듈 테스트
pytest tests/test_chunker/

# 커버리지 포함
pytest tests/ --cov=src
```

---

## 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `PINECONE_API_KEY` | Pinecone API 키 | - |
| `HUGGINGFACE_API_KEY` | HuggingFace API 키 | - |
| `EMBEDDING_MODEL` | 임베딩 모델 | `text-embedding-3-small` |
| `CHUNK_SIZE` | 청크 크기 | `1000` |
| `CHUNK_OVERLAP` | 청크 오버랩 | `200` |
| `TOP_K` | 검색 결과 수 | `5` |
| `LLM_MODEL` | LLM 모델 | `gpt-4o-mini` |

---

## 개발 가이드

### 브랜치 전략

- `main`: 안정 버전
- `develop`: 개발 버전
- `feature/*`: 기능 개발
- `fix/*`: 버그 수정

### 커밋 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
refactor: 코드 리팩토링
test: 테스트 추가/수정
```

---

## 라이선스

MIT License
