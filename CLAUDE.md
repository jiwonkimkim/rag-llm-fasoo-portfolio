# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Triple_c_rag is a modular RAG (Retrieval-Augmented Generation) system designed as a test module for the TripleC organization. It combines web crawling, document preprocessing, text chunking, embedding generation, vector storage, retrieval, and LLM-based generation into complete pipelines.

**Status:** v0.1.0 - Alpha | **License:** MIT

## Commands

### Installation
```bash
pip install -r requirements.txt           # Basic dependencies
pip install -e ".[dev]"                   # With dev tools
pip install -e ".[all]"                   # All extras (PDF, embeddings, FAISS, Pinecone)
```

### Testing
```bash
pytest tests/                              # Run all tests
pytest tests/ -v --tb=short               # Verbose output
pytest tests/ --cov=src                   # With coverage
pytest tests/test_chunker/                # Single module
pytest tests/test_chunker/test_fixed_chunker.py  # Single file
```

### Code Quality
```bash
black src/ tests/ --line-length 88        # Format code
isort src/ tests/ --profile black         # Sort imports
flake8 src/ tests/                         # Lint
mypy src/ --python-version 3.10           # Type check
```

### Running the Application
```bash
# Data ingestion
python scripts/run_ingestion.py --sources data/raw/doc.pdf --source-type file
python scripts/run_ingestion.py --sources https://example.com --source-type web

# RAG queries
python scripts/run_rag.py --query "Your question here"
python scripts/run_rag.py --interactive   # Interactive mode
```

## Architecture

### Pipeline Flow
```
Ingestion: Crawler → Cleaner → Normalizer → Chunker → Embedder → VectorStore
RAG Query: Query → Retriever → LLMClient → PromptBuilder → ResponseParser
```

### Module Structure
- **`src/crawler/`** - Data collection (`WebCrawler`, `FileLoader` for PDF/DOCX)
- **`src/preprocessor/`** - Text cleaning (`TextCleaner`, `TextNormalizer`)
- **`src/chunker/`** - Text splitting (`FixedChunker`, `SemanticChunker`, `RecursiveChunker`)
- **`src/embedder/`** - Vector generation (`OpenAIEmbedder`, `HuggingFaceEmbedder`)
- **`src/vectorstore/`** - Vector DB management (`ChromaStore`, `FAISSStore`, `PineconeStore`)
- **`src/retriever/`** - Document search (`DenseRetriever`, `SparseRetriever`, `HybridRetriever`)
- **`src/generator/`** - LLM response generation (`LLMClient`, `PromptBuilder`, `ResponseParser`)
- **`src/pipeline/`** - Orchestration (`IngestionPipeline`, `RAGPipeline`)
- **`config/`** - Settings (`Settings` dataclass) and logging

### Design Patterns
- **Abstract Base Classes**: Each component has a base class (`BaseCrawler`, `BaseChunker`, `BaseEmbedder`, `BaseVectorStore`, `BaseRetriever`) for implementation swapping
- **Typed Data Transfer Objects**: `Document`, `Chunk`, `RetrievalResult`, `SearchResult`, `RAGResponse`, `IngestionResult`
- **Dependency Injection**: Components receive dependencies in `__init__`

### Data Storage
- `data/raw/` - Original crawled documents
- `data/processed/` - Cleaned text
- `data/chunks/` - Text chunks
- `data/vectordb/` - Vector DB persistence

## Configuration

Settings are managed via `config/settings.py` dataclass with environment variable overrides. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMENSION` | 1536 | Vector dimension |
| `CHUNK_SIZE` | 1000 | Characters per chunk |
| `CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `TOP_K` | 5 | Retrieved documents count |
| `LLM_MODEL` | `gpt-4o-mini` | LLM for generation |
| `LLM_TEMPERATURE` | 0.7 | Response randomness |

Required environment variables in `.env`:
- `OPENAI_API_KEY` (required)
- `PINECONE_API_KEY` (optional, for Pinecone vector store)
- `HUGGINGFACE_API_KEY` (optional, for HuggingFace embeddings)

## Team Responsibilities
- **지원**: `crawler/`, `preprocessor/`
- **지윤**: `chunker/`, `embedder/`
- **동훈**: `vectorstore/`, `retriever/`
- **Collaborative**: `generator/`, `pipeline/`
