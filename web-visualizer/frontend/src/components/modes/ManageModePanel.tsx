import { Settings, RefreshCw, Loader2, Database, Trash2, Hash, Info, FileText, Calendar, Scissors, Eye } from 'lucide-react';
import { CollectionInfo } from '../../types';

interface ManageModePanelProps {
  collections: CollectionInfo[];
  selectedManageCollection: string | null;
  setSelectedManageCollection: (name: string | null) => void;
  manageLoading: boolean;
  loadCollections: () => Promise<void>;
  deleteCollection: (name: string) => Promise<void>;
}

export default function ManageModePanel({
  collections,
  selectedManageCollection,
  setSelectedManageCollection,
  manageLoading,
  loadCollections,
  deleteCollection,
}: ManageModePanelProps) {
  const selectedCol = collections.find(c => c.name === selectedManageCollection);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Settings className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-semibold">벡터 저장소 관리</h2>
          </div>
          <button
            onClick={loadCollections}
            disabled={manageLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50"
          >
            {manageLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            <span>새로고침</span>
          </button>
        </div>

        {collections.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Database className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg">저장된 벡터 저장소가 없습니다.</p>
            <p className="text-sm mt-2">Pipeline Mode에서 데이터를 저장하세요.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Collection List */}
            <div className="space-y-3">
              <h3 className="font-medium text-gray-700 mb-3">저장소 목록 ({collections.length}개)</h3>
              <div className="space-y-2 max-h-[600px] overflow-auto">
                {collections.map((col) => (
                  <div
                    key={col.name}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedManageCollection === col.name
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedManageCollection(col.name)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Database className="w-4 h-4 text-purple-500" />
                          <span className="font-medium text-gray-800">{col.display_name || col.name}</span>
                        </div>
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Hash className="w-3 h-3" />
                            {col.count}개 벡터
                          </span>
                          {col.embedder_type && (
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                              {col.embedder_type}
                            </span>
                          )}
                          {col.prep_store_type && (
                            <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                              {col.prep_store_type}
                            </span>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteCollection(col.name);
                        }}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="삭제"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Collection Details */}
            <div>
              {selectedCol ? (
                <div className="border rounded-lg p-5 bg-gray-50">
                  <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <Info className="w-5 h-5 text-purple-600" />
                    상세 정보
                  </h3>

                  {/* 기본 정보 */}
                  <div className="mb-5">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      기본 정보
                    </h4>
                    <div className="bg-white rounded-lg p-3 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">저장소명</span>
                        <span className="font-medium">{selectedCol.display_name || selectedCol.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">저장소 ID</span>
                        <span className="font-mono text-xs">{selectedCol.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">설명</span>
                        <span>{selectedCol.description || '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">임베딩 모델</span>
                        <span className="text-blue-600">{selectedCol.model_name || '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">prepStoreType</span>
                        <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{selectedCol.prep_store_type || 'legacy'}</span>
                      </div>
                      {selectedCol.created_at && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">생성일시</span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(selectedCol.created_at).toLocaleString('ko-KR')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 청킹 옵션 */}
                  <div className="mb-5">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <Scissors className="w-4 h-4" />
                      청킹 옵션
                    </h4>
                    <div className="bg-white rounded-lg p-3 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">청킹 알고리즘</span>
                        <span className="font-mono text-xs">{selectedCol.chunking_algorithm || '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">청크 사이즈</span>
                        <span>{selectedCol.chunk_size ?? '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">오버랩 사이즈</span>
                        <span>{selectedCol.chunk_overlap ?? '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">추가 본문 길이</span>
                        <span>{selectedCol.extra_body_length ?? '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">최소 그룹 사이즈</span>
                        <span>{selectedCol.min_chunk_group_size ?? '-'}</span>
                      </div>
                    </div>
                  </div>

                  {/* 청킹 통계 */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <Hash className="w-4 h-4" />
                      청킹 통계
                    </h4>
                    <div className="bg-white rounded-lg p-3 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">총 청킹 건수</span>
                        <span className="font-medium text-purple-600">{selectedCol.total_chunks ?? selectedCol.count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">전체 문서</span>
                        <span>{selectedCol.total_documents ?? '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">성공</span>
                        <span className="text-green-600">{selectedCol.success_documents ?? '-'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">실패</span>
                        <span className="text-red-600">{selectedCol.failed_documents ?? '-'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="border-2 border-dashed rounded-lg p-8 text-center text-gray-400 h-full flex flex-col items-center justify-center">
                  <Eye className="w-12 h-12 mb-3 opacity-50" />
                  <p>왼쪽 목록에서 저장소를 선택하면</p>
                  <p>상세 정보를 확인할 수 있습니다.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
