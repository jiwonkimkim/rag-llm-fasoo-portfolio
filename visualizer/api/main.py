"""FastAPI main application for RAG pipeline visualization.

Updated: Added demo mode for collect search endpoint.
"""

import sys
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .models import (
    PreprocessRequest, PreprocessResponse,
    ChunkRequest, ChunkResponse,
    EmbedRequest, EmbedResponse,
    RetrieveRequest, RetrieveResponse, RetrievalResultModel,
    GenerateRequest, GenerateResponse,
    PipelineRequest, PipelineResponse,
    HealthResponse,
    ChunkerType, EmbedderType, RetrieverType, EmbeddingMode,
    VectorStoreType, StoreRequest, StoreResponse,
    StoreListResponse, StoredVectorInfo, StoreStatsResponse,
    ModelStatusRequest, ModelStatusResponse,
    ModelInstallRequest, ModelInstallResponse,
    QuickQueryRequest, QuickQueryResponse,
)


# Global state for loaded modules
app_state: dict[str, Any] = {}
logger = logging.getLogger(__name__)


def _parse_cors_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8501",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _internal_server_error(error: Exception) -> HTTPException:
    logger.exception("Unhandled exception: %s", error)
    return HTTPException(status_code=500, detail="Internal server error")


def check_module_available(module_name: str) -> bool:
    """Check if a module is available."""
    try:
        if module_name == "preprocessor":
            from src.preprocessor.cleaner import TextCleaner
            from src.preprocessor.normalizer import TextNormalizer
            return True
        elif module_name == "chunker":
            from src.chunker.fixed_chunker import FixedChunker
            return True
        elif module_name == "embedder":
            from src.embedder.base_embedder import BaseEmbedder
            return True
        elif module_name == "retriever":
            from src.retriever.base_retriever import BaseRetriever
            return True
        elif module_name == "vectorstore":
            from src.vectorstore.base_store import BaseVectorStore
            return True
        elif module_name == "generator":
            from src.generator.llm_client import LLMClient
            return True
    except ImportError:
        return False
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: Check available modules
    app_state["modules"] = {
        "preprocessor": check_module_available("preprocessor"),
        "chunker": check_module_available("chunker"),
        "embedder": check_module_available("embedder"),
        "retriever": check_module_available("retriever"),
        "vectorstore": check_module_available("vectorstore"),
        "generator": check_module_available("generator"),
    }
    yield
    # Shutdown: Cleanup if needed
    app_state.clear()


app = FastAPI(
    title="Triple_c_rag Pipeline Visualizer API",
    description="API for visualizing and testing RAG pipeline components",
    version="1.0.0",
    lifespan=lifespan,
)

api_auth_key = os.getenv("API_AUTH_KEY")
cors_origins = _parse_cors_origins()
allow_all_origins = cors_origins == ["*"]


@app.middleware("http")
async def enforce_api_key(request: Request, call_next):
    if not api_auth_key:
        return await call_next(request)

    if request.url.path in {"/health", "/docs", "/openapi.json", "/redoc"}:
        return await call_next(request)

    request_api_key = request.headers.get("x-api-key")
    if request_api_key != api_auth_key:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        modules=app_state.get("modules", {}),
    )


# Preprocessor endpoints
@app.post("/api/v1/preprocess", response_model=PreprocessResponse, tags=["Preprocessor"])
async def preprocess_text(request: PreprocessRequest):
    """Preprocess text using cleaner and normalizer."""
    try:
        from src.preprocessor.cleaner import TextCleaner
        from src.preprocessor.normalizer import TextNormalizer

        steps = []
        current_text = request.text
        cleaned_text = None
        normalized_text = None

        # Step 1: Cleaner
        if request.use_cleaner:
            cleaner = TextCleaner(**request.cleaner_options)
            cleaned_text = cleaner.clean(current_text)
            steps.append({
                "step": "cleaner",
                "input": current_text,
                "output": cleaned_text,
                "options": request.cleaner_options,
            })
            current_text = cleaned_text

        # Step 2: Normalizer
        if request.use_normalizer:
            normalizer = TextNormalizer(**request.normalizer_options)
            normalized_text = normalizer.normalize(current_text)
            steps.append({
                "step": "normalizer",
                "input": current_text,
                "output": normalized_text,
                "options": request.normalizer_options,
            })
            current_text = normalized_text

        return PreprocessResponse(
            original=request.text,
            cleaned=cleaned_text,
            normalized=normalized_text,
            final=current_text,
            steps=steps,
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Preprocessor module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Chunker endpoints
@app.post("/api/v1/chunk", response_model=ChunkResponse, tags=["Chunker"])
async def chunk_text(request: ChunkRequest):
    """Chunk text using selected chunker."""
    try:
        chunks = []

        if request.chunker_type == ChunkerType.FIXED:
            from src.chunker.fixed_chunker import FixedChunker
            chunker = FixedChunker(
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
            )
            chunks = chunker.chunk(request.text)
        elif request.chunker_type == ChunkerType.SEMANTIC:
            from src.chunker.semantic_chunker import SemanticChunker
            chunker = SemanticChunker(
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
            )
            chunks = chunker.chunk(request.text)

        chunk_texts = [c.content if hasattr(c, 'content') else str(c) for c in chunks]

        return ChunkResponse(
            original_length=len(request.text),
            chunks=chunk_texts,
            chunk_count=len(chunk_texts),
            avg_chunk_size=sum(len(c) for c in chunk_texts) / len(chunk_texts) if chunk_texts else 0,
            settings={
                "chunker_type": request.chunker_type.value,
                "chunk_size": request.chunk_size,
                "chunk_overlap": request.chunk_overlap,
            },
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Chunker module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Helper function to convert numpy types to Python native types
def _convert_to_native(obj):
    """Recursively convert numpy types to Python native types for JSON serialization."""
    import numpy as np

    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: _convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_native(item) for item in obj]
    else:
        return obj


# Helper function to run sync code in executor
def _embed_sync(embedder_type: str, texts: list[str], model_name: str | None, api_key: str | None, embedding_mode: str | None):
    """Synchronous embedding function to be run in executor.

    Note: This function runs in a ThreadPoolExecutor to avoid blocking
    the async event loop, which resolves Windows-specific issues with
    sentence-transformers and uvicorn.
    """
    embedder = None
    extra_data = {}

    if embedder_type == "openai":
        from src.embedder.openai_embedder import OpenAIEmbedder
        model_name = model_name or "text-embedding-3-small"
        embedder = OpenAIEmbedder(model_name=model_name, api_key=api_key)
        embeddings = embedder.embed_batch(texts)
    elif embedder_type == "huggingface":
        from src.embedder.huggingface_embedder import HuggingFaceEmbedder
        model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        embedder = HuggingFaceEmbedder(model_name=model_name)
        embeddings = embedder.embed_batch(texts)
    elif embedder_type == "bge-m3":
        from src.embedder.bge_m3_embedder import BGEM3Embedder
        model_name = model_name or "BAAI/bge-m3"
        embedder = BGEM3Embedder(model_name=model_name)
        if embedding_mode == "dense":
            embeddings = embedder.embed_batch(texts)
        elif embedding_mode in ["dense+sparse", "all"]:
            result = embedder.embed_with_all(
                texts,
                return_dense=True,
                return_sparse=True,
                return_colbert=(embedding_mode == "all"),
            )
            embeddings = result.get("dense_vecs", [])
            # Convert numpy types to native Python types for JSON serialization
            extra_data["lexical_weights"] = _convert_to_native(result.get("lexical_weights", []))
            if "colbert_vecs" in result:
                extra_data["colbert_vecs"] = _convert_to_native(result["colbert_vecs"])
        else:
            embeddings = embedder.embed_batch(texts)
    else:
        raise ValueError(f"Invalid embedder type: {embedder_type}")

    # Ensure embeddings are also native Python types
    embeddings = _convert_to_native(embeddings)

    return embeddings, model_name, extra_data


# Embedder endpoints
@app.post("/api/v1/embed", tags=["Embedder"])
async def embed_texts(request: EmbedRequest):
    """Embed texts using selected embedder."""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    try:
        # Run sync embedding in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            embeddings, model_name, extra_data = await loop.run_in_executor(
                executor,
                _embed_sync,
                request.embedder_type.value,
                request.texts,
                request.model_name,
                request.api_key,
                request.embedding_mode.value if request.embedding_mode else "dense",
            )

        response_data = {
            "texts": request.texts,
            "embeddings": embeddings,
            "dimension": len(embeddings[0]) if embeddings else 0,
            "embedder_type": request.embedder_type.value,
            "model_name": model_name,
        }

        if extra_data:
            response_data["extra"] = extra_data

        return response_data

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Embedder module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Legacy embed endpoint (keeping for backward compatibility, but not used)
@app.post("/api/v1/embed_legacy", tags=["Embedder"])
async def embed_texts_legacy(request: EmbedRequest):
    """Legacy embed endpoint - kept for reference."""
    try:
        embedder = None
        model_name = request.model_name
        extra_data = {}

        if request.embedder_type == EmbedderType.OPENAI:
            from src.embedder.bge_m3_embedder import BGEM3Embedder
            model_name = model_name or "BAAI/bge-m3"
            embedder = BGEM3Embedder(model_name=model_name)

            # BGE-M3는 여러 타입의 임베딩을 지원
            if request.embedding_mode == EmbeddingMode.DENSE:
                embeddings = embedder.embed_batch(request.texts)
            elif request.embedding_mode in [EmbeddingMode.DENSE_SPARSE, EmbeddingMode.ALL]:
                result = embedder.embed_with_all(
                    request.texts,
                    return_dense=True,
                    return_sparse=True,
                    return_colbert=(request.embedding_mode == EmbeddingMode.ALL),
                )
                embeddings = result.get("dense_vecs", [])
                extra_data["lexical_weights"] = result.get("lexical_weights", [])
                if "colbert_vecs" in result:
                    extra_data["colbert_vecs"] = result["colbert_vecs"]
            else:
                embeddings = embedder.embed_batch(request.texts)
        else:
            raise HTTPException(status_code=400, detail="Invalid embedder type")

        response_data = {
            "texts": request.texts,
            "embeddings": embeddings,
            "dimension": len(embeddings[0]) if embeddings else 0,
            "embedder_type": request.embedder_type.value,
            "model_name": model_name,
        }

        # BGE-M3 추가 데이터 포함
        if extra_data:
            response_data["extra"] = extra_data

        return response_data

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Embedder module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Vector Store endpoints
def get_vector_store(store_type: VectorStoreType, collection_name: str):
    """Get vector store instance based on type."""
    persist_dir = project_root / "data" / "vectordb" / collection_name
    persist_dir.mkdir(parents=True, exist_ok=True)

    if store_type == VectorStoreType.CHROMA:
        from src.vectorstore.chroma_store import ChromaStore
        return ChromaStore(collection_name=collection_name, persist_directory=str(persist_dir))
    elif store_type == VectorStoreType.FAISS:
        from src.vectorstore.faiss_store import FAISSStore
        return FAISSStore(persist_directory=str(persist_dir))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported store type: {store_type}")


@app.post("/api/v1/store", response_model=StoreResponse, tags=["VectorStore"])
async def store_embeddings(request: StoreRequest):
    """Store embeddings in vector database."""
    try:
        store = get_vector_store(request.store_type, request.collection_name)

        # Generate IDs for each embedding
        import uuid
        from datetime import datetime
        ids = [str(uuid.uuid4()) for _ in request.texts]

        # Prepare metadatas with embedder info
        metadatas = request.metadatas or [{"index": i} for i in range(len(request.texts))]

        # Add embedder info to each metadata for auto-detection later
        embedder_type = request.embedder_type.value if request.embedder_type else "huggingface"
        model_name = request.model_name or "intfloat/multilingual-e5-base"

        # Collection-level metadata (stored in first vector for retrieval)
        collection_meta = {
            "_embedder_type": embedder_type,
            "_model_name": model_name,
            "_display_name": request.display_name or "",
            "_description": request.description or "",
            "_prep_store_type": request.prep_store_type or "standard",
            "_chunking_algorithm": request.chunking_algorithm or "FixedChunker",
            "_chunk_size": request.chunk_size or 512,
            "_chunk_overlap": request.chunk_overlap or 50,
            "_extra_body_length": request.extra_body_length or 0,
            "_min_chunk_group_size": request.min_chunk_group_size or 1,
            "_total_documents": request.total_documents or 1,
            "_success_documents": request.success_documents or 1,
            "_failed_documents": request.failed_documents or 0,
            "_total_chunks": len(request.texts),
            "_created_at": datetime.now().isoformat(),
        }

        for i, meta in enumerate(metadatas):
            # Add basic embedder info to all vectors
            meta["_embedder_type"] = embedder_type
            meta["_model_name"] = model_name
            # Add full collection metadata to first vector only
            if i == 0:
                meta.update(collection_meta)

        # Store embeddings
        store.add(
            ids=ids,
            embeddings=request.embeddings,
            documents=request.texts,
            metadatas=metadatas,
        )

        return StoreResponse(
            success=True,
            stored_count=len(request.texts),
            collection_name=request.collection_name,
            store_type=request.store_type.value,
            total_count=store.count(),
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"VectorStore module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


@app.get("/api/v1/store", response_model=StoreListResponse, tags=["VectorStore"])
async def list_stored_vectors(
    collection_name: str = "rag_collection",
    store_type: VectorStoreType = VectorStoreType.CHROMA,
    page: int = 1,
    page_size: int = 10,
):
    """List stored vectors in the database."""
    try:
        store = get_vector_store(store_type, collection_name)

        # Get all vectors from Chroma
        if store_type == VectorStoreType.CHROMA:
            result = store.collection.get(
                limit=page_size,
                offset=(page - 1) * page_size,
                include=["documents", "metadatas"],
            )

            vectors = []
            if result["ids"]:
                for i, id in enumerate(result["ids"]):
                    vectors.append(StoredVectorInfo(
                        id=id,
                        content=result["documents"][i] if result["documents"] else "",
                        metadata=result["metadatas"][i] if result["metadatas"] else {},
                    ))

            return StoreListResponse(
                collection_name=collection_name,
                store_type=store_type.value,
                total_count=store.count(),
                vectors=vectors,
                page=page,
                page_size=page_size,
            )
        else:
            # For other store types, return empty list for now
            return StoreListResponse(
                collection_name=collection_name,
                store_type=store_type.value,
                total_count=store.count(),
                vectors=[],
                page=page,
                page_size=page_size,
            )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"VectorStore module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


@app.get("/api/v1/store/stats", response_model=StoreStatsResponse, tags=["VectorStore"])
async def get_store_stats(
    collection_name: str = "rag_collection",
    store_type: VectorStoreType = VectorStoreType.CHROMA,
):
    """Get vector store statistics."""
    try:
        store = get_vector_store(store_type, collection_name)

        return StoreStatsResponse(
            collection_name=collection_name,
            store_type=store_type.value,
            total_count=store.count(),
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"VectorStore module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


@app.delete("/api/v1/store", tags=["VectorStore"])
async def delete_store(
    collection_name: str = "rag_collection",
    store_type: VectorStoreType = VectorStoreType.CHROMA,
):
    """Permanently delete a collection from the store."""
    try:
        store = get_vector_store(store_type, collection_name)
        store.delete_collection()

        return {"success": True, "message": f"Deleted collection: {collection_name}"}
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"VectorStore module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


@app.get("/api/v1/store/collections", tags=["VectorStore"])
async def list_collections(
    store_type: VectorStoreType = VectorStoreType.CHROMA,
):
    """List all available collections in the vector store with detailed metadata."""
    try:
        import os

        vectordb_dir = project_root / "data" / "vectordb"

        if not vectordb_dir.exists():
            return {"collections": [], "store_type": store_type.value}

        collections = []
        for item in vectordb_dir.iterdir():
            if item.is_dir():
                # Check if collection has data (chroma.sqlite3 for ChromaDB)
                chroma_db = item / "chroma.sqlite3"
                if chroma_db.exists() or any(item.iterdir()):
                    # Get collection stats and metadata
                    try:
                        store = get_vector_store(store_type, item.name)
                        count = store.count()

                        # Default collection info
                        collection_info = {
                            "name": item.name,
                            "count": count,
                            "store_type": store_type.value,
                            # Basic info
                            "display_name": "",
                            "embedder_type": None,
                            "model_name": None,
                            "description": "",
                            "prep_store_type": "legacy",
                            "created_at": None,
                            # Chunking options
                            "chunking_algorithm": None,
                            "chunk_size": None,
                            "chunk_overlap": None,
                            "extra_body_length": None,
                            "min_chunk_group_size": None,
                            # Stats
                            "total_chunks": count,
                            "total_documents": None,
                            "success_documents": None,
                            "failed_documents": None,
                        }

                        # Try to get full metadata from first vector
                        if count > 0 and store_type == VectorStoreType.CHROMA:
                            result = store.collection.get(limit=1, include=["metadatas"])
                            if result["metadatas"] and len(result["metadatas"]) > 0:
                                first_meta = result["metadatas"][0]
                                # Update with stored metadata
                                collection_info.update({
                                    "display_name": first_meta.get("_display_name", ""),
                                    "embedder_type": first_meta.get("_embedder_type"),
                                    "model_name": first_meta.get("_model_name"),
                                    "description": first_meta.get("_description", ""),
                                    "prep_store_type": first_meta.get("_prep_store_type", "legacy"),
                                    "created_at": first_meta.get("_created_at"),
                                    "chunking_algorithm": first_meta.get("_chunking_algorithm"),
                                    "chunk_size": first_meta.get("_chunk_size"),
                                    "chunk_overlap": first_meta.get("_chunk_overlap"),
                                    "extra_body_length": first_meta.get("_extra_body_length"),
                                    "min_chunk_group_size": first_meta.get("_min_chunk_group_size"),
                                    "total_chunks": first_meta.get("_total_chunks", count),
                                    "total_documents": first_meta.get("_total_documents"),
                                    "success_documents": first_meta.get("_success_documents"),
                                    "failed_documents": first_meta.get("_failed_documents"),
                                })

                        collections.append(collection_info)
                    except Exception:
                        # Collection exists but might be empty or corrupted
                        collections.append({
                            "name": item.name,
                            "count": 0,
                            "store_type": store_type.value,
                            "display_name": "",
                            "embedder_type": None,
                            "model_name": None,
                            "description": "",
                            "prep_store_type": "legacy",
                            "created_at": None,
                            "chunking_algorithm": None,
                            "chunk_size": None,
                            "chunk_overlap": None,
                            "extra_body_length": None,
                            "min_chunk_group_size": None,
                            "total_chunks": 0,
                            "total_documents": None,
                            "success_documents": None,
                            "failed_documents": None,
                        })

        # Sort by created_at or name (newest first)
        collections.sort(key=lambda x: x.get("created_at") or x["name"], reverse=True)

        return {"collections": collections, "store_type": store_type.value}
    except Exception as e:
        raise _internal_server_error(e)


# Retriever endpoints - actual vector search implementation
@app.post("/api/v1/retrieve", response_model=RetrieveResponse, tags=["Retriever"])
async def retrieve_documents(request: RetrieveRequest):
    """Retrieve documents from vector store using query embedding."""
    try:
        settings = {
            "retriever_type": request.retriever_type.value,
            "top_k": request.top_k,
            "collection_name": request.collection_name,
            "store_type": request.store_type.value,
        }

        if request.retriever_type == RetrieverType.HYBRID:
            settings["dense_weight"] = request.dense_weight
            settings["sparse_weight"] = request.sparse_weight

        # Get embedder for query
        embedder = None
        if request.embedder_type == EmbedderType.OPENAI:
            from src.embedder.openai_embedder import OpenAIEmbedder
            model_name = request.model_name or "text-embedding-3-small"
            embedder = OpenAIEmbedder(model_name=model_name, api_key=request.api_key)
        elif request.embedder_type == EmbedderType.HUGGINGFACE:
            from src.embedder.huggingface_embedder import HuggingFaceEmbedder
            model_name = request.model_name or "intfloat/multilingual-e5-base"
            embedder = HuggingFaceEmbedder(model_name=model_name)
        elif request.embedder_type == EmbedderType.BGE_M3:
            from src.embedder.bge_m3_embedder import BGEM3Embedder
            model_name = request.model_name or "BAAI/bge-m3"
            embedder = BGEM3Embedder(model_name=model_name)

        # Embed the query
        query_embedding = embedder.embed(request.query)

        # Get vector store and search
        store = get_vector_store(request.store_type, request.collection_name)

        # Search using ChromaDB's query method
        if request.store_type == VectorStoreType.CHROMA:
            search_results = store.collection.query(
                query_embeddings=[query_embedding],
                n_results=request.top_k,
                include=["documents", "metadatas", "distances"],
            )

            results = []
            if search_results["ids"] and search_results["ids"][0]:
                for i, doc_id in enumerate(search_results["ids"][0]):
                    # ChromaDB returns L2 distance, convert to similarity score
                    distance = search_results["distances"][0][i] if search_results["distances"] else 0
                    score = 1 / (1 + distance)  # Convert distance to similarity

                    content = search_results["documents"][0][i] if search_results["documents"] else ""
                    metadata = search_results["metadatas"][0][i] if search_results["metadatas"] else {}
                    metadata["id"] = doc_id

                    results.append(RetrievalResultModel(
                        content=content,
                        metadata=metadata,
                        score=round(score, 4),
                        source=metadata.get("source", f"chunk_{i}"),
                    ))
        else:
            # For other store types, return empty results for now
            results = []

        return RetrieveResponse(
            query=request.query,
            results=results,
            retriever_type=request.retriever_type.value,
            settings=settings,
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Generator endpoints
@app.post("/api/v1/generate", response_model=GenerateResponse, tags=["Generator"])
async def generate_response(request: GenerateRequest):
    """Generate response using LLM."""
    try:
        from src.generator.llm_client import LLMClient

        # Build context string from list of context documents
        context_str = "\n\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(request.context)])

        # Build messages for LLM (system + user message)
        system_prompt = """당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 AI 어시스턴트입니다.
컨텍스트에 있는 정보만을 사용하여 답변하세요.
컨텍스트에서 답을 찾을 수 없는 경우, "주어진 정보에서 답을 찾을 수 없습니다."라고 답변하세요.
답변은 명확하고 간결하게 작성하세요."""

        user_message = f"""컨텍스트:
{context_str}

질문: {request.query}

답변:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Generate response (use provided API key or fall back to environment variable)
        llm_client = LLMClient(
            model=request.model,
            temperature=request.temperature,
            api_key=request.api_key,
        )
        response = llm_client.generate(messages)

        return GenerateResponse(
            query=request.query,
            context_used=request.context,
            response=response,
            model=request.model,
            usage=None,  # Add usage stats if available
        )
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Generator module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# Quick Query endpoint (Retrieve + Generate in one call)
@app.post("/api/v1/query", response_model=QuickQueryResponse, tags=["Query Mode"])
async def quick_query(request: QuickQueryRequest):
    """Quick query: Retrieve documents and generate response in one call.

    This endpoint is designed for querying existing vector databases directly,
    without going through the full pipeline (preprocess, chunk, embed, store).
    """
    try:
        from src.generator.llm_client import LLMClient

        # Step 1: Get embedder for query
        embedder = None
        if request.embedder_type == EmbedderType.OPENAI:
            from src.embedder.openai_embedder import OpenAIEmbedder
            model_name = request.model_name or "text-embedding-3-small"
            embedder = OpenAIEmbedder(model_name=model_name, api_key=request.api_key)
        elif request.embedder_type == EmbedderType.HUGGINGFACE:
            from src.embedder.huggingface_embedder import HuggingFaceEmbedder
            model_name = request.model_name or "intfloat/multilingual-e5-base"
            embedder = HuggingFaceEmbedder(model_name=model_name)
        elif request.embedder_type == EmbedderType.BGE_M3:
            from src.embedder.bge_m3_embedder import BGEM3Embedder
            model_name = request.model_name or "BAAI/bge-m3"
            embedder = BGEM3Embedder(model_name=model_name)

        # Step 2: Embed the query
        query_embedding = embedder.embed(request.query)

        # Step 3: Get vector store and search
        store = get_vector_store(request.store_type, request.collection_name)

        # Search using ChromaDB's query method
        sources = []
        context_texts = []

        if request.store_type == VectorStoreType.CHROMA:
            search_results = store.collection.query(
                query_embeddings=[query_embedding],
                n_results=request.top_k,
                include=["documents", "metadatas", "distances"],
            )

            if search_results["ids"] and search_results["ids"][0]:
                for i, doc_id in enumerate(search_results["ids"][0]):
                    distance = search_results["distances"][0][i] if search_results["distances"] else 0
                    score = 1 / (1 + distance)

                    content = search_results["documents"][0][i] if search_results["documents"] else ""
                    metadata = search_results["metadatas"][0][i] if search_results["metadatas"] else {}

                    context_texts.append(content)
                    sources.append({
                        "content": content,
                        "score": round(score, 4),
                        "metadata": metadata,
                    })

        # Step 4: Generate response using LLM
        context_str = "\n\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(context_texts)])

        system_prompt = """당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 AI 어시스턴트입니다.
컨텍스트에 있는 정보만을 사용하여 답변하세요.
컨텍스트에서 답을 찾을 수 없는 경우, "주어진 정보에서 답을 찾을 수 없습니다."라고 답변하세요.
답변은 명확하고 간결하게 작성하세요."""

        user_message = f"""컨텍스트:
{context_str}

질문: {request.query}

답변:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        llm_client = LLMClient(
            model=request.llm_model,
            temperature=request.temperature,
            api_key=request.api_key,
        )
        answer = llm_client.generate(messages)

        return QuickQueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            retriever_type=request.retriever_type.value,
            llm_model=request.llm_model,
            collection_name=request.collection_name,
        )

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Module not available: {e}")
    except Exception as e:
        raise _internal_server_error(e)


# n8n Integration endpoints
@app.post("/api/v1/pipeline/full", response_model=PipelineResponse, tags=["n8n Integration"])
async def run_full_pipeline(request: PipelineRequest):
    """Run full RAG pipeline - designed for n8n webhook integration."""
    try:
        steps = []
        metadata = {}

        # Step 1: Preprocess query
        preprocess_req = PreprocessRequest(
            text=request.query,
            use_cleaner=request.use_cleaner,
            use_normalizer=request.use_normalizer,
        )
        preprocess_resp = await preprocess_text(preprocess_req)
        steps.append({
            "name": "preprocess",
            "input": request.query,
            "output": preprocess_resp.final,
            "details": preprocess_resp.steps,
        })
        processed_query = preprocess_resp.final

        # Step 2: Retrieve relevant documents
        retrieve_req = RetrieveRequest(
            query=processed_query,
            retriever_type=RetrieverType(request.retriever_type.value),
            top_k=request.top_k,
        )
        retrieve_resp = await retrieve_documents(retrieve_req)
        context = [r.content for r in retrieve_resp.results]
        steps.append({
            "name": "retrieve",
            "input": processed_query,
            "output": context,
            "result_count": len(context),
            "settings": retrieve_resp.settings,
        })

        # Step 3: Generate response
        generate_req = GenerateRequest(
            query=processed_query,
            context=context,
            model=request.model,
            temperature=request.temperature,
        )
        generate_resp = await generate_response(generate_req)
        steps.append({
            "name": "generate",
            "input": {"query": processed_query, "context_count": len(context)},
            "output": generate_resp.response,
            "model": request.model,
        })

        metadata = {
            "total_steps": len(steps),
            "retriever_type": request.retriever_type.value,
            "model": request.model,
            "top_k": request.top_k,
        }

        return PipelineResponse(
            query=request.query,
            steps=steps,
            final_response=generate_resp.response,
            metadata=metadata,
        )
    except Exception as e:
        raise _internal_server_error(e)


# n8n Webhook endpoints
@app.post("/webhook/n8n/query", tags=["n8n Integration"])
async def n8n_query_webhook(payload: dict[str, Any]):
    """Webhook endpoint for n8n to trigger RAG queries.

    Expected payload:
    {
        "query": "user question",
        "settings": {
            "retriever_type": "dense|sparse|hybrid",
            "top_k": 5,
            "model": "gpt-3.5-turbo"
        }
    }
    """
    try:
        query = payload.get("query", "")
        settings = payload.get("settings", {})

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        pipeline_req = PipelineRequest(
            query=query,
            retriever_type=RetrieverType(settings.get("retriever_type", "dense")),
            top_k=settings.get("top_k", 5),
            model=settings.get("model", "gpt-3.5-turbo"),
            temperature=settings.get("temperature", 0.7),
        )

        return await run_full_pipeline(pipeline_req)
    except Exception as e:
        raise _internal_server_error(e)


@app.post("/webhook/n8n/ingest", tags=["n8n Integration"])
async def n8n_ingest_webhook(payload: dict[str, Any]):
    """Webhook endpoint for n8n to trigger document ingestion.

    Expected payload:
    {
        "documents": ["doc1 content", "doc2 content"],
        "metadatas": [{"source": "file1.txt"}, {"source": "file2.txt"}],
        "settings": {
            "chunker_type": "fixed",
            "chunk_size": 512
        }
    }
    """
    try:
        documents = payload.get("documents", [])
        metadatas = payload.get("metadatas", [])
        settings = payload.get("settings", {})

        if not documents:
            raise HTTPException(status_code=400, detail="Documents are required")

        results = []
        for i, doc in enumerate(documents):
            # Chunk each document
            chunk_req = ChunkRequest(
                text=doc,
                chunker_type=ChunkerType(settings.get("chunker_type", "fixed")),
                chunk_size=settings.get("chunk_size", 512),
                chunk_overlap=settings.get("chunk_overlap", 50),
            )
            chunk_resp = await chunk_text(chunk_req)

            results.append({
                "document_index": i,
                "original_length": chunk_resp.original_length,
                "chunk_count": chunk_resp.chunk_count,
                "chunks": chunk_resp.chunks,
                "metadata": metadatas[i] if i < len(metadatas) else {},
            })

        return {
            "status": "success",
            "total_documents": len(documents),
            "total_chunks": sum(r["chunk_count"] for r in results),
            "results": results,
        }
    except Exception as e:
        raise _internal_server_error(e)


# Model Management endpoints
def _check_model_installed(embedder_type: str, model_name: str) -> tuple[bool, str | None, float | None]:
    """Check if a model is installed locally."""
    import os

    if embedder_type == "openai":
        # OpenAI models don't need local installation
        return True, None, None

    # For HuggingFace and BGE-M3 models, check the cache directory
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")

    # Convert model name to cache folder format (e.g., "sentence-transformers/all-MiniLM-L6-v2" -> "models--sentence-transformers--all-MiniLM-L6-v2")
    model_folder_name = f"models--{model_name.replace('/', '--')}"
    model_path = os.path.join(cache_dir, model_folder_name)

    if os.path.exists(model_path):
        # Calculate folder size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(model_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        size_mb = total_size / (1024 * 1024)
        return True, model_path, round(size_mb, 2)

    return False, None, None


def _install_model_sync(embedder_type: str, model_name: str) -> tuple[bool, str, str | None]:
    """Synchronous function to install/download a model."""
    try:
        if embedder_type == "openai":
            return True, "OpenAI models don't require local installation", None

        elif embedder_type == "huggingface":
            from sentence_transformers import SentenceTransformer
            # This will download the model if not already cached
            model = SentenceTransformer(model_name)
            cache_path = model._model_card_vars.get("modelId", model_name)
            return True, f"Model '{model_name}' installed successfully", cache_path

        elif embedder_type == "bge-m3":
            from FlagEmbedding import BGEM3FlagModel
            # This will download the model if not already cached
            model = BGEM3FlagModel(model_name, use_fp16=True)
            return True, f"Model '{model_name}' installed successfully", None

        else:
            return False, f"Unknown embedder type: {embedder_type}", None

    except Exception as e:
        return False, f"Failed to install model: {str(e)}", None


@app.post("/api/v1/model/status", response_model=ModelStatusResponse, tags=["Model Management"])
async def check_model_status(request: ModelStatusRequest):
    """Check if a model is installed locally."""
    try:
        installed, cache_path, size_mb = _check_model_installed(
            request.embedder_type.value,
            request.model_name
        )

        return ModelStatusResponse(
            model_name=request.model_name,
            embedder_type=request.embedder_type.value,
            installed=installed,
            cache_path=cache_path,
            size_mb=size_mb,
        )
    except Exception as e:
        raise _internal_server_error(e)


@app.post("/api/v1/model/install", response_model=ModelInstallResponse, tags=["Model Management"])
async def install_model(request: ModelInstallRequest):
    """Install/download a model."""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    try:
        # Run sync installation in thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            success, message, cache_path = await loop.run_in_executor(
                executor,
                _install_model_sync,
                request.embedder_type.value,
                request.model_name,
            )

        return ModelInstallResponse(
            model_name=request.model_name,
            embedder_type=request.embedder_type.value,
            success=success,
            message=message,
            cache_path=cache_path,
        )
    except Exception as e:
        raise _internal_server_error(e)


# =====================================================
# Collect Mode Endpoints (쇼핑몰 상품 수집)
# =====================================================

from .models import (
    ShoppingSource,
    CollectSearchRequest,
    CollectSearchResponse,
    ProductResult,
    CollectDownloadRequest,
    CollectDownloadResponse,
    CollectedImage,
    CollectImageListResponse,
    CollectDeleteRequest,
    CollectDeleteResponse,
)

# Initialize image downloader
_image_downloader = None

def get_image_downloader():
    """Get or create image downloader singleton."""
    global _image_downloader
    if _image_downloader is None:
        from src.crawler import ImageDownloader
        _image_downloader = ImageDownloader(str(project_root / "data" / "images"))
    return _image_downloader


def _generate_demo_products(keyword: str, sources: list, max_results: int) -> list:
    """데모용 상품 데이터 생성"""
    demo_products = []

    # 샘플 이미지 (placeholder 이미지 사용)
    sample_images = [
        "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Product+1",
        "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Product+2",
        "https://via.placeholder.com/300x300/EC4899/FFFFFF?text=Product+3",
        "https://via.placeholder.com/300x300/F59E0B/FFFFFF?text=Product+4",
        "https://via.placeholder.com/300x300/10B981/FFFFFF?text=Product+5",
        "https://via.placeholder.com/300x300/3B82F6/FFFFFF?text=Product+6",
    ]

    idx = 0
    for source in sources:
        source_name = source.value if hasattr(source, 'value') else str(source)
        for i in range(min(max_results, 6)):
            demo_products.append(ProductResult(
                product_id=f"demo_{source_name}_{i+1}",
                title=f"[데모] {keyword} 상품 {i+1} ({source_name})",
                price=f"{(i+1) * 10000 + 9900:,}원",
                image_url=sample_images[i % len(sample_images)],
                detail_url=f"https://example.com/product/{source_name}/{i+1}",
                source=source_name,
                rating=f"{4.0 + (i % 10) / 10:.1f}",
                review_count=f"{(i+1) * 100}",
            ))
            idx += 1

    return demo_products


@app.post("/api/v1/collect/search", response_model=CollectSearchResponse, tags=["Collect Mode"])
async def collect_search(request: CollectSearchRequest):
    """쇼핑몰에서 상품 검색

    Note: 데모 모드를 사용하면 실제 크롤링 없이 테스트용 데이터를 반환합니다.
    실제 크롤링은 headless=False 모드로 실행되며, IP 차단 시 0개 결과가 반환될 수 있습니다.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # 데모 모드 처리
    if request.demo_mode:
        demo_products = _generate_demo_products(
            request.keyword,
            request.sources,
            request.max_results
        )
        return CollectSearchResponse(
            keyword=request.keyword,
            total_count=len(demo_products),
            products=demo_products,
        )

    def search_sync():
        all_products = []
        errors = {}  # 소스별 에러 수집

        for source in request.sources:
            source_name = source.value if hasattr(source, 'value') else str(source)
            try:
                if source == ShoppingSource.COUPANG:
                    from src.crawler import CoupangCrawler, SHOPPING_CRAWLERS_AVAILABLE
                    if not SHOPPING_CRAWLERS_AVAILABLE:
                        errors[source_name] = "Selenium이 설치되어 있지 않습니다."
                        continue
                    # headless=False로 변경 (봇 감지 우회)
                    crawler = CoupangCrawler(headless=False, delay_range=(2.0, 4.0))
                    products = crawler.search_products(request.keyword, request.max_results)
                    crawler.close()

                elif source == ShoppingSource.NAVER:
                    from src.crawler import NaverShoppingCrawler, SHOPPING_CRAWLERS_AVAILABLE
                    if not SHOPPING_CRAWLERS_AVAILABLE:
                        errors[source_name] = "Selenium이 설치되어 있지 않습니다."
                        continue
                    # headless=False로 변경 (봇 감지 우회)
                    crawler = NaverShoppingCrawler(headless=False, delay_range=(2.0, 4.0))
                    products = crawler.search_products(request.keyword, request.max_results)
                    crawler.close()

                else:
                    continue

                for p in products:
                    all_products.append(ProductResult(
                        product_id=p.product_id,
                        title=p.title,
                        price=p.price,
                        image_url=p.image_url,
                        detail_url=p.detail_url,
                        source=p.source,
                        rating=p.rating,
                        review_count=p.review_count,
                    ))

            except Exception as e:
                error_msg = str(e)
                # 보안 페이지 관련 에러인지 확인
                if "보안" in error_msg or "차단" in error_msg or "blocked" in error_msg.lower():
                    errors[source_name] = f"보안 페이지 감지: IP가 일시적으로 차단되었습니다. VPN 또는 나중에 다시 시도해주세요."
                else:
                    errors[source_name] = error_msg
                logger.exception("Collect search failed for source %s: %s", source, e)
                continue

        return all_products, errors

    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            products, errors = await loop.run_in_executor(executor, search_sync)

        return CollectSearchResponse(
            keyword=request.keyword,
            total_count=len(products),
            products=products,
            errors=errors,
        )
    except Exception as e:
        raise _internal_server_error(e)


@app.post("/api/v1/collect/download", response_model=CollectDownloadResponse, tags=["Collect Mode"])
async def collect_download(request: CollectDownloadRequest):
    """선택된 상품 이미지 다운로드"""
    try:
        downloader = get_image_downloader()
        downloaded = []
        failed = 0

        for product in request.products:
            if not product.image_url:
                failed += 1
                continue

            result = downloader.download_image(
                url=product.image_url,
                product_id=product.product_id,
                product_title=product.title,
                source=product.source,
                metadata={
                    "price": product.price,
                    "detail_url": product.detail_url,
                    "rating": product.rating,
                    "review_count": product.review_count,
                }
            )

            if result:
                downloaded.append({
                    "id": result.id,
                    "product_id": result.product_id,
                    "product_title": result.product_title,
                    "local_path": result.local_path,
                    "source": result.source,
                })
            else:
                failed += 1

        return CollectDownloadResponse(
            success=True,
            downloaded_count=len(downloaded),
            failed_count=failed,
            images=downloaded,
        )
    except Exception as e:
        raise _internal_server_error(e)


@app.get("/api/v1/collect/images", response_model=CollectImageListResponse, tags=["Collect Mode"])
async def list_collected_images(
    source: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    """수집된 이미지 목록 조회"""
    try:
        downloader = get_image_downloader()
        images, total = downloader.list_images(source=source, page=page, page_size=page_size)

        result_images = []
        for img in images:
            result_images.append(CollectedImage(
                id=img.id,
                product_id=img.product_id,
                product_title=img.product_title,
                local_path=img.local_path,
                thumbnail_url=f"/api/v1/collect/images/{img.id}",
                original_url=img.original_url,
                source=img.source,
                downloaded_at=img.downloaded_at,
                size_kb=round(img.size_bytes / 1024, 2),
                selected=False,
            ))

        return CollectImageListResponse(
            total_count=total,
            images=result_images,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise _internal_server_error(e)


@app.get("/api/v1/collect/images/{image_id}", tags=["Collect Mode"])
async def get_collected_image(image_id: str):
    """이미지 파일 서빙"""
    from fastapi.responses import FileResponse

    try:
        downloader = get_image_downloader()
        file_path = downloader.get_image_path(image_id)

        if file_path and file_path.exists():
            return FileResponse(
                path=str(file_path),
                media_type="image/jpeg",
                filename=file_path.name,
            )
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException:
        raise
    except Exception as e:
        raise _internal_server_error(e)


@app.delete("/api/v1/collect/images", response_model=CollectDeleteResponse, tags=["Collect Mode"])
async def delete_collected_images(request: CollectDeleteRequest):
    """선택된 이미지 삭제"""
    try:
        downloader = get_image_downloader()
        deleted_count = downloader.delete_images(request.image_ids)

        return CollectDeleteResponse(
            deleted_count=deleted_count,
            success=True,
        )
    except Exception as e:
        raise _internal_server_error(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
