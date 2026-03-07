"""
프롬프트 빌더(PromptBuilder)

RAG(retrieval-augmented generation) 파이프라인에서 검색된 컨텍스트들을 모델 입력용 프롬프트로
정리하는 책임을 가집니다. 시스템 메시지(assistant 역할 규정)와 사용자 메시지(질문+컨텍스트)를
구성하는 유틸리티를 제공합니다.

설계 노트:
- `RetrievalResult`와 같은 외부 타입을 직접 참조하므로 상대 import를 사용합니다.
- 빌더는 텍스트 포맷팅만 담당하며, LLM 호출이나 후처리는 다른 컴포넌트에서 수행합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 검색된 문서 조각들을 읽기 좋은 형태로 합쳐서 LLM의 입력(프롬프트)으로 만드는 역할을 해요.
# 주요 포인트:
# - system_prompt: 모델에게 어떤 역할을 하라고 설명하는 텍스트(예: 규칙, 스타일)
# - user_template: 컨텍스트와 질문을 넣어 사용자 메시지를 만드는 틀입니다.
# - build/build_messages: 컨텍스트를 포맷팅해 최종 메시지 구조를 만듭니다.

from typing import Any
from ..retriever.base_retriever import RetrievalResult


class PromptBuilder:
    """RAG용 프롬프트 생성기.

    속성:
    - `system_prompt`: 시스템(assistant) 역할을 정의하는 텍스트
    - `user_template`: 사용자 메시지 템플릿. `{context}`와 `{question}` 치환을 지원
    """

    DEFAULT_SYSTEM_PROMPT = """당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 AI 어시스턴트입니다.
컨텍스트에 있는 정보만을 사용하여 답변하세요.
컨텍스트에서 답을 찾을 수 없는 경우, "주어진 정보에서 답을 찾을 수 없습니다."라고 답변하세요.
답변은 명확하고 간결하게 작성하세요."""

    DEFAULT_USER_TEMPLATE = """컨텍스트:
{context}

질문: {question}

답변:"""

    def __init__(
        self,
        system_prompt: str | None = None,
        user_template: str | None = None,
    ):
        """초기화: 사용자 지정 프롬프트를 선택적으로 제공할 수 있습니다."""
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.user_template = user_template or self.DEFAULT_USER_TEMPLATE

    def build(
        self,
        question: str,
        contexts: list[RetrievalResult],
        include_sources: bool = True,
    ) -> dict[str, Any]:
        """프롬프트를 조립하여 시스템/사용자 메시지를 포함하는 딕셔너리를 반환합니다."""
        # 컨텍스트를 포맷팅
        context_texts = []
        for i, ctx in enumerate(contexts, 1):
            text = f"[{i}] {ctx.content}"
            if include_sources and ctx.source:
                text += f"\n(출처: {ctx.source})"
            context_texts.append(text)

        context_str = "\n\n".join(context_texts)

        # 사용자 메시지 조립
        user_message = self.user_template.format(
            context=context_str,
            question=question,
        )

        return {
            "system": self.system_prompt,
            "user": user_message,
            "contexts": contexts,
        }

    def build_messages(
        self,
        question: str,
        contexts: list[RetrievalResult],
    ) -> list[dict[str, str]]:
        """LLM API 호출에 사용할 메시지 리스트(역할/내용)를 반환합니다."""
        prompt = self.build(question, contexts)

        # 이해가게 개념설명 알기쉽게 핵심 설명: LLM이 이해하는 형식(role/content)으로 메시지 리스트를 만듭니다.
        return [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ]
