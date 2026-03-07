"""
임베더(Embedder) 추상 베이스

임베딩 생성기는 텍스트를 고정 길이 벡터로 변환하는 책임이 있으며,
여기서는 통일된 인터페이스(`BaseEmbedder`)를 정의합니다. 구체 구현체(OpenAI, HuggingFace 등)는
이 클래스를 상속해 `embed`, `embed_batch`를 구현해야 합니다.

설계 노트:
- `embed`는 단일 텍스트 임베딩을 반환하고, `embed_batch`는 리스트 단위로 효율적으로 처리합니다.
- `cosine_similarity` 유틸리티는 임베딩 간 유사도 계산에 사용됩니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 '텍스트를 숫자 벡터로 바꾸는 방법'을 정의한 설계도예요.
# 주요 포인트:
# - 각 구현체는 `embed`와 `embed_batch`를 구현해 텍스트를 벡터로 바꿔줘야 합니다.
# - `cosine_similarity`는 두 벡터가 얼마나 비슷한지 간단히 계산해주는 함수예요.

from abc import ABC, abstractmethod
import numpy as np


class BaseEmbedder(ABC):
    """임베딩 생성기 추상 클래스.

    필수 구현 메서드:
    - `embed(text)`: 단일 텍스트 임베딩 생성
    - `embed_batch(texts)`: 다수 텍스트 임베딩 생성
    """

    def __init__(self, model_name: str, dimension: int):
        """기본 설정(모델 이름, 차원) 보관."""
        self.model_name = model_name
        self.dimension = dimension

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """단일 텍스트에 대한 임베딩 벡터를 반환합니다."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """다수의 텍스트에 대한 임베딩 리스트를 반환합니다."""
        pass

    def cosine_similarity(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        """두 임베딩 벡터 간 코사인 유사도를 계산합니다."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
