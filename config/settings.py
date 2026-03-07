"""
글로벌 설정 모듈

이 모듈은 환경변수(`.env`)에서 값을 읽어 애플리케이션 전역에서 사용할
설정 값을 `Settings` 데이터클래스 인스턴스(`settings`)로 제공합니다.

동작 순서 요약:
1. `python-dotenv`의 `load_dotenv()`가 호출되어 프로젝트 루트 또는 현재 디렉터리의
   `.env` 파일을 로드합니다. (환경 변수는 OS 환경변수를 우선합니다.)
2. `Settings` 데이터클래스의 필드들이 기본값으로 환경변수 또는 하드코딩된 디폴트를 사용합니다.
3. 모듈 하단의 `settings = Settings()`로 즉시 인스턴스가 생성되어 다른 모듈에서 바로 사용 가능합니다.

설계/사용 주의사항:
- 보안상 민감한 API 키는 `.env` 파일이 아닌 안전한 비밀 저장소에서 관리하는 것을 권장합니다.
- 환경 변수는 문자열로 들어오기 때문에 숫자 변환(`int()`, `float()`)을 수행합니다. 잘못된 값이 들어오면 예외가 발생할 수 있습니다.
- 필요하다면 필드 검증(예: pydantic)이나 기본값 검사를 추가하세요.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# .env 파일을 로드하여 os.getenv에서 값을 읽을 수 있게 함
load_dotenv()

# 이해가게 개념설명 알기쉽게 핵심 설명(간단 요약):
# - 이 파일은 환경변수(.env)에 적힌 설정값을 읽어서 프로그램에서 바로 쓸 수 있게 해줍니다.
# - `Settings`라는 데이터 클래스는 여러 설정(경로, API 키, 모델 이름 등)을 모아둔 그릇입니다.
# - `settings = Settings()`로 모듈 로드 시 기본 설정 인스턴스를 만들어서 어디서든 편하게 사용합니다.
# - 주의: 비밀 정보(API 키 등)는 안전하게 관리해야 합니다 (공개 저장소에 올리지 말기).


@dataclass
class Settings:
    """애플리케이션 설정 컨테이너.

    각 속성은 기본값으로 환경변수 값을 사용하며, 없을 경우 코드에 정의된 디폴트가 적용됩니다.
    - 타입 어노테이션은 개발 편의성(IDE 완성, 타입 검사)을 위해 제공됩니다.
    - 필드 이름은 환경변수 이름과 직접적으로 대응됩니다(예: `OPENAI_API_KEY`).
    """

    # Project paths --------------------------------------------------------
    # 프로젝트 루트: 이 파일의 부모(parent).parent -> 프로젝트 최상위 폴더
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    # data 관련 하위 디렉토리 경로들을 기본값으로 구성
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    CHUNKS_DIR: Path = DATA_DIR / "chunks"
    VECTORDB_DIR: Path = DATA_DIR / "vectordb"

    # API Keys (환경변수에서 읽음). 보안 주의: 실제 배포시에는 비밀 관리 사용 권장
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")

    # Embedding settings --------------------------------------------------
    # 임베딩 모델 이름: 환경변수로 지정 가능, 미지정 시 기본값 사용
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    # 임베딩 차원: 환경변수는 문자열이므로 int 변환
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    # 임베더 타입: openai, huggingface, bge-m3 중 선택
    EMBEDDER_TYPE: str = os.getenv("EMBEDDER_TYPE", "openai")
    # BGE-M3 설정
    BGE_M3_MODEL: str = os.getenv("BGE_M3_MODEL", "BAAI/bge-m3")
    BGE_M3_USE_FP16: bool = os.getenv("BGE_M3_USE_FP16", "true").lower() == "true"

    # Chunking settings ---------------------------------------------------
    # 문서 분할 시 조각의 최대 길이 및 중복(overlap)
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retriever settings --------------------------------------------------
    # 검색 시 반환할 상위 K개의 문서 수
    TOP_K: int = int(os.getenv("TOP_K", "5"))

    # LLM settings --------------------------------------------------------
    # 대화/응답 생성에 사용할 LLM 모델 및 파라미터
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))


# 모듈 로드 시 즉시 사용할 수 있는 기본 설정 인스턴스
settings = Settings()

# ---------------------------------------------------------------------------
# 추가 개념 설명: 모듈 수준 객체와 전역 사용, 순환 import 관련 권장사항
# ---------------------------------------------------------------------------
# 1) 모듈 수준 객체(module-level object):
#    - `settings`는 이 모듈에서 생성된 모듈 수준 객체입니다. 다른 모듈에서
#      `from config.settings import settings`로 가져오면 동일한 객체(인스턴스)를
#      참조하게 되므로 전역 구성(Global configuration)처럼 사용됩니다.
#    - 장점: 애플리케이션 전반에서 일관된 설정을 쉽게 공유할 수 있습니다.
#    - 단점: 전역 상태 변경 시 추적이 어려워지므로 가능한 불변(immutable) 또는
#      명확한 변경 API를 사용하는 것이 권장됩니다.
#
# 2) 전역 변수 사용 팁:
#    - 읽기 전용 설정(예: 경로, 상수, 기본값)은 모듈 수준에 두어도 안전합니다.
#    - 환경에 따라 동적으로 변경해야 하는 값은 함수 또는 팩터리(factory)로 캡슐화하세요.
#    - 테스트 시에는 `monkeypatch` 또는 테스트 전용 설정을 사용해 격리하세요.
#
# 3) 순환 import(circular import) 주의사항 및 방지 방법:
#    - 순환 import는 두 개 이상의 모듈이 서로를 직접 참조할 때 발생합니다.
#    - `config.settings`처럼 전역 객체를 제공하는 모듈은 가능한 한 독립적으로 유지하세요.
#    - 방지 전략:
#        a) 지연 import: 모듈 최상단이 아닌 함수/메서드 내부에서 import 실행
#        b) 의존성 분리: 공통 타입/상수는 별도 모듈로 분리
#        c) 의존성 주입(Dependency Injection): 필요한 객체를 파라미터로 전달
#
# 4) 예제: 지연 import로 순환 import 회피
#    def get_some_dependency():
#        # 함수 내부에서 import 하면 모듈 초기화 순서 문제를 피할 수 있음
#        from myapp.other_module import OtherClass
#        return OtherClass()
#
# 사용 예:
#   from config.settings import settings
#   print(settings.PROJECT_ROOT)

