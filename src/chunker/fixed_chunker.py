"""
고정 길이(Fixed-size) 청크 분할기

이 구현은 입력 텍스트를 `chunk_size`를 기준으로 잘라내되,
가능한 경우 문장(또는 단어) 경계에서 잘라 가독성을 유지합니다.

알고리즘 요약:
1. 현재 시작 인덱스에서 `chunk_size` 만큼 다음 끝 인덱스를 결정합니다.
2. 끝 인덱스가 텍스트 길이보다 작으면 문장/단어 경계(우선순위: ". ",".\n","\n\n","\n"," ")를 찾아
   적절한 분할 지점을 선택합니다.
3. 청크 텍스트를 만들어 `Chunk` 객체로 감싼 뒤 메타데이터(인덱스, 문자 범위 등)를 부달합니다.
4. 다음 청크 시작은 `end - chunk_overlap`으로 설정하여 중복(overlap)을 처리합니다.

주의사항:
- 이 방식은 단순하고 빠르지만, 언어별 문장 경계 처리의 한계가 있습니다.
- 더 정교한 분할(의미 단위 분할)이 필요하면 `SemanticChunker` 또는 외부 문장 분리 라이브러리를
  사용하는 것을 고려하세요.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 긴 텍스트를 일정한 크기의 조각(청크)으로 나누되 가능한 문장 경계에서 잘라
#   읽기 좋은 청크를 만드는 간단한 방법입니다.
# 주요 포인트(한줄씩):
# - start: 이번에 자르기 시작할 위치(처음에는 0)
# - end: 이번 청크의 끝 위치(초기값은 start + chunk_size)
# - rfind: 주어진 구간에서 마지막으로 나타나는 구분자 위치를 찾아 더 자연스러운 분할점을 찾습니다.
# - chunk_overlap: 청크끼리 일부 겹치게 하여 문맥을 유지합니다.
# 사용처: 빠른 분할/색인 구축이 필요할 때 유용합니다.

from .base_chunker import BaseChunker, Chunk


class FixedChunker(BaseChunker):
    """고정 길이 기반 청크 분할기.

    구현은 가능한 문장 경계에서 청크를 자르려고 시도하며, 결과에 메타데이터를 포함합니다.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 10,
    ):
        """초기화 - min_chunk_size 기본값을 10으로 설정하여 작은 청크도 허용"""
        super().__init__(chunk_size, chunk_overlap)
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        """
        텍스트를 고정 크기 청크로 분할합니다.

        Args:
            text: 입력 텍스트
            source: 출처 식별자(선택)

        Returns:
            List[Chunk]: 분할된 청크 리스트
        """
        chunks = []  # 결과를 담을 리스트
        start = 0  # 이해가게 개념설명 알기쉽게 핵심 설명: 지금 자를 시작 위치(처음에는 0)
        index = 0  # 이해가게 개념설명 알기쉽게 핵심 설명: 각 청크에 붙일 순서 번호

        # 이해가게 개념설명 알기쉽게 핵심 설명: while start < len(text): 는 시작 위치가 글 길이보다 작을 동안 계속 자르는 뜻이에요.
        while start < len(text):
            # 기본적으로 end는 시작 위치에서 chunk_size만큼 떨어진 지점이에요.
            end = start + self.chunk_size

            # 적절한 분할점 탐색(문장 또는 단어 경계 우선)
            # 이해가게 개념설명 알기쉽게 핵심 설명: end가 글 길이보다 작으면 문장이나 줄바꿈 같은 자연스러운 지점에서 잘라요.
            if end < len(text):
                for sep in [". ", ".\n", "\n\n", "\n", " "]:
                    # text.rfind(sep, start, end)는 start~end 구간에서 sep가 마지막으로 나온 위치를 찾아요.
                    break_point = text.rfind(sep, start, end)
                    if break_point != -1:
                        # sep가 있으면 sep 끝까지 포함하도록 end를 조정해요.
                        end = break_point + len(sep)
                        break

            # 이해가게 개념설명 알기쉽게 핵심 설명: 잘라낸 부분을 다듬어 공백을 없애고 chunk_text로 만듭니다.
            chunk_text = text[start:end].strip()

            # min_chunk_size 이상인 청크만 추가 (Semantic Chunker와 동일)
            if chunk_text and len(chunk_text) >= self.min_chunk_size:
                chunk = Chunk(
                    content=chunk_text,
                    metadata={
                        "chunk_index": index,
                        "start_char": start,
                        "end_char": end,
                        "chunk_size": len(chunk_text),
                    },
                    chunk_id=self._generate_chunk_id(source, index),
                    source=source,
                )
                chunks.append(chunk)
                index += 1

            # 다음 청크의 시작 위치: overlap을 고려 (이전 조각과 일부 겹치게 함)
            next_start = end - self.chunk_overlap
            # 무한 루프 방지: start가 반드시 증가해야 함
            if next_start <= start:
                next_start = end  # overlap 적용하지 않고 end에서 시작
            start = next_start
            if start >= len(text):
                break

        return chunks
