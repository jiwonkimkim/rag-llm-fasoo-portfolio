"""Tests for text normalizer."""

import pytest
from src.preprocessor.normalizer import TextNormalizer


class TestTextNormalizerInitialization:
    """Test cases for TextNormalizer initialization."""

    def test_default_initialization(self):
        """Test default initialization values."""
        normalizer = TextNormalizer()

        assert normalizer.lowercase is False
        assert normalizer.normalize_unicode is True
        assert normalizer.normalize_korean is True

    def test_custom_initialization(self):
        """Test custom initialization values."""
        normalizer = TextNormalizer(
            lowercase=True,
            normalize_unicode=False,
            normalize_korean=False,
        )

        assert normalizer.lowercase is True
        assert normalizer.normalize_unicode is False
        assert normalizer.normalize_korean is False


class TestTextNormalizerUnicode:
    """Test cases for unicode normalization."""

    def test_normalize_unicode_nfc(self):
        """Test NFC unicode normalization."""
        normalizer = TextNormalizer(normalize_unicode=True)
        # NFD form: 'ㅎ' + 'ㅏ' + 'ㄴ' composed separately
        text = "\u1112\u1161\u11ab"  # 한 in NFD
        result = normalizer.normalize(text)

        # Should be normalized to NFC form
        assert result == "한"

    def test_normalize_unicode_composed(self):
        """Test that already composed unicode stays composed."""
        normalizer = TextNormalizer(normalize_unicode=True)
        text = "안녕하세요"
        result = normalizer.normalize(text)

        assert result == "안녕하세요"

    def test_skip_unicode_when_disabled(self):
        """Test unicode normalization is skipped when disabled."""
        normalizer = TextNormalizer(normalize_unicode=False)
        text = "Hello World"
        result = normalizer.normalize(text)

        assert result == "Hello World"


class TestTextNormalizerKorean:
    """Test cases for Korean text normalization."""

    def test_remove_zero_width_chars(self):
        """Test removal of zero-width characters."""
        normalizer = TextNormalizer(normalize_korean=True)
        text = "Hello\u200bWorld\u200cTest\u200d"
        result = normalizer.normalize(text)

        assert "\u200b" not in result
        assert "\u200c" not in result
        assert "\u200d" not in result
        assert "HelloWorldTest" in result

    def test_remove_bom(self):
        """Test removal of BOM (Byte Order Mark)."""
        normalizer = TextNormalizer(normalize_korean=True)
        text = "\ufeffHello World"
        result = normalizer.normalize(text)

        assert "\ufeff" not in result
        assert "Hello World" in result

    def test_normalize_curly_double_quotes(self):
        """Test normalization of curly double quotes to straight quotes."""
        normalizer = TextNormalizer(normalize_korean=True)
        # Using unicode escape for curly quotes
        text = "\u201cHello\u201d"  # "Hello"
        result = normalizer.normalize(text)

        assert '"Hello"' in result

    def test_normalize_curly_single_quotes(self):
        """Test normalization of curly single quotes to straight quotes."""
        normalizer = TextNormalizer(normalize_korean=True)
        # Using unicode escape for curly quotes
        text = "\u2018World\u2019"  # 'World'
        result = normalizer.normalize(text)

        assert "'World'" in result

    def test_skip_korean_when_disabled(self):
        """Test Korean normalization is skipped when disabled."""
        normalizer = TextNormalizer(normalize_korean=False)
        text = "\u200bHello"
        result = normalizer.normalize(text)

        assert "\u200b" in result


class TestTextNormalizerLowercase:
    """Test cases for lowercase conversion."""

    def test_convert_to_lowercase(self):
        """Test conversion to lowercase."""
        normalizer = TextNormalizer(lowercase=True)
        text = "Hello WORLD"
        result = normalizer.normalize(text)

        assert result == "hello world"

    def test_lowercase_preserves_korean(self):
        """Test that Korean characters are unaffected by lowercase."""
        normalizer = TextNormalizer(lowercase=True)
        text = "안녕하세요 HELLO"
        result = normalizer.normalize(text)

        assert "안녕하세요" in result
        assert "hello" in result
        assert "HELLO" not in result

    def test_skip_lowercase_when_disabled(self):
        """Test lowercase is skipped when disabled."""
        normalizer = TextNormalizer(lowercase=False)
        text = "Hello WORLD"
        result = normalizer.normalize(text)

        assert result == "Hello WORLD"


class TestTextNormalizerStopwords:
    """Test cases for stopword removal."""

    def test_remove_english_stopwords(self):
        """Test removal of English stopwords."""
        normalizer = TextNormalizer()
        stopwords = ["the", "is", "a", "an"]
        text = "The cat is a cute animal"
        result = normalizer.remove_stopwords(text, stopwords)

        words = result.split()
        assert "The" not in words
        assert "is" not in words
        assert "a" not in words
        assert "cat" in words
        assert "cute" in words
        assert "animal" in words

    def test_remove_korean_stopwords(self):
        """Test removal of Korean stopwords."""
        normalizer = TextNormalizer()
        stopwords = ["은", "는", "이", "가"]
        text = "고양이 는 귀여운 동물 이다"
        result = normalizer.remove_stopwords(text, stopwords)

        assert "는" not in result
        assert "이다" in result  # "이다" is not "이"
        assert "고양이" in result
        assert "귀여운" in result

    def test_remove_stopwords_case_insensitive(self):
        """Test that stopword removal is case insensitive."""
        normalizer = TextNormalizer()
        stopwords = ["the", "is"]
        text = "THE cat IS cute"
        result = normalizer.remove_stopwords(text, stopwords)

        assert "THE" not in result
        assert "IS" not in result
        assert "cat" in result

    def test_remove_stopwords_empty_list(self):
        """Test with empty stopwords list."""
        normalizer = TextNormalizer()
        text = "Hello World"
        result = normalizer.remove_stopwords(text, [])

        assert result == "Hello World"

    def test_remove_stopwords_all_stopwords(self):
        """Test when all words are stopwords."""
        normalizer = TextNormalizer()
        stopwords = ["the", "is", "a"]
        text = "the is a"
        result = normalizer.remove_stopwords(text, stopwords)

        assert result == ""


class TestTextNormalizerCombined:
    """Test cases for combined normalization operations."""

    def test_normalize_with_all_options(self):
        """Test normalization with all options enabled."""
        normalizer = TextNormalizer(
            lowercase=True,
            normalize_unicode=True,
            normalize_korean=True,
        )
        text = "HELLO\u200b \u201cWorld\u201d"
        result = normalizer.normalize(text)

        assert "hello" in result
        assert "\u200b" not in result
        assert "\u201c" not in result  # curly quote should be normalized

    def test_normalize_with_no_options(self):
        """Test normalization with all options disabled."""
        normalizer = TextNormalizer(
            lowercase=False,
            normalize_unicode=False,
            normalize_korean=False,
        )
        text = "HELLO\u200b \u201cWorld\u201d"
        result = normalizer.normalize(text)

        assert "HELLO" in result
        assert "\u200b" in result
        assert "\u201c" in result

    def test_normalize_empty_string(self):
        """Test normalizing empty string."""
        normalizer = TextNormalizer()
        result = normalizer.normalize("")

        assert result == ""

    def test_normalize_korean_text(self):
        """Test normalizing Korean text."""
        normalizer = TextNormalizer(
            lowercase=True,
            normalize_unicode=True,
            normalize_korean=True,
        )
        text = "안녕하세요\u200b \u201c인용문\u201d"
        result = normalizer.normalize(text)

        assert "안녕하세요" in result
        assert "\u200b" not in result
        assert '"인용문"' in result

    def test_normalize_mixed_content(self):
        """Test normalizing mixed Korean/English content."""
        normalizer = TextNormalizer(lowercase=True)
        text = "Hello 안녕 WORLD 세계"
        result = normalizer.normalize(text)

        assert "hello" in result
        assert "안녕" in result
        assert "world" in result
        assert "세계" in result
        assert "WORLD" not in result


class TestTextNormalizerEdgeCases:
    """Test edge cases for TextNormalizer."""

    def test_normalize_numbers(self):
        """Test that numbers are preserved."""
        normalizer = TextNormalizer()
        text = "Price: 12345"
        result = normalizer.normalize(text)

        assert "12345" in result

    def test_normalize_special_chars(self):
        """Test that special characters are preserved."""
        normalizer = TextNormalizer()
        text = "Hello! @#$%"
        result = normalizer.normalize(text)

        assert "Hello!" in result
        assert "@#$%" in result

    def test_normalize_whitespace_preserved(self):
        """Test that whitespace is preserved."""
        normalizer = TextNormalizer()
        text = "Hello   World"
        result = normalizer.normalize(text)

        assert "Hello   World" in result

    def test_normalize_newlines_preserved(self):
        """Test that newlines are preserved."""
        normalizer = TextNormalizer()
        text = "Line 1\nLine 2\n\nLine 3"
        result = normalizer.normalize(text)

        assert "Line 1\nLine 2\n\nLine 3" in result
