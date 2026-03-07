"""Pipeline module for RAG orchestration."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 파이프라인 관련 클래스를 모아둔 패키지예요. 문서 수집과 질문 응답(RAG) 관련 흐름을 제공합니다.
# 주요 포인트:
# - `IngestionPipeline`: 문서를 수집/처리/임베딩하여 저장합니다.
# - `RAGPipeline`: 검색 결과를 이용해 모델에게 질문하고 답을 반환합니다.

from .ingestion_pipeline import IngestionPipeline
from .rag_pipeline import RAGPipeline

__all__ = ["IngestionPipeline", "RAGPipeline"]
