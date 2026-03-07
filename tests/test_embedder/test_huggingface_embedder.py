"""Tests for HuggingFace embedder."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - HuggingFace 임베더가 모델 초기화와 임베딩 반환을 올바르게 수행하는지 검사합니다.
# 주요 포인트:
# - 모델을 목(MagicMock)으로 대체해 외부 라이브러리 없이 동작을 확인합니다.

import sys
import pytest
import numpy as np
from unittest.mock import MagicMock


class TestHuggingFaceEmbedder:
    """Test cases for HuggingFaceEmbedder."""

    def setup_method(self):
        """Setup mock before each test."""
        # Remove cached modules
        modules_to_remove = [k for k in sys.modules.keys() if 'embedder' in k or k == 'sentence_transformers']
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Create fresh mock
        self.mock_st_module = MagicMock()
        self.mock_model = MagicMock()
        self.mock_st_module.SentenceTransformer.return_value = self.mock_model
        sys.modules["sentence_transformers"] = self.mock_st_module

    def teardown_method(self):
        """Cleanup after each test."""
        if "sentence_transformers" in sys.modules:
            del sys.modules["sentence_transformers"]
        modules_to_remove = [k for k in sys.modules.keys() if 'embedder' in k]
        for mod in modules_to_remove:
            del sys.modules[mod]

    def test_initialization_default_model(self):
        """Test initialization with default model."""
        self.mock_model.get_sentence_embedding_dimension.return_value = 384

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()

        assert embedder.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert embedder.dimension == 384

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        self.mock_model.get_sentence_embedding_dimension.return_value = 768

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder(
            model_name="sentence-transformers/all-mpnet-base-v2",
            device="cuda",
        )

        assert embedder.model_name == "sentence-transformers/all-mpnet-base-v2"
        assert embedder.dimension == 768

    def test_embed_single_text(self):
        """Test embedding single text."""
        mock_embedding = np.array([0.1, 0.2, 0.3])
        self.mock_model.get_sentence_embedding_dimension.return_value = 3
        self.mock_model.encode.return_value = mock_embedding

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        result = embedder.embed("test text")

        assert result == [0.1, 0.2, 0.3]
        self.mock_model.encode.assert_called_once_with(
            "test text",
            convert_to_numpy=True,
        )

    def test_embed_batch(self):
        """Test batch embedding."""
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ])
        self.mock_model.get_sentence_embedding_dimension.return_value = 3
        self.mock_model.encode.return_value = mock_embeddings

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        texts = ["text1", "text2", "text3"]
        result = embedder.embed_batch(texts)

        assert len(result) == 3
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]
        assert result[2] == [0.7, 0.8, 0.9]

    def test_embed_batch_custom_batch_size(self):
        """Test batch embedding with custom batch size."""
        mock_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.mock_model.get_sentence_embedding_dimension.return_value = 2
        self.mock_model.encode.return_value = mock_embeddings

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        texts = ["text1", "text2"]
        result = embedder.embed_batch(texts, batch_size=16)

        self.mock_model.encode.assert_called_once_with(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

    def test_embed_returns_list(self):
        """Test that embed returns a Python list, not numpy array."""
        mock_embedding = np.array([0.1, 0.2, 0.3])
        self.mock_model.get_sentence_embedding_dimension.return_value = 3
        self.mock_model.encode.return_value = mock_embedding

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        result = embedder.embed("test")

        assert isinstance(result, list)
        assert not isinstance(result, np.ndarray)

    def test_embed_batch_returns_list_of_lists(self):
        """Test that embed_batch returns list of lists, not numpy arrays."""
        mock_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.mock_model.get_sentence_embedding_dimension.return_value = 2
        self.mock_model.encode.return_value = mock_embeddings

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        result = embedder.embed_batch(["text1", "text2"])

        assert isinstance(result, list)
        assert all(isinstance(emb, list) for emb in result)

    def test_inherits_cosine_similarity(self):
        """Test that cosine_similarity is inherited from base class."""
        self.mock_model.get_sentence_embedding_dimension.return_value = 3

        from src.embedder.huggingface_embedder import HuggingFaceEmbedder

        embedder = HuggingFaceEmbedder()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = embedder.cosine_similarity(vec1, vec2)

        assert abs(similarity - 1.0) < 1e-6
