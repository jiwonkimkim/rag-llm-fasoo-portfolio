"""Preprocessor module for text cleaning and normalization."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 텍스트를 정리하고(청소) 표준 형태로 바꾸는 기능을 모아둔 패키지예요.
# 주요 포인트:
# - `TextCleaner`: 불필요한 HTML, URL, 특수문자 등을 제거합니다.
# - `TextNormalizer`: 유니코드 정리나 공백 정리 등을 수행해요.

from .cleaner import TextCleaner
from .normalizer import TextNormalizer

__all__ = ["TextCleaner", "TextNormalizer"]
