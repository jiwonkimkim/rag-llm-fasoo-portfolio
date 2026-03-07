"""
OpenAI 임베더 래퍼

OpenAI Embeddings API를 호출하여 텍스트 임베딩을 생성합니다. 모델별 차원 정보를
`MODEL_DIMENSIONS`로 관리하며, 필요 시 환경변수나 파라미터로 API 키를 전달할 수 있습니다.

주의사항:
- OpenAI SDK 의존성이 필요합니다. 생성자에서 지연 import를 사용합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - OpenAI의 Embeddings API를 이용해서 텍스트를 벡터로 바꾸는 예시 구현이에요.
# 주요 포인트:
# - 모델 이름에 따라 임베딩 차원이 미리 정해져 있고, API 호출로 임베딩을 받아옵니다.
# - 배치 처리로 여러 텍스트를 한 번에 요청해 효율을 높일 수 있어요.

from typing import Any
from .base_embedder import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI Embeddings API용 임베더.

    - `embed`: 단일 텍스트 임베딩 반환
    - `embed_batch`: 배치 처리로 여러 텍스트 임베딩을 생성
    """

    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
    ):
        """초기화: 모델 차원을 결정하고 OpenAI 클라이언트를 준비합니다."""
        dimension = self.MODEL_DIMENSIONS.get(model_name, 1536)
        super().__init__(model_name, dimension)

        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)

    def embed(self, text: str) -> list[float]:
        """단일 텍스트 임베딩을 생성합니다."""
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """배치 단위로 임베딩을 생성합니다. API 호출 횟수를 줄이기 위해 청크로 분할합니다."""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch,
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

        return all_embeddings
