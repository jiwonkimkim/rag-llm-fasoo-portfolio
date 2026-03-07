import { useState, useEffect } from 'react';
import {
  Search,
  Download,
  Trash2,
  CheckSquare,
  Square,
  RefreshCw,
  ShoppingCart,
  Image as ImageIcon,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { api } from '../../api';
import { ProductResult, CollectedImage, CollectProgress } from '../../types';

interface CollectModePanelProps {}

export default function CollectModePanel(_props: CollectModePanelProps) {
  // State
  const [keyword, setKeyword] = useState('');
  const [sources, setSources] = useState<string[]>(['coupang', 'naver']);
  const [maxResults, setMaxResults] = useState(20);
  const [demoMode, setDemoMode] = useState(true); // 기본값: 데모 모드 활성화
  const [searchResults, setSearchResults] = useState<ProductResult[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set());
  const [collectedImages, setCollectedImages] = useState<CollectedImage[]>([]);
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [progress, setProgress] = useState<CollectProgress>({ step: 'idle', message: '' });
  const [activeTab, setActiveTab] = useState<'search' | 'gallery'>('search');
  const [totalImages, setTotalImages] = useState(0);

  // 갤러리 탭 로드
  useEffect(() => {
    if (activeTab === 'gallery') {
      loadGallery();
    }
  }, [activeTab]);

  // 검색 핸들러
  const handleSearch = async () => {
    if (!keyword.trim()) {
      alert('검색 키워드를 입력해주세요.');
      return;
    }

    setProgress({ step: 'searching', message: '상품 검색 중...' });
    setSearchResults([]);
    setSelectedProducts(new Set());

    try {
      const response = await api.collectSearch({
        keyword,
        sources,
        maxResults,
        demo_mode: demoMode,
      });

      setSearchResults(response.data.products);

      // 에러 메시지 처리
      const errors = response.data.errors || {};
      const errorMessages = Object.entries(errors)
        .map(([source, msg]) => `${source}: ${msg}`)
        .join('\n');

      if (Object.keys(errors).length > 0 && response.data.total_count === 0) {
        // 모든 소스에서 에러 발생
        setProgress({
          step: 'error',
          message: `검색 실패\n${errorMessages}`,
        });
      } else if (Object.keys(errors).length > 0) {
        // 일부 소스에서 에러 발생
        setProgress({
          step: 'done',
          message: `${response.data.total_count}개 상품 발견 (일부 에러: ${Object.keys(errors).join(', ')})`,
        });
        // 콘솔에 상세 에러 출력
        console.warn('일부 소스에서 에러 발생:', errors);
      } else {
        setProgress({
          step: 'done',
          message: `${response.data.total_count}개 상품 발견`,
        });
      }
    } catch (error: any) {
      console.error('Search error:', error);
      setProgress({
        step: 'error',
        message: error.response?.data?.detail || '검색 실패',
      });
    }
  };

  // 다운로드 핸들러
  const handleDownload = async () => {
    const selected = searchResults.filter((p) =>
      selectedProducts.has(p.product_id)
    );

    if (selected.length === 0) {
      alert('다운로드할 상품을 선택해주세요.');
      return;
    }

    setProgress({
      step: 'downloading',
      message: `${selected.length}개 이미지 다운로드 중...`,
    });

    try {
      const response = await api.collectDownload({
        products: selected.map((p) => ({
          product_id: p.product_id,
          title: p.title,
          price: p.price,
          image_url: p.image_url,
          detail_url: p.detail_url,
          source: p.source,
          rating: p.rating,
          review_count: p.review_count,
        })),
      });

      setProgress({
        step: 'done',
        message: `${response.data.downloaded_count}개 다운로드 완료, ${response.data.failed_count}개 실패`,
      });

      // 갤러리 새로고침
      if (activeTab === 'gallery') {
        loadGallery();
      }
    } catch (error: any) {
      console.error('Download error:', error);
      setProgress({
        step: 'error',
        message: error.response?.data?.detail || '다운로드 실패',
      });
    }
  };

  // 갤러리 로드
  const loadGallery = async () => {
    try {
      const response = await api.listCollectedImages({
        page: 1,
        pageSize: 100,
      });

      setCollectedImages(response.data.images);
      setTotalImages(response.data.total_count);
    } catch (error) {
      console.error('Failed to load gallery:', error);
    }
  };

  // 이미지 삭제
  const handleDelete = async () => {
    if (selectedImages.size === 0) {
      alert('삭제할 이미지를 선택해주세요.');
      return;
    }

    if (!confirm(`${selectedImages.size}개 이미지를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await api.deleteCollectedImages({
        imageIds: Array.from(selectedImages),
      });

      setSelectedImages(new Set());
      loadGallery();
    } catch (error) {
      console.error('Delete error:', error);
      alert('삭제 실패');
    }
  };

  // 상품 선택 토글
  const toggleProduct = (productId: string) => {
    const newSelected = new Set(selectedProducts);
    if (newSelected.has(productId)) {
      newSelected.delete(productId);
    } else {
      newSelected.add(productId);
    }
    setSelectedProducts(newSelected);
  };

  // 이미지 선택 토글
  const toggleImage = (imageId: string) => {
    const newSelected = new Set(selectedImages);
    if (newSelected.has(imageId)) {
      newSelected.delete(imageId);
    } else {
      newSelected.add(imageId);
    }
    setSelectedImages(newSelected);
  };

  // 전체 선택
  const selectAllProducts = () => {
    if (selectedProducts.size === searchResults.length) {
      setSelectedProducts(new Set());
    } else {
      setSelectedProducts(new Set(searchResults.map((p) => p.product_id)));
    }
  };

  const selectAllImages = () => {
    if (selectedImages.size === collectedImages.length) {
      setSelectedImages(new Set());
    } else {
      setSelectedImages(new Set(collectedImages.map((img) => img.id)));
    }
  };

  // 소스 토글
  const toggleSource = (source: string) => {
    if (sources.includes(source)) {
      if (sources.length > 1) {
        setSources(sources.filter((s) => s !== source));
      }
    } else {
      setSources([...sources, source]);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ShoppingCart className="w-6 h-6 text-white" />
              <h2 className="text-xl font-semibold text-white">Collect Mode</h2>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('search')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'search'
                    ? 'bg-white text-indigo-700'
                    : 'bg-indigo-500 text-white hover:bg-indigo-400'
                }`}
              >
                <Search className="w-4 h-4 inline mr-2" />
                검색
              </button>
              <button
                onClick={() => setActiveTab('gallery')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'gallery'
                    ? 'bg-white text-indigo-700'
                    : 'bg-indigo-500 text-white hover:bg-indigo-400'
                }`}
              >
                <ImageIcon className="w-4 h-4 inline mr-2" />
                갤러리 ({totalImages})
              </button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {progress.step !== 'idle' && (
          <div
            className={`px-6 py-3 flex items-center space-x-3 ${
              progress.step === 'error'
                ? 'bg-red-50 text-red-700'
                : progress.step === 'done'
                ? 'bg-green-50 text-green-700'
                : 'bg-blue-50 text-blue-700'
            }`}
          >
            {progress.step === 'searching' || progress.step === 'downloading' ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : progress.step === 'error' ? (
              <AlertCircle className="w-5 h-5" />
            ) : (
              <CheckCircle2 className="w-5 h-5" />
            )}
            <span>{progress.message}</span>
          </div>
        )}

        <div className="p-6">
          {activeTab === 'search' ? (
            // 검색 탭
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* 왼쪽: 검색 설정 */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    검색 키워드
                  </label>
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="예: 노트북 가방"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    쇼핑몰 선택
                  </label>
                  <div className="flex space-x-3">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={sources.includes('coupang')}
                        onChange={() => toggleSource('coupang')}
                        className="w-4 h-4 text-indigo-600 rounded"
                      />
                      <span className="text-sm">쿠팡</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={sources.includes('naver')}
                        onChange={() => toggleSource('naver')}
                        className="w-4 h-4 text-indigo-600 rounded"
                      />
                      <span className="text-sm">네이버</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    최대 결과 수
                  </label>
                  <select
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  >
                    <option value={10}>10개</option>
                    <option value={20}>20개</option>
                    <option value={50}>50개</option>
                    <option value={100}>100개</option>
                  </select>
                </div>

                {/* 데모 모드 토글 */}
                <div className="flex items-center space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <input
                    type="checkbox"
                    id="demoMode"
                    checked={demoMode}
                    onChange={(e) => setDemoMode(e.target.checked)}
                    className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <label htmlFor="demoMode" className="text-sm text-gray-700">
                    <span className="font-medium">데모 모드</span>
                    <span className="text-gray-500 ml-1">
                      (테스트용 mock 데이터 사용)
                    </span>
                  </label>
                </div>
                {!demoMode && (
                  <div className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                    실제 크롤링은 IP 차단으로 인해 결과가 없을 수 있습니다.
                    브라우저 창이 열립니다.
                  </div>
                )}

                <button
                  onClick={handleSearch}
                  disabled={progress.step === 'searching'}
                  className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 flex items-center justify-center space-x-2"
                >
                  {progress.step === 'searching' ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                  <span>검색</span>
                </button>

                {searchResults.length > 0 && (
                  <>
                    <div className="border-t pt-4">
                      <div className="flex items-center justify-between mb-3">
                        <button
                          onClick={selectAllProducts}
                          className="text-sm text-indigo-600 hover:text-indigo-800"
                        >
                          {selectedProducts.size === searchResults.length
                            ? '전체 해제'
                            : '전체 선택'}
                        </button>
                        <span className="text-sm text-gray-500">
                          {selectedProducts.size}개 선택
                        </span>
                      </div>
                      <button
                        onClick={handleDownload}
                        disabled={
                          selectedProducts.size === 0 ||
                          progress.step === 'downloading'
                        }
                        className="w-full py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center space-x-2"
                      >
                        {progress.step === 'downloading' ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <Download className="w-5 h-5" />
                        )}
                        <span>다운로드</span>
                      </button>
                    </div>
                  </>
                )}
              </div>

              {/* 오른쪽: 검색 결과 */}
              <div className="lg:col-span-3">
                {searchResults.length === 0 ? (
                  <div className="text-center py-16 text-gray-500">
                    <ShoppingCart className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p>키워드를 입력하고 검색 버튼을 눌러주세요.</p>
                    <p className="text-sm mt-2">
                      쿠팡과 네이버 쇼핑에서 상품을 검색합니다.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                    {searchResults.map((product) => (
                      <div
                        key={product.product_id}
                        onClick={() => toggleProduct(product.product_id)}
                        className={`relative border rounded-lg overflow-hidden cursor-pointer transition-all ${
                          selectedProducts.has(product.product_id)
                            ? 'ring-2 ring-indigo-500 border-indigo-500'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {/* 체크박스 */}
                        <div className="absolute top-2 left-2 z-10">
                          {selectedProducts.has(product.product_id) ? (
                            <CheckSquare className="w-6 h-6 text-indigo-600 bg-white rounded" />
                          ) : (
                            <Square className="w-6 h-6 text-gray-400 bg-white rounded" />
                          )}
                        </div>

                        {/* 소스 뱃지 */}
                        <div className="absolute top-2 right-2 z-10">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${
                              product.source === 'coupang'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-green-100 text-green-700'
                            }`}
                          >
                            {product.source === 'coupang' ? '쿠팡' : '네이버'}
                          </span>
                        </div>

                        {/* 이미지 */}
                        <div className="aspect-square bg-gray-100">
                          {product.image_url ? (
                            <img
                              src={product.image_url}
                              alt={product.title}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                (e.target as HTMLImageElement).src =
                                  'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23f3f4f6"/%3E%3C/svg%3E';
                              }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <ImageIcon className="w-12 h-12 text-gray-300" />
                            </div>
                          )}
                        </div>

                        {/* 정보 */}
                        <div className="p-3">
                          <h3 className="text-sm font-medium text-gray-900 line-clamp-2 mb-1">
                            {product.title}
                          </h3>
                          <p className="text-sm font-bold text-indigo-600">
                            {product.price}
                          </p>
                          {product.rating && (
                            <p className="text-xs text-gray-500 mt-1">
                              평점: {product.rating}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            // 갤러리 탭
            <div>
              {/* 툴바 */}
              <div className="flex items-center justify-between mb-4 pb-4 border-b">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={selectAllImages}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    {selectedImages.size === collectedImages.length &&
                    collectedImages.length > 0
                      ? '전체 해제'
                      : '전체 선택'}
                  </button>
                  <span className="text-sm text-gray-500">
                    {selectedImages.size}개 선택 / 총 {totalImages}개
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={loadGallery}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 flex items-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>새로고침</span>
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={selectedImages.size === 0}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 flex items-center space-x-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>삭제</span>
                  </button>
                </div>
              </div>

              {/* 이미지 그리드 */}
              {collectedImages.length === 0 ? (
                <div className="text-center py-16 text-gray-500">
                  <ImageIcon className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p>수집된 이미지가 없습니다.</p>
                  <p className="text-sm mt-2">
                    검색 탭에서 상품을 검색하고 다운로드해주세요.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                  {collectedImages.map((image) => (
                    <div
                      key={image.id}
                      onClick={() => toggleImage(image.id)}
                      className={`relative aspect-square rounded-lg overflow-hidden cursor-pointer transition-all ${
                        selectedImages.has(image.id)
                          ? 'ring-2 ring-indigo-500'
                          : 'hover:opacity-90'
                      }`}
                    >
                      {/* 체크박스 */}
                      <div className="absolute top-1 left-1 z-10">
                        {selectedImages.has(image.id) ? (
                          <CheckSquare className="w-5 h-5 text-indigo-600 bg-white rounded" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-400 bg-white/80 rounded" />
                        )}
                      </div>

                      {/* 소스 뱃지 */}
                      <div className="absolute top-1 right-1 z-10">
                        <span
                          className={`px-1.5 py-0.5 text-xs font-medium rounded ${
                            image.source === 'coupang'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          {image.source === 'coupang' ? 'C' : 'N'}
                        </span>
                      </div>

                      {/* 이미지 */}
                      <img
                        src={api.getCollectedImageUrl(image.id)}
                        alt={image.product_title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src =
                            'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23f3f4f6"/%3E%3C/svg%3E';
                        }}
                      />

                      {/* 호버 정보 */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-2 text-white text-xs">
                        <p className="line-clamp-2 text-center mb-1">
                          {image.product_title}
                        </p>
                        <p className="text-gray-300">{image.size_kb.toFixed(1)} KB</p>
                        <a
                          href={image.original_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="mt-1 text-indigo-300 hover:text-indigo-200"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
