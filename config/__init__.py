"""
`config` 패키지 초기화 모듈

이 모듈은 프로젝트 전반에서 공유되는 설정 객체와 로그 설정 함수를
간단히 import/export 하기 위해 존재합니다. 패키지 사용자는
`from config import Settings, setup_logging` 형태로 편리하게 접근할 수 있습니다.

주요 목적:
- 패키지 레벨에서 핵심 구성요소(`Settings`, `setup_logging`)를 노출합니다.
- 다른 하위 모듈이 `config`를 import 할 때 순환 import를 최소화합니다.

사용 예:
	from config import Settings, setup_logging

	# 전역 설정 객체를 가져와 사용
	cfg = Settings()

	# 로거 설정 (콘솔 출력 + 선택적 파일 출력)
	logger = setup_logging()

명명 규칙/태그 안내 (참고용):
- 태그: `config`, `settings`, `logging` — 모듈의 역할을 빠르게 파악할 때 사용
- 명령어: 이 파일 자체에는 실행 가능한 CLI 명령이나 스크립트는 없습니다.
- 함수/클래스: 실제 구현은 하위 모듈에 있으며 여기서는 재노출(export)만 수행합니다.

"""

from .settings import Settings
from .logging_config import setup_logging

# 공개 API 목록: `from config import *` 했을 때 내보낼 이름
__all__ = ["Settings", "setup_logging"]

# 참고: 이 파일은 가볍게 유지하는 것이 좋습니다. 복잡한 초기화 로직은
# `settings.py` 또는 다른 초기화 전용 모듈로 분리하세요.

# 이해가게 개념설명 알기쉽게 핵심 설명(간단 요약):
# - 이 모듈은 프로젝트에서 공통으로 쓰이는 설정과 로깅 설정 함수를 쉽게 가져다 쓰도록 묶어둔 곳입니다.
# - 다른 곳에서 `from config import Settings`처럼 가져오면, 같은 설정 클래스를 편하게 쓸 수 있어요.
# - 순환 import를 피하려면 필요한 시점에만 import 하거나 의존성을 분리하면 됩니다.
#
# ---------------------------------------------------------------------------
# 개념 설명: 객체, 전역, 순환 import 등의 일반적인 Python 개념(한국어 요약)
# ---------------------------------------------------------------------------
# 객체(Object):
# - Python에서 모든 것은 객체입니다. 자료형(문자열, 정수, 리스트)뿐 아니라
#   함수와 클래스도 모두 객체입니다. 객체는 속성(attribute)과 동작(method)을 가질 수 있습니다.
# - 예: `settings = Settings()`에서 `settings`는 `Settings` 클래스의 인스턴스(객체)입니다.
#
# 전역(Global) / 전역 변수(Global Variable):
# - 모듈 수준에서 선언된 이름(변수, 상수, 함수 등)은 해당 모듈의 전역 네임스페이스에 존재합니다.
# - 다른 모듈에서 `from config import settings`처럼 가져와 재사용하면 사실상 전역처럼 동작합니다.
# - 전역 객체를 사용할 때는 변경 가능한 객체(mutable)를 직접 수정하면 사이드 이펙트가 발생할 수 있으므로
#   불변 데이터(immutable)를 사용하거나 명확한 API(함수)를 통해 상태를 변경하는 것이 좋습니다.
#
# 순환 import (Circular Import):
# - 정의: 모듈 A가 모듈 B를 import 하고, 동시에 모듈 B가 모듈 A를 import 하는 상황을 말합니다.
# - 문제: 순환 import는 런타임에서 한쪽 모듈의 네임스페이스가 완전히 초기화되기 전에 다른 모듈이
#   그 네임스페이스를 사용하려고 하여 AttributeError나 None 참조 같은 오류를 일으킬 수 있습니다.
#
# - 예시:
#     # a.py
#     from b import func_b
#     def func_a():
#         return "A"
#
#     # b.py
#     from a import func_a
#     def func_b():
#         return func_a()
#
# - 회피 방법:
#   1) 지연 import(함수 내부에서 import): 모듈 최상단이 아닌 함수 또는 메서드 내부에서 import 하여
#      필요할 때만 가져오면 초기화 순서 문제를 피할 수 있습니다.
#   2) 공통 의존성을 분리: 공통으로 참조되는 타입/상수/인터페이스를 별도의 모듈로 분리합니다.
#   3) 구조 변경: 클래스/함수의 책임을 재분배하거나 의존성 주입을 사용해 순환 의존을 제거합니다.
#
# - `config` 모듈에서의 주의점:
#   이 패키지는 전역 설정 객체(`settings`)와 로그 설정 헬퍼를 노출합니다. 다른 하위 모듈들이
#   `from config import settings`를 하고, 동시에 `config.settings`가 다른 하위 모듈을 import 할 경우
#   순환 import가 발생할 수 있습니다. 따라서 `settings.py`에서는 가능한 한 다른 프로젝트 모듈을
#   import 하지 않도록 설계하는 것이 안전합니다. 필요 시 지연 import를 사용하세요.

