"""
`base_chunker` 모듈

이 모듈은 텍스트를 조각(청크)으로 나누기 위한 추상 기반 클래스를 정의합니다.
다양한 분할 전략(고정 길이, 문장 기반, 재귀적 분할 등)은 이 추상 클래스를 상속하여
구현됩니다.

주요 구성요소:
- `Chunk` 데이터클래스: 하나의 청크를 표현하는 값 객체로, 내용(content),
  메타데이터(metadata), 고유 ID(chunk_id), 출처(source)를 포함합니다.
- `BaseChunker` 추상 클래스: 모든 청크 분할기(chunker)가 구현해야 하는 인터페이스를 제공합니다.

설계/사용 노트:
- 객체(Object): `Chunk`는 불변에 가깝게 사용되는 값 객체입니다(데이터 전달 목적).
- 전역(Global): `BaseChunker` 자체는 상태를 많이 가지지 않으며, 인스턴스 수준에서
  `chunk_size`와 `chunk_overlap` 같은 설정을 보관합니다. 전역 설정을 사용하려면
  `config.settings`와 같은 전역 설정 객체를 주입하는 방식이 안전합니다.
- 순환 import(Circular import): 하위 모듈들이 서로를 import 할 경우 순환 참조가 발생할 수
  있으니, 가능한 한 상대 import와 지연 import(함수 내부)로 회피하세요.

예제:
    class MyChunker(BaseChunker):
        def chunk(self, text: str, source: str = "") -> list[Chunk]:
            # 구현
            ...

"""

# ===== 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명) =====
# 목적:
# - 이 모듈은 긴 텍스트를 '청크'라는 작은 조각으로 나누는 기반(부모) 클래스를 제공합니다.
# - 다양한 분할 방식(고정 길이, 문장 단위, 재귀적 분할 등)은 이 클래스를 상속하여 만들 수 있어요.
#
# 주요 개념(쉽게 설명):
# - Chunk: 한 덩어리의 글(내용, 메타데이터, 고유 ID, 출처가 포함된 객체)
# - BaseChunker: 청크를 만드는 방법을 정의하는 클래스(실제로 동작하려면 상속해 구현해야 함)
#
# 사용 예시(간단):
# - class MyChunker(BaseChunker):
#     def chunk(...):
#         # 텍스트 분할 로직 구현
#
# 주의사항:
# - chunk_size와 chunk_overlap은 인스턴스 설정으로 문맥 보존과 성능에 영향을 줍니다.
# - 전역 설정을 사용할 땐 테스트 시에 다른 설정으로 바꿔가며 확인하세요.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Chunk:
    """데이터 전달용 청크 객체.

    필드 설명:
    - `content` : 청크에 담긴 텍스트 내용
    - `metadata` : 청크 관련 추가 정보(인덱스, 문자 범위 등)
    - `chunk_id` : 청크 식별자(일관된 해시 등 사용)
    - `source` : 청크의 원본 출처 식별자(파일 경로, URL 등)
    """

    content: str
    metadata: dict[str, Any]
    chunk_id: str
    source: str


class BaseChunker(ABC):
    """청크 분할기 인터페이스(추상 클래스).

    생성자 인자(`chunk_size`, `chunk_overlap`)는 인스턴스 레벨의 설정이며,
    필요하다면 외부 설정 객체를 주입하여 중앙에서 관리할 수 있습니다.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        초기화

        Args:
            chunk_size: 각 청크의 최대 문자 수
            chunk_overlap: 인접 청크 간 겹침(overlap) 문자 수
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 이해가게 개념설명 알기쉽게 핵심 설명:
        # - chunk_size: 한 청크(조각)에 들어갈 수 있는 최대 글자 수예요. (예: 1000)
        # - chunk_overlap: 연속된 청크가 겹치는 글자 수예요. 문맥이 잘 이어지도록 도와줍니다.
        # - 주의: chunk_overlap은 chunk_size보다 작아야 무한루프 등 문제가 생기지 않습니다.

    @abstractmethod
    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        """
        텍스트를 분할하여 `Chunk` 리스트를 반환하는 메서드(서브클래스 구현 필요).

        Args:
            text: 입력 텍스트
            source: 선택적 출처 식별자

        Returns:
            List[Chunk]: 분할된 청크들의 리스트
        """
        pass

    def _generate_chunk_id(self, source: str, index: int) -> str:
        """청크의 고유 ID를 생성합니다.

        구현은 간단한 MD5 해시의 앞부분을 사용합니다(충돌 가능성은 매우 낮음).
        이 메서드는 내부 사용용이며, 필요 시 더 강력한 ID 전략으로 교체하세요.
        """
        import hashlib

        content = f"{source}_{index}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

        # 이해가게 개념설명 알기쉽게 핵심 설명:
        # - 이 함수는 조각마다 고유한 짧은 ID를 만들어 줍니다.
        # - 방법: 출처(source)와 인덱스(index)를 합쳐 MD5 해시를 만들고 앞부분을 잘라 사용합니다.
        # - 왜 필요한가요? 각 청크를 데이터베이스나 검색 색인에서 빠르게 찾기 위해서예요.