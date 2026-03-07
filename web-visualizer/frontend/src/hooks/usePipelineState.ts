import { useState } from 'react';
import { BatchProgress } from '../api';
import {
  PipelineState,
  ModelStatus,
  CollectionInfo,
  IngestProgress,
  IngestResult,
  QueryModeResult,
  AppMode,
} from '../types';
import { generateCollectionName, DEFAULT_VALUES } from '../constants';

export function usePipelineState() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [storeProgress, setStoreProgress] = useState<BatchProgress | null>(null);
  const [results, setResults] = useState<PipelineState>({
    preprocess: null, chunk: null, embed: null, store: null, retrieve: null, generate: null,
  });

  const [preprocessInput, setPreprocessInput] = useState('');
  const [useCleaner, setUseCleaner] = useState(true);
  const [useNormalizer, setUseNormalizer] = useState(true);

  const [chunkerType, setChunkerType] = useState(DEFAULT_VALUES.chunkerType);
  const [chunkSize, setChunkSize] = useState(DEFAULT_VALUES.chunkSize);
  const [chunkOverlap, setChunkOverlap] = useState(DEFAULT_VALUES.chunkOverlap);

  const [embedderType, setEmbedderType] = useState(DEFAULT_VALUES.embedderType);
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [embedModel, setEmbedModel] = useState(DEFAULT_VALUES.embedModel);
  const [embeddingMode, setEmbeddingMode] = useState(DEFAULT_VALUES.embeddingMode);
  const [modelStatus, setModelStatus] = useState<ModelStatus>({ installed: false, checking: false, installing: false });

  const [storeType, setStoreType] = useState(DEFAULT_VALUES.storeType);
  const [collectionName, setCollectionName] = useState(generateCollectionName);
  const [collectionDescription, setCollectionDescription] = useState('');
  const [isGeneratingMeta, setIsGeneratingMeta] = useState(false);
  const [storedVectors, setStoredVectors] = useState<any[]>([]);
  const [storeStats, setStoreStats] = useState<any>(null);

  const [retrieverType, setRetrieverType] = useState(DEFAULT_VALUES.retrieverType);
  const [topK, setTopK] = useState(DEFAULT_VALUES.topK);
  const [denseWeight, setDenseWeight] = useState(DEFAULT_VALUES.denseWeight);
  const [retrieveQuery, setRetrieveQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<any>(null);

  const [model, setModel] = useState(DEFAULT_VALUES.model);
  const [temperature, setTemperature] = useState(DEFAULT_VALUES.temperature);
  const [generateApiKey, setGenerateApiKey] = useState('');

  const [appMode, setAppMode] = useState<AppMode>('pipeline');

  const [ingestText, setIngestText] = useState('');
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestProgress, setIngestProgress] = useState<IngestProgress>({ step: 'idle', message: '' });
  const [ingestCollectionName, setIngestCollectionName] = useState(generateCollectionName);
  const [ingestChunkerType, setIngestChunkerType] = useState(DEFAULT_VALUES.chunkerType);
  const [ingestChunkSize, setIngestChunkSize] = useState(DEFAULT_VALUES.chunkSize);
  const [ingestChunkOverlap, setIngestChunkOverlap] = useState(DEFAULT_VALUES.chunkOverlap);
  const [ingestEmbedderType, setIngestEmbedderType] = useState(DEFAULT_VALUES.embedderType);
  const [ingestEmbedModel, setIngestEmbedModel] = useState(DEFAULT_VALUES.embedModel);
  const [ingestUseCleaner, setIngestUseCleaner] = useState(true);
  const [ingestUseNormalizer, setIngestUseNormalizer] = useState(true);
  const [ingestResult, setIngestResult] = useState<IngestResult | null>(null);

  const [queryModeQuery, setQueryModeQuery] = useState('');
  const [queryModeLoading, setQueryModeLoading] = useState(false);
  const [queryModeResult, setQueryModeResult] = useState<QueryModeResult | null>(null);
  const [queryModeLLM, setQueryModeLLM] = useState('llama-3.3-70b-versatile');
  const [queryModeTopK, setQueryModeTopK] = useState(DEFAULT_VALUES.topK);
  const [queryModeTemperature, setQueryModeTemperature] = useState(DEFAULT_VALUES.temperature);
  const [queryModeRetrieverType, setQueryModeRetrieverType] = useState('hybrid');

  const [collections, setCollections] = useState<CollectionInfo[]>([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [selectedManageCollection, setSelectedManageCollection] = useState('');
  const [manageLoading, setManageLoading] = useState(false);

  return {
    currentStep, setCurrentStep, isConnected, setIsConnected, isLoading, setIsLoading,
    storeProgress, setStoreProgress, results, setResults,
    preprocessInput, setPreprocessInput, useCleaner, setUseCleaner, useNormalizer, setUseNormalizer,
    chunkerType, setChunkerType, chunkSize, setChunkSize, chunkOverlap, setChunkOverlap,
    embedderType, setEmbedderType, openaiApiKey, setOpenaiApiKey, embedModel, setEmbedModel,
    embeddingMode, setEmbeddingMode, modelStatus, setModelStatus,
    storeType, setStoreType, collectionName, setCollectionName, collectionDescription, setCollectionDescription,
    isGeneratingMeta, setIsGeneratingMeta, storedVectors, setStoredVectors, storeStats, setStoreStats,
    retrieverType, setRetrieverType, topK, setTopK, denseWeight, setDenseWeight,
    retrieveQuery, setRetrieveQuery, selectedResult, setSelectedResult,
    model, setModel, temperature, setTemperature, generateApiKey, setGenerateApiKey,
    appMode, setAppMode,
    ingestText, setIngestText, ingestLoading, setIngestLoading, ingestProgress, setIngestProgress,
    ingestCollectionName, setIngestCollectionName, ingestChunkerType, setIngestChunkerType,
    ingestChunkSize, setIngestChunkSize, ingestChunkOverlap, setIngestChunkOverlap,
    ingestEmbedderType, setIngestEmbedderType, ingestEmbedModel, setIngestEmbedModel,
    ingestUseCleaner, setIngestUseCleaner, ingestUseNormalizer, setIngestUseNormalizer, ingestResult, setIngestResult,
    queryModeQuery, setQueryModeQuery, queryModeLoading, setQueryModeLoading, queryModeResult, setQueryModeResult,
    queryModeLLM, setQueryModeLLM, queryModeTopK, setQueryModeTopK, queryModeTemperature, setQueryModeTemperature,
    queryModeRetrieverType, setQueryModeRetrieverType,
    collections, setCollections, selectedCollection, setSelectedCollection,
    selectedManageCollection, setSelectedManageCollection, manageLoading, setManageLoading,
  };
}
