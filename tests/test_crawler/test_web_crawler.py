"""Tests for web crawler."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 WebCrawler가 웹 페이지에서 텍스트를 잘 추출하는지 간단히 검증합니다.
# 주요 포인트:
# - 타임아웃과 헤더 설정이 올바른지, 잘못된 URL에 대해 빈 리스트를 반환하는지 확인합니다.

import pytest
from unittest.mock import patch, MagicMock
from src.crawler.web_crawler import WebCrawler


class TestWebCrawler:
    """Test cases for WebCrawler."""

    def test_crawler_initialization(self):
        """Test crawler initialization."""
        crawler = WebCrawler()
        assert crawler.timeout == 30
        assert "User-Agent" in crawler.headers

    @patch("src.crawler.web_crawler.requests.Session")
    def test_crawl_invalid_url(self, mock_session_class):
        """Test crawling invalid URL returns empty list."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session_class.return_value = mock_session

        crawler = WebCrawler()
        documents = crawler.crawl("http://invalid-url-that-does-not-exist.com")

        assert documents == []

    @patch("src.crawler.web_crawler.requests.Session")
    def test_crawl_success(self, mock_session_class):
        """Test successful crawl returns document."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test</title></head><body><p>Hello World</p></body></html>"
        mock_response.apparent_encoding = "utf-8"
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        crawler = WebCrawler()
        documents = crawler.crawl("http://example.com")

        assert len(documents) == 1
        assert "Hello World" in documents[0].content
        assert documents[0].metadata["title"] == "Test"
        assert documents[0].metadata["url"] == "http://example.com"
