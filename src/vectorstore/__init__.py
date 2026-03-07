"""Vector store module for embedding storage."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 패키지는 임베딩(숫자 벡터)을 저장하고 검색하는 여러 구현체를 모아둔 곳이에요(FAISS, Chroma, Pinecone).
# 주요 포인트:
# - `BaseVectorStore`는 규칙(인터페이스)을 정의하고, 각 구현체는 이를 따라 벡터를 저장/조회해요.

from .base_store import BaseVectorStore
from .chroma_store import ChromaStore
from .faiss_store import FAISSStore
from .pinecone_store import PineconeStore

__all__ = ["BaseVectorStore", "ChromaStore", "FAISSStore", "PineconeStore"]
