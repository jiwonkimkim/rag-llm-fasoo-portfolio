import { Database, Loader2, CheckCircle2, Circle, AlertCircle, Info, Sparkles } from 'lucide-react';
import { api } from '../../api';
import { IngestProgress, IngestResult } from '../../types';
import { generateCollectionName } from '../../constants';

interface IngestModePanelProps {
  ingestText: string;
  setIngestText: (text: string) => void;
  ingestCollectionId: string;
  setIngestCollectionId: (id: string) => void;
  ingestCollectionName: string;
  setIngestCollectionName: (name: string) => void;
  ingestDescription: string;
  setIngestDescription: (desc: string) => void;
  ingestUseCleaner: boolean;
  setIngestUseCleaner: (use: boolean) => void;
  ingestUseNormalizer: boolean;
  setIngestUseNormalizer: (use: boolean) => void;
  ingestChunkerType: string;
  setIngestChunkerType: (type: string) => void;
  ingestChunkSize: number;
  setIngestChunkSize: (size: number) => void;
  ingestChunkOverlap: number;
  setIngestChunkOverlap: (overlap: number) => void;
  ingestEmbedderType: string;
  setIngestEmbedderType: (type: string) => void;
  ingestEmbedModel: string;
  setIngestEmbedModel: (model: string) => void;
  ingestLoading: boolean;
  setIngestLoading: (loading: boolean) => void;
  ingestProgress: IngestProgress;
  setIngestProgress: (progress: IngestProgress) => void;
  ingestResult: IngestResult | null;
  setIngestResult: (result: IngestResult | null) => void;
  isGeneratingMeta: boolean;
  setIsGeneratingMeta: (generating: boolean) => void;
}

export default function IngestModePanel({
  ingestText, setIngestText,
  ingestCollectionId, setIngestCollectionId,
  ingestCollectionName, setIngestCollectionName,
  ingestDescription, setIngestDescription,
  ingestUseCleaner, setIngestUseCleaner,
  ingestUseNormalizer, setIngestUseNormalizer,
  ingestChunkerType, setIngestChunkerType,
  ingestChunkSize, setIngestChunkSize,
  ingestChunkOverlap, setIngestChunkOverlap,
  ingestEmbedderType, setIngestEmbedderType,
  ingestEmbedModel, setIngestEmbedModel,
  ingestLoading, setIngestLoading,
  ingestProgress, setIngestProgress,
  ingestResult, setIngestResult,
  isGeneratingMeta, setIsGeneratingMeta,
}: IngestModePanelProps) {

  // Groq API를 사용하여 Collection Name과 Description 자동 생성
  const generateCollectionMeta = async () => {
    if (!ingestText.trim()) {
      alert('먼저 텍스트를 입력해주세요.');
      return;
    }
    setIsGeneratingMeta(true);
    try {
      // 텍스트 샘플 추출 (앞부분 500자)
      const sampleText = ingestText.trim().substring(0, 500);

      const response = await api.generate({
        query: `Analyze the following text and respond ONLY with a JSON object in this exact format:
{"name": "english_collection_name_snake_case", "description": "Korean description summarizing the key topic (50 chars max)"}

Rules:
1. name: Use ONLY lowercase English letters and underscores (e.g., korean_economy_news, national_pension_fund)
2. name: Extract the main topic/theme and translate to English
3. name: Maximum 30 characters
4. description: Write in Korean, summarizing the core content
5. Output ONLY the JSON, nothing else`,
        context: [sampleText],
        model: 'llama-3.3-70b-versatile',
        temperature: 0.3,
      });

      const generatedText = response.data.generated_text || response.data.response || '';
      try {
        const jsonMatch = generatedText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.name) {
            const sanitizedName = parsed.name.toLowerCase().replace(/[^a-z0-9_]/g, '_').substring(0, 30);
            setIngestCollectionName(sanitizedName);
          }
          if (parsed.description) {
            setIngestDescription(parsed.description);
          }
        }
      } catch (parseError) {
        console.error('Failed to parse generated metadata:', parseError);
        // Fallback: 텍스트 첫 줄 사용
        const firstLine = ingestText.trim().split('\n')[0]?.substring(0, 50) || '';
        setIngestDescription(firstLine);
      }
    } catch (error) {
      console.error('Generate metadata error:', error);
      alert('메타데이터 생성에 실패했습니다. 다시 시도해주세요.');
    }
    setIsGeneratingMeta(false);
  };

  const handleIngest = async () => {
    if (!ingestText.trim()) {
      alert('텍스트를 입력해주세요.');
      return;
    }
    setIngestLoading(true);
    setIngestResult(null);
    setIngestProgress({ step: 'preprocess', message: '전처리 중...' });

    try {
      // Step 1: Preprocess
      const preprocessResult = await api.preprocess({
        text: ingestText,
        useCleaner: ingestUseCleaner,
        useNormalizer: ingestUseNormalizer,
      });
      setIngestProgress({ step: 'chunk', message: '청킹 중...', details: { preprocessed: preprocessResult.data.final?.length || 0 } });

      // Step 2: Chunk
      const chunkResult = await api.chunk({
        text: preprocessResult.data.final,
        chunkerType: ingestChunkerType,
        chunkSize: ingestChunkSize,
        chunkOverlap: ingestChunkOverlap,
      });
      const chunks = chunkResult.data.chunks || [];
      setIngestProgress({ step: 'embed', message: `임베딩 생성 중... (${chunks.length}개 청크)`, details: { chunks: chunks.length } });

      // Step 3: Embed
      const embedResult = await api.embed({
        texts: chunks,
        embedderType: ingestEmbedderType,
        modelName: ingestEmbedModel,
      });
      const embeddings = embedResult.data.embeddings || [];
      setIngestProgress({ step: 'store', message: `벡터 저장 중... (${embeddings.length}개)`, details: { chunks: chunks.length, embeddings: embeddings.length } });

      // Collection ID is always auto-generated format, display name is separate
      const displayName = ingestCollectionName.trim() || ingestCollectionId;
      const finalDescription = ingestDescription.trim() || displayName;

      // Step 4: Store with batch - always use ingestCollectionId as the actual collection name
      const storeResult = await api.batchStore({
        texts: chunks,
        embeddings: embeddings,
        storeType: 'chroma',
        collectionName: ingestCollectionId,  // Always use the rag_collection_YYYYMMDD_HHMMSS format
        embedderType: ingestEmbedderType,
        modelName: ingestEmbedModel,
        displayName: displayName,  // Separate display name field
        description: finalDescription,  // Description without embedded display name
        prepStoreType: 'standard',
        chunkingAlgorithm: ingestChunkerType,
        chunkSize: ingestChunkSize,
        chunkOverlap: ingestChunkOverlap,
        totalDocuments: 1,
        successDocuments: 1,
        failedDocuments: 0,
      }, (progress) => {
        setIngestProgress({
          step: 'store',
          message: `벡터 저장 중... (${progress.storedVectors}/${progress.totalVectors})`,
          details: {
            chunks: chunks.length,
            embeddings: embeddings.length,
            currentBatch: progress.currentBatch,
            totalBatches: progress.totalBatches,
            storedVectors: progress.storedVectors,
            totalVectors: progress.totalVectors,
          }
        });
      });

      setIngestProgress({ step: 'done', message: '완료!', details: { chunks: chunks.length, embeddings: embeddings.length, stored: storeResult.totalStored } });
      setIngestResult({
        success: true,
        chunks: chunks.length,
        embeddings: embeddings.length,
        stored: storeResult.totalStored,
        collectionName: displayName,  // Show the display name to user
        collectionId: ingestCollectionId,  // Store the actual ID
        description: finalDescription,
      });
      // Reset for next ingest
      setIngestCollectionId(generateCollectionName());
      setIngestCollectionName('');
      setIngestDescription('');
    } catch (error: any) {
      console.error('Ingest error:', error);
      setIngestProgress({ step: 'error', message: error.response?.data?.detail || error.message || '오류가 발생했습니다.' });
    } finally {
      setIngestLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Database className="w-6 h-6 text-orange-600" />
          <h2 className="text-xl font-semibold">VectorDB Ingest Mode</h2>
        </div>
        <p className="text-gray-600 mb-6">
          텍스트를 입력하면 전처리 → 청킹 → 임베딩 → 벡터 저장까지 한 번에 실행합니다.
        </p>

        <div className="grid grid-cols-2 gap-6">
          {/* Left Column - Settings */}
          <div className="space-y-4">
            {/* Text Input */}
            <div>
              <label className="block text-sm font-medium mb-1">Input</label>
              <textarea
                value={ingestText}
                onChange={(e) => setIngestText(e.target.value)}
                placeholder="벡터 데이터베이스에 저장할 텍스트를 입력하세요..."
                className="w-full h-40 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">{ingestText.length.toLocaleString()} 글자</p>
            </div>

            {/* Collection Name - Editable with auto-generate using Groq LLM */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium">Collection Name</label>
                <button
                  onClick={generateCollectionMeta}
                  disabled={!ingestText.trim() || isGeneratingMeta}
                  className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                  title="Groq LLM으로 영문 저장소명과 설명 자동 생성"
                >
                  {isGeneratingMeta ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>생성 중...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3 h-3" />
                      <span>자동 생성</span>
                    </>
                  )}
                </button>
              </div>
              <input
                type="text"
                value={ingestCollectionName}
                onChange={(e) => setIngestCollectionName(e.target.value)}
                placeholder={ingestCollectionId}
                className="w-full p-2 border rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">벡터를 저장할 컬렉션 이름 (문자, 숫자, 언더스코어만 사용)</p>
            </div>

            {/* Collection Description */}
            <div>
              <label className="block text-sm font-medium mb-1">Collection Description</label>
              <input
                type="text"
                value={ingestDescription}
                onChange={(e) => setIngestDescription(e.target.value)}
                placeholder="컬렉션에 대한 설명 (선택사항)"
                className="w-full p-2 border rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">관리 화면에서 표시될 설명입니다</p>
            </div>

            {/* Preprocessing Options */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium mb-2">전처리 옵션</p>
              <div className="flex space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={ingestUseCleaner}
                    onChange={(e) => setIngestUseCleaner(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">클리너</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={ingestUseNormalizer}
                    onChange={(e) => setIngestUseNormalizer(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">정규화</span>
                </label>
              </div>
            </div>

            {/* Chunking Options */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium mb-2">청킹 옵션</p>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">알고리즘</label>
                  <select
                    value={ingestChunkerType}
                    onChange={(e) => setIngestChunkerType(e.target.value)}
                    className="w-full p-2 border rounded text-sm"
                  >
                    <option value="fixed">Fixed</option>
                    <option value="semantic">Semantic</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">청크 크기</label>
                  <input
                    type="number"
                    value={ingestChunkSize}
                    onChange={(e) => setIngestChunkSize(Number(e.target.value))}
                    className="w-full p-2 border rounded text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">오버랩</label>
                  <input
                    type="number"
                    value={ingestChunkOverlap}
                    onChange={(e) => setIngestChunkOverlap(Number(e.target.value))}
                    className="w-full p-2 border rounded text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Embedding Options */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium mb-2">임베딩 옵션</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">임베더</label>
                  <select
                    value={ingestEmbedderType}
                    onChange={(e) => {
                      setIngestEmbedderType(e.target.value);
                      if (e.target.value === 'huggingface') {
                        setIngestEmbedModel('intfloat/multilingual-e5-base');
                      } else if (e.target.value === 'bge-m3') {
                        setIngestEmbedModel('BAAI/bge-m3');
                      } else if (e.target.value === 'openai') {
                        setIngestEmbedModel('text-embedding-3-small');
                      }
                    }}
                    className="w-full p-2 border rounded text-sm"
                  >
                    <option value="huggingface">HuggingFace</option>
                    <option value="bge-m3">BGE-M3</option>
                    <option value="openai">OpenAI</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">모델</label>
                  <select
                    value={ingestEmbedModel}
                    onChange={(e) => setIngestEmbedModel(e.target.value)}
                    className="w-full p-2 border rounded text-sm"
                  >
                    {ingestEmbedderType === 'huggingface' && (
                      <option value="intfloat/multilingual-e5-base">multilingual-e5-base</option>
                    )}
                    {ingestEmbedderType === 'bge-m3' && (
                      <option value="BAAI/bge-m3">bge-m3</option>
                    )}
                    {ingestEmbedderType === 'openai' && (
                      <>
                        <option value="text-embedding-3-small">text-embedding-3-small</option>
                        <option value="text-embedding-3-large">text-embedding-3-large</option>
                      </>
                    )}
                  </select>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleIngest}
              disabled={ingestLoading || !ingestText.trim()}
              className="w-full py-3 px-4 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {ingestLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Database className="w-5 h-5" />
              )}
              <span>{ingestLoading ? '처리 중...' : 'VectorDB에 저장'}</span>
            </button>
          </div>

          {/* Right Column - Progress & Result */}
          <div className="space-y-4">
            {/* Progress Indicator */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-4">진행 상태</h3>
              <div className="space-y-3">
                {['preprocess', 'chunk', 'embed', 'store'].map((step, idx) => {
                  const stepLabels: Record<string, string> = {
                    preprocess: '1. 전처리',
                    chunk: '2. 청킹',
                    embed: '3. 임베딩',
                    store: '4. 저장',
                  };
                  const isActive = ingestProgress.step === step;
                  const isDone = ['preprocess', 'chunk', 'embed', 'store', 'done'].indexOf(ingestProgress.step) > idx;

                  return (
                    <div key={step} className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isDone ? 'bg-green-100 text-green-600' :
                        isActive ? 'bg-orange-100 text-orange-600' :
                        'bg-gray-100 text-gray-400'
                      }`}>
                        {isDone ? (
                          <CheckCircle2 className="w-5 h-5" />
                        ) : isActive ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                      </div>
                      <span className={`text-sm ${isActive ? 'font-medium text-orange-600' : isDone ? 'text-green-600' : 'text-gray-500'}`}>
                        {stepLabels[step]}
                      </span>
                    </div>
                  );
                })}
              </div>

              {ingestProgress.step !== 'idle' && (
                <div className={`mt-4 p-3 rounded-lg ${
                  ingestProgress.step === 'done' ? 'bg-green-50 text-green-700' :
                  ingestProgress.step === 'error' ? 'bg-red-50 text-red-700' :
                  'bg-orange-50 text-orange-700'
                }`}>
                  <p className="text-sm">{ingestProgress.message}</p>
                  {ingestProgress.step === 'store' && ingestProgress.details?.totalVectors && (
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>배치 {ingestProgress.details.currentBatch}/{ingestProgress.details.totalBatches}</span>
                        <span>{ingestProgress.details.storedVectors}/{ingestProgress.details.totalVectors} 벡터</span>
                      </div>
                      <div className="w-full bg-orange-200 rounded-full h-2">
                        <div
                          className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(ingestProgress.details.storedVectors / ingestProgress.details.totalVectors) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Result */}
            {ingestResult && (
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-800">저장 완료!</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="bg-white p-2 rounded">
                    <p className="text-gray-500">Collection Name</p>
                    <p className="font-medium">{ingestResult.collectionName}</p>
                  </div>
                  {ingestResult.collectionId && (
                    <div className="bg-white p-2 rounded">
                      <p className="text-gray-500">저장소 ID</p>
                      <p className="font-mono text-xs text-gray-600">{ingestResult.collectionId}</p>
                    </div>
                  )}
                  {ingestResult.description && (
                    <div className="bg-white p-2 rounded">
                      <p className="text-gray-500">Collection Description</p>
                      <p className="text-gray-700 text-xs">{ingestResult.description}</p>
                    </div>
                  )}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-white p-2 rounded text-center">
                      <p className="text-gray-500 text-xs">청크</p>
                      <p className="font-medium">{ingestResult.chunks}개</p>
                    </div>
                    <div className="bg-white p-2 rounded text-center">
                      <p className="text-gray-500 text-xs">임베딩</p>
                      <p className="font-medium">{ingestResult.embeddings}개</p>
                    </div>
                    <div className="bg-white p-2 rounded text-center">
                      <p className="text-gray-500 text-xs">벡터</p>
                      <p className="font-medium">{ingestResult.stored}개</p>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  Query Mode에서 이 Collection을 선택하여 질문할 수 있습니다.
                </p>
              </div>
            )}

            {/* Error */}
            {ingestProgress.step === 'error' && (
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <span className="font-medium text-red-800">오류 발생</span>
                </div>
                <p className="text-sm text-red-700">{ingestProgress.message}</p>
              </div>
            )}

            {/* Help text when idle */}
            {ingestProgress.step === 'idle' && !ingestResult && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Info className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-blue-800">사용 방법</span>
                </div>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>1. 왼쪽에 저장할 텍스트를 입력하세요</li>
                  <li>2. Collection 이름과 옵션을 설정하세요</li>
                  <li>3. 'VectorDB에 저장' 버튼을 클릭하세요</li>
                  <li>4. 저장 완료 후 Query Mode에서 사용 가능합니다</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
