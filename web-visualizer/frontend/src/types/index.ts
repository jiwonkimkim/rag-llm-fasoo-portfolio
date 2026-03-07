import { LucideIcon } from 'lucide-react';

// Pipeline Step Result
export interface StepResult {
  input: any;
  output: any;
  timestamp: Date;
}

// Pipeline State
export interface PipelineState {
  preprocess: StepResult | null;
  chunk: StepResult | null;
  embed: StepResult | null;
  store: StepResult | null;
  retrieve: StepResult | null;
  generate: StepResult | null;
}

// Step Definition
export interface StepDefinition {
  id: string;
  name: string;
  icon: LucideIcon;
  description: string;
}

// Collection Info
export interface CollectionInfo {
  name: string;
  count: number;
  store_type: string;
  embedder_type?: string;
  model_name?: string;
  display_name?: string;  // Human-readable collection name for display
  description?: string;
  prep_store_type?: string;
  created_at?: string;
  chunking_algorithm?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  extra_body_length?: number;
  min_chunk_group_size?: number;
  total_chunks?: number;
  total_documents?: number;
  success_documents?: number;
  failed_documents?: number;
}

// Model Status
export interface ModelStatus {
  installed: boolean;
  checking: boolean;
  installing: boolean;
  sizeMb?: number;
}

// Model Option
export interface ModelOption {
  value: string;
  label: string;
  dim: number;
  desc: string;
}

// Embedding Mode Option
export interface EmbeddingModeOption {
  value: string;
  label: string;
  desc: string;
}

// Ingest Progress
export interface IngestProgress {
  step: 'idle' | 'preprocess' | 'chunk' | 'embed' | 'store' | 'done' | 'error';
  message: string;
  details?: any;
}

// Ingest Result
export interface IngestResult {
  success: boolean;
  chunks: number;
  embeddings: number;
  stored: number;
  collectionName: string;  // Display name
  collectionId?: string;   // Actual ID (rag_collection_YYYYMMDD_HHMMSS format)
  description?: string;
}

// Query Mode Result
export interface QueryModeResult {
  query: string;
  answer: string;
  sources: any[];
  llm_model: string;
  collection_name: string;
}

// App Mode
export type AppMode = 'pipeline' | 'ingest' | 'query' | 'manage' | 'collect';

// Step Status
export type StepStatus = 'completed' | 'current' | 'pending';

// Collect Mode Types
export interface ProductResult {
  product_id: string;
  title: string;
  price: string;
  image_url: string;
  detail_url: string;
  source: 'coupang' | 'naver';
  rating?: string;
  review_count?: string;
}

export interface CollectedImage {
  id: string;
  product_id: string;
  product_title: string;
  local_path: string;
  thumbnail_url: string;
  original_url: string;
  source: string;
  downloaded_at: string;
  size_kb: number;
  selected: boolean;
}

export interface CollectProgress {
  step: 'idle' | 'searching' | 'downloading' | 'done' | 'error';
  message: string;
  current?: number;
  total?: number;
}
