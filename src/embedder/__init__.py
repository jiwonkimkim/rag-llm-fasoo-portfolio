"""Embedder module for text vectorization."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 패키지는 텍스트를 숫자 벡터로 바꿔주는 여러 방식(OpenAI, HuggingFace 등)을 모아둔 곳이에요.
# 주요 포인트:
# - 모델마다 성능과 차원이 달라서 사용 목적에 맞게 골라 쓸 수 있어요.

from .base_embedder import BaseEmbedder
from .openai_embedder import OpenAIEmbedder
from .huggingface_embedder import HuggingFaceEmbedder
from .bge_m3_embedder import BGEM3Embedder


def create_embedder(embedder_type: str = "openai", **kwargs) -> BaseEmbedder:
    """설정에 따라 적절한 Embedder를 생성합니다.

    Args:
        embedder_type: embedder 타입 ("openai", "huggingface", "bge-m3")
        **kwargs: 각 embedder에 전달할 추가 인자

    Returns:
        BaseEmbedder 구현체
    """
    embedder_type = embedder_type.lower()

    if embedder_type == "openai":
        return OpenAIEmbedder(**kwargs)
    elif embedder_type == "huggingface":
        return HuggingFaceEmbedder(**kwargs)
    elif embedder_type in ("bge-m3", "bgem3", "bge_m3"):
        return BGEM3Embedder(**kwargs)
    else:
        raise ValueError(f"Unknown embedder type: {embedder_type}")


__all__ = [
    "BaseEmbedder",
    "OpenAIEmbedder",
    "HuggingFaceEmbedder",
    "BGEM3Embedder",
    "create_embedder",
]
