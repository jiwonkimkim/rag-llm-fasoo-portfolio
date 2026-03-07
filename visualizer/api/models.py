"""Pydantic models for API request/response."""

from pydantic import BaseModel, Field
from typing import Any
from enum import Enum


# Enums for component selection
class CleanerOption(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class NormalizerOption(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class ChunkerType(str, Enum):
    FIXED = "fixed"
    SEMANTIC = "semantic"


class EmbedderType(str, Enum):
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    BGE_M3 = "bge-m3"


class EmbeddingMode(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    DENSE_SPARSE = "dense+sparse"
    ALL = "all"  # dense + sparse + colbert


class RetrieverType(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


class VectorStoreType(str, Enum):
    CHROMA = "chroma"
    FAISS = "faiss"
    PINECONE = "pinecone"


# Request Models
class PreprocessRequest(BaseModel):
    text: str = Field(..., description="Input text to preprocess")
    use_cleaner: bool = Field(default=True, description="Whether to use cleaner")
    use_normalizer: bool = Field(default=True, description="Whether to use normalizer")
    cleaner_options: dict[str, Any] = Field(default_factory=dict, description="Cleaner options")
    normalizer_options: dict[str, Any] = Field(default_factory=dict, description="Normalizer options")


class ChunkRequest(BaseModel):
    text: str = Field(..., description="Text to chunk")
    chunker_type: ChunkerType = Field(default=ChunkerType.FIXED, description="Chunker type")
    chunk_size: int = Field(default=512, description="Chunk size")
    chunk_overlap: int = Field(default=50, description="Chunk overlap")


class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., description="Texts to embed")
    embedder_type: EmbedderType = Field(default=EmbedderType.OPENAI, description="Embedder type")
    model_name: str | None = Field(default=None, description="Model name override")
    api_key: str | None = Field(default=None, description="API key for OpenAI embedder")
    embedding_mode: EmbeddingMode = Field(default=EmbeddingMode.DENSE, description="Embedding mode for BGE-M3")


class RetrieveRequest(BaseModel):
    query: str = Field(..., description="Query text")
    retriever_type: RetrieverType = Field(default=RetrieverType.DENSE, description="Retriever type")
    top_k: int = Field(default=5, description="Number of results")
    dense_weight: float = Field(default=0.5, description="Dense weight for hybrid")
    sparse_weight: float = Field(default=0.5, description="Sparse weight for hybrid")
    # Vector store settings for actual retrieval
    collection_name: str = Field(default="rag_collection", description="Collection name")
    store_type: VectorStoreType = Field(default=VectorStoreType.CHROMA, description="Vector store type")
    embedder_type: EmbedderType = Field(default=EmbedderType.HUGGINGFACE, description="Embedder for query")
    model_name: str | None = Field(default="intfloat/multilingual-e5-base", description="Embedding model name")
    api_key: str | None = Field(default=None, description="API key for OpenAI embedder")


class GenerateRequest(BaseModel):
    query: str = Field(..., description="User query")
    context: list[str] = Field(..., description="Retrieved context documents")
    model: str = Field(default="gpt-3.5-turbo", description="LLM model")
    temperature: float = Field(default=0.7, description="Temperature")
    api_key: str | None = Field(default=None, description="OpenAI API key")


class PipelineRequest(BaseModel):
    """Full pipeline request for n8n integration."""
    query: str = Field(..., description="User query")

    # Preprocessor settings
    use_cleaner: bool = Field(default=True)
    use_normalizer: bool = Field(default=True)

    # Chunker settings (for ingestion)
    chunker_type: ChunkerType = Field(default=ChunkerType.FIXED)
    chunk_size: int = Field(default=512)

    # Retriever settings
    retriever_type: RetrieverType = Field(default=RetrieverType.DENSE)
    top_k: int = Field(default=5)

    # Generator settings
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)


# Response Models
class PreprocessResponse(BaseModel):
    original: str
    cleaned: str | None = None
    normalized: str | None = None
    final: str
    steps: list[dict[str, Any]]


class ChunkResponse(BaseModel):
    original_length: int
    chunks: list[str]
    chunk_count: int
    avg_chunk_size: float
    settings: dict[str, Any]


class EmbedResponse(BaseModel):
    texts: list[str]
    embeddings: list[list[float]]
    dimension: int
    embedder_type: str
    model_name: str


class RetrievalResultModel(BaseModel):
    content: str
    metadata: dict[str, Any]
    score: float
    source: str


class RetrieveResponse(BaseModel):
    query: str
    results: list[RetrievalResultModel]
    retriever_type: str
    settings: dict[str, Any]


class GenerateResponse(BaseModel):
    query: str
    context_used: list[str]
    response: str
    model: str
    usage: dict[str, Any] | None = None


class PipelineResponse(BaseModel):
    """Full pipeline response for n8n integration."""
    query: str
    steps: list[dict[str, Any]]
    final_response: str
    metadata: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    modules: dict[str, bool]


# Vector Store Models
class StoreRequest(BaseModel):
    """Request to store embeddings in vector database."""
    model_config = {"populate_by_name": True}

    texts: list[str] = Field(..., description="Original texts")
    embeddings: list[list[float]] = Field(..., description="Embedding vectors")
    metadatas: list[dict[str, Any]] | None = Field(default=None, description="Metadata for each text")
    store_type: VectorStoreType = Field(default=VectorStoreType.CHROMA, alias="storeType", description="Vector store type")
    collection_name: str = Field(default="rag_collection", alias="collectionName", description="Collection name")
    embedder_type: EmbedderType | None = Field(default=None, alias="embedderType", description="Embedder type used for embeddings")
    model_name: str | None = Field(default=None, alias="modelName", description="Model name used for embeddings")
    # Collection metadata for management
    display_name: str | None = Field(default=None, alias="displayName", description="Human-readable collection name for display")
    description: str | None = Field(default=None, description="Collection description")
    prep_store_type: str | None = Field(default="standard", alias="prepStoreType", description="Preprocessing store type (e.g., legacy, standard)")
    # Chunking options
    chunking_algorithm: str | None = Field(default=None, alias="chunkingAlgorithm", description="Chunking algorithm used")
    chunk_size: int | None = Field(default=None, alias="chunkSize", description="Chunk size")
    chunk_overlap: int | None = Field(default=None, alias="chunkOverlap", description="Chunk overlap")
    extra_body_length: int | None = Field(default=None, alias="extraBodyLength", description="Extra body length")
    min_chunk_group_size: int | None = Field(default=None, alias="minChunkGroupSize", description="Minimum chunk group size")
    # Document stats
    total_documents: int | None = Field(default=None, alias="totalDocuments", description="Total number of documents")
    success_documents: int | None = Field(default=None, alias="successDocuments", description="Successfully processed documents")
    failed_documents: int | None = Field(default=None, alias="failedDocuments", description="Failed documents")


class StoreResponse(BaseModel):
    """Response after storing embeddings."""
    success: bool
    stored_count: int
    collection_name: str
    store_type: str
    total_count: int


class StoredVectorInfo(BaseModel):
    """Information about a stored vector."""
    id: str
    content: str
    metadata: dict[str, Any]


class StoreListResponse(BaseModel):
    """Response for listing stored vectors."""
    collection_name: str
    store_type: str
    total_count: int
    vectors: list[StoredVectorInfo]
    page: int
    page_size: int


class StoreStatsResponse(BaseModel):
    """Response for vector store statistics."""
    collection_name: str
    store_type: str
    total_count: int
    dimension: int | None = None


# Model Management Models
class ModelStatusRequest(BaseModel):
    """Request for checking model status."""
    model_name: str = Field(..., description="Model name to check")
    embedder_type: EmbedderType = Field(..., description="Embedder type")


class ModelStatusResponse(BaseModel):
    """Response for model status check."""
    model_name: str
    embedder_type: str
    installed: bool
    cache_path: str | None = None
    size_mb: float | None = None


class ModelInstallRequest(BaseModel):
    """Request for installing a model."""
    model_name: str = Field(..., description="Model name to install")
    embedder_type: EmbedderType = Field(..., description="Embedder type")


class ModelInstallResponse(BaseModel):
    """Response for model installation."""
    model_name: str
    embedder_type: str
    success: bool
    message: str
    cache_path: str | None = None


# Quick Query Models (for Query Mode)
class QuickQueryRequest(BaseModel):
    """Request for quick query (retrieve + generate in one call)."""
    query: str = Field(..., description="User query")
    collection_name: str = Field(..., description="Collection to search")
    store_type: VectorStoreType = Field(default=VectorStoreType.CHROMA, description="Vector store type")
    embedder_type: EmbedderType = Field(default=EmbedderType.HUGGINGFACE, description="Embedder for query")
    model_name: str | None = Field(default="intfloat/multilingual-e5-base", description="Embedding model name")
    retriever_type: RetrieverType = Field(default=RetrieverType.DENSE, description="Retriever type")
    top_k: int = Field(default=5, description="Number of documents to retrieve")
    llm_model: str = Field(default="llama-3.3-70b-versatile", description="LLM model for generation")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    api_key: str | None = Field(default=None, description="API key (for OpenAI models)")


class QuickQueryResponse(BaseModel):
    """Response for quick query."""
    query: str
    answer: str
    sources: list[dict[str, Any]]
    retriever_type: str
    llm_model: str
    collection_name: str


# =====================================================
# Collect Mode Models (쇼핑몰 상품 수집)
# =====================================================

class ShoppingSource(str, Enum):
    """쇼핑몰 소스 타입"""
    COUPANG = "coupang"
    NAVER = "naver"


class CollectSearchRequest(BaseModel):
    """상품 검색 요청"""
    keyword: str = Field(..., description="검색 키워드")
    sources: list[ShoppingSource] = Field(
        default=[ShoppingSource.COUPANG, ShoppingSource.NAVER],
        description="검색할 쇼핑몰 목록"
    )
    max_results: int = Field(default=20, ge=1, le=100, description="쇼핑몰당 최대 결과 수")
    demo_mode: bool = Field(default=False, description="데모 모드 (테스트용 mock 데이터 반환)")


class ProductResult(BaseModel):
    """상품 검색 결과"""
    product_id: str
    title: str
    price: str
    image_url: str
    detail_url: str
    source: str
    rating: str = ""
    review_count: str = ""


class CollectSearchResponse(BaseModel):
    """검색 응답"""
    keyword: str
    total_count: int
    products: list[ProductResult]
    errors: dict[str, str] = Field(default_factory=dict, description="소스별 에러 메시지 (예: {'naver': '보안 페이지 감지'})")


class CollectDownloadRequest(BaseModel):
    """이미지 다운로드 요청"""
    products: list[ProductResult]


class DownloadProgress(BaseModel):
    """다운로드 진행 상황"""
    total: int
    completed: int
    failed: int
    current_product: str = ""


class CollectDownloadResponse(BaseModel):
    """다운로드 응답"""
    success: bool
    downloaded_count: int
    failed_count: int
    images: list[dict[str, Any]]


class CollectedImage(BaseModel):
    """수집된 이미지 정보"""
    id: str
    product_id: str
    product_title: str
    local_path: str
    thumbnail_url: str  # 프론트엔드 표시용
    original_url: str
    source: str
    downloaded_at: str
    size_kb: float
    selected: bool = False


class CollectImageListResponse(BaseModel):
    """이미지 목록 응답"""
    total_count: int
    images: list[CollectedImage]
    page: int
    page_size: int


class CollectDeleteRequest(BaseModel):
    """이미지 삭제 요청"""
    image_ids: list[str]


class CollectDeleteResponse(BaseModel):
    """삭제 응답"""
    deleted_count: int
    success: bool
