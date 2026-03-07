"""
Retriever(검색기) 베이스 모듈

검색기는 쿼리 입력에 대해 관련 문서를 찾아 반환하는 역할을 합니다. 이 모듈은
결과를 표현하는 `RetrievalResult` 데이터클래스와 검색기 인터페이스 `BaseRetriever`를 제공합니다.

설계 노트:
- 검색 구현은 벡터 기반 검색(Dense), Sparse(키워드), Hybrid(두 방식 결합) 등으로 다양합니다.
- 파이프라인 내에서는 `retrieve`로 후보 문서를 가져오고, `rerank`로 우선순위를 재정렬할 수 있습니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 검색기는 질문(쿼리)에 맞는 문서들을 찾아주는 역할을 해요.
# 주요 포인트:
# - Dense: 벡터(숫자)로 비슷한 문서를 찾아요. Sparse: 키워드나 텍스트 매칭을 사용해요.
# - `retrieve`가 후보를 가져오고, 필요하면 `rerank`로 순서를 바꿀 수 있어요.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalResult:
    """검색 결과를 담는 값 객체.

    필드:
    - `content`: 문서 내용
    - `metadata`: 문서 관련 메타데이터
    - `score`: 검색 점수(유사도 등)
    - `source`: 출처 식별자(파일 경로, URL 등)
    """

    content: str
    metadata: dict[str, Any]
    score: float
    source: str


class BaseRetriever(ABC):
    """검색기 추상 클래스. `retrieve` 메서드 구현 필요."""

    def __init__(self, top_k: int = 5):
        """초기화: 기본적으로 반환할 상위 K개 수를 설정합니다."""
        self.top_k = top_k

    @abstractmethod
    def retrieve(self, query: str) -> list[RetrievalResult]:
        """쿼리 문자열로부터 관련 문서를 검색하여 `RetrievalResult` 리스트를 반환합니다."""
        pass

    def rerank(
        self,
        results: list[RetrievalResult],
        query: str,
    ) -> list[RetrievalResult]:
        """검색 결과에 대해 재정렬을 수행할 수 있는 훅(기본은 변경 없음)."""
        return results
