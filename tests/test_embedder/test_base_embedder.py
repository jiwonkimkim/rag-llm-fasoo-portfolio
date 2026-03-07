"""Tests for base embedder."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - BaseEmbedder의 기본 동작, 특히 `cosine_similarity`가 올바르게 작동하는지 검사합니다.
# 주요 포인트:
# - 구체 클래스(ConcreteEmbedder)를 만들어 추상 메서드 계약을 테스트합니다.

import pytest
import numpy as np
from src.embedder.base_embedder import BaseEmbedder


class ConcreteEmbedder(BaseEmbedder):
    """Concrete implementation for testing."""

    def embed(self, text: str) -> list[float]:
        return [0.1] * self.dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self.dimension for _ in texts]


class TestBaseEmbedder:
    """Test cases for BaseEmbedder."""

    def test_initialization(self):
        """Test embedder initialization."""
        embedder = ConcreteEmbedder(model_name="test-model", dimension=128)

        assert embedder.model_name == "test-model"
        assert embedder.dimension == 128

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        embedder = ConcreteEmbedder(model_name="test", dimension=3)
        vec = [1.0, 2.0, 3.0]

        similarity = embedder.cosine_similarity(vec, vec)

        assert abs(similarity - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        embedder = ConcreteEmbedder(model_name="test", dimension=2)
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert abs(similarity - 0.0) < 1e-6

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors."""
        embedder = ConcreteEmbedder(model_name="test", dimension=3)
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert abs(similarity - (-1.0)) < 1e-6

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector returns 0."""
        embedder = ConcreteEmbedder(model_name="test", dimension=3)
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [0.0, 0.0, 0.0]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert similarity == 0.0

    def test_cosine_similarity_similar_vectors(self):
        """Test cosine similarity with similar vectors."""
        embedder = ConcreteEmbedder(model_name="test", dimension=3)
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.1, 2.1, 3.1]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert 0.99 < similarity < 1.0

    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods raise TypeError if not implemented."""

        class IncompleteEmbedder(BaseEmbedder):
            pass

        with pytest.raises(TypeError):
            IncompleteEmbedder(model_name="test", dimension=128)
