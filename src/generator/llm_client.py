"""
LLM API 클라이언트 래퍼

이 모듈은 외부 LLM(예: OpenAI) 라이브러리에 대한 얇은 래퍼를 제공합니다.
직접 라이브러리 호출 코드를 중앙에 모아 재시도, 스트리밍 처리 등의 공통 로직을 관리합니다.

설계 노트:
- 라이브러리 import를 생성자 내부에서 수행하는 이유:
  1) 모듈 임포트 시점의 불필요한 의존성 로드를 피함
  2) 테스트나 일부 환경에서 해당 클라이언트가 설치되어 있지 않은 경우를 안전하게 처리
  3) 순환 import 이슈를 완화 (외부 패키지와의 의존성 문제와는 별개)

사용 예:
    client = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.generate(messages)
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 모듈은 외부 LLM(예: OpenAI) 호출 코드를 한 곳에 모아서 재시도, 스트리밍,
#   설정 관리를 쉽게 하도록 도와줍니다.
# 주요 포인트:
# - 지연 import: OpenAI 같은 패키지를 생성자에서 불러오면 모듈을 바로 임포트해도
#   불필요한 의존성을 피할 수 있어요. (테스트나 설치 환경에서 안전함)
# - generate: 전체 응답을 한 번에 받아서 문자열로 돌려줘요.
# - generate_stream: 응답을 작은 조각(청크)으로 순차적으로 받아서 보여줘요.
# - generate_with_retry: 실패하면 잠시 기다리고 재시도하는 간단한 로직이에요.

from typing import Any, Generator


class LLMClient:
    """LLM 호출을 추상화한 클라이언트 클래스.

    기본적으로 `generate`, `generate_stream`, `generate_with_retry` 메서드를 제공합니다.
    OpenAI와 Groq API를 지원합니다.
    """

    # Groq 모델 목록 (Groq API 사용 - OpenAI 호환)
    # 2025년 최신 모델 - https://console.groq.com/docs/models
    GROQ_MODELS = [
        # Production Models (고성능)
        "llama-3.3-70b-versatile",      # Meta 70B, 280 t/sec, 131K context
        "llama-3.1-8b-instant",          # Meta 8B, 560 t/sec, 가장 빠름
        "openai/gpt-oss-120b",           # OpenAI 120B, 추론 기능 포함
        "openai/gpt-oss-20b",            # OpenAI 20B, 1000 t/sec 초고속
        # Preview Models (실험적)
        "qwen/qwen3-32b",                # Qwen3 32B, 400 t/sec
        "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout, 750 t/sec
        # Legacy Models
        "gemma2-9b-it",                  # Google Gemma2
        "mixtral-8x7b-32768",            # Mistral MoE
    ]

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """초기화

        Args:
            model: 사용할 LLM 모델 이름
            api_key: API 키(선택)
            temperature: 샘플링 온도
            max_tokens: 응답 토큰 상한
        """

        # 이해가게 개념설명 알기쉽게 핵심 설명: LLM을 호출할 때 사용하는 설정들을 이곳에 저장해둡니다.
        # - model: 예를 들어 'gpt-4o-mini' 같은 모델 이름이에요.
        # - api_key: API 키가 있으면 직접 넣고, 없으면 환경변수를 사용하기도 해요.
        # - temperature: 숫자가 작을수록 답이 더 정해진 느낌, 클수록 다양해져요.
        # - max_tokens: 응답의 길이를 제한하는 최대치에요.
        # 지연 import: 모듈 임포트 시점에 OpenAI 패키지가 반드시 필요하지 않도록 함
        import os
        from openai import OpenAI

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Groq 모델인지 확인하고 적절한 클라이언트 설정
        # 이해가게 개념설명 알기쉽게 핵심 설명: Groq는 OpenAI와 호환되는 API를 제공해요.
        # 모델 이름이 Groq 모델 목록에 있으면 Groq API를 사용하고,
        # 그렇지 않으면 OpenAI API를 사용해요.
        if model in self.GROQ_MODELS:
            # Groq API 사용 (OpenAI 호환)
            groq_key = api_key or os.getenv("GROQ_API_KEY")
            self.client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            # OpenAI API 사용
            self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """동기 방식으로 응답을 생성하고 전체 텍스트를 반환합니다."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )

        return response.choices[0].message.content or ""

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """스트리밍 모드로 응답 조각을 순차적으로 yield 합니다."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stream=True,
        )

        for chunk in response:
            # 스트리밍 응답의 조각에서 실제 텍스트 델타가 존재하면 yield
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_with_retry(
        self,
        messages: list[dict[str, str]],
        max_retries: int = 3,
        **kwargs: Any,
    ) -> str:
        """단순 재시도 로직을 적용한 generate 래퍼.

        Exponential backoff을 적용하여 일시적인 네트워크 오류를 견딜 수 있게 합니다.
        """
        import time

        # 이해가게 개념설명 알기쉽게 핵심 설명: 잠깐 기다렸다가(retry) 다시 시도하는 간단한 재시도 로직이에요.
        for attempt in range(max_retries):
            try:
                return self.generate(messages, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    # 이해가게 개념설명 알기쉽게 핵심 설명: 마지막 시도에서도 실패하면 예외를 그대로 올려요.
                    raise e
                # 이해가게 개념설명 알기쉽게 핵심 설명: 실패할 때마다 기다리는 시간을 늘립니다(2^attempt 초).
                time.sleep(2**attempt)  # 지수 백오프

        return ""
