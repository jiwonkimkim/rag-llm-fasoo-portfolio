"""
텍스트 전처리용 클리너

이 모듈은 HTML 태그, URL, 이메일 주소, 특수문자 등을 제거하는 유틸리티 클래스를 제공합니다.
전처리 파이프라인의 초기 단계에서 잡음을 제거하여 이후 임베딩/인덱싱 품질을 향상시키는 목적입니다.

설계 노트(객체/전역/순환 import 관련):
- `TextCleaner`는 상태를 갖는 인스턴스(객체)로 구성되어 있으며, 각 인스턴스의 옵션에 따라 동작이 달라집니다.
- 전역으로 하나의 인스턴스를 공유하려면 `config.settings`와 함께 팩터리 또는 싱글턴 패턴을 사용할 수 있습니다.
- 이 모듈은 다른 패키지를 import 하지 않으므로 순환 import 위험이 낮습니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 모듈은 HTML 태그, URL, 이메일, 불필요한 특수문자를 제거해서
#   모델에 넣기 좋게 텍스트를 정리해 줍니다.
# 주요 함수(한줄 설명):
# - clean(text): 설정에 따라 여러 정제 단계를 차례로 실행해요.
# - _remove_html_tags(text): <...> 같은 HTML을 지웁니다.
# - _remove_urls(text): http://... 같은 URL을 지웁니다.
# - _remove_emails(text): 이메일 주소를 지웁니다.
# - _normalize_whitespace(text): 여러 공백과 개행을 정리합니다.

import re
from typing import Any


class TextCleaner:
    """텍스트 정제기를 제공하는 클래스.

    기본적으로 HTML 태그, URL, 이메일을 제거하도록 설정되어 있으며,
    필요에 따라 특수문자 제거 옵션을 켜거나 끌 수 있습니다.
    """

    def __init__(
        self,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_special_chars: bool = False,
        reduce_repeated_chars: bool = True,
        max_repeat: int = 2,
    ):
        """
        초기화

        Args:
            remove_html: HTML 태그 제거 여부
            remove_urls: URL 제거 여부
            remove_emails: 이메일 주소 제거 여부
            remove_special_chars: 한글/기본 구두점 외 특수문자 제거 여부
            reduce_repeated_chars: 반복 문자 축소 여부 (예: 'zzzzz' -> 'zz')
            max_repeat: 허용할 최대 반복 횟수 (기본값: 2)
        """
        self.remove_html = remove_html
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_special_chars = remove_special_chars
        self.reduce_repeated_chars = reduce_repeated_chars
        self.max_repeat = max_repeat

        # 이해가게 개념설명 알기쉽게 핵심 설명:
        # - remove_html/remove_urls/remove_emails/remove_special_chars는 어떤 정제 단계를 켤지 끌지 정해요.
        # - True이면 해당 단계가 실행됩니다.

    def clean(self, text: str) -> str:
        """
        입력 텍스트를 순차적으로 정제하고 최종 결과를 반환합니다.

        Args:
            text: 입력 문자열

        Returns:
            정제된 문자열
        """
        if self.remove_html:
            # 이해가게 개념설명 알기쉽게 핵심 설명: HTML 태그가 있으면 이 줄에서 지워요.
            text = self._remove_html_tags(text)

        if self.remove_urls:
            # 이해가게 개념설명 알기쉽게 핵심 설명: URL 형태(http://...)를 찾아서 지워요.
            text = self._remove_urls(text)

        if self.remove_emails:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 이메일 주소 형태를 찾아서 지워요.
            text = self._remove_emails(text)

        if self.remove_special_chars:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 특수문자(의미없는 기호)를 지우는 단계예요.
            text = self._remove_special_chars(text)

        if self.reduce_repeated_chars:
            # 이해가게 개념설명 알기쉽게 핵심 설명: 연속으로 반복되는 문자를 줄여줘요 (예: 'zzzzz' -> 'zz')
            text = self._reduce_repeated_chars(text)

        # 불필요한 공백 정리
        # 이해가게 개념설명 알기쉽게 핵심 설명: 여러 개의 공백이나 지나친 줄바꿈을 정리해요.
        text = self._normalize_whitespace(text)

        return text

    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그를 제거합니다 (간단한 정규식 기반)."""
        pattern = re.compile(r"<[^>]+>")
        return pattern.sub("", text)

    def _remove_urls(self, text: str) -> str:
        """URL을 제거합니다 (http/https 패턴)."""
        pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        return pattern.sub("", text)

    def _remove_emails(self, text: str) -> str:
        """이메일 주소를 제거합니다."""
        pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        return pattern.sub("", text)

    def _remove_special_chars(self, text: str) -> str:
        """특수문자를 제거하되 한글과 자주 쓰이는 구두점은 유지합니다."""
        pattern = re.compile(r"[^\w\s가-힣.,!?;:'\"-]")
        return pattern.sub("", text)

    def _normalize_whitespace(self, text: str) -> str:
        """여러 공백/연속 개행을 정규화합니다."""
        # 연속된 스페이스를 단일 스페이스로
        text = re.sub(r" +", " ", text)
        # 3개 이상의 연속 개행은 2개의 개행으로 축소
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _reduce_repeated_chars(self, text: str) -> str:
        """연속으로 반복되는 문자를 max_repeat 개수로 축소합니다.

        예: max_repeat=2일 때
        - 'zzzzzz' -> 'zz'
        - '!!!!!!' -> '!!'
        - 'sooooo' -> 'soo'
        - 'hahaha' -> 'haha' (패턴 반복도 처리)
        """
        # 동일 문자 연속 반복 처리 (예: zzzzz -> zz)
        pattern = re.compile(r"(.)\1{" + str(self.max_repeat) + r",}")
        text = pattern.sub(r"\1" * self.max_repeat, text)

        # 2-3글자 패턴 반복 처리 (예: hahaha -> haha, lololol -> lolo)
        # 2글자 패턴
        text = re.sub(r"(.{2})\1{2,}", r"\1\1", text)
        # 3글자 패턴
        text = re.sub(r"(.{3})\1{2,}", r"\1\1", text)

        return text
