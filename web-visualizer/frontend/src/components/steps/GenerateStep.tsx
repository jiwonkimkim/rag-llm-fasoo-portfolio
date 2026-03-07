import { Bot, Loader2 } from 'lucide-react';
import { StepResult } from '../../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface GenerateStepProps {
  retrieveResult: StepResult | null;
  model: string;
  setModel: (value: string) => void;
  generateApiKey: string;
  setGenerateApiKey: (value: string) => void;
  temperature: number;
  setTemperature: (value: number) => void;
  isGroqModel: boolean;
  isLoading: boolean;
  result: StepResult | null;
  onRun: () => void;
}

export default function GenerateStep({
  retrieveResult,
  model,
  setModel,
  generateApiKey,
  setGenerateApiKey,
  temperature,
  setTemperature,
  isGroqModel,
  isLoading,
  result,
  onRun,
}: GenerateStepProps) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Input</h3>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">쿼리 (Retrieve 단계에서 사용)</p>
          <p className="text-gray-800">{retrieveResult?.input?.query || '검색 쿼리가 없습니다'}</p>
        </div>
        <div className="p-3 bg-blue-50 rounded-lg h-24 overflow-auto">
          <p className="text-sm text-blue-600 mb-1">Context ({retrieveResult?.output?.results?.length || 0}개)</p>
          {retrieveResult?.output?.results?.slice(0, 3).map((r: any, i: number) => (
            <p key={i} className="text-xs text-gray-600">• {r.content.substring(0, 50)}...</p>
          ))}
        </div>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full p-2 border rounded-lg"
            >
              <optgroup label="OpenAI (API 키 필요)">
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
              </optgroup>
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
            </select>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              {(model === 'mixtral-8x7b-32768' || model.includes('gpt-oss')) && (
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded font-medium">멀티모델 (MoE)</span>
              )}
              {model.includes('gpt-oss') && (
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-medium">추론 지원</span>
              )}
              <p className="text-xs text-gray-500">
                {isGroqModel
                  ? '✓ Groq 모델 - 무료 사용 가능'
                  : 'OpenAI 모델 - API 키 필요'}
              </p>
            </div>
          </div>
          {/* OpenAI 모델 선택 시에만 API 키 입력 표시 */}
          {!isGroqModel && (
            <div>
              <label className="block text-sm font-medium mb-1">OpenAI API Key</label>
              <input
                type="password"
                value={generateApiKey}
                onChange={(e) => setGenerateApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full p-2 border rounded-lg font-mono text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">GPT 모델 사용을 위해 필수입니다</p>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium mb-1">Temperature: {temperature.toFixed(1)}</label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
        <button
          onClick={onRun}
          disabled={!retrieveResult || (!isGroqModel && !generateApiKey) || isLoading}
          className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Bot className="w-5 h-5" />}
          <span>Generate Response</span>
        </button>
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Output</h3>
        {result ? (
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600 mb-2 font-medium">Generated Response</p>
            <div className="text-gray-800 prose prose-sm max-w-none prose-table:border-collapse prose-th:border prose-th:border-gray-300 prose-th:bg-gray-100 prose-th:p-2 prose-td:border prose-td:border-gray-300 prose-td:p-2">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.output.response}
              </ReactMarkdown>
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
