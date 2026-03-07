"""
`logging_config` 모듈

이 모듈은 애플리케이션 전반에서 사용할 로거를 설정하는 헬퍼 함수를 제공합니다.
중앙에서 로깅 설정을 관리하면 출력 형식 및 핸들러 구성이 일관되게 유지됩니다.

주요 기능:
- `setup_logging`: 프로젝트 공통 로거(`rag_system`)를 생성/반환합니다.

사용 예:
    from config.logging_config import setup_logging

    logger = setup_logging()
    logger.info("앱 시작")

매개변수 설명(요약):
- `level` : 로깅 레벨 (예: `logging.DEBUG`, `logging.INFO` 등)
- `log_file` : 파일 경로를 지정하면 파일 핸들러도 추가됩니다. None이면 콘솔 전용.

설계 노트:
- 동일한 로거 이름("rag_system")을 사용하므로 이 함수를 여러 번 호출하더라도
  동일한 로거 객체에 핸들러가 중복 추가되는 것을 주의해야 합니다. 필요하다면
  추가 호출 시 기존 핸들러를 제거하는 로직을 별도로 추가할 수 있습니다.

# 이해가게 개념설명 알기쉽게 핵심 설명(자세한 설명):
# 목적:
# - 이 모듈은 애플리케이션 전체에서 동일한 방식으로 로그를 남기게 도와줘요.
#   로그는 프로그램 실행 중 일어난 일을 기록해서 문제를 찾거나 동작을 확인할 때 쓰입니다.
#
# 사용 방법:
# - `setup_logging(level, log_file)`을 호출하면 바로 쓸 수 있는 로거(logger)를 돌려줘요.
# - `level`은 얼마나 자세히 남길지 정해요 (예: DEBUG는 아주 자세하게, INFO는 보통 수준).
# - `log_file`에 경로를 주면 로그를 파일에 저장하고, 주지 않으면 화면(콘솔)에만 보여줘요.
#
# 매개변수 상세:
# - level (int): 출력할 로그의 최소 레벨을 정합니다. 낮은 레벨일수록 더 많은 로그가 기록됩니다.
# - log_file (Path | None): 파일 경로를 주면 그 파일에 로그를 기록합니다. 없으면 콘솔 전용입니다.
#
# 주요 함수/코드 설명 (줄 단위로 이해하기 쉬운 설명):
# - logging.getLogger(name): 같은 이름이라면 같은 로거 객체를 돌려줘요. 여러 곳에서 같은 이름을 쓰면
#   같은 로그 모음을 공유할 수 있어요.
# - logger.setLevel(level): 이 로거가 받아들일 최소 로그 수준을 정해요. INFO로 설정하면 DEBUG는 무시돼요.
# - Formatter: 로그의 '보이는 모양'을 정해요. 보통은 시간, 로거 이름, 레벨, 메시지를 포함해요.
# - StreamHandler(sys.stdout): 콘솔(터미널)에 로그를 보여주는 도구를 만들어요.
# - FileHandler(path): 파일에 로그를 저장하는 도구를 만들어요.
# - logger.addHandler(handler): 만든 도구(핸들러)를 로거에 붙여서 실제로 로그가 출력되게 해요.
#
# 예시:
# - 간단한 사용: logger = setup_logging(); logger.info("앱 시작")
# - 파일에 기록: logger = setup_logging(level=logging.DEBUG, log_file=Path("app.log"))
#
# 주의사항:
# - 같은 핸들러를 여러 번 추가하면 같은 로그가 중복으로 찍힐 수 있어요. 함수가 여러 번 호출될 때는
#   기존 핸들러를 확인하거나 제거하는 로직이 필요할 수 있어요.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None
) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.

    상세 설명:
    - 이름이 `rag_system`인 로거를 반환합니다. 이 이름은 애플리케이션 전체에서
      동일한 로거를 참조할 때 사용됩니다.
    - 기본적으로 콘솔 핸들러(`sys.stdout`)를 추가하여 표준 출력으로 로그를 보냅니다.
    - `log_file`이 주어지면 UTF-8 인코딩의 파일 핸들러도 추가합니다.

    Args:
        level: 로깅 레벨 (int). 기본값은 `logging.INFO`.
        log_file: Optional[Path] - 로그를 파일에 남기려면 파일 경로를 전달합니다.

    Returns:
        logging.Logger: 구성된 로거 인스턴스

    주의:
        이 함수가 여러 번 호출될 때 같은 로거에 중복 핸들러가 붙을 수 있습니다.
        (핸들러 중복 제거가 필요한 경우 호출 전에 `logger.handlers`를 확인하세요.)
    """
    # logger: 프로젝트에서 공통으로 쓰일 로거 객체를 얻습니다.
    # - logging.getLogger(name)는 같은 name을 주면 동일한 로거 객체를 반환합니다.
    # - 이 덕분에 애플리케이션 여러 위치에서 같은 로거 이름으로 로그를 모을 수 있습니다.
    logger = logging.getLogger("rag_system")  # 이해가게 개념설명 알기쉽게 핵심 설명: 'rag_system'이라는 이름의 로거를 가져와요. 같은 이름은 같은 로거를 뜻해요.

    # setLevel: 이 로거가 처리할 최소 로그 레벨을 정합니다.
    # - level이 INFO면 DEBUG 레벨의 로그는 무시됩니다.
    # - 호출 시 전달된 level 파라미터를 그대로 사용합니다.
    logger.setLevel(level)  # 이해가게 개념설명 알기쉽게 핵심 설명: 이 줄은 로그를 얼마나 자세히 남길지 정해요 (예: INFO, DEBUG).

    # formatter: 로그 메시지의 출력 형식을 정의합니다.
    # - 예: 시간, 로거 이름, 레벨, 메시지를 포함하도록 포맷 문자열을 지정합니다.
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )  # 이해가게 개념설명 알기쉽게 핵심 설명: 로그가 화면에 나올 때 '시간 - 이름 - 레벨 - 메시지'처럼 보이게 하는 설정이에요.

    # console_handler: 콘솔(터미널 표준 출력)으로 로그를 보내는 핸들러입니다.
    console_handler = logging.StreamHandler(sys.stdout)  # 이해가게 개념설명 알기쉽게 핵심 설명: 콘솔(터미널)로 로그를 보여주기 위한 도구를 만들어요.
    console_handler.setLevel(level)  # 이해가게 개념설명 알기쉽게 핵심 설명: 이 도구가 어떤 수준의 로그를 보여줄지 정해요.
    console_handler.setFormatter(formatter)  # 이해가게 개념설명 알기쉽게 핵심 설명: 위에서 만든 '보기 형식'을 이 도구에 연결해요.

    # logger.addHandler: 구성한 핸들러를 로거에 연결합니다.
    # - 핸들러는 실제 로그를 출력하는 역할을 수행합니다.
    # - 같은 핸들러를 여러 번 추가하면 같은 로그가 중복 출력되니 주의가 필요합니다.
    logger.addHandler(console_handler)  # 이해가게 개념설명 알기쉽게 핵심 설명: 콘솔로 로그를 내보내는 도구를 로거에 붙여서 실제로 로그가 나오게 해요.

    # 파일 핸들러(선택): log_file이 주어지면 파일에도 로그를 남깁니다.
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")  # 이해가게 개념설명 알기쉽게 핵심 설명: 로그를 파일에 저장하는 도구를 만들어요.
        file_handler.setLevel(level)  # 이해가게 개념설명 알기쉽게 핵심 설명: 파일에 남길 로그의 최소 레벨을 정해요.
        file_handler.setFormatter(formatter)  # 이해가게 개념설명 알기쉽게 핵심 설명: 파일에 쓸 로그의 형식을 정해요.
        logger.addHandler(file_handler)  # 이해가게 개념설명 알기쉽게 핵심 설명: 파일로 로그를 남기도록 로거에 붙여요.

    # 반환: 구성된 로거를 반환합니다.
    # - 호출자는 반환된 로거로 logger.info(...) 같은 호출을 할 수 있습니다.
    return logger  # 이해가게 개념설명 알기쉽게 핵심 설명: 완성된 로거를 돌려줘서 다른 코드에서 로그를 남길 수 있게 해요.
