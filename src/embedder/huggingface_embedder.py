"""
HuggingFace(sentence-transformers) 임베더 구현

이 구현은 `sentence_transformers` 라이브러리를 사용해 문장 임베딩을 생성합니다.
모델 로드는 생성자에서 수행되며, 로컬 GPU 사용 시 `device='cuda'`로 지정할 수 있습니다.

주의사항:
- `sentence_transformers` 설치가 필요합니다. 대형 모델은 메모리를 많이 소비하니 모델 선택에 유의하세요.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - HuggingFace의 sentence-transformers 모델을 사용해 텍스트 벡터(임베딩)를 만드는 예시 파일이에요.
# 주요 포인트:
# - `model.encode`로 텍스트를 숫자 배열로 바꾸고, 이를 리스트로 반환해요.
# - 배치 처리를 사용하면 많은 문서를 더 빠르게 임베딩할 수 있어요.

from .base_embedder import BaseEmbedder


class HuggingFaceEmbedder(BaseEmbedder):
    """sentence-transformers 기반 임베더.

    - `embed`: 단일 텍스트 임베딩 반환
    - `embed_batch`: 배치 단위 임베딩 반환(성능 우선)
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        """모델을 로드하고 차원을 추출합니다."""
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)
        dimension = self.model.get_sentence_embedding_dimension()

        super().__init__(model_name, dimension)

    def embed(self, text: str) -> list[float]:
        """단일 텍스트 임베딩을 생성합니다."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """배치 단위로 임베딩을 생성합니다. `show_progress_bar`로 진행 표시를 출력합니다."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,  # Windows에서 터미널 문제 방지
        )
        return embeddings.tolist()
