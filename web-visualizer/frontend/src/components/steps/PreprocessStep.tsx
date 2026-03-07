import { PlayCircle, Loader2 } from 'lucide-react';
import { StepResult } from '../../types';

interface PreprocessStepProps {
  preprocessInput: string;
  setPreprocessInput: (value: string) => void;
  useCleaner: boolean;
  setUseCleaner: (value: boolean) => void;
  useNormalizer: boolean;
  setUseNormalizer: (value: boolean) => void;
  isLoading: boolean;
  result: StepResult | null;
  onRun: () => void;
}

export default function PreprocessStep({
  preprocessInput,
  setPreprocessInput,
  useCleaner,
  setUseCleaner,
  useNormalizer,
  setUseNormalizer,
  isLoading,
  result,
  onRun,
}: PreprocessStepProps) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <textarea
          className="w-full h-48 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="전처리할 텍스트를 입력하세요..."
          value={preprocessInput}
          onChange={(e) => setPreprocessInput(e.target.value)}
        />
        <div className="space-y-3">
          <div className="p-3 bg-gray-50 rounded-lg">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={useCleaner}
                onChange={(e) => setUseCleaner(e.target.checked)}
                className="rounded"
              />
              <span className="font-medium">Cleaner 사용</span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">HTML 태그, URL, 이메일, 특수문자 제거 및 공백 정규화</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={useNormalizer}
                onChange={(e) => setUseNormalizer(e.target.checked)}
                className="rounded"
              />
              <span className="font-medium">Normalizer 사용</span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">유니코드 정규화, 소문자 변환, 불용어 제거</p>
          </div>
        </div>
        <button
          onClick={onRun}
          disabled={!preprocessInput || isLoading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <PlayCircle className="w-5 h-5" />}
          <span>Run Preprocessor</span>
        </button>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Output</h3>
        {result ? (
          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">처리된 텍스트</p>
              <p className="text-gray-800">{result.output.final}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600 mb-2">처리 단계</p>
              {result.output.steps?.map((step: any, i: number) => (
                <div key={i} className="text-sm mb-2">
                  <span className="font-medium">{step.step}:</span>
                  <span className="text-gray-600 ml-2">{step.output?.substring(0, 100)}...</span>
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
