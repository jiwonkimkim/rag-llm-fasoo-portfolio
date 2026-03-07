import { api, BatchProgress } from '../api';
import { PipelineState, CollectionInfo } from '../types';

interface UsePipelineActionsProps {
  // State setters
  setIsLoading: (loading: boolean) => void;
  setStoreProgress: (progress: BatchProgress | null) => void;
  setResults: React.Dispatch<React.SetStateAction<PipelineState>>;
  setModelStatus: (status: any) => void;
  setIsConnected: (connected: boolean) => void;
  setCurrentStep: (step: number) => void;
  setPreprocessInput: (input: string) => void;
  setStoredVectors: (vectors: any[]) => void;
  setStoreStats: (stats: any) => void;
  setCollectionName: (name: string) => void;
  setCollectionDescription: (desc: string) => void;
  setIsGeneratingMeta: (generating: boolean) => void;
  setCollections: (collections: CollectionInfo[]) => void;
  setManageLoading: (loading: boolean) => void;
  setSelectedCollection: (name: string) => void;
  setSelectedManageCollection: (name: string | null) => void;
  setQueryModeEmbedderType: (type: string) => void;
  setQueryModeModel: (model: string) => void;

  // Current state values
  preprocessInput: string;
  useCleaner: boolean;
  useNormalizer: boolean;
  chunkerType: string;
  chunkSize: number;
  chunkOverlap: number;
  embedderType: string;
  embedModel: string;
  openaiApiKey: string;
  embeddingMode: string;
  storeType: string;
  collectionId: string;
  collectionName: string;
  collectionDescription: string;
  retrieverType: string;
  topK: number;
  denseWeight: number;
  retrieveQuery: string;
  model: string;
  temperature: number;
  generateApiKey: string;
  results: PipelineState;
  selectedCollection: string;
  collections: CollectionInfo[];
  selectedManageCollection: string | null;
}

export function usePipelineActions(props: UsePipelineActionsProps) {
  const {
    setIsLoading, setStoreProgress, setResults, setModelStatus,
    setIsConnected, setCurrentStep, setPreprocessInput,
    setStoredVectors, setStoreStats, setCollectionName, setCollectionDescription,
    setIsGeneratingMeta, setCollections, setManageLoading, setSelectedCollection,
    setSelectedManageCollection, setQueryModeEmbedderType, setQueryModeModel,
    preprocessInput, useCleaner, useNormalizer, chunkerType, chunkSize, chunkOverlap,
    embedderType, embedModel, openaiApiKey, embeddingMode, storeType, collectionId, collectionName,
    collectionDescription, retrieverType, topK, denseWeight, retrieveQuery,
    model, temperature, generateApiKey, results, selectedCollection, collections,
    selectedManageCollection,
  } = props;

  const checkConnection = async () => {
    try {
      await api.healthCheck();
      setIsConnected(true);
    } catch {
      setIsConnected(false);
    }
  };

  const checkModelStatus = async () => {
    setModelStatus((prev: any) => ({ ...prev, checking: true }));
    try {
      const response = await api.checkModelStatus({
        modelName: embedModel,
        embedderType: embedderType,
      });
      setModelStatus({
        installed: response.data.installed,
        checking: false,
        installing: false,
        sizeMb: response.data.size_mb,
      });
    } catch (error) {
      console.error('Model status check error:', error);
      setModelStatus({ installed: false, checking: false, installing: false });
    }
  };

  const installModel = async () => {
    setModelStatus((prev: any) => ({ ...prev, installing: true }));
    try {
      const response = await api.installModel({
        modelName: embedModel,
        embedderType: embedderType,
      });
      if (response.data.success) {
        setModelStatus({ installed: true, checking: false, installing: false });
      } else {
        alert(`모델 설치 실패: ${response.data.message}`);
        setModelStatus((prev: any) => ({ ...prev, installing: false }));
      }
    } catch (error: any) {
      console.error('Model install error:', error);
      alert(`모델 설치 중 오류 발생: ${error.response?.data?.detail || error.message}`);
      setModelStatus((prev: any) => ({ ...prev, installing: false }));
    }
  };

  const resetPipeline = () => {
    setCurrentStep(0);
    setResults({
      preprocess: null, chunk: null, embed: null,
      store: null, retrieve: null, generate: null,
    });
    setPreprocessInput('');
  };

  const runPreprocess = async () => {
    setIsLoading(true);
    try {
      const response = await api.preprocess({
        text: preprocessInput,
        useCleaner,
        useNormalizer,
      });
      setResults(prev => ({
        ...prev,
        preprocess: {
          input: { text: preprocessInput, useCleaner, useNormalizer },
          output: response.data,
          timestamp: new Date(),
        },
      }));
    } catch (error) {
      console.error('Preprocess error:', error);
    }
    setIsLoading(false);
  };

  const runChunk = async () => {
    const textToChunk = results.preprocess?.output?.final || preprocessInput;
    setIsLoading(true);
    try {
      const result = await api.batchChunk(
        { text: textToChunk, chunkerType, chunkSize, chunkOverlap },
        (progress) => {
          console.log(`[runChunk] Batch ${progress.currentBatch}/${progress.totalBatches}`);
        }
      );
      setResults(prev => ({
        ...prev,
        chunk: {
          input: { text: textToChunk, chunkerType, chunkSize, chunkOverlap },
          output: result,
          timestamp: new Date(),
        },
      }));
    } catch (error: any) {
      console.error('[runChunk] Error:', error);
    }
    setIsLoading(false);
  };

  const runEmbed = async () => {
    const textsToEmbed = results.chunk?.output?.chunks || [];
    setIsLoading(true);
    try {
      const response = await api.embed({
        texts: textsToEmbed,
        embedderType,
        modelName: embedModel,
        apiKey: embedderType === 'openai' ? openaiApiKey : undefined,
        embeddingMode: embedderType === 'bge-m3' ? embeddingMode : undefined,
      });
      setResults(prev => ({
        ...prev,
        embed: {
          input: { texts: textsToEmbed, embedderType },
          output: response.data,
          timestamp: new Date(),
        },
      }));
    } catch (error) {
      console.error('Embed error:', error);
    }
    setIsLoading(false);
  };

  const generateCollectionMeta = async () => {
    const chunks = results.chunk?.output?.chunks || [];
    if (chunks.length === 0) {
      alert('먼저 청킹 단계를 실행해주세요.');
      return;
    }
    setIsGeneratingMeta(true);
    try {
      const sampleChunks = chunks.slice(0, Math.min(5, chunks.length));
      const contextText = sampleChunks.join('\n\n---\n\n');
      const response = await api.generate({
        query: `다음 텍스트 청크들을 분석하여 JSON 형식으로 응답해주세요. 반드시 아래 형식만 출력하세요:
{"name": "영문_컬렉션명_snake_case", "description": "한글로 작성된 핵심 주제 및 내용 요약 (50자 이내)"}

규칙:
1. name은 영문 소문자와 언더스코어만 사용 (예: korean_history_doc)
2. description은 문서의 핵심 주제와 내용을 간결하게 요약
3. JSON 외의 다른 텍스트는 출력하지 마세요`,
        context: [contextText],
        model: 'llama-3.3-70b-versatile',
        temperature: 0.3,
      });
      const generatedText = response.data.generated_text || response.data.response || '';
      try {
        const jsonMatch = generatedText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.name) {
            const sanitizedName = parsed.name.toLowerCase().replace(/[^a-z0-9_]/g, '_').substring(0, 50);
            setCollectionName(sanitizedName);
          }
          if (parsed.description) {
            setCollectionDescription(parsed.description);
          }
        }
      } catch (parseError) {
        console.error('Failed to parse generated metadata:', parseError);
        setCollectionDescription(generatedText.substring(0, 100));
      }
    } catch (error) {
      console.error('Generate metadata error:', error);
      alert('메타데이터 생성에 실패했습니다. 다시 시도해주세요.');
    }
    setIsGeneratingMeta(false);
  };

  const runStore = async () => {
    const texts = results.chunk?.output?.chunks || [];
    const embeddings = results.embed?.output?.embeddings || [];
    if (texts.length === 0 || embeddings.length === 0) return;

    setIsLoading(true);
    setStoreProgress(null);
    try {
      const usedEmbedderType = results.embed?.input?.embedderType || embedderType;
      const usedModelName = results.embed?.output?.model_name || embedModel;
      const chunkInput = results.chunk?.input;
      const usedChunkerType = chunkInput?.chunkerType || chunkerType;
      const usedChunkSize = chunkInput?.chunkSize || chunkSize;
      const usedChunkOverlap = chunkInput?.chunkOverlap || chunkOverlap;

      // Display name: use collectionName if set, otherwise use collectionId
      const displayName = collectionName.trim() || collectionId;
      const finalDescription = collectionDescription.trim() || displayName;

      const response = await api.batchStore({
        texts,
        embeddings,
        storeType,
        collectionName: collectionId,  // Always use the rag_collection_YYYYMMDD_HHMMSS format as actual ID
        metadatas: texts.map((_: string, i: number) => ({ chunk_index: i })),
        embedderType: usedEmbedderType,
        modelName: usedModelName,
        displayName: displayName,  // Separate display name field
        description: finalDescription,  // Description without embedded display name
        prepStoreType: 'standard',
        chunkingAlgorithm: usedChunkerType,
        chunkSize: usedChunkSize,
        chunkOverlap: usedChunkOverlap,
        extraBodyLength: 0,
        minChunkGroupSize: 1,
        totalDocuments: 1,
        successDocuments: 1,
        failedDocuments: 0,
      }, (progress) => {
        setStoreProgress(progress);
      });

      setResults(prev => ({
        ...prev,
        store: {
          input: { texts: texts.length, embeddings: embeddings.length, storeType, collectionName },
          output: { success: true, totalStored: response.totalStored, batches: response.batches },
          timestamp: new Date(),
        },
      }));
      await loadStoreStats();
      await loadStoredVectors();
    } catch (error) {
      console.error('Store error:', error);
    }
    setStoreProgress(null);
    setIsLoading(false);
  };

  const loadStoreStats = async () => {
    try {
      const response = await api.getStoreStats({ collectionName: collectionId, storeType });
      setStoreStats(response.data);
    } catch (error) {
      console.error('Load stats error:', error);
    }
  };

  const loadStoredVectors = async () => {
    try {
      const response = await api.getStoreList({ collectionName: collectionId, storeType, page: 1, pageSize: 10 });
      setStoredVectors(response.data.vectors || []);
    } catch (error) {
      console.error('Load vectors error:', error);
    }
  };

  const handleClearStore = async () => {
    if (!confirm('정말로 모든 벡터를 삭제하시겠습니까?')) return;
    setIsLoading(true);
    try {
      await api.clearStore({ collectionName: collectionId, storeType });
      setStoredVectors([]);
      setStoreStats(null);
      setResults(prev => ({ ...prev, store: null }));
    } catch (error) {
      console.error('Clear store error:', error);
    }
    setIsLoading(false);
  };

  const runRetrieve = async () => {
    const query = retrieveQuery.trim();
    if (!query) return;
    setIsLoading(true);
    const usedEmbedderType = results.embed?.input?.embedderType || embedderType;
    const usedModelName = results.embed?.output?.model_name || embedModel;
    try {
      const response = await api.retrieve({
        query,
        retrieverType,
        topK,
        denseWeight,
        sparseWeight: 1 - denseWeight,
        collectionName: collectionId,  // Use collectionId as the actual ChromaDB collection name
        storeType,
        embedderType: usedEmbedderType,
        modelName: usedModelName,
        apiKey: usedEmbedderType === 'openai' ? openaiApiKey : undefined,
      });
      setResults(prev => ({
        ...prev,
        retrieve: {
          input: { query, retrieverType, topK },
          output: response.data,
          timestamp: new Date(),
        },
      }));
    } catch (error) {
      console.error('Retrieve error:', error);
    }
    setIsLoading(false);
  };

  const runGenerate = async () => {
    const query = results.retrieve?.input?.query || retrieveQuery;
    const context = results.retrieve?.output?.results?.map((r: any) => r.content) || [];
    setIsLoading(true);
    try {
      const response = await api.generate({
        query,
        context,
        model,
        temperature,
        apiKey: generateApiKey || undefined,
      });
      setResults(prev => ({
        ...prev,
        generate: {
          input: { query, context, model, temperature },
          output: response.data,
          timestamp: new Date(),
        },
      }));
    } catch (error) {
      console.error('Generate error:', error);
    }
    setIsLoading(false);
  };

  const loadCollections = async () => {
    setManageLoading(true);
    try {
      const response = await api.getCollections({ storeType: 'chroma' });
      const collectionData: CollectionInfo[] = (response.data.collections || []).map((c: any) => ({
        name: c.name,
        count: c.count,
        store_type: c.store_type,
        embedder_type: c.embedder_type,
        model_name: c.model_name,
        display_name: c.display_name,
        description: c.description,
        prep_store_type: c.prep_store_type,
        created_at: c.created_at,
        chunking_algorithm: c.chunking_algorithm,
        chunk_size: c.chunk_size,
        chunk_overlap: c.chunk_overlap,
        extra_body_length: c.extra_body_length,
        min_chunk_group_size: c.min_chunk_group_size,
        total_chunks: c.total_chunks,
        total_documents: c.total_documents,
        success_documents: c.success_documents,
        failed_documents: c.failed_documents,
      }));
      setCollections(collectionData);
      if (collectionData.length > 0 && !selectedCollection) {
        const firstCollection = collectionData[0];
        setSelectedCollection(firstCollection.name);
        if (firstCollection.embedder_type) {
          setQueryModeEmbedderType(firstCollection.embedder_type);
        }
        if (firstCollection.model_name) {
          setQueryModeModel(firstCollection.model_name);
        }
      }
    } catch (error) {
      console.error('Failed to load collections:', error);
    }
    setManageLoading(false);
  };

  const deleteCollection = async (collectionNameToDelete: string) => {
    if (!confirm(`정말 "${collectionNameToDelete}" 컬렉션을 삭제하시겠습니까?`)) return;
    setManageLoading(true);
    try {
      await api.clearStore({ collectionName: collectionNameToDelete, storeType: 'chroma' });
      await loadCollections();
      if (selectedManageCollection === collectionNameToDelete) {
        setSelectedManageCollection(null);
      }
    } catch (error) {
      console.error('Failed to delete collection:', error);
      alert('컬렉션 삭제에 실패했습니다.');
    }
    setManageLoading(false);
  };

  const handleCollectionChange = (name: string) => {
    setSelectedCollection(name);
    const selected = collections.find(c => c.name === name);
    if (selected) {
      if (selected.embedder_type) {
        setQueryModeEmbedderType(selected.embedder_type);
      }
      if (selected.model_name) {
        setQueryModeModel(selected.model_name);
      }
    }
  };

  return {
    checkConnection,
    checkModelStatus,
    installModel,
    resetPipeline,
    runPreprocess,
    runChunk,
    runEmbed,
    generateCollectionMeta,
    runStore,
    loadStoreStats,
    loadStoredVectors,
    handleClearStore,
    runRetrieve,
    runGenerate,
    loadCollections,
    deleteCollection,
    handleCollectionChange,
  };
}
