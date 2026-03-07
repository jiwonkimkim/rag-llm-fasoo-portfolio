"""Crawler module for data collection."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 패키지는 웹이나 로컬 파일에서 글을 모으는 도구들을 모아둔 곳이에요.
# 주요 포인트:
# - `WebCrawler`: 웹 페이지에서 텍스트를 추출합니다.
# - `FileLoader`: 로컬 파일을 읽어서 `Document`로 반환해요.
# - `CoupangCrawler`: 쿠팡에서 상품 정보를 수집합니다.
# - `NaverShoppingCrawler`: 네이버 쇼핑에서 상품 정보를 수집합니다.
# - `ImageDownloader`: 이미지를 다운로드하고 관리합니다.

from .base_crawler import BaseCrawler, Document
from .web_crawler import WebCrawler
from .file_loader import FileLoader
from .shopping_crawler import BaseShoppingCrawler, ProductData
from .image_downloader import ImageDownloader, DownloadedImage

# 쇼핑 크롤러는 Selenium 필요 시에만 import
try:
    from .coupang_crawler import CoupangCrawler
    from .naver_shopping_crawler import NaverShoppingCrawler
    SHOPPING_CRAWLERS_AVAILABLE = True
except ImportError:
    CoupangCrawler = None
    NaverShoppingCrawler = None
    SHOPPING_CRAWLERS_AVAILABLE = False

__all__ = [
    "BaseCrawler",
    "Document",
    "WebCrawler",
    "FileLoader",
    "BaseShoppingCrawler",
    "ProductData",
    "ImageDownloader",
    "DownloadedImage",
    "CoupangCrawler",
    "NaverShoppingCrawler",
    "SHOPPING_CRAWLERS_AVAILABLE",
]
