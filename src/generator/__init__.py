"""Generator module for RAG response generation."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 패키지는 LLM 호출, 프롬프트 생성, 응답 파싱을 담당하는 구성요소들을 모아둔 곳이에요.
# 주요 포인트:
# - `PromptBuilder`: 컨텍스트와 질문을 합쳐 모델에 넘길 메시지를 만듭니다.
# - `LLMClient`: 실제로 모델에 요청을 보내 응답을 받아옵니다.
# - `ResponseParser`: 모델의 긴 응답을 정리하고 출처를 추출합니다.

from .prompt_builder import PromptBuilder
from .llm_client import LLMClient
from .response_parser import ResponseParser

__all__ = ["PromptBuilder", "LLMClient", "ResponseParser"]
