"""
BGE-M3 임베더 구현

BGE-M3는 BAAI에서 개발한 다국어 임베딩 모델로, Dense, Sparse, ColBERT 세 가지
임베딩을 동시에 생성할 수 있습니다. 이를 통해 Hybrid Retrieval 성능을 극대화할 수 있습니다.

주의사항:
- `FlagEmbedding` 패키지 설치 필요: pip install FlagEmbedding
- 첫 실행 시 모델 다운로드에 시간이 걸립니다 (약 2GB)
- GPU 사용 시 성능이 크게 향상됩니다
"""

from typing import Any
from .base_embedder import BaseEmbedder


class BGEM3Embedder(BaseEmbedder):
    """BGE-M3 기반 임베더.

    Dense, Sparse, ColBERT 임베딩을 모두 지원합니다.

    - `embed`: 단일 텍스트 임베딩 반환 (기본: Dense)
    - `embed_batch`: 배치 처리로 여러 텍스트 임베딩 생성
    - `embed_with_sparse`: Dense + Sparse 임베딩 동시 반환
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        use_fp16: bool = True,
        device: str | None = None,
        embedding_type: str = "dense",  # dense, sparse, colbert, all
    ):
        """초기화

        Args:
            model_name: 모델 이름 (기본: BAAI/bge-m3)
            use_fp16: FP16 사용 여부 (메모리 절약, 속도 향상)
            device: 디바이스 지정 (None이면 자동 감지)
            embedding_type: 임베딩 타입 (dense, sparse, colbert, all)
        """
        from FlagEmbedding import BGEM3FlagModel

        self.embedding_type = embedding_type
        self.model = BGEM3FlagModel(
            model_name,
            use_fp16=use_fp16,
            device=device,
        )

        # Dense 임베딩 차원은 1024
        dimension = 1024
        super().__init__(model_name, dimension)

    def embed(self, text: str) -> list[float]:
        """단일 텍스트 임베딩을 생성합니다 (Dense)."""
        result = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )
        return result["dense_vecs"][0].tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """배치 단위로 Dense 임베딩을 생성합니다."""
        result = self.model.encode(
            texts,
            batch_size=batch_size,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )
        return [vec.tolist() for vec in result["dense_vecs"]]

    def embed_with_all(
        self,
        texts: list[str],
        batch_size: int = 32,
        return_dense: bool = True,
        return_sparse: bool = True,
        return_colbert: bool = False,
    ) -> dict[str, Any]:
        """Dense, Sparse, ColBERT 임베딩을 동시에 생성합니다.

        Args:
            texts: 입력 텍스트 리스트
            batch_size: 배치 크기
            return_dense: Dense 임베딩 반환 여부
            return_sparse: Sparse 임베딩 반환 여부
            return_colbert: ColBERT 벡터 반환 여부

        Returns:
            dict: {
                "dense_vecs": Dense 임베딩 리스트,
                "lexical_weights": Sparse 가중치 딕셔너리 리스트,
                "colbert_vecs": ColBERT 벡터 리스트 (요청 시)
            }
        """
        result = self.model.encode(
            texts,
            batch_size=batch_size,
            return_dense=return_dense,
            return_sparse=return_sparse,
            return_colbert_vecs=return_colbert,
        )

        output = {}

        if return_dense and "dense_vecs" in result:
            output["dense_vecs"] = [vec.tolist() for vec in result["dense_vecs"]]

        if return_sparse and "lexical_weights" in result:
            # Sparse weights는 {token_id: weight} 형태의 딕셔너리
            output["lexical_weights"] = result["lexical_weights"]

        if return_colbert and "colbert_vecs" in result:
            output["colbert_vecs"] = [vec.tolist() for vec in result["colbert_vecs"]]

        return output

    def compute_sparse_scores(
        self,
        query_weights: dict[int, float],
        doc_weights_list: list[dict[int, float]],
    ) -> list[float]:
        """Sparse 가중치를 이용한 유사도 계산.

        Args:
            query_weights: 쿼리의 lexical weights
            doc_weights_list: 문서들의 lexical weights 리스트

        Returns:
            각 문서와의 유사도 점수 리스트
        """
        scores = []
        for doc_weights in doc_weights_list:
            score = 0.0
            for token_id, q_weight in query_weights.items():
                if token_id in doc_weights:
                    score += q_weight * doc_weights[token_id]
            scores.append(score)
        return scores
