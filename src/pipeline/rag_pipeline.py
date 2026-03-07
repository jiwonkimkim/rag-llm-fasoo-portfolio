"""RAG pipeline for question answering."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - RAG(Retrieval-Augmented Generation) 파이프라인은 관련 문서를 찾아(Lookup) 그 정보를
#   모델에게 주고(Generation) 답변을 만드는 과정을 자동화해요.
# 주요 포인트:
# - 단계: 검색 -> 프롬프트 구성 -> LLM 호출 -> 응답 파싱
# - `query`는 동기 응답, `query_stream`은 스트리밍 방식 응답을 제공합니다.

from typing import Any, Generator
from dataclasses import dataclass

from ..retriever.base_retriever import BaseRetriever, RetrievalResult
from ..generator.prompt_builder import PromptBuilder
from ..generator.llm_client import LLMClient
from ..generator.response_parser import ResponseParser, ParsedResponse


@dataclass
class RAGResponse:
    """RAG pipeline response."""

    answer: str
    sources: list[str]
    contexts: list[RetrievalResult]
    confidence: float | None
    metadata: dict[str, Any]


class RAGPipeline:
    """Complete RAG pipeline for question answering."""

    def __init__(
        self,
        retriever: BaseRetriever,
        llm_client: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
        response_parser: ResponseParser | None = None,
    ):
        """
        Initialize RAG pipeline.

        Args:
            retriever: Document retriever
            llm_client: LLM client for generation
            prompt_builder: Prompt builder
            response_parser: Response parser
        """
        self.retriever = retriever
        self.llm_client = llm_client or LLMClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.response_parser = response_parser or ResponseParser()

    def query(self, question: str) -> RAGResponse:
        """
        Process a question through the RAG pipeline.

        Args:
            question: User question

        Returns:
            RAGResponse with answer and metadata
        """
        # Step 1: Retrieve relevant contexts
        contexts = self.retriever.retrieve(question)

        if not contexts:
            return RAGResponse(
                answer="관련된 정보를 찾을 수 없습니다.",
                sources=[],
                contexts=[],
                confidence=0.0,
                metadata={"query": question},
            )

        # Step 2: Build prompt
        messages = self.prompt_builder.build_messages(question, contexts)

        # Step 3: Generate response
        response = self.llm_client.generate(messages)

        # Step 4: Parse response
        parsed = self.response_parser.parse(response, contexts)

        return RAGResponse(
            answer=parsed.answer,
            sources=parsed.sources or [ctx.source for ctx in contexts],
            contexts=contexts,
            confidence=parsed.confidence,
            metadata={
                "query": question,
                "context_count": len(contexts),
                "model": self.llm_client.model,
            },
        )

    def query_stream(
        self,
        question: str,
    ) -> Generator[str, None, RAGResponse]:
        """
        Process a question with streaming response.

        Args:
            question: User question

        Yields:
            Response chunks

        Returns:
            Final RAGResponse
        """
        # Step 1: Retrieve
        contexts = self.retriever.retrieve(question)

        if not contexts:
            yield "관련된 정보를 찾을 수 없습니다."
            return RAGResponse(
                answer="관련된 정보를 찾을 수 없습니다.",
                sources=[],
                contexts=[],
                confidence=0.0,
                metadata={"query": question},
            )

        # Step 2: Build prompt
        messages = self.prompt_builder.build_messages(question, contexts)

        # Step 3: Stream response
        full_response = ""
        for chunk in self.llm_client.generate_stream(messages):
            full_response += chunk
            yield chunk

        # Step 4: Parse final response
        parsed = self.response_parser.parse(full_response, contexts)

        return RAGResponse(
            answer=parsed.answer,
            sources=parsed.sources or [ctx.source for ctx in contexts],
            contexts=contexts,
            confidence=parsed.confidence,
            metadata={
                "query": question,
                "context_count": len(contexts),
                "model": self.llm_client.model,
            },
        )

    def batch_query(
        self,
        questions: list[str],
    ) -> list[RAGResponse]:
        """
        Process multiple questions.

        Args:
            questions: List of questions

        Returns:
            List of RAGResponse objects
        """
        return [self.query(q) for q in questions]
