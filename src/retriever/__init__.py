"""Retriever module for document retrieval."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 다양한 검색 방법(Dense, Sparse, Hybrid)을 한곳에 모아 쓰기 편하게 구성한 패키지예요.
# 주요 포인트:
# - Dense: 벡터(숫자)로 유사문서를 찾고, Sparse: 키워드로 찾습니다.
# - Hybrid는 두 방식을 섞어 더 좋은 결과를 얻습니다.

from .base_retriever import BaseRetriever, RetrievalResult
from .dense_retriever import DenseRetriever
from .sparse_retriever import SparseRetriever
from .hybrid_retriever import HybridRetriever

__all__ = [
    "BaseRetriever",
    "RetrievalResult",
    "DenseRetriever",
    "SparseRetriever",
    "HybridRetriever",
]
