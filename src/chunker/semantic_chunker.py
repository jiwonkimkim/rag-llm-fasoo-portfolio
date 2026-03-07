"""
의미 기반(Semantic) 청크 분할기

문장 경계 기반으로 텍스트를 합쳐가며 의미 단위의 청크를 생성합니다.
문장 단위로 결합하여 `chunk_size`를 넘으면 현재까지 모아온 문장들을 청크로 만들고,
`chunk_overlap`만큼 이전 문장을 남겨 겹침을 생성합니다.
"""
# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 문장 경계(마침표 등)를 기준으로 문장들을 모아 의미가 통하는 청크를 만듭니다.
# 주요 포인트:
# - sentences: 텍스트를 문장 리스트로 나눈 결과
# - current_chunk/current_size: 현재 모으고 있는 문장들과 그 길이
# - overlap: 청크 간 문맥 보존을 위해 이전 문장 일부를 남겨둡니다.
# 사용처: 자연어 의미가 중요할 때(예: 요약, Q&A) 더 좋은 결과를 냅니다.
import re
from .base_chunker import BaseChunker, Chunk


class SemanticChunker(BaseChunker):
    """문장 경계를 이용한 의미 기반 청크 분할기.

    주요 파라미터:
    - `chunk_size`: 목표 청크 길이
    - `chunk_overlap`: 겹침 허용 길이
    - `min_chunk_size`: 최소 청크 길이(너무 작은 청크 방지)
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
    ):
        """
        초기화
        """
        super().__init__(chunk_size, chunk_overlap)
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        """
        문장 단위 결합을 통해 의미 단위 청크를 생성합니다.

        알고리즘 요약:
        - 문장으로 분할한 뒤 순차적으로 문장을 추가하여 `chunk_size`를 초과하면
          현재까지 모은 문장들로 청크를 만든다.
        - 겹침은 직전 문장들 중에서 `chunk_overlap`을 넘지 않는 범위까지 유지한다.
        """
        sentences = self._split_sentences(text)
        chunks = []  # 결과 리스트
        current_chunk = []  # 지금 모으는 문장들
        current_size = 0  # 지금까지 모은 문자 수
        index = 0  # 청크 인덱스

        for sentence in sentences:
            sentence_size = len(sentence)  # 문장의 길이(문자 수)

            # 이해가게 개념설명 알기쉽게 핵심 설명: 만약 지금까지 모은 것 + 새 문장의 길이가 chunk_size보다 크면
            # 지금까지 모아둔 문장들을 하나의 청크로 만든 다음 겹침을 계산합니다.
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # 청크 생성
                chunk_text = " ".join(current_chunk).strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunk = Chunk(
                        content=chunk_text,
                        metadata={
                            "chunk_index": index,
                            "sentence_count": len(current_chunk),
                            "chunk_size": len(chunk_text),
                        },
                        chunk_id=self._generate_chunk_id(source, index),
                        source=source,
                    )
                    chunks.append(chunk)
                    index += 1

                # 이해가게 개념설명 알기쉽게 핵심 설명: 겹침 계산은 뒤쪽 문장들을 거꾸로 보면서 중복으로 남길 만큼 골라요.
                overlap_size = 0
                overlap_sentences = []
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break

                current_chunk = overlap_sentences
                current_size = overlap_size

            current_chunk.append(sentence)
            current_size += sentence_size

        # 남은 텍스트 처리
        if current_chunk:
            chunk_text = " ".join(current_chunk).strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunk = Chunk(
                    content=chunk_text,
                    metadata={
                        "chunk_index": index,
                        "sentence_count": len(current_chunk),
                        "chunk_size": len(chunk_text),
                    },
                    chunk_id=self._generate_chunk_id(source, index),
                    source=source,
                )
                chunks.append(chunk)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """문장 경계로 텍스트를 분할합니다.

        정규식 패턴은 영어/한국어/일본어 등에서 일반적으로 쓰이는 문장종결자(.!?。？！)
        이후의 공백을 기준으로 분리합니다. 간단한 패턴이므로 특수한 경우에는
        언어별 문장 분리 라이브러리를 사용하는 것이 더 정확합니다.
        """
        pattern = r"(?<=[.!?。？！])\s+"
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]
