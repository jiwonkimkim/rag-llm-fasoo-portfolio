"""
Dense retriever

이 구현은 임베딩(embedding) 기반 검색을 수행합니다. 주어진 쿼리를 임베딩으로 변환한 뒤
벡터 저장소에서 유사 문서를 조회하고, `RetrievalResult` 객체 리스트로 변환하여 반환합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 쿼리를 숫자(임베딩)로 바꾼 뒤, 비슷한 벡터를 가진 문서를 찾아 결과로 돌려줘요.
# 주요 포인트:
# - 외부에서 `embedder`와 `vectorstore`를 주입받아 조합합니다.
# - retrieve 함수는 임베딩을 만든 뒤, vectorstore.search로 후보를 가져와 `RetrievalResult`로 바꿔요.

from typing import Any

from .base_retriever import BaseRetriever, RetrievalResult
from ..embedder.base_embedder import BaseEmbedder
from ..vectorstore.base_store import BaseVectorStore


class DenseRetriever(BaseRetriever):
    """임베딩 기반의 검색기.

    외부에서 `embedder`와 `vectorstore`를 주입 받아 조합할 수 있도록 설계되어 있습니다.
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        vectorstore: BaseVectorStore,
        top_k: int = 5,
    ):
        super().__init__(top_k)
        self.embedder = embedder
        self.vectorstore = vectorstore

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """쿼리를 임베딩으로 변환 후 벡터 저장소를 조회합니다."""
        query_embedding = self.embedder.embed(query)

        results = self.vectorstore.search(query_embedding, top_k=self.top_k)

        retrieval_results = []
        for result in results:
            retrieval_results.append(
                RetrievalResult(
                    content=result.content,
                    metadata=result.metadata,
                    score=result.score,
                    source=result.metadata.get("source", result.id),
                )
            )

        return retrieval_results

    def retrieve_with_filter(
        self,
        query: str,
        filter: dict[str, Any],
    ) -> list[RetrievalResult]:
        """메타데이터 필터를 적용하여 검색 결과를 제한합니다."""
        query_embedding = self.embedder.embed(query)
        results = self.vectorstore.search(
            query_embedding,
            top_k=self.top_k,
            filter=filter,
        )

        retrieval_results = []
        for result in results:
            retrieval_results.append(
                RetrievalResult(
                    content=result.content,
                    metadata=result.metadata,
                    score=result.score,
                    source=result.metadata.get("source", result.id),
                )
            )

        return retrieval_results
