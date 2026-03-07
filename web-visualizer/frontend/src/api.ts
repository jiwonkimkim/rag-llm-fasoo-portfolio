import axios from 'axios';

const API_BASE = '/api';

// Batch size for store operations (number of vectors per batch)
const STORE_BATCH_SIZE = 50;

// Batch size for chunk operations (characters per batch)
const CHUNK_BATCH_SIZE = 50000; // 50K characters per batch

export interface ChunkBatchProgress {
  currentBatch: number;
  totalBatches: number;
  processedChars: number;
  totalChars: number;
  chunksGenerated: number;
}

export interface StoreData {
  texts: string[];
  embeddings: number[][];
  metadatas?: Record<string, any>[];
  storeType: string;
  collectionName: string;
  embedderType?: string;
  modelName?: string;
  displayName?: string;
  description?: string;
  prepStoreType?: string;
  chunkingAlgorithm?: string;
  chunkSize?: number;
  chunkOverlap?: number;
  extraBodyLength?: number;
  minChunkGroupSize?: number;
  totalDocuments?: number;
  successDocuments?: number;
  failedDocuments?: number;
}

export interface BatchProgress {
  currentBatch: number;
  totalBatches: number;
  storedVectors: number;
  totalVectors: number;
}

export const api = {
  healthCheck: () => axios.get(`${API_BASE}/health`),

  preprocess: (data: {
    text: string;
    useCleaner: boolean;
    useNormalizer: boolean;
  }) => axios.post(`${API_BASE}/preprocess`, data),

  chunk: (data: {
    text: string;
    chunkerType: string;
    chunkSize: number;
    chunkOverlap: number;
  }) => axios.post(`${API_BASE}/chunk`, data),

  embed: (data: {
    texts: string[];
    embedderType: string;
    modelName?: string;
    apiKey?: string;
    embeddingMode?: string;
  }) => axios.post(`${API_BASE}/embed`, data),

  // Vector Store APIs
  store: (data: {
    texts: string[];
    embeddings: number[][];
    metadatas?: Record<string, any>[];
    storeType: string;
    collectionName: string;
    embedderType?: string;
    modelName?: string;
    // Collection metadata
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
  }) => axios.post(`${API_BASE}/store`, data),

  getStoreList: (params: {
    collectionName: string;
    storeType: string;
    page: number;
    pageSize: number;
  }) => axios.get(`${API_BASE}/store`, { params }),

  getStoreStats: (params: {
    collectionName: string;
    storeType: string;
  }) => axios.get(`${API_BASE}/store/stats`, { params }),

  clearStore: (params: {
    collectionName: string;
    storeType: string;
  }) => axios.delete(`${API_BASE}/store`, { params }),

  retrieve: (data: {
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
  }) => axios.post(`${API_BASE}/retrieve`, data),

  generate: (data: {
    query: string;
    context: string[];
    model: string;
    temperature: number;
    apiKey?: string;
  }) => axios.post(`${API_BASE}/generate`, data),

  runFullPipeline: (data: {
    query: string;
    retrieverType: string;
    topK: number;
    model: string;
    temperature: number;
  }) => axios.post(`${API_BASE}/pipeline/full`, data),

  // Model Management APIs
  checkModelStatus: (data: {
    modelName: string;
    embedderType: string;
  }) => axios.post(`${API_BASE}/model/status`, data),

  installModel: (data: {
    modelName: string;
    embedderType: string;
  }) => axios.post(`${API_BASE}/model/install`, data, {
    timeout: 600000, // 10 minutes timeout for model download
  }),

  // Query Mode APIs
  getCollections: (params: {
    storeType: string;
  }) => axios.get(`${API_BASE}/store/collections`, { params }),

  quickQuery: (data: {
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
  }) => axios.post(`${API_BASE}/query`, data, {
    timeout: 120000, // 2 minutes timeout
  }),

  // Batch chunk with progress callback (for large documents)
  batchChunk: async (
    data: {
      text: string;
      chunkerType: string;
      chunkSize: number;
      chunkOverlap: number;
    },
    onProgress?: (progress: ChunkBatchProgress) => void
  ): Promise<{
    original_length: number;
    chunks: string[];
    chunk_count: number;
    avg_chunk_size: number;
    settings: any;
  }> => {
    const { text, ...config } = data;

    // Handle empty or undefined text
    if (!text || text.length === 0) {
      console.warn('[batchChunk] Empty text provided');
      return {
        original_length: 0,
        chunks: [],
        chunk_count: 0,
        avg_chunk_size: 0,
        settings: {
          chunker_type: config.chunkerType,
          chunk_size: config.chunkSize,
          chunk_overlap: config.chunkOverlap,
        },
      };
    }

    const totalChars = text.length;
    console.log('[batchChunk] Starting with', totalChars, 'chars, chunkerType:', config.chunkerType);

    // If text is small enough, process in one call
    if (totalChars <= CHUNK_BATCH_SIZE) {
      console.log('[batchChunk] Small text, single request');
      const response = await axios.post(`${API_BASE}/chunk`, data, {
        timeout: 300000, // 5 minutes timeout
      });
      console.log('[batchChunk] Response received:', response.data?.chunk_count, 'chunks');
      return response.data;
    }

    // Split text into batches with overlap for context
    const overlapChars = config.chunkSize; // Use chunk_size as overlap between batches
    const totalBatches = Math.ceil(totalChars / (CHUNK_BATCH_SIZE - overlapChars));
    const allChunks: string[] = [];
    let processedChars = 0;

    for (let i = 0; i < totalBatches; i++) {
      const start = i === 0 ? 0 : i * (CHUNK_BATCH_SIZE - overlapChars);
      const end = Math.min(start + CHUNK_BATCH_SIZE, totalChars);
      const batchText = text.slice(start, end);

      console.log(`[batchChunk] Processing batch ${i + 1}/${totalBatches}`);
      const response = await axios.post(`${API_BASE}/chunk`, {
        text: batchText,
        chunkerType: config.chunkerType,
        chunkSize: config.chunkSize,
        chunkOverlap: config.chunkOverlap,
      }, {
        timeout: 300000, // 5 minutes timeout per batch
      });

      // For first batch, take all chunks. For subsequent batches, skip first chunk (overlap)
      const batchChunks = response.data.chunks as string[];
      if (i === 0) {
        allChunks.push(...batchChunks);
      } else {
        // Skip first chunk to avoid duplicates from overlap
        allChunks.push(...batchChunks.slice(1));
      }

      processedChars = end;

      if (onProgress) {
        onProgress({
          currentBatch: i + 1,
          totalBatches,
          processedChars,
          totalChars,
          chunksGenerated: allChunks.length,
        });
      }
    }

    return {
      original_length: totalChars,
      chunks: allChunks,
      chunk_count: allChunks.length,
      avg_chunk_size: allChunks.length > 0
        ? allChunks.reduce((sum, c) => sum + c.length, 0) / allChunks.length
        : 0,
      settings: {
        chunker_type: config.chunkerType,
        chunk_size: config.chunkSize,
        chunk_overlap: config.chunkOverlap,
      },
    };
  },

  // Batch store with progress callback
  batchStore: async (
    data: StoreData,
    onProgress?: (progress: BatchProgress) => void
  ): Promise<{ success: boolean; totalStored: number; batches: number }> => {
    const { texts, embeddings, metadatas, ...config } = data;
    const totalVectors = texts.length;
    const totalBatches = Math.ceil(totalVectors / STORE_BATCH_SIZE);
    let storedVectors = 0;

    for (let i = 0; i < totalBatches; i++) {
      const start = i * STORE_BATCH_SIZE;
      const end = Math.min(start + STORE_BATCH_SIZE, totalVectors);

      const batchTexts = texts.slice(start, end);
      const batchEmbeddings = embeddings.slice(start, end);
      const batchMetadatas = metadatas?.slice(start, end);

      // Only send collection metadata with the first batch
      const batchData = i === 0
        ? {
            texts: batchTexts,
            embeddings: batchEmbeddings,
            metadatas: batchMetadatas,
            storeType: config.storeType,
            collectionName: config.collectionName,
            embedderType: config.embedderType,
            modelName: config.modelName,
            displayName: config.displayName,
            description: config.description,
            prepStoreType: config.prepStoreType,
            chunkingAlgorithm: config.chunkingAlgorithm,
            chunkSize: config.chunkSize,
            chunkOverlap: config.chunkOverlap,
            extraBodyLength: config.extraBodyLength,
            minChunkGroupSize: config.minChunkGroupSize,
            totalDocuments: config.totalDocuments,
            successDocuments: config.successDocuments,
            failedDocuments: config.failedDocuments,
          }
        : {
            texts: batchTexts,
            embeddings: batchEmbeddings,
            metadatas: batchMetadatas,
            storeType: config.storeType,
            collectionName: config.collectionName,
            embedderType: config.embedderType,
            modelName: config.modelName,
          };

      await axios.post(`${API_BASE}/store`, batchData);
      storedVectors += batchTexts.length;

      if (onProgress) {
        onProgress({
          currentBatch: i + 1,
          totalBatches,
          storedVectors,
          totalVectors,
        });
      }
    }

    return { success: true, totalStored: storedVectors, batches: totalBatches };
  },

  // Collect Mode APIs
  collectSearch: (data: {
    keyword: string;
    sources?: string[];
    maxResults?: number;
    demo_mode?: boolean;
  }) =>
    axios.post(`${API_BASE}/collect/search`, data, {
      timeout: 120000, // 2분 타임아웃
    }),

  collectDownload: (data: {
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
  }) =>
    axios.post(`${API_BASE}/collect/download`, data, {
      timeout: 300000, // 5분 타임아웃
    }),

  listCollectedImages: (params: {
    source?: string;
    page?: number;
    pageSize?: number;
  }) =>
    axios.get(`${API_BASE}/collect/images`, { params }),

  deleteCollectedImages: (data: { imageIds: string[] }) =>
    axios.delete(`${API_BASE}/collect/images`, { data }),

  getCollectedImageUrl: (imageId: string) =>
    `http://localhost:8000/api/v1/collect/images/${imageId}`,
};
