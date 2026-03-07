# 테스트 실행 가이드

이 문서는 Triple_c_rag 프로젝트의 테스트 실행 방법을 설명합니다.

## 사전 요구사항

```bash
# pytest 설치 (이미 설치되어 있지 않은 경우)
pip install pytest

# 커버리지 리포트를 원하는 경우
pip install pytest-cov
```

## 전체 테스트 실행

```bash
# 모든 테스트 실행 (상세 출력)
python -m pytest tests/ -v

# 모든 테스트 실행 (간단한 출력)
python -m pytest tests/
```

## 모듈별 테스트 실행

### Embedder 모듈
```bash
python -m pytest tests/test_embedder/ -v
```
- `test_base_embedder.py`: BaseEmbedder 추상 클래스 테스트
- `test_openai_embedder.py`: OpenAI 임베더 테스트
- `test_huggingface_embedder.py`: HuggingFace 임베더 테스트

### Pipeline 모듈
```bash
python -m pytest tests/test_pipeline/ -v
```
- `test_ingestion_pipeline.py`: 데이터 수집 파이프라인 테스트
- `test_rag_pipeline.py`: RAG 파이프라인 테스트

### Preprocessor 모듈
```bash
python -m pytest tests/test_preprocessor/ -v
```
- `test_cleaner.py`: 텍스트 클리너 테스트
- `test_normalizer.py`: 텍스트 정규화 테스트

### Retriever 모듈
```bash
python -m pytest tests/test_retriever/ -v
```
- `test_base_retriever.py`: BaseRetriever 추상 클래스 테스트
- `test_dense_retriever.py`: Dense(임베딩 기반) 검색기 테스트
- `test_sparse_retriever.py`: Sparse(BM25) 검색기 테스트
- `test_hybrid_retriever.py`: 하이브리드 검색기 테스트

### Vectorstore 모듈
```bash
python -m pytest tests/test_vectorstore/ -v
```
- `test_base_store.py`: BaseVectorStore 추상 클래스 테스트
- `test_chroma_store.py`: ChromaDB 벡터 저장소 테스트
- `test_faiss_store.py`: FAISS 벡터 저장소 테스트
- `test_pinecone_store.py`: Pinecone 벡터 저장소 테스트

## 특정 파일/클래스/함수 실행

### 특정 파일만 실행
```bash
python -m pytest tests/test_vectorstore/test_chroma_store.py -v
```

### 특정 테스트 클래스만 실행
```bash
python -m pytest tests/test_vectorstore/test_chroma_store.py::TestChromaStoreSearch -v
```

### 특정 테스트 함수만 실행
```bash
python -m pytest tests/test_vectorstore/test_chroma_store.py::TestChromaStoreSearch::test_search_returns_results -v
```

## 유용한 pytest 옵션

| 옵션 | 설명 |
|------|------|
| `-v` | 상세 출력 (verbose) |
| `-vv` | 더 상세한 출력 |
| `-s` | print 문 출력 표시 |
| `-x` | 첫 번째 실패에서 중단 |
| `--lf` | 마지막 실행에서 실패한 테스트만 재실행 |
| `--ff` | 실패한 테스트를 먼저 실행 |
| `-k "keyword"` | 키워드가 포함된 테스트만 실행 |
| `--tb=short` | 짧은 트레이스백 출력 |
| `--tb=no` | 트레이스백 출력 안함 |

### 옵션 사용 예시

```bash
# print 문 출력과 함께 상세 실행
python -m pytest tests/ -v -s

# 첫 번째 실패에서 중단
python -m pytest tests/ -x

# 실패한 테스트만 재실행
python -m pytest tests/ --lf

# "search" 키워드가 포함된 테스트만 실행
python -m pytest tests/ -k "search" -v

# "chroma"와 "add"가 모두 포함된 테스트만 실행
python -m pytest tests/ -k "chroma and add" -v
```

## 테스트 커버리지

### 커버리지 리포트 생성
```bash
# 터미널에 커버리지 출력
python -m pytest tests/ --cov=src

# HTML 리포트 생성 (htmlcov/ 폴더에 저장)
python -m pytest tests/ --cov=src --cov-report=html

# XML 리포트 생성 (CI/CD 연동용)
python -m pytest tests/ --cov=src --cov-report=xml
```

### 커버리지 리포트 확인
```bash
# HTML 리포트 열기 (Windows)
start htmlcov/index.html

# HTML 리포트 열기 (macOS)
open htmlcov/index.html

# HTML 리포트 열기 (Linux)
xdg-open htmlcov/index.html
```

## 테스트 구조

```
tests/
├── TEST_GUIDE.md              # 이 문서
├── __init__.py
├── test_embedder/
│   ├── __init__.py
│   ├── test_base_embedder.py
│   ├── test_openai_embedder.py
│   └── test_huggingface_embedder.py
├── test_pipeline/
│   ├── __init__.py
│   ├── test_ingestion_pipeline.py
│   └── test_rag_pipeline.py
├── test_preprocessor/
│   ├── __init__.py
│   ├── test_cleaner.py
│   └── test_normalizer.py
├── test_retriever/
│   ├── __init__.py
│   ├── test_base_retriever.py
│   ├── test_dense_retriever.py
│   ├── test_sparse_retriever.py
│   └── test_hybrid_retriever.py
└── test_vectorstore/
    ├── __init__.py
    ├── test_base_store.py
    ├── test_chroma_store.py
    ├── test_faiss_store.py
    └── test_pinecone_store.py
```

## 문제 해결

### 모듈을 찾을 수 없는 경우
프로젝트 루트 디렉토리에서 실행하고 있는지 확인하세요:
```bash
cd Triple_c_rag
python -m pytest tests/ -v
```

### 의존성 오류
외부 라이브러리(chromadb, faiss, pinecone 등)가 없어도 테스트는 실행됩니다.
테스트는 mock 객체를 사용하여 외부 의존성 없이 동작합니다.

### 특정 테스트가 실패하는 경우
```bash
# 실패한 테스트만 상세히 확인
python -m pytest tests/ --lf -v --tb=long
```
