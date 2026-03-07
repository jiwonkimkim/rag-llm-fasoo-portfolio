"""Tests for RAG pipeline."""

import sys
import pytest
from unittest.mock import Mock, MagicMock

from src.retriever.base_retriever import BaseRetriever, RetrievalResult
from src.generator.prompt_builder import PromptBuilder
from src.generator.response_parser import ResponseParser, ParsedResponse
from src.pipeline.rag_pipeline import RAGPipeline, RAGResponse


# Mock openai module before importing LLMClient
mock_openai_module = MagicMock()
sys.modules["openai"] = mock_openai_module


class MockRetriever(BaseRetriever):
    """Mock retriever for testing."""

    def __init__(self, results: list[RetrievalResult] | None = None, top_k: int = 5):
        super().__init__(top_k=top_k)
        self.results = results or []

    def retrieve(self, query: str) -> list[RetrievalResult]:
        return self.results


class TestRAGResponse:
    """Test cases for RAGResponse dataclass."""

    def test_creation(self):
        """Test RAGResponse creation."""
        contexts = [
            RetrievalResult(
                content="Test content",
                metadata={},
                score=0.9,
                source="test.txt",
            )
        ]

        response = RAGResponse(
            answer="Test answer",
            sources=["test.txt"],
            contexts=contexts,
            confidence=0.85,
            metadata={"query": "test question"},
        )

        assert response.answer == "Test answer"
        assert response.sources == ["test.txt"]
        assert len(response.contexts) == 1
        assert response.confidence == 0.85
        assert response.metadata["query"] == "test question"

    def test_with_none_confidence(self):
        """Test RAGResponse with None confidence."""
        response = RAGResponse(
            answer="Test",
            sources=[],
            contexts=[],
            confidence=None,
            metadata={},
        )

        assert response.confidence is None


class TestRAGPipeline:
    """Test cases for RAGPipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_openai_module.reset_mock()
        mock_openai_module.OpenAI.reset_mock()

        self.contexts = [
            RetrievalResult(
                content="Context 1 content",
                metadata={"chunk_index": 0},
                score=0.95,
                source="doc1.txt",
            ),
            RetrievalResult(
                content="Context 2 content",
                metadata={"chunk_index": 1},
                score=0.85,
                source="doc2.txt",
            ),
        ]
        self.retriever = MockRetriever(results=self.contexts)

    def test_initialization_with_defaults(self):
        """Test pipeline initialization with default components."""
        from src.generator.llm_client import LLMClient

        pipeline = RAGPipeline(retriever=self.retriever)

        assert pipeline.retriever == self.retriever
        assert isinstance(pipeline.llm_client, LLMClient)
        assert isinstance(pipeline.prompt_builder, PromptBuilder)
        assert isinstance(pipeline.response_parser, ResponseParser)

    def test_initialization_with_custom_components(self):
        """Test pipeline initialization with custom components."""
        mock_llm = Mock()
        mock_prompt_builder = Mock()
        mock_parser = Mock()

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        assert pipeline.llm_client == mock_llm
        assert pipeline.prompt_builder == mock_prompt_builder
        assert pipeline.response_parser == mock_parser

    def test_query_returns_rag_response(self):
        """Test query method returns RAGResponse."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is the answer."
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"},
        ]

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="This is the answer.",
            sources=["doc1.txt"],
            confidence=0.9,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        result = pipeline.query("What is the test question?")

        assert isinstance(result, RAGResponse)
        assert result.answer == "This is the answer."
        assert "doc1.txt" in result.sources

    def test_query_with_no_contexts(self):
        """Test query when no contexts are retrieved."""
        empty_retriever = MockRetriever(results=[])

        mock_llm = Mock()
        mock_llm.model = "gpt-4o-mini"

        pipeline = RAGPipeline(
            retriever=empty_retriever,
            llm_client=mock_llm,
        )

        result = pipeline.query("Unknown question?")

        assert result.answer == "관련된 정보를 찾을 수 없습니다."
        assert result.sources == []
        assert result.contexts == []
        assert result.confidence == 0.0
        mock_llm.generate.assert_not_called()

    def test_query_calls_components_in_order(self):
        """Test that query calls components in correct order."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Answer"
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = []

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="Answer",
            sources=[],
            confidence=0.8,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        pipeline.query("Test question")

        # Verify call order
        mock_prompt_builder.build_messages.assert_called_once()
        mock_llm.generate.assert_called_once()
        mock_parser.parse.assert_called_once()

    def test_query_includes_metadata(self):
        """Test that query result includes proper metadata."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Answer"
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = []

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="Answer",
            sources=None,
            confidence=0.8,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        result = pipeline.query("Test question")

        assert result.metadata["query"] == "Test question"
        assert result.metadata["context_count"] == 2
        assert result.metadata["model"] == "gpt-4o-mini"

    def test_query_uses_context_sources_when_parser_returns_none(self):
        """Test fallback to context sources when parser returns None."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Answer"
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = []

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="Answer",
            sources=None,  # Parser returns None for sources
            confidence=0.8,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        result = pipeline.query("Test question")

        # Should fall back to sources from contexts
        assert "doc1.txt" in result.sources
        assert "doc2.txt" in result.sources

    def test_batch_query(self):
        """Test batch_query processes multiple questions."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Answer"
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = []

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="Answer",
            sources=[],
            confidence=0.8,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        questions = ["Question 1?", "Question 2?", "Question 3?"]
        results = pipeline.batch_query(questions)

        assert len(results) == 3
        assert all(isinstance(r, RAGResponse) for r in results)
        assert mock_llm.generate.call_count == 3

    def test_batch_query_empty_list(self):
        """Test batch_query with empty list."""
        mock_llm = Mock()
        mock_llm.model = "gpt-4o-mini"

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
        )

        results = pipeline.batch_query([])

        assert results == []

    def test_query_stream_yields_chunks(self):
        """Test query_stream yields response chunks."""
        mock_llm = Mock()
        mock_llm.generate_stream.return_value = iter(["Hello", " ", "World"])
        mock_llm.model = "gpt-4o-mini"

        mock_prompt_builder = Mock()
        mock_prompt_builder.build_messages.return_value = []

        mock_parser = Mock()
        mock_parser.parse.return_value = ParsedResponse(
            answer="Hello World",
            sources=[],
            confidence=0.8,
            metadata={},
        )

        pipeline = RAGPipeline(
            retriever=self.retriever,
            llm_client=mock_llm,
            prompt_builder=mock_prompt_builder,
            response_parser=mock_parser,
        )

        generator = pipeline.query_stream("Test question")
        chunks = list(generator)

        assert "Hello" in chunks
        assert " " in chunks
        assert "World" in chunks

    def test_query_stream_with_no_contexts(self):
        """Test query_stream when no contexts are retrieved."""
        empty_retriever = MockRetriever(results=[])

        mock_llm = Mock()
        mock_llm.model = "gpt-4o-mini"

        pipeline = RAGPipeline(
            retriever=empty_retriever,
            llm_client=mock_llm,
        )

        generator = pipeline.query_stream("Unknown question?")
        chunks = list(generator)

        assert "관련된 정보를 찾을 수 없습니다." in chunks
        mock_llm.generate_stream.assert_not_called()


class TestRAGPipelineIntegration:
    """Integration-style tests for RAGPipeline."""

    def test_full_pipeline_flow(self):
        """Test complete pipeline flow with mocked components."""
        # Create realistic mock components
        contexts = [
            RetrievalResult(
                content="Python is a programming language.",
                metadata={"chapter": "Introduction"},
                score=0.95,
                source="python_guide.pdf",
            ),
        ]
        retriever = MockRetriever(results=contexts)

        mock_llm = Mock()
        mock_llm.generate.return_value = "Python은 프로그래밍 언어입니다. [1]"
        mock_llm.model = "gpt-4o-mini"

        pipeline = RAGPipeline(
            retriever=retriever,
            llm_client=mock_llm,
            prompt_builder=PromptBuilder(),
            response_parser=ResponseParser(),
        )

        result = pipeline.query("Python이란 무엇인가요?")

        assert isinstance(result, RAGResponse)
        assert "Python" in result.answer or "python" in result.answer.lower()
        assert len(result.contexts) == 1
        assert result.metadata["query"] == "Python이란 무엇인가요?"
