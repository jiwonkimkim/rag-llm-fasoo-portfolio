"""
Sparse retriever (BM25)

BM25 알고리즘을 사용한 키워드 기반 검색 구현입니다. 소규모 문서 집합이나 정확한 키워드 매칭이
중요할 때 유용합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - BM25라는 방법을 사용해 '키워드 중심'으로 문서를 찾는 예시예요.
# 주요 포인트:
# - 문서를 토큰(단어) 단위로 나누어 빈도와 문서 길이를 고려하여 점수를 계산합니다.
# - 작은 데이터셋이나 정확한 키워드 검색이 필요한 상황에서 유리합니다.

from typing import Any

from .base_retriever import BaseRetriever, RetrievalResult


class SparseRetriever(BaseRetriever):
    """BM25 기반의 스파스 검색기.

    - 문서를 로드하고 내부적으로 토크나이즈하여 BM25 인덱스를 구성합니다.
    - 한국어의 경우 더 정교한 토크나이저(konlpy 등)를 사용하면 성능이 향상됩니다.
    """

    def __init__(
        self,
        documents: list[str] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
        top_k: int = 5,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        super().__init__(top_k)
        self.k1 = k1
        self.b = b
        self.documents: list[str] = []
        self.metadatas: list[dict[str, Any]] = []
        self.bm25 = None

        if documents:
            self.add_documents(documents, metadatas)

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """문서를 추가하고 BM25 인덱스를 재구성합니다."""
        from rank_bm25 import BM25Okapi

        self.documents.extend(documents)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{}] * len(documents))

        tokenized_docs = [self._tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs, k1=self.k1, b=self.b)

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """쿼리에 대해 BM25 점수를 계산하여 상위 결과를 반환합니다."""
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: self.top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append(
                    RetrievalResult(
                        content=self.documents[idx],
                        metadata=self.metadatas[idx],
                        score=float(scores[idx]),
                        source=self.metadatas[idx].get("source", f"doc_{idx}"),
                    )
                )

        return results

    def _tokenize(self, text: str) -> list[str]:
        """간단한 토크나이저(영어/숫자 중심). 한국어는 외부 라이브러리 권장."""
        import re

        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens
