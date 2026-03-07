"""
텍스트 정규화기

이 모듈은 유니코드 정규화, 한국어 공백 처리, 소문자 변환, 불용어 제거 등
텍스트를 모델 입력용으로 정리하는 기능을 제공합니다.

설계/주의:
- 유니코드 정규화는 NFC 표준을 사용합니다. 외부 데이터의 인코딩이 불확실한 경우 유용합니다.
- 한국어 공백 정규화는 간단한 규칙 기반이며 모든 케이스를 완벽히 처리하지 못할 수 있습니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 모듈은 텍스트를 컴퓨터가 잘 처리할 수 있는 형태로 정리합니다(유니코드 정규화, 공백 정리, 따옴표 통일 등).
# 주요 함수(한줄 설명):
# - normalize(text): 여러 정규화 단계를 차례로 적용합니다.
# - _normalize_unicode: 유니코드 표준(NFC)으로 맞춰줍니다.
# - _normalize_korean_spacing: 한국어 공백과 특수문자를 간단히 정리합니다.
# 사용처: 모델 입력 전처리, 임베딩 전 텍스트 정리 등

import unicodedata
import re


class TextNormalizer:
    """텍스트 정규화 도우미 클래스.

    인스턴스별로 동작 옵션을 지정할 수 있으므로, 파이프라인의 요구에 맞게 구성하세요.
    """

    def __init__(
        self,
        lowercase: bool = False,
        normalize_unicode: bool = True,
        normalize_korean: bool = True,
    ):
        """초기화

        Args:
            lowercase: 소문자 변환 여부
            normalize_unicode: 유니코드 정규화(NFC) 적용 여부
            normalize_korean: 한국어 공백/특수문자 정규화 적용 여부
        """
        self.lowercase = lowercase
        self.normalize_unicode = normalize_unicode
        self.normalize_korean = normalize_korean

        # 이해가게 개념설명 알기쉽게 핵심 설명:
        # - lowercase: 모든 글자를 소문자로 바꿀지 여부입니다. (검색에 따라 달라요)
        # - normalize_unicode: 문자의 표준 형태로 바꾸는 설정입니다.
        # - normalize_korean: 한국어 띄어쓰기/기호 처리를 할지 여부입니다.

    def normalize(self, text: str) -> str:
        """여러 정규화 단계를 순차적으로 적용하고 결과를 반환합니다."""
        if self.normalize_unicode:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 유니코드 정리 단계로, 문자 표현을 표준으로 맞춰요.
            text = self._normalize_unicode(text)

        if self.normalize_korean:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 한국어 공백/따옴표 등을 간단히 정리해요.
            text = self._normalize_korean_spacing(text)

        if self.lowercase:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 모든 문자를 소문자로 바꿔서 대소문자 차이를 없애요.
            text = text.lower()

        return text
    def _normalize_unicode(self, text: str) -> str:
        """유니코드를 NFC 형태로 정규화합니다."""
        return unicodedata.normalize("NFC", text)

    def _normalize_korean_spacing(self, text: str) -> str:
        """간단한 한국어 공백 및 특수문자 정규화.

        주의: 복잡한 한국어 띄어쓰기 규칙을 완벽히 처리하지는 않습니다. 더 정교한 처리가
        필요하면 외부 라이브러리(예: `kospacing`) 사용을 권장합니다.
        """
        # zero-width 문자 제거
        text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

        # 기본적인 따옴표/인용부호 정규화 (단순 치환)
        # (환경에 따라 더 많은 치환 규칙을 추가할 수 있음)
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace("‘", "'").replace("’", "'")

        return text

    def remove_stopwords(self, text: str, stopwords: list[str]) -> str:
        """주어진 불용어 목록을 기준으로 단어를 필터링합니다."""
        words = text.split()
        filtered_words = [w for w in words if w.lower() not in stopwords]
        return " ".join(filtered_words)
