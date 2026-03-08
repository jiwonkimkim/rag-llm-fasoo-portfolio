"""
이미지 다운로더 모듈

상품 이미지를 다운로드하고 로컬에 저장/관리합니다.
"""

import os
import json
import hashlib
import requests
import socket
import ipaddress
import logging
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any
from urllib.parse import urlparse
import uuid

logger = logging.getLogger(__name__)


@dataclass
class DownloadedImage:
    """다운로드된 이미지 정보"""
    id: str
    original_url: str
    local_path: str
    filename: str
    size_bytes: int
    product_id: str
    product_title: str
    source: str
    downloaded_at: str
    metadata: dict[str, Any]


class ImageDownloader:
    """이미지 다운로드 및 관리 클래스"""

    def __init__(self, base_dir: str = "data/images"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / "metadata.json"
        self._load_metadata()

    def _sanitize_segment(self, value: str, fallback: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", (value or "").strip())
        sanitized = sanitized.strip("._-")
        return sanitized[:64] if sanitized else fallback

    def _resolve_local_path(self, local_path: str) -> Path | None:
        base_resolved = self.base_dir.resolve()
        candidate = (self.base_dir / local_path).resolve()
        try:
            candidate.relative_to(base_resolved)
        except ValueError:
            return None
        return candidate

    def _load_metadata(self):
        """메타데이터 파일 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {"images": {}}

    def _save_metadata(self):
        """메타데이터 파일 저장"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, ensure_ascii=False, indent=2)

    def _get_file_extension(self, url: str, content_type: str = "") -> str:
        """URL 또는 Content-Type에서 파일 확장자 추출"""
        # Content-Type 우선
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
        elif "png" in content_type:
            return ".png"
        elif "gif" in content_type:
            return ".gif"
        elif "webp" in content_type:
            return ".webp"

        # URL에서 추출
        url_lower = url.lower().split("?")[0]
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            if url_lower.endswith(ext):
                return ext if ext != ".jpeg" else ".jpg"

        return ".jpg"  # 기본값

    def _generate_filename(self, url: str, product_id: str) -> str:
        """URL 해시 기반 파일명 생성"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"{product_id}_{url_hash}"

    def _is_blocked_host(self, hostname: str) -> bool:
        """Return True when hostname resolves to local/private networks."""
        blocked_names = {"localhost", "127.0.0.1", "::1", "metadata.google.internal"}
        if not hostname:
            return True
        normalized = hostname.strip().lower()
        if normalized in blocked_names or normalized.endswith(".local"):
            return True

        try:
            infos = socket.getaddrinfo(normalized, None)
        except socket.gaierror:
            return True

        for info in infos:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return True
        return False

    def _validate_image_url(self, url: str) -> bool:
        """Validate URL to reduce SSRF risk."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        return not self._is_blocked_host(parsed.hostname or "")

    def download_image(
        self,
        url: str,
        product_id: str,
        product_title: str,
        source: str,
        metadata: dict[str, Any] = None
    ) -> DownloadedImage | None:
        """이미지 다운로드 및 저장

        Args:
            url: 이미지 URL
            product_id: 상품 ID
            product_title: 상품 제목
            source: 출처 (coupang, naver)
            metadata: 추가 메타데이터

        Returns:
            다운로드된 이미지 정보 또는 None
        """
        try:
            if not self._validate_image_url(url):
                logger.warning("Blocked image download from unsafe URL: %s", url)
                return None

            # 요청 헤더 설정
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Referer": f"https://www.{source}.com/",
            }

            response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                logger.warning("Blocked non-image response from URL: %s (%s)", url, content_type)
                return None
            safe_source = self._sanitize_segment(source, "unknown")
            safe_product_id = self._sanitize_segment(product_id, "item")
            ext = self._get_file_extension(url, content_type)
            filename = self._generate_filename(url, safe_product_id) + ext

            # 날짜별 디렉토리 생성
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_dir = self.base_dir / safe_source / date_str
            save_dir.mkdir(parents=True, exist_ok=True)

            file_path = save_dir / filename

            # 이미지 저장
            with open(file_path, "wb") as f:
                f.write(response.content)

            # 이미지 정보 생성
            image_id = str(uuid.uuid4())[:8]
            downloaded_image = DownloadedImage(
                id=image_id,
                original_url=url,
                local_path=file_path.resolve().relative_to(self.base_dir.resolve()).as_posix(),
                filename=filename,
                size_bytes=len(response.content),
                product_id=safe_product_id,
                product_title=product_title,
                source=safe_source,
                downloaded_at=datetime.now().isoformat(),
                metadata=metadata or {}
            )

            # 메타데이터 저장
            self._metadata["images"][image_id] = asdict(downloaded_image)
            self._save_metadata()

            return downloaded_image

        except Exception as e:
            logger.exception("Error downloading image %s: %s", url, e)
            return None

    def list_images(
        self,
        source: str = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[list[DownloadedImage], int]:
        """저장된 이미지 목록 조회

        Args:
            source: 필터링할 소스 (선택)
            page: 페이지 번호
            page_size: 페이지 크기

        Returns:
            (이미지 목록, 전체 개수)
        """
        images = list(self._metadata["images"].values())

        # 소스 필터링
        if source:
            images = [img for img in images if img["source"] == source]

        # 최신순 정렬
        images.sort(key=lambda x: x["downloaded_at"], reverse=True)

        total = len(images)

        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        paginated = images[start:end]

        return [DownloadedImage(**img) for img in paginated], total

    def get_image(self, image_id: str) -> DownloadedImage | None:
        """이미지 정보 조회"""
        if image_id in self._metadata["images"]:
            return DownloadedImage(**self._metadata["images"][image_id])
        return None

    def get_image_path(self, image_id: str) -> Path | None:
        """이미지 파일 경로 반환"""
        if image_id in self._metadata["images"]:
            return self._resolve_local_path(self._metadata["images"][image_id]["local_path"])
        return None

    def delete_images(self, image_ids: list[str]) -> int:
        """이미지 삭제

        Args:
            image_ids: 삭제할 이미지 ID 목록

        Returns:
            삭제된 개수
        """
        deleted_count = 0

        for image_id in image_ids:
            if image_id in self._metadata["images"]:
                image_info = self._metadata["images"][image_id]
                file_path = self._resolve_local_path(image_info["local_path"])

                # 파일 삭제
                try:
                    if file_path and file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    logger.exception("Error deleting file %s: %s", file_path, e)

                # 메타데이터에서 제거
                del self._metadata["images"][image_id]
                deleted_count += 1

        self._save_metadata()
        return deleted_count

    def clear_all(self) -> int:
        """모든 이미지 삭제"""
        image_ids = list(self._metadata["images"].keys())
        return self.delete_images(image_ids)
