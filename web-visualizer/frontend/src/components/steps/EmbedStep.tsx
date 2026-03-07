import { PlayCircle, Loader2, CheckCircle2, AlertCircle, Download } from 'lucide-react';
import { StepResult, ModelStatus, ModelOption, EmbeddingModeOption } from '../../types';

interface EmbedStepProps {
  chunkResult: StepResult | null;
  embedderType: string;
  setEmbedderType: (value: string) => void;
  embedModel: string;
  setEmbedModel: (value: string) => void;
  openaiApiKey: string;
  setOpenaiApiKey: (value: string) => void;
  embeddingMode: string;
  setEmbeddingMode: (value: string) => void;
  modelStatus: ModelStatus;
  openaiModels: ModelOption[];
  huggingfaceModels: ModelOption[];
  bgeM3Models: ModelOption[];
  embeddingModes: EmbeddingModeOption[];
  isLoading: boolean;
  result: StepResult | null;
  onRun: () => void;
  onInstallModel: () => void;
}

export default function EmbedStep({
  chunkResult,
  embedderType,
  setEmbedderType,
  embedModel,
  setEmbedModel,
  openaiApiKey,
  setOpenaiApiKey,
  embeddingMode,
  setEmbeddingMode,
  modelStatus,
  openaiModels,
  huggingfaceModels,
  bgeM3Models,
  embeddingModes,
  isLoading,
  result,
  onRun,
  onInstallModel,
}: EmbedStepProps) {
  const chunks = chunkResult?.output?.chunks || [];
  const models = embedderType === 'openai' ? openaiModels : embedderType === 'bge-m3' ? bgeM3Models : huggingfaceModels;

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <div className="p-3 bg-gray-50 rounded-lg h-32 overflow-auto">
          <p className="text-sm text-gray-500 mb-2">
            임베딩할 청크 ({chunks.length}개)
          </p>
          {chunks.slice(0, 10).map((chunk: string, i: number) => (
            <p key={i} className="text-xs text-gray-600 mb-1">• {chunk.substring(0, 50)}...</p>
          )) || <p className="text-gray-400">이전 단계를 먼저 실행하세요</p>}
          {chunks.length > 10 && (
            <p className="text-xs text-gray-400">... 외 {chunks.length - 10}개</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Embedder Type</label>
          <select
            value={embedderType}
            onChange={(e) => setEmbedderType(e.target.value)}
            className="w-full p-2 border rounded-lg"
          >
            <option value="openai">OpenAI</option>
            <option value="huggingface">HuggingFace</option>
            <option value="bge-m3">BGE-M3 (추천)</option>
          </select>
          <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
            {embedderType === 'openai' && (
              <p><strong>OpenAI:</strong> 유료 API, 빠름, 고품질 (API 키 필요)</p>
            )}
            {embedderType === 'huggingface' && (
              <p><strong>HuggingFace:</strong> 무료 로컬, 첫 실행 시 모델 다운로드</p>
            )}
            {embedderType === 'bge-m3' && (
              <p><strong>BGE-M3:</strong> Dense+Sparse+ColBERT 동시 지원, 다국어 최고 성능 (pip install FlagEmbedding 필요)</p>
            )}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Model</label>
          <select
            value={embedModel}
            onChange={(e) => setEmbedModel(e.target.value)}
            className="w-full p-2 border rounded-lg text-sm"
          >
            {models.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label} ({m.dim}D) - {m.desc}
              </option>
            ))}
          </select>
          {embedderType !== 'openai' && (
            <div className={`mt-2 p-2 rounded-lg text-sm flex items-center justify-between ${
              modelStatus.checking || modelStatus.installing
                ? 'bg-yellow-50 border border-yellow-200'
                : modelStatus.installed
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center space-x-2">
                {modelStatus.checking ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-yellow-600" />
                    <span className="text-yellow-700">모델 상태 확인 중...</span>
                  </>
                ) : modelStatus.installing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-yellow-600" />
                    <span className="text-yellow-700">모델 설치 중... (수 분 소요)</span>
                  </>
                ) : modelStatus.installed ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <span className="text-green-700">
                      모델 설치됨 {modelStatus.sizeMb && `(${modelStatus.sizeMb.toFixed(1)} MB)`}
                    </span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-red-700">모델 미설치</span>
                  </>
                )}
              </div>
              {!modelStatus.installed && !modelStatus.checking && !modelStatus.installing && (
                <button
                  onClick={onInstallModel}
                  className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 flex items-center space-x-1"
                >
                  <Download className="w-3 h-3" />
                  <span>모델 설치</span>
                </button>
              )}
            </div>
          )}
        </div>
        {embedderType === 'bge-m3' && (
          <div>
            <label className="block text-sm font-medium mb-1">Embedding Mode</label>
            <select
              value={embeddingMode}
              onChange={(e) => setEmbeddingMode(e.target.value)}
              className="w-full p-2 border rounded-lg text-sm"
            >
              {embeddingModes.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {embeddingModes.find(m => m.value === embeddingMode)?.desc}
            </p>
          </div>
        )}
        {embedderType === 'openai' && (
          <div>
            <label className="block text-sm font-medium mb-1">OpenAI API Key</label>
            <input
              type="password"
              value={openaiApiKey}
              onChange={(e) => setOpenaiApiKey(e.target.value)}
              placeholder="sk-..."
              className="w-full p-2 border rounded-lg font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">API 키는 서버로 전송되며 저장되지 않습니다</p>
          </div>
        )}
        <button
          onClick={onRun}
          disabled={!chunkResult || isLoading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <PlayCircle className="w-5 h-5" />}
          <span>Run Embedder</span>
        </button>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Output</h3>
        {result ? (
          <div className="space-y-3">
            <div className="p-3 bg-purple-50 rounded-lg text-center">
              <p className="text-2xl font-bold text-purple-600">{result.output.dimension}</p>
              <p className="text-sm text-purple-600">Dimension</p>
            </div>
            <div className="h-48 overflow-auto space-y-2">
              {result.output.embeddings?.map((emb: number[], i: number) => (
                <div key={i} className="p-2 bg-gray-50 rounded text-xs font-mono">
                  <span className="text-purple-600">Vector {i + 1}:</span>
                  <span className="text-gray-500 ml-2">[{emb.slice(0, 4).map(v => v.toFixed(4)).join(', ')}...]</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
            결과가 여기에 표시됩니다
          </div>
        )}
      </div>
    </div>
  );
}
