import { Sparkles, Scissors, Binary, Database, Search, Bot } from 'lucide-react';
import { ModelOption, EmbeddingModeOption } from '../types';

// Pipeline Steps
export const STEPS = [
  { id: 'preprocess', name: 'Preprocess', icon: Sparkles, description: '텍스트 전처리' },
  { id: 'chunk', name: 'Chunk', icon: Scissors, description: '텍스트 분할' },
  { id: 'embed', name: 'Embed', icon: Binary, description: '임베딩 생성' },
  { id: 'store', name: 'Store', icon: Database, description: '벡터 저장' },
  { id: 'retrieve', name: 'Retrieve', icon: Search, description: '문서 검색' },
  { id: 'generate', name: 'Generate', icon: Bot, description: '응답 생성' },
] as const;

// Generate collection name with Korean timezone (KST) datetime
export const generateCollectionName = () => {
  const now = new Date();
  // Convert to Korean timezone (UTC+9)
  const kstOffset = 9 * 60; // KST is UTC+9
  const kstTime = new Date(now.getTime() + (kstOffset + now.getTimezoneOffset()) * 60000);

  const year = kstTime.getFullYear();
  const month = String(kstTime.getMonth() + 1).padStart(2, '0');
  const day = String(kstTime.getDate()).padStart(2, '0');
  const hours = String(kstTime.getHours()).padStart(2, '0');
  const minutes = String(kstTime.getMinutes()).padStart(2, '0');
  const seconds = String(kstTime.getSeconds()).padStart(2, '0');

  return `rag_collection_${year}${month}${day}_${hours}${minutes}${seconds}`;
};

// OpenAI Embedding Models
export const OPENAI_MODELS: ModelOption[] = [
  { value: 'text-embedding-3-small', label: 'text-embedding-3-small', dim: 1536, desc: '가성비 좋음, 빠름' },
  { value: 'text-embedding-3-large', label: 'text-embedding-3-large', dim: 3072, desc: '고품질, 비용 높음' },
  { value: 'text-embedding-ada-002', label: 'text-embedding-ada-002', dim: 1536, desc: '레거시, 안정적' },
];

// HuggingFace Embedding Models
export const HUGGINGFACE_MODELS: ModelOption[] = [
  { value: 'intfloat/multilingual-e5-base', label: 'multilingual-e5-base (추천)', dim: 768, desc: '다국어, 한국어 지원, 로컬 설치됨' },
];

// BGE-M3 Embedding Models
export const BGE_M3_MODELS: ModelOption[] = [
  { value: 'BAAI/bge-m3', label: 'bge-m3', dim: 1024, desc: '다국어, Dense+Sparse+ColBERT' },
];

// Embedding Modes for BGE-M3
export const EMBEDDING_MODES: EmbeddingModeOption[] = [
  { value: 'dense', label: 'Dense Only', desc: '의미 기반 벡터만 생성' },
  { value: 'dense+sparse', label: 'Dense + Sparse', desc: '의미 + 키워드 벡터 (Hybrid용)' },
  { value: 'all', label: 'All (Dense+Sparse+ColBERT)', desc: '모든 벡터 타입 생성' },
];

// Groq LLM Models (server-side API key configured)
// 2025 latest models - https://console.groq.com/docs/models
export const GROQ_MODELS = [
  // Production Models
  'llama-3.3-70b-versatile',
  'llama-3.1-8b-instant',
  'openai/gpt-oss-120b',
  'openai/gpt-oss-20b',
  // Preview Models
  'qwen/qwen3-32b',
  'meta-llama/llama-4-scout-17b-16e-instruct',
  // Legacy Models
  'gemma2-9b-it',
  'mixtral-8x7b-32768',
] as const;

// Default values
export const DEFAULT_VALUES = {
  chunkerType: 'semantic',
  chunkSize: 512,
  chunkOverlap: 50,
  embedderType: 'huggingface',
  embedModel: 'intfloat/multilingual-e5-base',
  embeddingMode: 'dense',
  storeType: 'chroma',
  retrieverType: 'dense',
  topK: 5,
  denseWeight: 0.5,
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
} as const;
