"""
쇼핑몰 크롤러 베이스 모듈

쿠팡, 네이버 쇼핑 등 쇼핑몰에서 상품 정보를 수집하기 위한
베이스 클래스와 데이터 구조를 정의합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime


@dataclass
class ProductData:
    """수집된 상품 데이터"""
    product_id: str
    title: str
    price: str
    image_url: str
    detail_url: str
    description: str = ""
    source: str = ""  # 'coupang' | 'naver'
    rating: str = ""
    review_count: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseShoppingCrawler(ABC):
    """쇼핑몰 크롤러 추상 베이스 클래스"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """크롤러 소스 이름 (예: 'coupang', 'naver')"""
        pass

    @abstractmethod
    def search_products(self, keyword: str, max_results: int = 20) -> list[ProductData]:
        """키워드로 상품 검색

        Args:
            keyword: 검색 키워드
            max_results: 최대 결과 수

        Returns:
            상품 데이터 리스트
        """
        pass

    @abstractmethod
    def get_product_detail(self, product_url: str) -> ProductData | None:
        """상품 상세 정보 수집

        Args:
            product_url: 상품 상세 페이지 URL

        Returns:
            상품 데이터 또는 None
        """
        pass

    def close(self):
        """리소스 정리 (필요시 오버라이드)"""
        pass
