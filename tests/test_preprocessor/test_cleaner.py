"""Tests for text cleaner."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 테스트 파일은 TextCleaner가 HTML, URL, 과도한 공백 등을 잘 제거하는지 확인해요.
# 주요 포인트:
# - 각각의 테스트는 특정 기능(HTML 제거, URL 제거, 공백 정리)을 검증합니다.

import pytest
from src.preprocessor.cleaner import TextCleaner


class TestTextCleanerInitialization:
    """Test cases for TextCleaner initialization."""

    def test_default_initialization(self):
        """Test default initialization values."""
        cleaner = TextCleaner()

        assert cleaner.remove_html is True
        assert cleaner.remove_urls is True
        assert cleaner.remove_emails is True
        assert cleaner.remove_special_chars is False

    def test_custom_initialization(self):
        """Test custom initialization values."""
        cleaner = TextCleaner(
            remove_html=False,
            remove_urls=False,
            remove_emails=False,
            remove_special_chars=True,
        )

        assert cleaner.remove_html is False
        assert cleaner.remove_urls is False
        assert cleaner.remove_emails is False
        assert cleaner.remove_special_chars is True


class TestTextCleanerHtmlRemoval:
    """Test cases for HTML tag removal."""

    def test_remove_simple_html_tags(self):
        """Test removal of simple HTML tags."""
        cleaner = TextCleaner(remove_html=True)
        text = "<p>Hello <b>World</b></p>"
        result = cleaner.clean(text)

        assert "<p>" not in result
        assert "</p>" not in result
        assert "<b>" not in result
        assert "</b>" not in result
        assert "Hello" in result
        assert "World" in result

    def test_remove_html_with_attributes(self):
        """Test removal of HTML tags with attributes."""
        cleaner = TextCleaner(remove_html=True)
        text = '<div class="container" id="main">Content</div>'
        result = cleaner.clean(text)

        assert "<div" not in result
        assert "class=" not in result
        assert "Content" in result

    def test_remove_self_closing_tags(self):
        """Test removal of self-closing tags."""
        cleaner = TextCleaner(remove_html=True)
        text = "Line 1<br/>Line 2<hr/>"
        result = cleaner.clean(text)

        assert "<br/>" not in result
        assert "<hr/>" not in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_keep_html_when_disabled(self):
        """Test HTML tags are preserved when removal is disabled."""
        cleaner = TextCleaner(remove_html=False)
        text = "<p>Hello</p>"
        result = cleaner.clean(text)

        assert "<p>" in result
        assert "</p>" in result


class TestTextCleanerUrlRemoval:
    """Test cases for URL removal."""

    def test_remove_https_url(self):
        """Test removal of HTTPS URLs."""
        cleaner = TextCleaner(remove_urls=True)
        text = "Visit https://example.com for more info"
        result = cleaner.clean(text)

        assert "https://example.com" not in result
        assert "Visit" in result
        assert "for more info" in result

    def test_remove_http_url(self):
        """Test removal of HTTP URLs."""
        cleaner = TextCleaner(remove_urls=True)
        text = "Go to http://test.org/page"
        result = cleaner.clean(text)

        assert "http://test.org" not in result

    def test_remove_url_with_path(self):
        """Test removal of URLs with path."""
        cleaner = TextCleaner(remove_urls=True)
        text = "Check https://example.com/path/to/page?query=1"
        result = cleaner.clean(text)

        assert "https://" not in result
        assert "example.com" not in result

    def test_keep_url_when_disabled(self):
        """Test URLs are preserved when removal is disabled."""
        cleaner = TextCleaner(remove_urls=False)
        text = "Visit https://example.com"
        result = cleaner.clean(text)

        assert "https://example.com" in result


class TestTextCleanerEmailRemoval:
    """Test cases for email removal."""

    def test_remove_simple_email(self):
        """Test removal of simple email addresses."""
        cleaner = TextCleaner(remove_emails=True)
        text = "Contact us at test@example.com"
        result = cleaner.clean(text)

        assert "test@example.com" not in result
        assert "Contact us at" in result

    def test_remove_email_with_dots(self):
        """Test removal of emails with dots in local part."""
        cleaner = TextCleaner(remove_emails=True)
        text = "Email: john.doe@company.co.kr"
        result = cleaner.clean(text)

        assert "john.doe@company.co.kr" not in result

    def test_remove_email_with_subdomain(self):
        """Test removal of emails with subdomain."""
        cleaner = TextCleaner(remove_emails=True)
        text = "Send to admin@mail.example.org"
        result = cleaner.clean(text)

        assert "@mail.example.org" not in result

    def test_keep_email_when_disabled(self):
        """Test emails are preserved when removal is disabled."""
        cleaner = TextCleaner(remove_emails=False)
        text = "Email: test@example.com"
        result = cleaner.clean(text)

        assert "test@example.com" in result


class TestTextCleanerSpecialCharsRemoval:
    """Test cases for special character removal."""

    def test_remove_special_chars(self):
        """Test removal of special characters."""
        cleaner = TextCleaner(remove_special_chars=True)
        text = "Hello @#$%^& World!"
        result = cleaner.clean(text)

        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "%" not in result
        assert "^" not in result
        assert "&" not in result
        assert "Hello" in result
        assert "World!" in result  # ! is preserved

    def test_preserve_korean_chars(self):
        """Test that Korean characters are preserved."""
        cleaner = TextCleaner(remove_special_chars=True)
        text = "안녕하세요! Hello @#$"
        result = cleaner.clean(text)

        assert "안녕하세요!" in result
        assert "Hello" in result
        assert "@" not in result
        assert "#" not in result

    def test_preserve_punctuation(self):
        """Test that common punctuation is preserved."""
        cleaner = TextCleaner(remove_special_chars=True)
        text = "Hello, World! How are you?"
        result = cleaner.clean(text)

        assert "," in result
        assert "!" in result
        assert "?" in result

    def test_keep_special_chars_when_disabled(self):
        """Test special chars are preserved when removal is disabled."""
        cleaner = TextCleaner(remove_special_chars=False)
        text = "Hello @#$% World"
        result = cleaner.clean(text)

        assert "@" in result
        assert "#" in result


class TestTextCleanerWhitespaceNormalization:
    """Test cases for whitespace normalization."""

    def test_normalize_multiple_spaces(self):
        """Test normalization of multiple spaces."""
        cleaner = TextCleaner()
        text = "Hello    World"
        result = cleaner.clean(text)

        assert "    " not in result
        assert "Hello World" in result

    def test_normalize_multiple_newlines(self):
        """Test normalization of multiple newlines."""
        cleaner = TextCleaner()
        text = "Line 1\n\n\n\nLine 2"
        result = cleaner.clean(text)

        assert "\n\n\n\n" not in result
        # 3+ newlines should become 2 newlines
        assert result == "Line 1\n\nLine 2"

    def test_strip_leading_trailing_whitespace(self):
        """Test stripping of leading and trailing whitespace."""
        cleaner = TextCleaner()
        text = "   Hello World   "
        result = cleaner.clean(text)

        assert result == "Hello World"

    def test_preserve_double_newlines(self):
        """Test that double newlines are preserved (paragraph breaks)."""
        cleaner = TextCleaner()
        text = "Paragraph 1\n\nParagraph 2"
        result = cleaner.clean(text)

        assert result == "Paragraph 1\n\nParagraph 2"


class TestTextCleanerCombined:
    """Test cases for combined cleaning operations."""

    def test_clean_with_all_options(self):
        """Test cleaning with all options enabled."""
        cleaner = TextCleaner(
            remove_html=True,
            remove_urls=True,
            remove_emails=True,
            remove_special_chars=True,
        )
        text = "<p>Visit https://example.com or email test@test.com @#$%</p>"
        result = cleaner.clean(text)

        assert "<p>" not in result
        assert "https://" not in result
        assert "@test.com" not in result
        assert "@#$%" not in result
        assert "Visit" in result

    def test_clean_with_no_options(self):
        """Test cleaning with all options disabled."""
        cleaner = TextCleaner(
            remove_html=False,
            remove_urls=False,
            remove_emails=False,
            remove_special_chars=False,
        )
        text = "<p>test@example.com https://example.com @#$</p>"
        result = cleaner.clean(text)

        # Only whitespace normalization should happen
        assert "<p>" in result
        assert "test@example.com" in result
        assert "https://example.com" in result
        assert "@#$" in result

    def test_clean_empty_string(self):
        """Test cleaning empty string."""
        cleaner = TextCleaner()
        result = cleaner.clean("")

        assert result == ""

    def test_clean_whitespace_only(self):
        """Test cleaning whitespace-only string."""
        cleaner = TextCleaner()
        result = cleaner.clean("   \n\n   ")

        assert result == ""

    def test_clean_real_world_html(self):
        """Test cleaning real-world HTML content."""
        cleaner = TextCleaner()
        text = """
        <html>
        <body>
            <h1>Welcome</h1>
            <p>Contact us at info@company.com</p>
            <a href="https://company.com">Visit our site</a>
        </body>
        </html>
        """
        result = cleaner.clean(text)

        assert "<html>" not in result
        assert "<body>" not in result
        assert "<h1>" not in result
        assert "info@company.com" not in result
        assert "https://company.com" not in result
        assert "Welcome" in result
        assert "Contact us at" in result
        assert "Visit our site" in result
