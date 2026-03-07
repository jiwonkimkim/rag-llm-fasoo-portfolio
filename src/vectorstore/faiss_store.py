"""
FAISS 기반 벡터 저장소 구현

이 구현체는 로컬 FAISS 인덱스를 사용하여 고속 근사 최근접탐색을 제공합니다.
인메모리 인덱스에 데이터를 추가하고, 필요 시 디스크에 인덱스 파일과 메타데이터를 저장합니다.

주의사항:
- `faiss`와 `numpy` 등의 외부 라이브러리가 필요합니다. 생성자 및 저장/로드 메서드에서 지연 import를 사용합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 FAISS라는 빠른 라이브러리를 사용해 '벡터 검색'을 하는 방법을 구현한 예시예요.
# 주요 포인트:
# - add: 벡터를 인덱스에 넣고, 문서/메타데이터를 내부 맵에 저장합니다.
# - search: 쿼리 벡터를 정규화한 뒤 가장 비슷한 항목을 찾아 돌려줍니다.
# - _save/_load: 인덱스와 메타데이터를 파일로 저장하거나 불러오는 기능이에요.

from typing import Any
from pathlib import Path
import json

from .base_store import BaseVectorStore, SearchResult


class FAISSStore(BaseVectorStore):
    """FAISS 기반 벡터 저장소 래퍼.

    - `dimension`: 임베딩 벡터 차원
    - `index_path`: 인덱스 및 메타데이터 저장 경로(디렉토리)
    """

    def __init__(
        self,
        dimension: int = 1536,
        index_path: str | Path | None = None,
    ):
        """초기화: FAISS 인덱스와 내부 메타데이터 저장 구조를 준비합니다."""
        import faiss
        import numpy as np

        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else None

        # FAISS 인덱스 생성 (Inner product 사용; 입력 벡터는 정규화되어야 함)
        self.index = faiss.IndexFlatIP(dimension)

        # 문서 및 메타데이터 저장소(간단한 맵 기반)
        self.documents: dict[str, str] = {}
        self.metadatas: dict[str, dict[str, Any]] = {}
        self.id_to_idx: dict[str, int] = {}
        self.idx_to_id: dict[int, str] = {}

        # 기존 인덱스가 있으면 로드
        if self.index_path and self.index_path.exists():
            self._load()

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """문서와 임베딩을 FAISS 인덱스에 추가합니다.

        임베딩은 L2 정규화를 수행하여 코사인 유사도로 검색할 수 있도록 합니다.
        """
        import numpy as np

        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss_module = __import__("faiss")
        faiss_module.normalize_L2(embeddings_array)

        # 현재 인덱스 총 수를 시작 인덱스로 사용
        start_idx = self.index.ntotal
        self.index.add(embeddings_array)

        # 문서 및 메타데이터 저장
        for i, id in enumerate(ids):
            idx = start_idx + i
            self.id_to_idx[id] = idx
            self.idx_to_id[idx] = id
            self.documents[id] = documents[i]
            self.metadatas[id] = metadatas[i] if metadatas else {}

        # 영속화 경로가 지정되면 저장
        if self.index_path:
            self._save()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """쿼리 임베딩과 유사한 문서를 FAISS에서 조회합니다."""
        import numpy as np

        if self.index.ntotal == 0:
            return []

        # 쿼리 임베딩 정규화
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss_module = __import__("faiss")
        faiss_module.normalize_L2(query_array)

        scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            id = self.idx_to_id.get(idx)
            if id is None:
                continue

            # 필터 조건이 있으면 메타데이터로 검증
            if filter:
                metadata = self.metadatas.get(id, {})
                if not all(metadata.get(k) == v for k, v in filter.items()):
                    continue

            results.append(
                SearchResult(
                    content=self.documents.get(id, ""),
                    metadata=self.metadatas.get(id, {}),
                    score=float(score),
                    id=id,
                )
            )

        return results[:top_k]

    def delete(self, ids: list[str]) -> None:
        """문서 삭제: 내부 맵에서 제거합니다(FAISS 인덱스에서는 실제 삭제는 재구성 필요)."""
        for id in ids:
            if id in self.documents:
                del self.documents[id]
                del self.metadatas[id]
                idx = self.id_to_idx.pop(id, None)
                if idx is not None:
                    del self.idx_to_id[idx]

    def clear(self) -> None:
        """모든 데이터를 초기화합니다(인메모리 인덱스로 재생성)."""
        import faiss

        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents.clear()
        self.metadatas.clear()
        self.id_to_idx.clear()
        self.idx_to_id.clear()

    def count(self) -> int:
        """저장된 문서 수를 반환합니다."""
        return len(self.documents)

    def _save(self) -> None:
        """인덱스와 메타데이터를 디스크에 저장합니다."""
        import faiss

        if self.index_path:
            faiss.write_index(self.index, str(self.index_path / "index.faiss"))

            metadata_path = self.index_path / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "documents": self.documents,
                        "metadatas": self.metadatas,
                        "id_to_idx": self.id_to_idx,
                        "idx_to_id": {str(k): v for k, v in self.idx_to_id.items()},
                    },
                    f,
                    ensure_ascii=False,
                )

    def _load(self) -> None:
        """디스크에서 인덱스와 메타데이터를 로드합니다."""
        import faiss

        if self.index_path:
            index_file = self.index_path / "index.faiss"
            metadata_file = self.index_path / "metadata.json"

            if index_file.exists():
                self.index = faiss.read_index(str(index_file))

            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", {})
                    self.metadatas = data.get("metadatas", {})
                    self.id_to_idx = data.get("id_to_idx", {})
                    self.idx_to_id = {int(k): v for k, v in data.get("idx_to_id", {}).items()}
