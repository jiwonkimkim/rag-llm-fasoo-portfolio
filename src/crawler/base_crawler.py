"""
크롤러 베이스 모듈

웹 페이지나 파일 등 외부 소스에서 텍스트를 수집하여 `Document` 객체로 반환하는
크롤러(혹은 로더)의 인터페이스를 정의합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 '어디서 글을 가져오는가'를 정의하는 설계도예요(웹, 파일 등).
# 주요 포인트:
# - `crawl`은 한 곳에서 문서를 수집하고, `crawl_multiple`은 여러 곳을 순회해 문서를 모아요.
# - `Document`는 수집된 텍스트와 출처 정보를 담는 작은 상자입니다.

from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass


@dataclass
class Document:
    """크롤러가 반환하는 문서 값 객체.

    필드:
    - `content`: 수집한 텍스트 내용
    - `metadata`: 수집시 생성되는 메타데이터(출처, 타임스탬프 등)
    - `source`: 원본 식별자(예: URL 또는 파일 경로)
    """

    content: str
    metadata: dict[str, Any]
    source: str


class BaseCrawler(ABC):
    """크롤러/로더의 추상 인터페이스.

    - `crawl`: 단일 소스에서 문서를 수집
    - `crawl_multiple`: 여러 소스를 순회하며 문서를 수집
    """

    @abstractmethod
    def crawl(self, source: str) -> list[Document]:
        """단일 소스에서 문서 목록을 수집하여 반환합니다."""
        pass

    @abstractmethod
    def crawl_multiple(self, sources: list[str]) -> list[Document]:
        """복수의 소스를 순회하여 문서를 수집합니다."""
        pass
