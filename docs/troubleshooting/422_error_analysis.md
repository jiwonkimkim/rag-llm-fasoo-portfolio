# 422 Unprocessable Entity 오류 분석 및 해결

## 개요

- **발생일**: 2025-12-21
- **증상**: Pipeline Mode와 Ingest Mode에서 Chunk 단계에서 422/500 오류 발생
- **영향 범위**: 웹 UI의 모든 청킹 기능

---

## 시스템 아키텍처

```
┌─────────────┐    camelCase    ┌─────────────┐    snake_case    ┌─────────────┐
│  Frontend   │ ───────────────▶│   NestJS    │ ───────────────▶│   FastAPI   │
│  (React)    │                 │  (Proxy)    │                 │  (Backend)  │
└─────────────┘                 └─────────────┘                 └─────────────┘
     Port 80                        Port 3001                       Port 8000
```

### 필드 명명 규칙 흐름

| 계층 | 명명 규칙 | 예시 |
|------|-----------|------|
| Frontend (React/TypeScript) | camelCase | `chunkerType`, `chunkSize` |
| NestJS (DTO) | camelCase | `chunkerType`, `chunkSize` |
| NestJS → FastAPI 변환 | snake_case | `chunker_type`, `chunk_size` |
| FastAPI (Pydantic) | snake_case | `chunker_type`, `chunk_size` |

---

## 문제 1: 필드 명명 규칙 불일치

### 증상
- Pipeline Mode에서 Chunk 단계 무한 로딩
- Docker 로그에서 422 Unprocessable Entity 오류

### 원인 분석

**잘못된 수정 (이전에 적용됨)**:
```typescript
// api.ts - 잘못된 코드 (snake_case 직접 전송)
chunk: (data) => axios.post(`${API_BASE}/chunk`, {
  text: data.text,
  chunker_type: data.chunkerType,  // ❌ snake_case
  chunk_size: data.chunkSize,
  chunk_overlap: data.chunkOverlap,
})
```

**문제점**:
- Frontend가 snake_case로 전송 → NestJS DTO가 바인딩 실패
- NestJS DTO는 camelCase 필드를 기대함
- 결과: NestJS가 `undefined` 값을 FastAPI로 전달

### 해결

**올바른 코드 (camelCase 유지)**:
```typescript
// api.ts - 수정된 코드
chunk: (data: {
  text: string;
  chunkerType: string;
  chunkSize: number;
  chunkOverlap: number;
}) => axios.post(`${API_BASE}/chunk`, data)  // ✅ camelCase 그대로 전송
```

**NestJS 서비스에서 변환 처리**:
```typescript
// pipeline.service.ts
async chunk(data: ChunkDto) {
  const response = await this.httpService.post(`${FASTAPI_URL}/api/v1/chunk`, {
    text: data.text,
    chunker_type: data.chunkerType,     // camelCase → snake_case 변환
    chunk_size: data.chunkSize,
    chunk_overlap: data.chunkOverlap,
  });
  return response.data;
}
```

---

## 문제 2: Ingest Mode 응답 필드명 불일치

### 증상
- Pipeline Mode는 정상 작동
- Ingest Mode에서만 Chunk 단계 500 오류

### 원인 분석

**Preprocess API 응답 구조**:
```json
{
  "original": "원본 텍스트",
  "cleaned": "클리닝된 텍스트",
  "normalized": "정규화된 텍스트",
  "final": "최종 처리된 텍스트",    // ✅ 실제 필드명
  "steps": [...]
}
```

**Pipeline Mode (정상)**:
```typescript
// App.tsx - Pipeline Mode
const textToChunk = results.preprocess?.output?.final || preprocessInput;
//                                              ^^^^^ 올바른 필드명
```

**Ingest Mode (오류)**:
```typescript
// App.tsx - Ingest Mode (수정 전)
const chunkResult = await api.chunk({
  text: preprocessResult.data.processed_text,  // ❌ 존재하지 않는 필드
  //                          ^^^^^^^^^^^^^^
});
```

### 해결

```typescript
// App.tsx - Ingest Mode (수정 후)
const chunkResult = await api.chunk({
  text: preprocessResult.data.final,  // ✅ 올바른 필드명
  chunkerType: ingestChunkerType,
  chunkSize: ingestChunkSize,
  chunkOverlap: ingestChunkOverlap,
});
```

---

## 수정된 파일 목록

| 파일 | 수정 내용 |
|------|-----------|
| `web-visualizer/frontend/src/api.ts` | 모든 API 함수에서 camelCase 유지 |
| `web-visualizer/frontend/src/App.tsx` | Ingest Mode에서 `processed_text` → `final` 변경 |

---

## Docker 재빌드 명령

```bash
# 전체 재빌드 (캐시 무효화)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 프론트엔드만 재빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 검증 방법

### curl 테스트
```bash
# Chunk API 테스트
curl -X POST "http://localhost/api/chunk" \
  -H "Content-Type: application/json" \
  -d '{"text": "테스트 텍스트", "chunkerType": "fixed", "chunkSize": 100, "chunkOverlap": 10}'

# 예상 응답
{
  "original_length": 7,
  "chunks": ["테스트 텍스트"],
  "chunk_count": 1,
  "avg_chunk_size": 7,
  "settings": {
    "chunker_type": "fixed",
    "chunk_size": 100,
    "chunk_overlap": 10
  }
}
```

### 웹 UI 테스트
1. http://localhost 접속
2. **Pipeline Mode**: Preprocess → Chunk 순서 실행
3. **Ingest Mode**: 텍스트 입력 후 "처리 시작" 클릭

---

## 교훈 및 권장사항

### 1. 명명 규칙 일관성 유지
- Frontend ↔ Backend 간 명명 규칙 변환은 **한 곳에서만** 처리
- 이 프로젝트에서는 NestJS가 변환 담당

### 2. API 응답 필드명 문서화
- API 응답 구조를 TypeScript 인터페이스로 정의
- 실제 응답과 코드의 필드명 일치 여부 확인

### 3. Docker 캐시 주의
- 코드 수정 후 Docker 이미지에 반영되지 않을 수 있음
- `--no-cache` 옵션으로 완전 재빌드 권장

### 4. 로그 확인
```bash
# NestJS 로그 (프록시 오류 확인)
docker-compose logs --tail=50 nestjs

# FastAPI 로그 (백엔드 오류 확인)
docker-compose logs --tail=50 fastapi
```

---

## 관련 파일 참조

- `web-visualizer/frontend/src/api.ts` - API 호출 함수
- `web-visualizer/frontend/src/App.tsx` - 프론트엔드 로직
- `web-visualizer/backend/src/pipeline/pipeline.service.ts` - NestJS 서비스 (변환 로직)
- `web-visualizer/backend/src/pipeline/pipeline.controller.ts` - NestJS DTO 정의
