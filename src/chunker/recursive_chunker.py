"""
재귀적(Recursive) 청크 분할기

여러 구분자(separators)를 우선순위로 사용하여 텍스트를 점차적으로 분할합니다.
큰 덩어리가 남아있을 때는 더 작은 구분자로 재귀 분할을 시도하는 방식으로 동작합니다.

특징:
- 문단/문장/단어 등 다양한 분할 기준을 순차적으로 적용하여 의미 단위가 보전되도록 합니다.
- 최후의 수단으로는 문자 단위 분할을 수행합니다.

사용 예 및 주의:
- 긴 텍스트를 가능한 자연스러운 경계에서 나누고 싶을 때 유용합니다.
- 분리 기준(`separators`)를 적절히 구성하면 결과 품질을 크게 향상시킬 수 있습니다.
"""

# ===== 초등학생용 간단 설명 (쉽게 읽을 수 있도록 한 줄씩 설명함) =====
# 이 파일은 아주 긴 글을 작은 조각들로 나누는 도구예요.
# - '청크(chunk)'는 글의 작은 조각을 말해요.
# - 먼저 큰 경계(문단, 문장)를 기준으로 나눠보고, 그래도 너무 크면 더 작은 경계로 또 나눠요.
# - 모든 방법으로도 못 나누면, 마지막으로 한글자씩 잘라서 조각을 만들어요.
# - 이렇게 나눈 조각은 검색이나 요약 같은 작업에서 쓰기 쉬워져요.


from .base_chunker import BaseChunker, Chunk


class RecursiveChunker(BaseChunker):
    """재귀적 분할을 사용하는 청크 분할기.

    - `DEFAULT_SEPARATORS`는 우선순위가 높은 구분자 순입니다. (문단 > 줄바꿈 > 문장 등)
    - 생성자에서 커스터마이즈된 구분자 리스트를 받을 수 있습니다.
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ):
        """
        초기화

        Args:
            chunk_size: 각 청크의 최대 문자 수
            chunk_overlap: 인접 청크 간 겹침 문자 수
            separators: 우선순위가 적용된 구분자 리스트
        """
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or self.DEFAULT_SEPARATORS

    # 고등학생 설명(세부사항):
    # - chunk_size (int): 각 청크가 가질 수 있는 최대 문자 수입니다. API나 모델 토큰 제한을 고려하여 설정합니다.
    # - chunk_overlap (int): 인접 청크 사이에 중복으로 포함될 문자 수입니다. 문맥 보존을 위해 사용되며,
    #   일반적으로는 0 <= chunk_overlap < chunk_size를 유지해야 합니다. 그렇지 않으면 `start`가 증가하지 않아
    #   무한루프나 로직 오류가 발생할 수 있습니다.
    # - separators (list[str]): 분할 우선순위를 나타내는 문자열 목록입니다. 앞에서부터 차례로 적용되며,
    #   구분자의 선택과 순서가 결과의 의미 결속력(문장 단위 유지 등)에 큰 영향을 미칩니다.
    # - 성능/메모리 고려: `chunk_size`가 작을수록 생성되는 청크 수가 증가해 I/O와 저장 비용이 커집니다.

    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        """
        다단계 분할을 적용하여 텍스트를 청크로 변환합니다.

        Returns:
            List[Chunk]
        """
        # 1) 먼저 재귀적으로 텍스트를 분할해서 문자열 목록을 얻어요.
        #    이 목록은 아직 Chunk 객체로 포장되기 전의 "작은 글 덩어리"들이에요.
        chunks = self._recursive_split(text, self.separators)

        result = []
        for index, chunk_text in enumerate(chunks):
            chunk_text = chunk_text.strip()
            if chunk_text:
                chunk = Chunk(
                    content=chunk_text,
                    metadata={
                        "chunk_index": index,
                        "chunk_size": len(chunk_text),
                    },
                    chunk_id=self._generate_chunk_id(source, index),
                    source=source,
                )
                result.append(chunk)

        # 고등학생 설명:
        # - enumerate(chunks)는 인덱스(0 기반)를 함께 반환하므로 각 청크에 정확한 위치정보(chunk_index)를 붙일 수 있습니다.
        # - chunk_id는 `_generate_chunk_id`를 통해 생성되는 고유 식별자이며, 분산 저장소나 인덱스에서 레코드를 조회할 때 사용됩니다.
        # - metadata에는 chunk_index, chunk_size 등 유용한 메타정보를 포함해 검색결과 정렬, 페이징, 디버깅 등에 활용합니다.
        # - `strip()`로 앞뒤 공백을 제거해 불필요한 공백이 인덱싱에 영향을 주지 않도록 합니다.

        return result

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """구분자 리스트를 사용하여 재귀적으로 텍스트를 분할합니다.

        알고리즘 요약:
        - 현재 구분자를 사용해 split을 시도하고, 부분 문자열이 여전히 크면
          다음 구분자로 재귀 분할을 수행합니다.
        - 모든 구분자를 소진하면 문자 단위 분할로 처리합니다.
        """
        if not text:
            return []

        # 고등학생 설명(동작 요약 및 복잡도):
        # - 기저 사례: 입력이 비어 있거나, 텍스트 길이가 `chunk_size` 이하인 경우 빠르게 반환합니다.
        # - 재귀 전략: 첫 번째(우선순위) 구분자로 split하고, 각 segment가 `chunk_size`를 초과하면
        #   남은 구분자 목록으로 재귀 호출합니다. 이로써 큰 문단 단위에서 점차 세부 단위로 내려갑니다.
        # - 복잡도/특이사항: 최악의 경우 각 분할 단계에서 많은 split을 시도하므로 입력 길이 n과
        #   구분자 수 k에 따라 O(n * k) 수준의 연산이 발생할 수 있으며, 재귀 깊이는 최대 k입니다n
        # - 안정성: 빈 구분자("")는 문자 단위 분할을 의미하므로 별도 처리되어 무한루프를 방지합니다.

        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # 마지막 수단: 문자 단위 분할
            return self._character_split(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            return self._character_split(text)

        # separator로 문자열을 잘라봅니다.
        # 예: separator가 '\n'이면 줄바꿈 단위로 나눠요.
        splits = text.split(separator)

        # chunks: 최종적으로 모을 조각들의 목록이에요.
        chunks = []

        # current_chunk: 지금까지 모은 글 조각(아직 결과에 확정되지 않았음)
        current_chunk = ""

        for split in splits:
            # split: separator로 잘랐을 때 생기는 부분 문자열 한 조각이에요.
            # potential_chunk: current_chunk와 split을 합쳐서 하나의 조각으로 만들면
            # 크기가 chunk_size보다 작아지는지 시험해보는 임시 변수예요.
            potential_chunk = (
                current_chunk + separator + split if current_chunk else split
            )

            # 고등학생 설명(병합 전략):
            # - potential_chunk는 현재 모아둔 current_chunk와 새로 분할된 split을 합쳐서 얻은 문자열입니다.
            # - 알고리즘은 탐욕적(greedy)으로 가능한 한 합쳐서(`chunk_size` 이하) 더 긴 청크를 만듭니다.
            # - 이렇게 하면 문맥(문장/절의 연결)을 보존하지만, 공백이나 구분자가 중복될 수 있으니
            #   분할 기준(separators)과 separator 포함 여부를 설계할 때 주의해야 합니다.
            # - split 자체가 `chunk_size`보다 큰 경우는 다음 구분자로 세분화하여 처리합니다.
            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # potential_chunk가 너무 크면, 지금까지 모인 current_chunk를 확정해서 결과에 넣어요.
                if current_chunk:
                    chunks.append(current_chunk)

                # split 자체가 너무 크면(한 조각이 이미 chunk_size보다 크면),
                # 더 작은 구분자로 재귀적으로 나누도록 넘겨요.
                if len(split) > self.chunk_size:
                    # 다음 구분자를 사용해서 이 조각을 다시 나눠보아요.
                    sub_chunks = self._recursive_split(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    # split은 작으니 다음 current_chunk로 설정해요.
                    current_chunk = split

        # 마지막에 남은 current_chunk가 있으면 결과에 추가해요.
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _character_split(self, text: str) -> list[str]:
        """마지막 수단으로 문자 단위 분할을 수행합니다.

        이해가게 개념설명 알기쉽게 핵심 설명:
        - 이 함수는 입력 텍스트를 `chunk_size` 단위로 잘라 여러 조각을 만드는 작업을 합니다.
        - 변수 설명(쉽게 이해하기):
        #   - text (str): 전체 글(나누려는 대상)
        #   - chunks (list[str]): 만들어진 조각들을 담는 상자(리스트)
        #   - start (int): 다음에 자를 시작 위치(문자 인덱스, 0부터 시작)
        #   - end (int): 이번에 자를 끝 위치(비포함 인덱스)
        #   - len(text): 글의 전체 길이(문자 수)
        - 동작(쉽게):
        #   1) start가 글 길이보다 작으면 계속 반복(while)해서 자릅니다.
        #   2) end는 start + chunk_size 또는 글 끝 중 더 작은 값으로 정합니다.
        #   3) text[start:end]를 잘라서 결과에 추가하고, start를 end - chunk_overlap으로 이동해
        #      다음 조각과 일부 겹치게 합니다.
        - 주의: chunk_overlap >= chunk_size이면 반복이 멈추지 않아 무한루프가 발생할 수 있습니다.

        고등학생 설명(정확한 동작과 유의사항):
        - 목적: 모든 구분자 기준으로도 적절히 분할되지 않는 긴 문자열을 안전하게 나누기 위한 최후의 수단입니다.
        - 변수 및 불변 조건:
        #   - text (str): 분할 대상 전체 문자열
        #   - chunks (list[str]): 생성된 청크를 모아두는 리스트
        #   - start (int): 현재 분할 시작 인덱스
        #   - end (int): 분할 끝 인덱스(비포함)
        #   - 불변(invariant): 반드시 0 <= chunk_overlap < chunk_size를 만족해야 루프가 정상 종료됩니다.
        - 동작 원리:
        #   1) start가 텍스트 길이보다 작을 동안 반복합니다.
        #   2) end = min(start + chunk_size, len(text))로 안전하게 끝 인덱스를 계산합니다.
        #   3) slices = text[start:end]를 chunks에 추가하고, start를 end - chunk_overlap으로 업데이트합니다.
        - 복잡도 및 메모리:
        #   - 이 루프는 약 O(n / (chunk_size - chunk_overlap)) 번 반복되며, 청크 개수는 대략 n / (chunk_size - chunk_overlap) 입니다.
        - 안전 주의사항:
        #   - 만약 chunk_overlap >= chunk_size라면 start가 증가하지 않거나 감소하여 무한루프가 발생할 수 있습니다.
        #   - 멀티바이트 문자(예: UTF-8에서 1문자 다중 바이트)는 Python의 `len()`이 코드포인트 기준이므로
        #     바이트 크기와는 다를 수 있습니다(문자 단위로는 문제 없지만 바이트 기준 제한이 있는 경우 주의).
        - 권장: 파라미터 유효성 검사를 초기화(또는 생성자)에서 수행하여 잘못된 값이 들어오지 않도록 하세요.

        사용처:
        - `_recursive_split`에서 더 이상 분할 기준이 남아있지 않거나, 단일 토큰이 `chunk_size`보다 큰 경우 호출됩니다.
        """
        chunks = []  # 잘라서 넣을 상자
        # 이해가게 개념설명 알기쉽게 핵심 설명: 'start'는 지금 자를 위치를 말해요. 처음엔 0부터 시작합니다.
        start = 0  # 지금 자를 시작 위치

        # 이해가게 개념설명 알기쉽게 핵심 설명: while start < len(text): 는 'start가 글 길이보다 작을 동안 계속 반복'이라는 뜻이에요.
        while start < len(text):
            # 이해가게 개념설명 알기쉽게 핵심 설명: end = min(start + self.chunk_size, len(text))는 이번에 어디까지 자를지 정하는 거예요.
            # 글 끝을 넘지 않게 작은 값을 선택합니다.
            end = min(start + self.chunk_size, len(text))

            # 이해가게 개념설명 알기쉽게 핵심 설명: text[start:end]는 start부터 end-1까지의 글을 뜻해요. 그걸 잘라서 넣습니다.
            chunks.append(text[start:end])

            # 이해가게 개념설명 알기쉽게 핵심 설명: 다음 번엔 이전 조각과 일부 겹치도록 start를 옮겨요 (문맥을 보존하기 위해서예요).
            start = end - self.chunk_overlap

        return chunks
