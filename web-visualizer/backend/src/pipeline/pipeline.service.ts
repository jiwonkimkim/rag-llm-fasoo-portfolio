import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

@Injectable()
export class PipelineService {
  constructor(private readonly httpService: HttpService) {
    const apiAuthKey = process.env.API_AUTH_KEY;
    if (apiAuthKey) {
      this.httpService.axiosRef.defaults.headers.common['x-api-key'] = apiAuthKey;
    }
  }

  async healthCheck() {
    try {
      const response = await firstValueFrom(
        this.httpService.get(`${FASTAPI_URL}/health`)
      );
      return response.data;
    } catch (error) {
      return { status: 'error', message: 'FastAPI not available' };
    }
  }

  async preprocess(data: {
    text: string;
    useCleaner: boolean;
    useNormalizer: boolean;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/preprocess`, {
        text: data.text,
        use_cleaner: data.useCleaner,
        use_normalizer: data.useNormalizer,
      })
    );
    return response.data;
  }

  async chunk(data: {
    text: string;
    chunkerType: string;
    chunkSize: number;
    chunkOverlap: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/chunk`, {
        text: data.text,
        chunker_type: data.chunkerType,
        chunk_size: data.chunkSize,
        chunk_overlap: data.chunkOverlap,
      }, {
        timeout: 300000, // 5 minutes timeout for large documents
      })
    );
    return response.data;
  }

  async embed(data: {
    texts: string[];
    embedderType: string;
    modelName?: string;
    apiKey?: string;
    embeddingMode?: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/embed`, {
        texts: data.texts,
        embedder_type: data.embedderType,
        model_name: data.modelName,
        api_key: data.apiKey,
        embedding_mode: data.embeddingMode,
      })
    );
    return response.data;
  }

  async retrieve(data: {
    query: string;
    retrieverType: string;
    topK: number;
    denseWeight?: number;
    sparseWeight?: number;
    collectionName?: string;
    storeType?: string;
    embedderType?: string;
    modelName?: string;
    apiKey?: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/retrieve`, {
        query: data.query,
        retriever_type: data.retrieverType,
        top_k: data.topK,
        dense_weight: data.denseWeight || 0.5,
        sparse_weight: data.sparseWeight || 0.5,
        collection_name: data.collectionName || 'rag_collection',
        store_type: data.storeType || 'chroma',
        embedder_type: data.embedderType || 'huggingface',
        model_name: data.modelName || 'intfloat/multilingual-e5-base',
        api_key: data.apiKey,
      })
    );
    return response.data;
  }

  async generate(data: {
    query: string;
    context: string[];
    model: string;
    temperature: number;
    apiKey?: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/generate`, {
        query: data.query,
        context: data.context,
        model: data.model,
        temperature: data.temperature,
        api_key: data.apiKey,
      })
    );
    return response.data;
  }

  async runFullPipeline(data: {
    query: string;
    retrieverType: string;
    topK: number;
    model: string;
    temperature: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/pipeline/full`, {
        query: data.query,
        retriever_type: data.retrieverType,
        top_k: data.topK,
        model: data.model,
        temperature: data.temperature,
      })
    );
    return response.data;
  }

  // Vector Store methods
  async store(data: {
    texts: string[];
    embeddings: number[][];
    metadatas?: Record<string, any>[];
    storeType: string;
    collectionName: string;
    embedderType?: string;
    modelName?: string;
    // Collection metadata
    displayName?: string;
    description?: string;
    prepStoreType?: string;
    // Chunking options
    chunkingAlgorithm?: string;
    chunkSize?: number;
    chunkOverlap?: number;
    extraBodyLength?: number;
    minChunkGroupSize?: number;
    // Document stats
    totalDocuments?: number;
    successDocuments?: number;
    failedDocuments?: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/store`, {
        texts: data.texts,
        embeddings: data.embeddings,
        metadatas: data.metadatas,
        store_type: data.storeType,
        collection_name: data.collectionName,
        embedder_type: data.embedderType,
        model_name: data.modelName,
        display_name: data.displayName,
        description: data.description,
        prep_store_type: data.prepStoreType,
        chunking_algorithm: data.chunkingAlgorithm,
        chunk_size: data.chunkSize,
        chunk_overlap: data.chunkOverlap,
        extra_body_length: data.extraBodyLength,
        min_chunk_group_size: data.minChunkGroupSize,
        total_documents: data.totalDocuments,
        success_documents: data.successDocuments,
        failed_documents: data.failedDocuments,
      })
    );
    return response.data;
  }

  async getStoreList(params: {
    collectionName: string;
    storeType: string;
    page: number;
    pageSize: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.get(`${FASTAPI_URL}/api/v1/store`, {
        params: {
          collection_name: params.collectionName,
          store_type: params.storeType,
          page: params.page,
          page_size: params.pageSize,
        },
      })
    );
    return response.data;
  }

  async getStoreStats(params: {
    collectionName: string;
    storeType: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.get(`${FASTAPI_URL}/api/v1/store/stats`, {
        params: {
          collection_name: params.collectionName,
          store_type: params.storeType,
        },
      })
    );
    return response.data;
  }

  async clearStore(params: {
    collectionName: string;
    storeType: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.delete(`${FASTAPI_URL}/api/v1/store`, {
        params: {
          collection_name: params.collectionName,
          store_type: params.storeType,
        },
      })
    );
    return response.data;
  }

  // Model Management methods
  async checkModelStatus(data: {
    modelName: string;
    embedderType: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/model/status`, {
        model_name: data.modelName,
        embedder_type: data.embedderType,
      })
    );
    return response.data;
  }

  async installModel(data: {
    modelName: string;
    embedderType: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/model/install`, {
        model_name: data.modelName,
        embedder_type: data.embedderType,
      }, {
        timeout: 600000, // 10 minutes timeout for model download
      })
    );
    return response.data;
  }

  // Query Mode methods
  async getCollections(params: { storeType: string }) {
    const response = await firstValueFrom(
      this.httpService.get(`${FASTAPI_URL}/api/v1/store/collections`, {
        params: {
          store_type: params.storeType,
        },
      })
    );
    return response.data;
  }

  async quickQuery(data: {
    query: string;
    collectionName: string;
    storeType?: string;
    embedderType?: string;
    modelName?: string;
    retrieverType?: string;
    topK?: number;
    llmModel?: string;
    temperature?: number;
    apiKey?: string;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/query`, {
        query: data.query,
        collection_name: data.collectionName,
        store_type: data.storeType || 'chroma',
        embedder_type: data.embedderType || 'huggingface',
        model_name: data.modelName || 'intfloat/multilingual-e5-base',
        retriever_type: data.retrieverType || 'dense',
        top_k: data.topK || 5,
        llm_model: data.llmModel || 'llama-3.3-70b-versatile',
        temperature: data.temperature || 0.7,
        api_key: data.apiKey,
      }, {
        timeout: 120000, // 2 minutes timeout for query
      })
    );
    return response.data;
  }

  // Collect Mode methods
  async collectSearch(data: {
    keyword: string;
    sources?: string[];
    maxResults?: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/collect/search`, {
        keyword: data.keyword,
        sources: data.sources || ['coupang', 'naver'],
        max_results: data.maxResults || 20,
      }, {
        timeout: 120000, // 2 minutes timeout for crawling
      })
    );
    return response.data;
  }

  async collectDownload(data: {
    products: Array<{
      product_id: string;
      title: string;
      price: string;
      image_url: string;
      detail_url: string;
      source: string;
      rating?: string;
      review_count?: string;
    }>;
  }) {
    const response = await firstValueFrom(
      this.httpService.post(`${FASTAPI_URL}/api/v1/collect/download`, {
        products: data.products,
      }, {
        timeout: 300000, // 5 minutes timeout for downloading
      })
    );
    return response.data;
  }

  async listCollectedImages(params: {
    source?: string;
    page: number;
    pageSize: number;
  }) {
    const response = await firstValueFrom(
      this.httpService.get(`${FASTAPI_URL}/api/v1/collect/images`, {
        params: {
          source: params.source,
          page: params.page,
          page_size: params.pageSize,
        },
      })
    );
    return response.data;
  }

  async deleteCollectedImages(data: {
    imageIds: string[];
  }) {
    const response = await firstValueFrom(
      this.httpService.delete(`${FASTAPI_URL}/api/v1/collect/images`, {
        data: {
          image_ids: data.imageIds,
        },
      })
    );
    return response.data;
  }
}
