"""
`chunker` 패키지 초기화 모듈

이 파일은 패키지 외부에서 주요 Chunker 클래스를 간편하게 import 할 수 있도록
핵심 클래스들을 재노출(export)합니다. 예:

	from src.chunker import FixedChunker

주의:
- `__all__`에 나열된 이름들은 `from src.chunker import *` 사용 시 노출됩니다.
- 가능한 한 상대 import를 사용해 순환 import를 방지하세요.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 여러 청크 분할기(Fixed, Semantic, Recursive)를 쉽고 깔끔하게 불러오기 위해
#   한곳에 모아놓은 '목록표' 같은 역할을 해요.
# 주요 포인트:
# - 패키지의 주요 클래스를 `__all__`로 정의하면 외부에서 간편하게 사용할 수 있어요.
# - 상대 import를 사용하면 서로 다른 파일들 사이에 순환 참조가 생기는 것을 줄일 수 있어요.

from .base_chunker import BaseChunker, Chunk
from .fixed_chunker import FixedChunker
from .semantic_chunker import SemanticChunker
from .recursive_chunker import RecursiveChunker

__all__ = ["BaseChunker", "Chunk", "FixedChunker", "SemanticChunker", "RecursiveChunker"]
