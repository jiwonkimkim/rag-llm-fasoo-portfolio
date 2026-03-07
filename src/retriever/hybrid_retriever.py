"""
Hybrid retriever (Dense + Sparse)

이 클래스는 임베딩 기반 검색(dense)과 전통적 키워드 기반 검색(sparse)을 결합하여
더 안정적인 검색 결과를 생성합니다. 두 검색 결과를 결합할 때 Reciprocal Rank Fusion(RRF)
기법을 사용합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 두 가지 검색 방법(벡터 기반 + 키워드 기반)을 섞어 더 좋은 결과를 만드는 방법을 보여줘요.
# 주요 포인트:
# - 두 결과의 순위를 합쳐서(score)를 재계산하는 RRF 방식을 사용합니다.
# - dense/sparse의 비중을 조절해 원하는 성향(정확성 vs 포괄성)을 맞출 수 있어요.

from typing import Any

from .base_retriever import BaseRetriever, RetrievalResult
from .dense_retriever import DenseRetriever
from .sparse_retriever import SparseRetriever


class HybridRetriever(BaseRetriever):
    """Dense와 Sparse 검색을 결합한 하이브리드 검색기."""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        top_k: int = 5,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5,
    ):
        super().__init__(top_k)
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """두 검색기의 결과를 결합하여 상위 `top_k` 결과를 반환합니다."""
        dense_results = self.dense_retriever.retrieve(query)
        sparse_results = self.sparse_retriever.retrieve(query)

        combined_scores = self._reciprocal_rank_fusion(
            dense_results,
            sparse_results,
        )

        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True,
        )[: self.top_k]

        results = []
        for content, data in sorted_results:
            results.append(
                RetrievalResult(
                    content=content,
                    metadata=data["metadata"],
                    score=data["score"],
                    source=data["source"],
                )
            )

        return results

    def _reciprocal_rank_fusion(
        self,
        dense_results: list[RetrievalResult],
        sparse_results: list[RetrievalResult],
        k: int = 60,
    ) -> dict[str, dict[str, Any]]:
        """RRF 기법으로 두 결과 집합을 합산하여 점수를 계산합니다."""
        combined = {}

        for rank, result in enumerate(dense_results):
            content = result.content
            if content not in combined:
                combined[content] = {
                    "score": 0,
                    "metadata": result.metadata,
                    "source": result.source,
                }
            combined[content]["score"] += self.dense_weight / (k + rank + 1)

        for rank, result in enumerate(sparse_results):
            content = result.content
            if content not in combined:
                combined[content] = {
                    "score": 0,
                    "metadata": result.metadata,
                    "source": result.source,
                }
            combined[content]["score"] += self.sparse_weight / (k + rank + 1)

        return combined

    def retrieve_with_rerank(
        self,
        query: str,
        reranker: Any = None,
    ) -> list[RetrievalResult]:
        """검색 후 선택적으로 재정렬(rerank)을 적용합니다."""
        results = self.retrieve(query)

        if reranker:
            results = self.rerank(results, query)

        return results
