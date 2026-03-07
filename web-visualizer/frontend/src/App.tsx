import { useState, useEffect } from 'react';
import { BatchProgress } from './api';
import {
  ChevronRight,
  ChevronLeft,
  RotateCcw,
  CheckCircle2,
  Circle,
  Layers,
  Database,
  MessageSquare,
  Settings,
  ShoppingCart,
} from 'lucide-react';
import {
  PreprocessStep,
  ChunkStep,
  EmbedStep,
  StoreStep,
  RetrieveStep,
  GenerateStep,
} from './components/steps';
import { IngestModePanel, QueryModePanel, ManageModePanel, CollectModePanel } from './components/modes';
import { usePipelineActions } from './hooks';
import {
  STEPS,
  generateCollectionName,
  OPENAI_MODELS,
  HUGGINGFACE_MODELS,
  BGE_M3_MODELS,
  EMBEDDING_MODES,
  GROQ_MODELS,
} from './constants';
import { PipelineState, AppMode } from './types';

export default function App() {
  // Pipeline state
  const [currentStep, setCurrentStep] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [storeProgress, setStoreProgress] = useState<BatchProgress | null>(null);
  const [results, setResults] = useState<PipelineState>({
    preprocess: null, chunk: null, embed: null, store: null, retrieve: null, generate: null,
  });

  // Pipeline form states
  const [preprocessInput, setPreprocessInput] = useState('');
  const [useCleaner, setUseCleaner] = useState(true);
  const [useNormalizer, setUseNormalizer] = useState(true);
  const [chunkerType, setChunkerType] = useState('semantic');
  const [chunkSize, setChunkSize] = useState(512);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [embedderType, setEmbedderType] = useState('huggingface');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [embedModel, setEmbedModel] = useState('intfloat/multilingual-e5-base');
  const [embeddingMode, setEmbeddingMode] = useState('dense');
  const [modelStatus, setModelStatus] = useState<any>({ installed: false, checking: false, installing: false });
  const [storeType, setStoreType] = useState('chroma');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [collectionId, _setCollectionId] = useState(generateCollectionName);  // Actual ID: rag_collection_YYYYMMDD_HHMMSS (read-only, auto-generated)
  const [collectionName, setCollectionName] = useState('');  // Display name (user input or auto-generated)
  const [collectionDescription, setCollectionDescription] = useState('');
  const [isGeneratingMeta, setIsGeneratingMeta] = useState(false);
  const [storedVectors, setStoredVectors] = useState<any[]>([]);
  const [storeStats, setStoreStats] = useState<any>(null);
  const [retrieverType, setRetrieverType] = useState('dense');
  const [topK, setTopK] = useState(5);
  const [denseWeight, setDenseWeight] = useState(0.5);
  const [retrieveQuery, setRetrieveQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<any>(null);
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [temperature, setTemperature] = useState(0.7);
  const [generateApiKey, setGenerateApiKey] = useState('');

  // App mode
  const [appMode, setAppMode] = useState<AppMode>('pipeline');

  // Ingest mode states
  const [ingestText, setIngestText] = useState('');
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestProgress, setIngestProgress] = useState<any>({ step: 'idle', message: '' });
  const [ingestCollectionId, setIngestCollectionId] = useState(generateCollectionName);
  const [ingestCollectionName, setIngestCollectionName] = useState('');
  const [ingestDescription, setIngestDescription] = useState('');
  const [ingestChunkerType, setIngestChunkerType] = useState('semantic');
  const [ingestChunkSize, setIngestChunkSize] = useState(512);
  const [ingestChunkOverlap, setIngestChunkOverlap] = useState(50);
  const [ingestEmbedderType, setIngestEmbedderType] = useState('huggingface');
  const [ingestEmbedModel, setIngestEmbedModel] = useState('intfloat/multilingual-e5-base');
  const [ingestUseCleaner, setIngestUseCleaner] = useState(true);
  const [ingestUseNormalizer, setIngestUseNormalizer] = useState(true);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [ingestIsGeneratingMeta, setIngestIsGeneratingMeta] = useState(false);

  // Query mode states
  const [collections, setCollections] = useState<any[]>([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [queryModeEmbedderType, setQueryModeEmbedderType] = useState('huggingface');
  const [queryModeModel, setQueryModeModel] = useState('intfloat/multilingual-e5-base');
  const [queryModeLLM, setQueryModeLLM] = useState('llama-3.3-70b-versatile');
  const [queryModeTopK, setQueryModeTopK] = useState(5);
  const [queryModeTemperature, setQueryModeTemperature] = useState(0.7);
  const [queryModeRetrieverType, setQueryModeRetrieverType] = useState('dense');
  const [queryModeQuery, setQueryModeQuery] = useState('');
  const [queryModeLoading, setQueryModeLoading] = useState(false);
  const [queryModeResult, setQueryModeResult] = useState<any>(null);

  // Manage mode states
  const [selectedManageCollection, setSelectedManageCollection] = useState<string | null>(null);
  const [manageLoading, setManageLoading] = useState(false);

  const isGroqModel = (GROQ_MODELS as readonly string[]).includes(model);

  // Actions
  const actions = usePipelineActions({
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
  });

  // Effects
  useEffect(() => { actions.checkConnection(); }, []);
  useEffect(() => {
    if (appMode === 'query' || appMode === 'manage' || appMode === 'ingest') {
      actions.loadCollections();
    }
  }, [appMode]);
  useEffect(() => {
    if (embedderType === 'openai') setEmbedModel('text-embedding-3-small');
    else if (embedderType === 'bge-m3') setEmbedModel('BAAI/bge-m3');
    else setEmbedModel('intfloat/multilingual-e5-base');
  }, [embedderType]);
  useEffect(() => {
    if (embedderType !== 'openai') actions.checkModelStatus();
    else setModelStatus({ installed: true, checking: false, installing: false });
  }, [embedderType, embedModel]);

  const getStepStatus = (index: number) => {
    const stepId = STEPS[index].id as keyof PipelineState;
    if (results[stepId]) return 'completed';
    if (index === currentStep) return 'current';
    return 'pending';
  };

  const renderStepContent = () => {
    const stepId = STEPS[currentStep].id;
    switch (stepId) {
      case 'preprocess':
        return <PreprocessStep preprocessInput={preprocessInput} setPreprocessInput={setPreprocessInput}
          useCleaner={useCleaner} setUseCleaner={setUseCleaner} useNormalizer={useNormalizer}
          setUseNormalizer={setUseNormalizer} isLoading={isLoading} result={results.preprocess}
          onRun={actions.runPreprocess} />;
      case 'chunk':
        return <ChunkStep preprocessResult={results.preprocess} chunkerType={chunkerType}
          setChunkerType={setChunkerType} chunkSize={chunkSize} setChunkSize={setChunkSize}
          chunkOverlap={chunkOverlap} setChunkOverlap={setChunkOverlap} isLoading={isLoading}
          result={results.chunk} onRun={actions.runChunk} />;
      case 'embed':
        return <EmbedStep chunkResult={results.chunk} embedderType={embedderType}
          setEmbedderType={setEmbedderType} embedModel={embedModel} setEmbedModel={setEmbedModel}
          openaiApiKey={openaiApiKey} setOpenaiApiKey={setOpenaiApiKey} embeddingMode={embeddingMode}
          setEmbeddingMode={setEmbeddingMode} modelStatus={modelStatus} openaiModels={OPENAI_MODELS}
          huggingfaceModels={HUGGINGFACE_MODELS} bgeM3Models={BGE_M3_MODELS} embeddingModes={EMBEDDING_MODES}
          isLoading={isLoading} result={results.embed} onRun={actions.runEmbed}
          onInstallModel={actions.installModel} />;
      case 'store':
        return <StoreStep chunkResult={results.chunk} embedResult={results.embed} storeType={storeType}
          setStoreType={setStoreType} collectionId={collectionId} collectionName={collectionName}
          setCollectionName={setCollectionName} collectionDescription={collectionDescription}
          setCollectionDescription={setCollectionDescription} isGeneratingMeta={isGeneratingMeta}
          storeProgress={storeProgress} storedVectors={storedVectors} storeStats={storeStats}
          isLoading={isLoading} result={results.store} onRun={actions.runStore}
          onRefresh={actions.loadStoredVectors} onClear={actions.handleClearStore}
          onGenerateMeta={actions.generateCollectionMeta} />;
      case 'retrieve':
        return <RetrieveStep retrieveQuery={retrieveQuery} setRetrieveQuery={setRetrieveQuery}
          collectionId={collectionId} collectionName={collectionName} embedderType={embedderType}
          embedResult={results.embed} retrieverType={retrieverType} setRetrieverType={setRetrieverType}
          topK={topK} setTopK={setTopK} denseWeight={denseWeight} setDenseWeight={setDenseWeight}
          isLoading={isLoading} result={results.retrieve} selectedResult={selectedResult}
          setSelectedResult={setSelectedResult} onRun={actions.runRetrieve} />;
      case 'generate':
        return <GenerateStep retrieveResult={results.retrieve} model={model} setModel={setModel}
          generateApiKey={generateApiKey} setGenerateApiKey={setGenerateApiKey} temperature={temperature}
          setTemperature={setTemperature} isGroqModel={isGroqModel} isLoading={isLoading}
          result={results.generate} onRun={actions.runGenerate} />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🔍 RAG Pipeline Visualizer</h1>
          <div className="flex items-center space-x-4">
            <div className="flex bg-gray-100 rounded-lg p-1">
              {[
                { mode: 'pipeline' as AppMode, label: 'Pipeline Mode', Icon: Layers, color: 'blue' },
                { mode: 'ingest' as AppMode, label: 'Ingest Mode', Icon: Database, color: 'orange' },
                { mode: 'query' as AppMode, label: 'Query Mode', Icon: MessageSquare, color: 'green' },
                { mode: 'manage' as AppMode, label: 'Manage', Icon: Settings, color: 'purple' },
                { mode: 'collect' as AppMode, label: 'Collect', Icon: ShoppingCart, color: 'indigo' },
              ].map(({ mode, label, Icon, color }) => (
                <button key={mode} onClick={() => setAppMode(mode)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    appMode === mode ? `bg-white text-${color}-600 shadow-sm` : 'text-gray-600 hover:text-gray-800'
                  }`}>
                  <Icon className="w-4 h-4" /><span>{label}</span>
                </button>
              ))}
            </div>
            <span className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </span>
            {appMode === 'pipeline' && (
              <button onClick={actions.resetPipeline}
                className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800">
                <RotateCcw className="w-4 h-4" /><span>Reset</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {appMode === 'pipeline' ? (
        <>
          {/* Progress Steps */}
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between bg-white rounded-lg shadow p-4">
              {STEPS.map((step, index) => {
                const status = getStepStatus(index);
                const Icon = step.icon;
                return (
                  <div key={step.id} className="flex items-center">
                    <button onClick={() => setCurrentStep(index)}
                      className={`flex flex-col items-center p-3 rounded-lg transition-all ${
                        status === 'current' ? 'bg-blue-50' : ''
                      } hover:bg-gray-50`}>
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        status === 'completed' ? 'bg-green-100 text-green-600' :
                        status === 'current' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                      }`}>
                        {status === 'completed' ? <CheckCircle2 className="w-6 h-6" /> :
                         status === 'current' ? <Icon className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
                      </div>
                      <span className={`mt-2 text-sm font-medium ${
                        status === 'current' ? 'text-blue-600' : 'text-gray-600'
                      }`}>{step.name}</span>
                      <span className="text-xs text-gray-400">{step.description}</span>
                    </button>
                    {index < STEPS.length - 1 && <ChevronRight className="w-6 h-6 text-gray-300 mx-2" />}
                  </div>
                );
              })}
            </div>
          </div>
          {/* Step Content */}
          <div className="max-w-7xl mx-auto px-4 pb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-3 mb-6">
                {(() => { const Icon = STEPS[currentStep].icon; return <Icon className="w-6 h-6 text-blue-600" />; })()}
                <h2 className="text-xl font-semibold">Step {currentStep + 1}: {STEPS[currentStep].name}</h2>
              </div>
              {renderStepContent()}
              <div className="flex justify-between mt-6 pt-6 border-t">
                <button onClick={() => setCurrentStep(Math.max(0, currentStep - 1))} disabled={currentStep === 0}
                  className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50">
                  <ChevronLeft className="w-5 h-5" /><span>Previous</span>
                </button>
                <button onClick={() => setCurrentStep(Math.min(STEPS.length - 1, currentStep + 1))}
                  disabled={currentStep === STEPS.length - 1}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  <span>Next</span><ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </>
      ) : appMode === 'ingest' ? (
        <IngestModePanel
          ingestText={ingestText} setIngestText={setIngestText}
          ingestCollectionId={ingestCollectionId} setIngestCollectionId={setIngestCollectionId}
          ingestCollectionName={ingestCollectionName} setIngestCollectionName={setIngestCollectionName}
          ingestDescription={ingestDescription} setIngestDescription={setIngestDescription}
          ingestUseCleaner={ingestUseCleaner} setIngestUseCleaner={setIngestUseCleaner}
          ingestUseNormalizer={ingestUseNormalizer} setIngestUseNormalizer={setIngestUseNormalizer}
          ingestChunkerType={ingestChunkerType} setIngestChunkerType={setIngestChunkerType}
          ingestChunkSize={ingestChunkSize} setIngestChunkSize={setIngestChunkSize}
          ingestChunkOverlap={ingestChunkOverlap} setIngestChunkOverlap={setIngestChunkOverlap}
          ingestEmbedderType={ingestEmbedderType} setIngestEmbedderType={setIngestEmbedderType}
          ingestEmbedModel={ingestEmbedModel} setIngestEmbedModel={setIngestEmbedModel}
          ingestLoading={ingestLoading} setIngestLoading={setIngestLoading}
          ingestProgress={ingestProgress} setIngestProgress={setIngestProgress}
          ingestResult={ingestResult} setIngestResult={setIngestResult}
          isGeneratingMeta={ingestIsGeneratingMeta} setIsGeneratingMeta={setIngestIsGeneratingMeta}
        />
      ) : appMode === 'query' ? (
        <QueryModePanel
          collections={collections} selectedCollection={selectedCollection}
          queryModeEmbedderType={queryModeEmbedderType} queryModeModel={queryModeModel}
          queryModeRetrieverType={queryModeRetrieverType} setQueryModeRetrieverType={setQueryModeRetrieverType}
          queryModeLLM={queryModeLLM} setQueryModeLLM={setQueryModeLLM}
          queryModeTopK={queryModeTopK} setQueryModeTopK={setQueryModeTopK}
          queryModeTemperature={queryModeTemperature} setQueryModeTemperature={setQueryModeTemperature}
          queryModeQuery={queryModeQuery} setQueryModeQuery={setQueryModeQuery}
          queryModeLoading={queryModeLoading} setQueryModeLoading={setQueryModeLoading}
          queryModeResult={queryModeResult} setQueryModeResult={setQueryModeResult}
          loadCollections={actions.loadCollections} handleCollectionChange={actions.handleCollectionChange}
        />
      ) : appMode === 'manage' ? (
        <ManageModePanel
          collections={collections} selectedManageCollection={selectedManageCollection}
          setSelectedManageCollection={setSelectedManageCollection} manageLoading={manageLoading}
          loadCollections={actions.loadCollections} deleteCollection={actions.deleteCollection}
        />
      ) : appMode === 'collect' ? (
        <CollectModePanel />
      ) : null}
    </div>
  );
}
