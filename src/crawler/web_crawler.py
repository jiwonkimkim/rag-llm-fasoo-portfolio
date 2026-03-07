"""
웹 크롤러 구현

간단한 HTML 파싱을 통해 웹 페이지의 텍스트를 추출하고 `Document` 객체로 반환합니다.
외부 라이브러리(`requests`, `beautifulsoup4`)에 의존합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 인터넷의 웹 페이지에서 텍스트를 긁어와서 `Document`로 만들어 주는 도구예요.
# 주요 포인트:
# - requests로 페이지를 받아오고, BeautifulSoup으로 HTML을 파싱해 필요한 텍스트를 추출합니다.
# - 스크립트나 스타일 등 불필요한 태그는 지워서 보기 좋은 텍스트만 남깁니다.

import requests
from bs4 import BeautifulSoup
from typing import Any
from urllib.parse import urljoin, urlparse

from .base_crawler import BaseCrawler, Document


class WebCrawler(BaseCrawler):
    """웹 페이지를 가져와 텍스트를 추출하는 크롤러."""

    def __init__(
        self,
        headers: dict[str, str] | None = None,
        timeout: int = 30
    ):
        """세션 설정 및 기본 헤더 초기화."""
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def crawl(self, source: str) -> list[Document]:
        """단일 URL에서 텍스트를 추출하여 `Document`로 반환합니다."""
        try:
            response = self.session.get(source, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, "html.parser")

            # 스크립트/스타일/네비게이션/푸터 등 불필요한 요소 제거
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)

            metadata = {
                "title": soup.title.string if soup.title else "",
                "url": source,
                "domain": urlparse(source).netloc,
                "status_code": response.status_code,
            }

            return [Document(content=text, metadata=metadata, source=source)]

        except Exception as e:
            print(f"Error crawling {source}: {e}")
            return []

    def crawl_multiple(self, sources: list[str]) -> list[Document]:
        """여러 URL을 순회하여 문서를 수집합니다."""
        documents = []
        for source in sources:
            documents.extend(self.crawl(source))
        return documents
