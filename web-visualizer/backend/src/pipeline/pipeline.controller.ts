import { Controller, Get, Post, Delete, Body, Query } from '@nestjs/common';
import { PipelineService } from './pipeline.service';

// DTOs
class PreprocessDto {
  text: string;
  useCleaner: boolean;
  useNormalizer: boolean;
}

class ChunkDto {
  text: string;
  chunkerType: string;
  chunkSize: number;
  chunkOverlap: number;
}

class EmbedDto {
  texts: string[];
  embedderType: string;
  modelName?: string;
  apiKey?: string;
  embeddingMode?: string;
}

class RetrieveDto {
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
}

class GenerateDto {
  query: string;
  context: string[];
  model: string;
  temperature: number;
  apiKey?: string;
}

class FullPipelineDto {
  query: string;
  retrieverType: string;
  topK: number;
  model: string;
  temperature: number;
}

class StoreDto {
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
}

class ModelStatusDto {
  modelName: string;
  embedderType: string;
}

class ModelInstallDto {
  modelName: string;
  embedderType: string;
}

class QuickQueryDto {
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
}

// Collect Mode DTOs
class CollectSearchDto {
  keyword: string;
  sources?: string[];
  maxResults?: number;
}

class ProductResultDto {
  product_id: string;
  title: string;
  price: string;
  image_url: string;
  detail_url: string;
  source: string;
  rating?: string;
  review_count?: string;
}

class CollectDownloadDto {
  products: ProductResultDto[];
}

class CollectDeleteDto {
  imageIds: string[];
}

@Controller('api')
export class PipelineController {
  constructor(private readonly pipelineService: PipelineService) {}

  @Get('health')
  async healthCheck() {
    return this.pipelineService.healthCheck();
  }

  @Post('preprocess')
  async preprocess(@Body() dto: PreprocessDto) {
    return this.pipelineService.preprocess(dto);
  }

  @Post('chunk')
  async chunk(@Body() dto: ChunkDto) {
    return this.pipelineService.chunk(dto);
  }

  @Post('embed')
  async embed(@Body() dto: EmbedDto) {
    return this.pipelineService.embed(dto);
  }

  @Post('retrieve')
  async retrieve(@Body() dto: RetrieveDto) {
    return this.pipelineService.retrieve(dto);
  }

  @Post('generate')
  async generate(@Body() dto: GenerateDto) {
    return this.pipelineService.generate(dto);
  }

  @Post('pipeline/full')
  async runFullPipeline(@Body() dto: FullPipelineDto) {
    return this.pipelineService.runFullPipeline(dto);
  }

  // Vector Store endpoints
  @Post('store')
  async store(@Body() dto: StoreDto) {
    return this.pipelineService.store(dto);
  }

  @Get('store')
  async getStoreList(
    @Query('collectionName') collectionName: string = 'rag_collection',
    @Query('storeType') storeType: string = 'chroma',
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
  ) {
    return this.pipelineService.getStoreList({
      collectionName,
      storeType,
      page: Number(page),
      pageSize: Number(pageSize),
    });
  }

  @Get('store/stats')
  async getStoreStats(
    @Query('collectionName') collectionName: string = 'rag_collection',
    @Query('storeType') storeType: string = 'chroma',
  ) {
    return this.pipelineService.getStoreStats({
      collectionName,
      storeType,
    });
  }

  @Delete('store')
  async clearStore(
    @Query('collectionName') collectionName: string = 'rag_collection',
    @Query('storeType') storeType: string = 'chroma',
  ) {
    return this.pipelineService.clearStore({
      collectionName,
      storeType,
    });
  }

  // Model Management endpoints
  @Post('model/status')
  async checkModelStatus(@Body() dto: ModelStatusDto) {
    return this.pipelineService.checkModelStatus(dto);
  }

  @Post('model/install')
  async installModel(@Body() dto: ModelInstallDto) {
    return this.pipelineService.installModel(dto);
  }

  // Query Mode endpoints
  @Get('store/collections')
  async getCollections(@Query('storeType') storeType: string = 'chroma') {
    return this.pipelineService.getCollections({ storeType });
  }

  @Post('query')
  async quickQuery(@Body() dto: QuickQueryDto) {
    return this.pipelineService.quickQuery(dto);
  }

  // Collect Mode endpoints
  @Post('collect/search')
  async collectSearch(@Body() dto: CollectSearchDto) {
    return this.pipelineService.collectSearch(dto);
  }

  @Post('collect/download')
  async collectDownload(@Body() dto: CollectDownloadDto) {
    return this.pipelineService.collectDownload(dto);
  }

  @Get('collect/images')
  async listCollectedImages(
    @Query('source') source?: string,
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 50,
  ) {
    return this.pipelineService.listCollectedImages({
      source,
      page: Number(page),
      pageSize: Number(pageSize),
    });
  }

  @Delete('collect/images')
  async deleteCollectedImages(@Body() dto: CollectDeleteDto) {
    return this.pipelineService.deleteCollectedImages(dto);
  }
}
