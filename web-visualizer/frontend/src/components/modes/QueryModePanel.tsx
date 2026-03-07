import { MessageSquare, RefreshCw, Binary, Search, Loader2, Bot, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../../api';
import { CollectionInfo, QueryModeResult } from '../../types';

interface QueryModePanelProps {
  collections: CollectionInfo[];
  selectedCollection: string;
  queryModeEmbedderType: string;
  queryModeModel: string;
  queryModeRetrieverType: string;
  setQueryModeRetrieverType: (type: string) => void;
  queryModeLLM: string;
  setQueryModeLLM: (llm: string) => void;
  queryModeTopK: number;
  setQueryModeTopK: (topK: number) => void;
  queryModeTemperature: number;
  setQueryModeTemperature: (temp: number) => void;
  queryModeQuery: string;
  setQueryModeQuery: (query: string) => void;
  queryModeLoading: boolean;
  setQueryModeLoading: (loading: boolean) => void;
  queryModeResult: QueryModeResult | null;
  setQueryModeResult: (result: QueryModeResult | null) => void;
  loadCollections: () => Promise<void>;
  handleCollectionChange: (name: string) => void;
}

export default function QueryModePanel({
  collections, selectedCollection,
  queryModeEmbedderType, queryModeModel,
  queryModeRetrieverType, setQueryModeRetrieverType,
  queryModeLLM, setQueryModeLLM,
  queryModeTopK, setQueryModeTopK,
  queryModeTemperature, setQueryModeTemperature,
  queryModeQuery, setQueryModeQuery,
  queryModeLoading, setQueryModeLoading,
  queryModeResult, setQueryModeResult,
  loadCollections, handleCollectionChange,
}: QueryModePanelProps) {

  const runQuickQuery = async () => {
    if (!selectedCollection || !queryModeQuery.trim()) return;
    setQueryModeLoading(true);
    try {
      const response = await api.quickQuery({
        query: queryModeQuery,
        collectionName: selectedCollection,
        storeType: 'chroma',
        embedderType: queryModeEmbedderType,
        modelName: queryModeModel,
        retrieverType: queryModeRetrieverType,
        topK: queryModeTopK,
        llmModel: queryModeLLM,
        temperature: queryModeTemperature,
      });
      setQueryModeResult(response.data);
    } catch (error: any) {
      console.error('Quick query error:', error);
      alert(`쿼리 실행 중 오류 발생: ${error.response?.data?.detail || error.message}`);
    }
    setQueryModeLoading(false);
  };

  const selectedCollectionInfo = collections.find(c => c.name === selectedCollection);

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-6">
          <MessageSquare className="w-6 h-6 text-green-600" />
          <h2 className="text-xl font-semibold">Quick Query Mode</h2>
        </div>
        <p className="text-gray-600 mb-6">
          기존 벡터 데이터베이스에서 직접 질문하세요. Pipeline 과정 없이 바로 검색하고 답변을 받을 수 있습니다.
        </p>

        <div className="grid grid-cols-2 gap-6">
          {/* Left Column - Input */}
          <div className="space-y-4">
            {/* Collection Selector */}
            <div>
              <label className="block text-sm font-medium mb-1">Collection 선택</label>
              <div className="flex space-x-2">
                <select
                  value={selectedCollection}
                  onChange={(e) => handleCollectionChange(e.target.value)}
                  className="flex-1 p-2 border rounded-lg"
                >
                  {collections.length === 0 ? (
                    <option value="">Collection이 없습니다</option>
                  ) : (
                    collections.map((col) => (
                      <option key={col.name} value={col.name}>
                        {col.name} ({col.count}개)
                      </option>
                    ))
                  )}
                </select>
                <button
                  onClick={loadCollections}
                  className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">Pipeline Mode에서 저장한 Collection을 선택하세요</p>
            </div>

            {/* Auto-detected Embedder Info */}
            {selectedCollectionInfo && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Binary className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">자동 감지된 임베더</span>
                </div>
                <p className="text-sm text-blue-700">
                  {selectedCollectionInfo.embedder_type === 'openai' ? 'OpenAI' :
                   selectedCollectionInfo.embedder_type === 'bge-m3' ? 'BGE-M3' :
                   selectedCollectionInfo.embedder_type === 'huggingface' ? 'HuggingFace' :
                   selectedCollectionInfo.embedder_type || '알 수 없음'}
                  {selectedCollectionInfo.model_name && <span className="ml-1 text-blue-600">({selectedCollectionInfo.model_name})</span>}
                </p>
                {!selectedCollectionInfo.embedder_type && (
                  <p className="text-xs text-amber-600 mt-1">
                    ⚠️ 임베더 정보가 없는 이전 데이터입니다. 수동으로 확인 후 선택하세요.
                  </p>
                )}
              </div>
            )}

            {/* Retriever Type Selector */}
            <div>
              <label className="block text-sm font-medium mb-1">검색 전략 (Retriever)</label>
              <select
                value={queryModeRetrieverType}
                onChange={(e) => setQueryModeRetrieverType(e.target.value)}
                className="w-full p-2 border rounded-lg"
              >
                <option value="dense">Dense (벡터 유사도)</option>
                <option value="sparse">Sparse (BM25 키워드)</option>
                <option value="hybrid">Hybrid (Dense + Sparse)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {queryModeRetrieverType === 'dense' && '의미적 유사도 기반 검색 - 동의어 인식 가능'}
                {queryModeRetrieverType === 'sparse' && '키워드 매칭 기반 검색 - 정확한 단어 일치'}
                {queryModeRetrieverType === 'hybrid' && '의미 + 키워드 결합 - 가장 안정적인 성능'}
              </p>
            </div>

            {/* LLM Settings */}
            <div>
              <label className="block text-sm font-medium mb-1">LLM 모델</label>
              <select
                value={queryModeLLM}
                onChange={(e) => setQueryModeLLM(e.target.value)}
                className="w-full p-2 border rounded-lg"
              >
                <optgroup label="Groq 고성능 (무료, API 키 불필요)">
                  <option value="openai/gpt-oss-120b">GPT-OSS 120B (최고성능, 추론)</option>
                  <option value="openai/gpt-oss-20b">GPT-OSS 20B (초고속 1000t/s)</option>
                  <option value="llama-3.3-70b-versatile">Llama 3.3 70B (추천)</option>
                  <option value="llama-3.1-8b-instant">Llama 3.1 8B (빠름 560t/s)</option>
                </optgroup>
                <optgroup label="Groq 실험적 (무료)">
                  <option value="qwen/qwen3-32b">Qwen3 32B (400t/s)</option>
                  <option value="meta-llama/llama-4-scout-17b-16e-instruct">Llama 4 Scout 17B (750t/s)</option>
                  <option value="gemma2-9b-it">Gemma2 9B</option>
                  <option value="mixtral-8x7b-32768">Mixtral 8x7B [멀티모델]</option>
                </optgroup>
                <optgroup label="OpenAI (API 키 필요)">
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                </optgroup>
              </select>
              <div className="flex items-center gap-2 mt-1">
                {(queryModeLLM === 'mixtral-8x7b-32768' || queryModeLLM.includes('gpt-oss')) && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded font-medium">멀티모델 (MoE)</span>
                )}
                {queryModeLLM.includes('gpt-oss') && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-medium">추론 지원</span>
                )}
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Top K: {queryModeTopK}</label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={queryModeTopK}
                  onChange={(e) => setQueryModeTopK(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Temperature: {queryModeTemperature.toFixed(1)}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={queryModeTemperature}
                  onChange={(e) => setQueryModeTemperature(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            {/* Query Input */}
            <div>
              <label className="block text-sm font-medium mb-1">질문 입력</label>
              <textarea
                value={queryModeQuery}
                onChange={(e) => setQueryModeQuery(e.target.value)}
                placeholder="벡터 데이터베이스에 질문하세요..."
                className="w-full h-32 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            {/* Submit Button */}
            <button
              onClick={runQuickQuery}
              disabled={!selectedCollection || !queryModeQuery.trim() || queryModeLoading}
              className="w-full py-3 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {queryModeLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              <span>{queryModeLoading ? '검색 및 답변 생성 중...' : 'Query 실행'}</span>
            </button>
          </div>

          {/* Right Column - Result */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">결과</h3>
            {queryModeResult ? (
              <div className="space-y-4">
                {/* Answer */}
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center space-x-2 mb-2">
                    <Bot className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">AI 답변</span>
                  </div>
                  <div className="text-gray-800 prose prose-sm max-w-none prose-table:border-collapse prose-th:border prose-th:border-gray-300 prose-th:bg-gray-100 prose-th:p-2 prose-td:border prose-td:border-gray-300 prose-td:p-2">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {queryModeResult.answer}
                    </ReactMarkdown>
                  </div>
                </div>

                {/* Sources */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Database className="w-5 h-5 text-gray-600" />
                    <span className="font-medium text-gray-700">참조 문서 ({queryModeResult.sources?.length || 0}개)</span>
                  </div>
                  <div className="space-y-2 max-h-64 overflow-auto">
                    {queryModeResult.sources?.map((source: any, i: number) => (
                      <div key={i} className="p-2 bg-white rounded border text-sm">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-blue-600 font-medium">Source {i + 1}</span>
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                            Score: {source.score?.toFixed(4) || 'N/A'}
                          </span>
                        </div>
                        <p className="text-gray-600 text-xs">{source.content?.substring(0, 150)}...</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Meta Info */}
                <div className="text-xs text-gray-500 flex items-center space-x-4">
                  <span>Collection: {queryModeResult.collection_name}</span>
                  <span>Model: {queryModeResult.llm_model}</span>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>질문을 입력하고 Query 실행을 클릭하세요</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
