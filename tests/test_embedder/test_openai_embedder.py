"""Tests for OpenAI embedder."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 테스트는 OpenAI 임베더가 올바르게 초기화되고 임베딩을 반환하는지 확인해요.
# 주요 포인트:
# - openai 모듈을 목(mock)으로 만들어 외부 호출 없이 동작을 검증합니다.

import sys
import pytest
from unittest.mock import Mock, MagicMock


class TestOpenAIEmbedder:
    """Test cases for OpenAIEmbedder."""

    def setup_method(self):
        """Setup mock before each test."""
        # Remove cached modules
        modules_to_remove = [k for k in sys.modules.keys() if 'embedder' in k or k == 'openai']
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Create fresh mock
        self.mock_openai_module = MagicMock()
        self.mock_client = MagicMock()
        self.mock_openai_module.OpenAI.return_value = self.mock_client
        sys.modules["openai"] = self.mock_openai_module

    def teardown_method(self):
        """Cleanup after each test."""
        if "openai" in sys.modules:
            del sys.modules["openai"]
        modules_to_remove = [k for k in sys.modules.keys() if 'embedder' in k]
        for mod in modules_to_remove:
            del sys.modules[mod]

    def test_initialization_default_model(self):
        """Test initialization with default model."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")

        assert embedder.model_name == "text-embedding-3-small"
        assert embedder.dimension == 1536

    def test_initialization_large_model(self):
        """Test initialization with large model."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(
            model_name="text-embedding-3-large",
            api_key="test-key",
        )

        assert embedder.model_name == "text-embedding-3-large"
        assert embedder.dimension == 3072

    def test_initialization_ada_model(self):
        """Test initialization with ada model."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(
            model_name="text-embedding-ada-002",
            api_key="test-key",
        )

        assert embedder.model_name == "text-embedding-ada-002"
        assert embedder.dimension == 1536

    def test_initialization_unknown_model(self):
        """Test initialization with unknown model defaults to 1536 dimension."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(
            model_name="unknown-model",
            api_key="test-key",
        )

        assert embedder.dimension == 1536

    def test_embed_single_text(self):
        """Test embedding single text."""
        mock_embedding = [0.1] * 1536
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        self.mock_client.embeddings.create.return_value = mock_response

        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")
        result = embedder.embed("test text")

        assert result == mock_embedding

    def test_embed_batch(self):
        """Test batch embedding."""
        mock_embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
        mock_response = Mock()
        mock_response.data = [Mock(embedding=emb) for emb in mock_embeddings]
        self.mock_client.embeddings.create.return_value = mock_response

        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")
        texts = ["text1", "text2", "text3"]
        result = embedder.embed_batch(texts)

        assert len(result) == 3
        assert result == mock_embeddings

    def test_embed_batch_with_batching(self):
        """Test batch embedding with multiple API calls."""
        mock_embedding = [0.1] * 1536
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding), Mock(embedding=mock_embedding)]
        self.mock_client.embeddings.create.return_value = mock_response

        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")
        texts = ["text1", "text2", "text3", "text4"]
        result = embedder.embed_batch(texts, batch_size=2)

        assert len(result) == 4

    def test_embed_batch_empty_list(self):
        """Test batch embedding with empty list."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")
        result = embedder.embed_batch([])

        assert result == []

    def test_model_dimensions_constant(self):
        """Test MODEL_DIMENSIONS constant."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        assert OpenAIEmbedder.MODEL_DIMENSIONS == {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

    def test_inherits_cosine_similarity(self):
        """Test that cosine_similarity is inherited from base class."""
        from src.embedder.openai_embedder import OpenAIEmbedder

        embedder = OpenAIEmbedder(api_key="test-key")
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert abs(similarity - 1.0) < 1e-6
