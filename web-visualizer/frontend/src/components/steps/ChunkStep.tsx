import { PlayCircle, Loader2 } from 'lucide-react';
import { StepResult } from '../../types';

interface ChunkStepProps {
  preprocessResult: StepResult | null;
  chunkerType: string;
  setChunkerType: (value: string) => void;
  chunkSize: number;
  setChunkSize: (value: number) => void;
  chunkOverlap: number;
  setChunkOverlap: (value: number) => void;
  isLoading: boolean;
  result: StepResult | null;
  onRun: () => void;
}

export default function ChunkStep({
  preprocessResult,
  chunkerType,
  setChunkerType,
  chunkSize,
  setChunkSize,
  chunkOverlap,
  setChunkOverlap,
  isLoading,
  result,
  onRun,
}: ChunkStepProps) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <div className="p-3 bg-gray-50 rounded-lg h-32 overflow-auto">
          <p className="text-sm text-gray-600">
            {preprocessResult?.output?.final || '이전 단계를 먼저 실행하세요'}
          </p>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Chunker Type</label>
            <select
              value={chunkerType}
              onChange={(e) => setChunkerType(e.target.value)}
              className="w-full p-2 border rounded-lg"
            >
              <option value="fixed">Fixed</option>
              <option value="semantic">Semantic</option>
            </select>
            <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
              {chunkerType === 'fixed' ? (
                <p><strong>Fixed:</strong> 고정 길이로 분할. 빠르고 단순하며, 문장 경계에서 자르려고 시도합니다.</p>
              ) : (
                <p><strong>Semantic:</strong> 의미 단위로 분할. 문맥을 고려해 더 자연스러운 청크를 생성하지만 속도가 느립니다.</p>
              )}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Chunk Size: {chunkSize}</label>
            <input
              type="range"
              min="100"
              max="2000"
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">
              <span className="text-blue-600 font-medium">추천: 500~1000자</span>
              <span className="ml-2">| 작으면 문맥 손실, 크면 검색 정확도 저하</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Overlap: {chunkOverlap}</label>
            <input
              type="range"
              min="0"
              max="200"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              {chunkerType === 'fixed'
                ? '인접 청크 간 겹치는 문자 수 (문자 단위)'
                : '인접 청크 간 겹치는 문장 길이 (문장 단위로 계산)'}
            </p>
          </div>
        </div>
        <button
          onClick={onRun}
          disabled={!preprocessResult || isLoading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <PlayCircle className="w-5 h-5" />}
          <span>Run Chunker</span>
        </button>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Output</h3>
        {result ? (
          <div className="space-y-3">
            <div className="flex space-x-4">
              <div className="p-3 bg-green-50 rounded-lg flex-1 text-center">
                <p className="text-2xl font-bold text-green-600">{result.output.chunk_count}</p>
                <p className="text-sm text-green-600">Chunks</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg flex-1 text-center">
                <p className="text-2xl font-bold text-blue-600">{Math.round(result.output.avg_chunk_size)}</p>
                <p className="text-sm text-blue-600">Avg Size</p>
              </div>
            </div>
            <div className="h-64 overflow-auto space-y-2">
              {result.output.chunks?.map((chunk: string, i: number) => (
                <div key={i} className="p-2 bg-gray-50 rounded text-sm">
                  <span className="font-medium text-blue-600">Chunk {i + 1}:</span>
                  <p className="text-gray-600 mt-1">{chunk.substring(0, 150)}...</p>
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
