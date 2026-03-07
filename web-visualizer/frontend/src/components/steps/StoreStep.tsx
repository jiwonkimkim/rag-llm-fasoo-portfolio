import { Sparkles, Database, Loader2, Trash2, RefreshCw } from 'lucide-react';
import { StepResult } from '../../types';
import { BatchProgress } from '../../api';

interface StoreStepProps {
  chunkResult: StepResult | null;
  embedResult: StepResult | null;
  storeType: string;
  setStoreType: (value: string) => void;
  collectionId: string;  // Actual ID: rag_collection_YYYYMMDD_HHMMSS (hidden, auto-generated)
  collectionName: string;  // Display name (user editable or auto-generated)
  setCollectionName: (value: string) => void;
  collectionDescription: string;
  setCollectionDescription: (value: string) => void;
  isGeneratingMeta: boolean;
  storeProgress: BatchProgress | null;
  storedVectors: any[];
  storeStats: any;
  isLoading: boolean;
  result: StepResult | null;
  onRun: () => void;
  onRefresh: () => void;
  onClear: () => void;
  onGenerateMeta: () => void;
}

export default function StoreStep({
  chunkResult,
  embedResult,
  storeType,
  setStoreType,
  collectionId,
  collectionName,
  setCollectionName,
  collectionDescription,
  setCollectionDescription,
  isGeneratingMeta,
  storeProgress,
  storedVectors,
  storeStats,
  isLoading,
  result,
  onRun,
  onRefresh,
  onClear,
  onGenerateMeta,
}: StoreStepProps) {
  const chunksCount = chunkResult?.output?.chunks?.length || 0;
  const embeddingsCount = embedResult?.output?.embeddings?.length || 0;

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">저장할 데이터</p>
          <p className="text-gray-600">
            청크: {chunksCount}개 | 임베딩: {embeddingsCount}개
          </p>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Vector Store Type</label>
            <select
              value={storeType}
              onChange={(e) => setStoreType(e.target.value)}
              className="w-full p-2 border rounded-lg"
            >
              <option value="chroma">ChromaDB (로컬)</option>
              <option value="faiss">FAISS (로컬)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">ChromaDB: 간편한 로컬 저장, FAISS: 고성능 벡터 검색</p>
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium">저장소명 (Collection Name)</label>
              <button
                onClick={onGenerateMeta}
                disabled={isGeneratingMeta || !chunkResult}
                className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
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
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              className="w-full p-2 border rounded-lg"
              placeholder={collectionId}
            />
            <p className="text-xs text-gray-500 mt-1">
              벡터를 저장할 컬렉션 이름 (문자, 숫자, 언더스코어만 사용)
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              저장소 ID: {collectionId}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">저장소 설명 (Collection Description)</label>
            <textarea
              value={collectionDescription}
              onChange={(e) => setCollectionDescription(e.target.value)}
              className="w-full p-2 border rounded-lg resize-none"
              placeholder="컬렉션에 대한 설명 (선택사항, 자동생성 버튼으로 함께 생성)"
              rows={2}
            />
            <p className="text-xs text-gray-500 mt-1">컬렉션의 핵심 주제 및 내용 설명 (자동생성시 저장소명과 함께 생성됨)</p>
          </div>
        </div>
        {storeProgress && (
          <div className="mb-3 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between text-sm text-blue-700 mb-2">
              <span>저장 중... 배치 {storeProgress.currentBatch}/{storeProgress.totalBatches}</span>
              <span>{storeProgress.storedVectors}/{storeProgress.totalVectors} 벡터</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(storeProgress.storedVectors / storeProgress.totalVectors) * 100}%` }}
              />
            </div>
          </div>
        )}
        <div className="flex space-x-2">
          <button
            onClick={onRun}
            disabled={!embedResult || isLoading}
            className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Database className="w-5 h-5" />}
            <span>{storeProgress ? `${storeProgress.currentBatch}/${storeProgress.totalBatches} 배치 저장 중...` : 'Store Vectors'}</span>
          </button>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={onClear}
            disabled={isLoading}
            className="py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Stored Vectors</h3>
        {storeStats && (
          <div className="flex space-x-4 mb-3">
            <div className="p-3 bg-indigo-50 rounded-lg flex-1 text-center">
              <p className="text-2xl font-bold text-indigo-600">{storeStats.total_count}</p>
              <p className="text-sm text-indigo-600">Total Vectors</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg flex-1 text-center">
              <p className="text-lg font-bold text-gray-600">{storeStats.collection_name}</p>
              <p className="text-sm text-gray-500">Collection</p>
            </div>
          </div>
        )}
        {result && (
          <div className="p-3 bg-green-50 rounded-lg mb-3">
            <p className="text-sm text-green-600">
              {result.output.totalStored || result.output.stored_count}개 벡터 저장 완료
            </p>
          </div>
        )}
        <div className="h-48 overflow-auto space-y-2">
          {storedVectors.length > 0 ? (
            storedVectors.map((vec: any, i: number) => (
              <div key={vec.id || i} className="p-2 bg-gray-50 rounded text-sm">
                <div className="flex justify-between items-start">
                  <span className="text-indigo-600 font-mono text-xs">{vec.id?.substring(0, 8)}...</span>
                  <span className="text-xs text-gray-400">#{i + 1}</span>
                </div>
                <p className="text-gray-600 mt-1 text-xs">{vec.content?.substring(0, 100)}...</p>
              </div>
            ))
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
              저장된 벡터가 없습니다
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
