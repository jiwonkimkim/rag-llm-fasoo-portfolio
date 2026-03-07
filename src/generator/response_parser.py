"""
LLM 응답 파서

이 모듈은 모델이 반환한 문자열을 파싱하여 구조화된 `ParsedResponse` 객체로 변환합니다.
주요 기능은 다음과 같습니다:
- 응답에서 출처(예: [1], [2])를 추출
- 응답 텍스트 정리 및 포맷팅
- 간단한 휴리스틱 기반 신뢰도(confidence) 추정

설계 노트:
- 파서는 모델 응답의 형식에 강하게 의존하므로 실제 사용 모델의 출력 포맷에 맞춰
  커스터마이즈 해야 합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 모델이 준 긴 문자열을 깔끔하게 정리하고, 응답에서 참조한 출처를 찾아 목록으로 만들어요.
# 주요 기능:
# - _extract_sources: [1], [2] 같은 인용 표기를 찾아 원본 컨텍스트의 출처를 연결합니다.
# - _clean_response: 너무 많은 개행을 정리하고 불필요한 공백을 제거합니다.
# - _estimate_confidence: 단순한 규칙으로 응답의 신뢰도를 추정합니다.

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedResponse:
    """파싱된 응답을 담는 데이터 객체.

    필드:
    - `answer`: 정제된 응답 텍스트
    - `sources`: 응답에서 참조된 출처 목록
    - `confidence`: 응답 신뢰도(0.0-1.0) 또는 None
    - `metadata`: 원본 응답 등 추가 메타데이터
    """

    answer: str
    sources: list[str]
    confidence: float | None
    metadata: dict[str, Any]


class ResponseParser:
    """모델 응답을 해석하는 파서 클래스."""

    def __init__(self):
        """초기화(현재 상태 없음)."""
        pass

    def parse(
        self,
        response: str,
        contexts: list[Any] | None = None,
    ) -> ParsedResponse:
        """원시 응답을 파싱하여 `ParsedResponse`를 반환합니다."""
        # 인용된 출처 추출
        sources = self._extract_sources(response, contexts)

        # 응답 텍스트 정리
        answer = self._clean_response(response)

        # 간단한 휴리스틱으로 신뢰도 추정
        confidence = self._estimate_confidence(response, contexts)

        return ParsedResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            metadata={
                "raw_response": response,
                "context_count": len(contexts) if contexts else 0,
            },
        )

    def _extract_sources(
        self,
        response: str,
        contexts: list[Any] | None,
    ) -> list[str]:
        """응답에서 [1], [2] 형식의 인용을 찾아 원본 컨텍스트의 출처를 매핑합니다."""
        sources = []

        # [1], [2] 같은 패턴을 찾음
        citations = re.findall(r"\[(\d+)\]", response)

        if contexts and citations:
            for citation in set(citations):
                idx = int(citation) - 1
                if 0 <= idx < len(contexts):
                    source = getattr(contexts[idx], "source", None)
                    if source and source not in sources:
                        sources.append(source)

        return sources

    def _clean_response(self, response: str) -> str:
        """여러 개의 연속 개행을 정리하고 앞뒤 공백을 제거합니다."""
        response = re.sub(r"\n{3,}", "\n\n", response)
        response = response.strip()

        return response

    def _estimate_confidence(
        self,
        response: str,
        contexts: list[Any] | None,
    ) -> float | None:
        """간단한 휴리스틱을 사용해 응답의 신뢰도를 추정합니다.

        휴리스틱 예:
        - 불확실 표현(예: "잘 모르겠음")이 있으면 신뢰도 감소
        - 사용된 컨텍스트 수가 많으면 신뢰도 소폭 증가
        """
        if not contexts:
            return None

        confidence = 0.8  # 기본 신뢰도

        uncertainty_phrases = [
            "잘 모르겠",
            "확실하지 않",
            "찾을 수 없",
            "정보가 부족",
            "불확실",
            "may not",
            "not sure",
            "cannot find",
        ]

        # 이해가게 개념설명 알기쉽게 핵심 설명: 불확실을 나타내는 표현이 응답에 있으면 신뢰도를 깎습니다.
        for phrase in uncertainty_phrases:
            if phrase in response.lower():
                confidence -= 0.2
                break

        # 컨텍스트 수 기반 보정
        if len(contexts) >= 3:
            confidence += 0.1
        elif len(contexts) == 1:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))
