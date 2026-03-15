# Triple C RAG Portfolio

문서/웹 데이터를 수집해 RAG(Retrieval-Augmented Generation) 질의를 수행하는 Python 기반 프로젝트입니다. 

- "RAG를 단계별 모듈로 분리해, 벡터DB/임베더/리트리버 전략을 교체하며 실험할 수 있게 구성했습니다."
- "Hybrid Retrieval과 프롬프트 규칙, fallback 테스트를 통해 답변 신뢰성을 높이려는 구현을 포함했습니다."
- "보안/운영 관점에서는 URL 검증, 예외 수집, 재시도 로직 같은 기본 안전장치를 코드에 반영했습니다."

## 🧪 QA & Reliability Engineering (핵심 검증 포인트)

**"RAG의 답변 신뢰성을 확보하기 위해 다음의 테스트 시나리오를 설계하고 통과시켰습니다."**

1. **데이터 품질 예외 처리**: 텍스트가 없는 PDF, 손상된 URL 인제스트 시 파이프라인 중단 없이 에러 로그를 수집하고 해당 문서만 스킵하는 예외 처리 로직 검증.
2. **Retrieval Edge Cases**: 검색 결과가 0건일 때(Empty Result) 시스템이 중단되지 않고 "관련 정보를 찾을 수 없습니다"라는 Fallback 메시지를 정상 출력하는지 테스트.
3. **Prompt Injection 방어**: 시스템 프롬프트 규칙을 위반하려는 입력을 PromptBuilder 단계에서 필터링하거나 가이드라인 내에서만 답변하도록 제어.
4. **성능 임계점 파악**: 대량의 청킹(Chunking) 작업 시 메모리 사용량 및 임베딩 API 타임아웃 발생 지점 확인 및 재시도 로직 적용.

## 1) 프로젝트 요약
- 데이터 수집부터 답변 생성까지 RAG 파이프라인을 모듈 단위로 분리해 구현
- Dense/Sparse/Hybrid 검색 방식을 선택해 실험 가능
- 프롬프트 규칙과 출처(source) 전달 로직 포함
- 테스트 코드로 주요 동작(fallback, top-k, dedup, 빈 결과 처리 등) 검증
- 시각화 도구(`visualizer/`, `web-visualizer/`)로 단계별 확인 가능

## 2) 저장소에서 확인되는 범위
### 구현된 것
- Ingestion 파이프라인: `crawler -> preprocessor -> chunker -> embedder -> vectorstore`
- Query 파이프라인: `retriever -> prompt_builder -> llm_client -> response_parser`
- 벡터스토어: Chroma / FAISS / Pinecone 구현체
- 임베더: OpenAI / HuggingFace / BGE-M3 선택
- 리트리버: Dense / Sparse(BM25) / Hybrid(RRF)
- 실행 스크립트: `scripts/run_ingestion.py`, `scripts/run_rag.py`
- 테스트: `tests/` 하위 모듈별 단위 테스트

### 구현되지 않았거나 문서화만 된 것
- 정량 평가 리포트(정확도, 비용, 지연시간 자동 집계)
- 정책 기반 Guardrail(민감정보/금칙어 정책 엔진)
- 법무/컴플라이언스 체계 자체 구현

## 3) 아키텍처

```text
[Ingestion]
Crawler -> Preprocessor -> Chunker -> Embedder -> VectorStore

[Query]
User Query -> Retriever -> PromptBuilder -> LLMClient -> ResponseParser
```

핵심 설계 포인트:
- Base 인터페이스 중심 구조로 구현체 교체 가능
- 파이프라인 클래스(`IngestionPipeline`, `RAGPipeline`)로 단계 오케스트레이션
- CLI 스크립트로 로컬 재현 가능

## 4) 사실 기반 역량 매핑 (AI 컨설턴트 직무 관점)
| 공고 역량 | 저장소에서 확인 가능한 근거 |
|---|---|
| RAG 아키텍처 구성 지원 | 파이프라인/모듈 분리 구조 및 실행 스크립트 |
| 프롬프트 엔지니어링 및 테스트 | `PromptBuilder` 규칙 + 파이프라인/리트리버 테스트 |
| 기술적 개념을 구조화해 전달 | 모듈 구조, README, visualizer 문서로 단계별 설명 |
| 보안 리스크 인지 및 기본 대응 | 이미지 다운로드 경로의 URL/호스트 검증(SSRF 완화 목적) |
| 운영 안정성 고려 | 재시도(backoff), 예외 수집, timeout/오류 처리 코드 |

## 5) 주요 구현 포인트
### 5-1. Hybrid Retrieval
- Dense + Sparse 결과를 RRF로 결합
- 중복 문서 dedup, top-k 제한 동작 포함

### 5-2. Prompt 구성
- "컨텍스트 기반으로 답변"하도록 시스템 프롬프트 기본 규칙 포함
- 출처(source) 정보를 컨텍스트와 함께 전달

### 5-3. LLM 호출 안정성
- 동기 호출, 스트리밍 호출 지원
- 재시도(Exponential Backoff) 메서드 제공

### 5-4. 파이프라인 오류 처리
- 인제스트 단계에서 문서별 예외를 수집하여 결과에 포함
- 빈 검색 결과 처리 및 source fallback 테스트 존재

### 5-5. 보안 관련 구현(제한적)
- 이미지 URL 스킴/호스트/IP 대역 검증
- 비이미지 Content-Type 차단
- 목적: 외부 URL 다운로드 시 기본적인 위험 감소

## 6) 실행 방법
### 1. 환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. 인제스트
```bash
python scripts/run_ingestion.py --sources data/raw/document.pdf --source-type file
```

### 3. 질의
```bash
python scripts/run_rag.py --query "질문 내용"
```

### 4. 테스트
```bash
pytest tests/
```


## 7) 참고 문서
- `QUICKSTART.md`
- `visualizer/README.md`
- `docs/troubleshooting/422_error_analysis.md`
