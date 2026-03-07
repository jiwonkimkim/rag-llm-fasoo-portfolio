import { PlayCircle, Loader2, Binary, Search, Sparkles, Eye, X } from 'lucide-react';
import { StepResult } from '../../types';

interface RetrieveStepProps {
  retrieveQuery: string;
  setRetrieveQuery: (value: string) => void;
  collectionId: string;  // Actual ID: rag_collection_YYYYMMDD_HHMMSS (used for API)
  collectionName: string;  // Display name
  embedderType: string;
  embedResult: StepResult | null;
  retrieverType: string;
  setRetrieverType: (value: string) => void;
  topK: number;
  setTopK: (value: number) => void;
  denseWeight: number;
  setDenseWeight: (value: number) => void;
  isLoading: boolean;
  result: StepResult | null;
  selectedResult: any;
  setSelectedResult: (value: any) => void;
  onRun: () => void;
}

export default function RetrieveStep({
  retrieveQuery,
  setRetrieveQuery,
  collectionId,
  collectionName,
  embedderType,
  embedResult,
  retrieverType,
  setRetrieverType,
  topK,
  setTopK,
  denseWeight,
  setDenseWeight,
  isLoading,
  result,
  selectedResult,
  setSelectedResult,
  onRun,
}: RetrieveStepProps) {
  // 사용할 임베더 결정
  const currentEmbedderType = embedResult?.input?.embedderType || embedderType;
  const embedderLabel = currentEmbedderType === 'openai' ? 'OpenAI' :
                        currentEmbedderType === 'bge-m3' ? 'BGE-M3' :
                        currentEmbedderType === 'huggingface' ? 'HuggingFace' : 'HuggingFace';

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <div>
          <label className="block text-sm font-medium mb-1">검색 쿼리</label>
          <textarea
            className="w-full h-20 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="벡터 DB에서 유사한 문서를 검색할 질문을 입력하세요..."
            value={retrieveQuery}
            onChange={(e) => setRetrieveQuery(e.target.value)}
          />
        </div>
        <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
          <label className="block text-sm font-medium mb-1 text-indigo-800">검색할 Collection</label>
          <p className="text-sm text-indigo-700 font-medium">
            {collectionName || collectionId}
          </p>
          <p className="text-xs text-indigo-500 mt-1">
            저장소 ID: {collectionId}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Store 단계에서 설정된 컬렉션에서 검색합니다.
          </p>
        </div>
        {/* 임베더 자동 선택 안내 */}
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Binary className="w-4 h-4 text-amber-600" />
            <span className="text-sm font-medium text-amber-800">사용할 임베더</span>
          </div>
          <p className="text-sm text-amber-700 font-medium">
            {embedderLabel}
            {embedResult && <span className="ml-1 text-amber-600">(Embed 단계에서 자동 설정됨)</span>}
          </p>
          <p className="text-xs text-amber-600 mt-1">
            검색 시 저장된 벡터와 동일한 임베더를 사용해야 정확한 결과를 얻을 수 있습니다.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">Retriever Type</label>
            <select
              value={retrieverType}
              onChange={(e) => setRetrieverType(e.target.value)}
              className="w-full p-2 border rounded-lg"
            >
              <option value="dense">Dense (벡터 유사도)</option>
              <option value="sparse">Sparse (BM25 키워드)</option>
              <option value="hybrid">Hybrid (Dense + Sparse)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Top K: {topK}</label>
            <input
              type="range"
              min="1"
              max="20"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full mt-2"
            />
          </div>
        </div>

        {/* 알고리즘 설명 섹션 */}
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
          {retrieverType === 'dense' && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <Binary className="w-4 h-4 text-purple-600" />
                </div>
                <h4 className="font-semibold text-purple-800">Dense Retriever (벡터 유사도 검색)</h4>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-green-700 font-medium">✓ 장점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 의미적 유사성 파악 (동의어 인식)</li>
                    <li>• 자연어 질문에 강함</li>
                    <li>• 문맥 기반 검색 가능</li>
                  </ul>
                </div>
                <div>
                  <p className="text-red-700 font-medium">✗ 단점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 임베딩 모델 품질에 의존</li>
                    <li>• 정확한 키워드 매칭 약함</li>
                    <li>• API 비용 발생 가능</li>
                  </ul>
                </div>
              </div>
              <details className="mt-2">
                <summary className="cursor-pointer text-sm font-medium text-purple-700 hover:text-purple-900">
                  📄 핵심 코드 보기
                </summary>
                <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded text-xs overflow-x-auto">
{`def retrieve(self, query: str) -> list[RetrievalResult]:
    # 1. 쿼리 → 임베딩 벡터 변환
    query_embedding = self.embedder.embed(query)

    # 2. 벡터 저장소에서 유사도 검색
    results = self.vectorstore.search(
        query_embedding,
        top_k=self.top_k
    )

    # 3. RetrievalResult로 변환하여 반환
    return [RetrievalResult(
        content=r.content,
        score=r.score,  # 코사인 유사도
        ...
    ) for r in results]`}
                </pre>
              </details>
            </div>
          )}

          {retrieverType === 'sparse' && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  <Search className="w-4 h-4 text-orange-600" />
                </div>
                <h4 className="font-semibold text-orange-800">Sparse Retriever (BM25 키워드 검색)</h4>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-green-700 font-medium">✓ 장점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 정확한 키워드 매칭</li>
                    <li>• 빠른 검색 속도</li>
                    <li>• 외부 API 불필요 (무료)</li>
                  </ul>
                </div>
                <div>
                  <p className="text-red-700 font-medium">✗ 단점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 동의어/유사어 인식 불가</li>
                    <li>• 의미적 유사성 무시</li>
                    <li>• 오타에 민감</li>
                  </ul>
                </div>
              </div>
              <div className="mt-2 p-2 bg-orange-50 rounded text-xs">
                <span className="font-medium text-orange-700">BM25 공식:</span>
                <span className="text-gray-600 ml-2">score = TF(단어빈도) × IDF(역문서빈도) × 길이정규화</span>
              </div>
              <details className="mt-2">
                <summary className="cursor-pointer text-sm font-medium text-orange-700 hover:text-orange-900">
                  📄 핵심 코드 보기
                </summary>
                <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded text-xs overflow-x-auto">
{`def retrieve(self, query: str) -> list[RetrievalResult]:
    # 1. 쿼리 토큰화
    tokenized_query = self._tokenize(query)

    # 2. BM25 점수 계산 (TF-IDF 기반)
    scores = self.bm25.get_scores(tokenized_query)

    # 3. 점수 기준 상위 K개 선택
    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:self.top_k]

    # 4. 점수 > 0인 결과만 반환
    return [RetrievalResult(...)
            for idx in top_indices
            if scores[idx] > 0]`}
                </pre>
              </details>
            </div>
          )}

          {retrieverType === 'hybrid' && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                </div>
                <h4 className="font-semibold text-blue-800">Hybrid Retriever (Dense + Sparse 결합)</h4>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-green-700 font-medium">✓ 장점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 의미 + 키워드 동시 활용</li>
                    <li>• 가장 안정적인 성능</li>
                    <li>• 가중치로 성향 조절 가능</li>
                  </ul>
                </div>
                <div>
                  <p className="text-red-700 font-medium">✗ 단점</p>
                  <ul className="text-gray-600 text-xs mt-1 space-y-1">
                    <li>• 두 검색기 모두 필요</li>
                    <li>• 연산량 증가</li>
                    <li>• 가중치 튜닝 필요</li>
                  </ul>
                </div>
              </div>
              <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                <span className="font-medium text-blue-700">RRF 공식:</span>
                <span className="text-gray-600 ml-2">score = Σ (weight / (k + rank + 1)), k=60</span>
              </div>
              <details className="mt-2">
                <summary className="cursor-pointer text-sm font-medium text-blue-700 hover:text-blue-900">
                  📄 핵심 코드 보기
                </summary>
                <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded text-xs overflow-x-auto">
{`def retrieve(self, query: str) -> list[RetrievalResult]:
    # 1. 각 검색기에서 결과 가져오기
    dense_results = self.dense_retriever.retrieve(query)
    sparse_results = self.sparse_retriever.retrieve(query)

    # 2. RRF (Reciprocal Rank Fusion)로 점수 결합
    combined = {}
    for rank, r in enumerate(dense_results):
        combined[r.content]["score"] += \\
            dense_weight / (60 + rank + 1)
    for rank, r in enumerate(sparse_results):
        combined[r.content]["score"] += \\
            sparse_weight / (60 + rank + 1)

    # 3. 결합 점수로 정렬 후 반환
    return sorted(combined, key=score, reverse=True)`}
                </pre>
              </details>
            </div>
          )}
        </div>

        {retrieverType === 'hybrid' && (
          <div>
            <label className="block text-sm font-medium mb-1">
              Dense Weight: {denseWeight.toFixed(2)} | Sparse Weight: {(1 - denseWeight).toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={denseWeight}
              onChange={(e) => setDenseWeight(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>← 키워드 중심</span>
              <span>의미 중심 →</span>
            </div>
          </div>
        )}
        <button
          onClick={onRun}
          disabled={!retrieveQuery.trim() || isLoading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <PlayCircle className="w-5 h-5" />}
          <span>Run Retriever</span>
        </button>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Output</h3>
        {result ? (
          <div className="h-72 overflow-auto space-y-2">
            {result.output.results?.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
                검색 결과가 없습니다. 먼저 Store 단계에서 벡터를 저장하세요.
              </div>
            ) : (
              result.output.results?.map((r: any, i: number) => (
                <div
                  key={i}
                  className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors border border-transparent hover:border-blue-200"
                  onClick={() => setSelectedResult(r)}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-blue-600 flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      Result {i + 1}
                    </span>
                    <span className="text-sm bg-green-100 text-green-700 px-2 py-0.5 rounded">
                      Score: {r.score?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">{r.content?.substring(0, 150)}...</p>
                  <p className="text-xs text-blue-500 mt-1">클릭하여 전체 내용 보기</p>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
            결과가 여기에 표시됩니다
          </div>
        )}
      </div>

      {/* Result Detail Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-xl">
            <div className="flex justify-between items-center p-4 border-b bg-blue-50">
              <h3 className="font-semibold text-lg text-blue-800">검색 결과 상세</h3>
              <button
                onClick={() => setSelectedResult(null)}
                className="p-1 hover:bg-blue-100 rounded"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[60vh]">
              <div className="mb-4">
                <span className="text-sm font-medium text-gray-500">유사도 점수</span>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(selectedResult.score || 0) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold text-green-600">{(selectedResult.score || 0).toFixed(4)}</span>
                </div>
              </div>
              <div className="mb-4">
                <span className="text-sm font-medium text-gray-500">메타데이터</span>
                <div className="mt-1 p-2 bg-gray-50 rounded text-xs font-mono">
                  {JSON.stringify(selectedResult.metadata || {}, null, 2)}
                </div>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">전체 내용</span>
                <div className="mt-1 p-3 bg-gray-50 rounded-lg whitespace-pre-wrap text-sm text-gray-800">
                  {selectedResult.content}
                </div>
              </div>
            </div>
            <div className="p-4 border-t bg-gray-50 flex justify-end">
              <button
                onClick={() => setSelectedResult(null)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
