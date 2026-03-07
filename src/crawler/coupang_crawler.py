"""
쿠팡 상품 크롤러

쿠팡에서 키워드로 상품을 검색하고 정보를 수집합니다.
undetected-chromedriver를 사용하여 봇 감지를 우회합니다.
"""

import time
import random
from urllib.parse import quote
from typing import Optional

from .shopping_crawler import BaseShoppingCrawler, ProductData

# undetected-chromedriver 우선 사용, 없으면 일반 selenium
UNDETECTED_AVAILABLE = False
SELENIUM_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    UNDETECTED_AVAILABLE = True
    SELENIUM_AVAILABLE = True
except ImportError:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        SELENIUM_AVAILABLE = True
    except ImportError:
        pass


class CoupangCrawler(BaseShoppingCrawler):
    """쿠팡 상품 크롤러 (Selenium 기반)"""

    BASE_URL = "https://www.coupang.com"
    SEARCH_URL = "https://www.coupang.com/np/search?component=&q={keyword}&channel=user"

    # 랜덤 User-Agent 리스트
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def __init__(
        self,
        headless: bool = True,
        delay_range: tuple[float, float] = (1.0, 2.0),
        max_retries: int = 3
    ):
        """
        Args:
            headless: 헤드리스 모드 사용 여부
            delay_range: 요청 간 딜레이 범위 (초)
            max_retries: 최대 재시도 횟수
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium이 설치되어 있지 않습니다. "
                "pip install selenium webdriver-manager 로 설치해주세요."
            )

        self.headless = headless
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.driver: Optional[webdriver.Chrome] = None

    @property
    def source_name(self) -> str:
        return "coupang"

    def _get_random_user_agent(self) -> str:
        """랜덤 User-Agent 반환"""
        return random.choice(self.USER_AGENTS)

    def _init_driver(self):
        """WebDriver 초기화 (undetected-chromedriver 우선 사용)"""
        if self.driver is not None:
            return

        user_agent = self._get_random_user_agent()
        print(f"Using User-Agent: {user_agent[:50]}...")

        try:
            if UNDETECTED_AVAILABLE:
                # undetected-chromedriver 사용 (봇 감지 우회)
                options = uc.ChromeOptions()
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-extensions")
                options.add_argument(f"--user-agent={user_agent}")
                options.add_argument("--lang=ko-KR")

                self.driver = uc.Chrome(
                    options=options,
                    headless=self.headless,
                    use_subprocess=True,
                )
                print("Using undetected-chromedriver")
            else:
                # 일반 Selenium 사용
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager

                options = Options()
                if self.headless:
                    options.add_argument("--headless=new")

                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-extensions")
                options.add_argument(f"--user-agent={user_agent}")
                options.add_argument("--lang=ko-KR")

                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                print("Using standard Selenium")

            # JavaScript로 navigator.webdriver 숨기기
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })

        except Exception as e:
            print(f"ChromeDriver 초기화 실패: {e}")
            raise

    def _random_delay(self):
        """랜덤 딜레이 적용"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

    def _check_security_page(self) -> bool:
        """보안 확인 페이지 감지"""
        try:
            page_source = self.driver.page_source.lower()
            title = self.driver.title.lower() if self.driver.title else ""

            # 보안 확인 페이지 키워드
            security_keywords = [
                "access denied",
                "blocked",
                "접근이 거부",
                "차단",
                "captcha",
                "보안문자",
                "자동등록방지",
                "비정상적인 접근",
                "robot",
            ]

            for keyword in security_keywords:
                if keyword in page_source or keyword in title:
                    print(f"⚠️ 쿠팡 보안 페이지 감지: '{keyword}' 발견")
                    return True

            return False
        except:
            return False

    def search_products(self, keyword: str, max_results: int = 20) -> list[ProductData]:
        """쿠팡에서 키워드 검색

        Args:
            keyword: 검색 키워드
            max_results: 최대 결과 수

        Returns:
            상품 데이터 리스트

        Raises:
            Exception: 보안 페이지 감지 시 예외 발생
        """
        self._init_driver()
        products = []

        # 쿠팡 상품 선택자 (다양한 경우에 대응)
        PRODUCT_SELECTORS = [
            "li.search-product",
            "li[class*='search-product']",
            "ul.search-product-list > li",
            "div.search-product",
            "li[data-product-id]",
            "a.search-product-link",
        ]

        try:
            search_url = self.SEARCH_URL.format(keyword=quote(keyword))
            self.driver.get(search_url)
            self._random_delay()

            # 보안 페이지 체크
            if self._check_security_page():
                raise Exception("쿠팡 보안 페이지가 감지되었습니다. IP가 일시적으로 차단된 상태입니다. VPN 사용 또는 나중에 다시 시도해주세요.")

            # 페이지 로딩 대기 - 여러 선택자 시도
            page_loaded = False
            for selector in PRODUCT_SELECTORS:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    page_loaded = True
                    print(f"Found products with selector: {selector}")
                    break
                except:
                    continue

            if not page_loaded:
                print("페이지 로딩 실패 - 상품 요소를 찾을 수 없음")
                print(f"Page title: {self.driver.title}")
                return products

            # 스크롤하여 더 많은 상품 로드
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 3

            while len(products) < max_results and scroll_count < max_scrolls:
                # 여러 선택자로 상품 찾기
                product_items = []
                for selector in PRODUCT_SELECTORS:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        product_items = items
                        break

                for item in product_items:
                    if len(products) >= max_results:
                        break

                    try:
                        product = self._parse_product_item(item)
                        if product and product.product_id not in [p.product_id for p in products]:
                            products.append(product)
                    except Exception as e:
                        continue

                # 스크롤 다운
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self._random_delay()

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1

        except Exception as e:
            print(f"검색 오류: {e}")
            import traceback
            traceback.print_exc()

        return products[:max_results]

    def _parse_product_item(self, item) -> ProductData | None:
        """상품 아이템 파싱"""
        try:
            import hashlib

            # 상품 ID 추출
            product_id = item.get_attribute("data-product-id") or ""
            detail_url = ""

            # 링크에서 상품 ID 추출 시도
            LINK_SELECTORS = [
                "a.search-product-link",
                "a[href*='/vp/products/']",
                "a[href*='coupang.com']",
                "a",
            ]

            for selector in LINK_SELECTORS:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, selector)
                    href = link_elem.get_attribute("href") or ""
                    if href and "coupang" in href:
                        detail_url = href
                        if "/vp/products/" in href:
                            product_id = href.split("/vp/products/")[1].split("?")[0]
                        elif "/products/" in href:
                            product_id = href.split("/products/")[1].split("?")[0]
                        break
                except:
                    continue

            if not product_id and detail_url:
                product_id = hashlib.md5(detail_url.encode()).hexdigest()[:12]

            if not product_id:
                return None

            # 상품명
            TITLE_SELECTORS = [
                "div.name",
                "div[class*='name']",
                "a.search-product-link div",
                "div.product-name",
            ]

            title = ""
            for selector in TITLE_SELECTORS:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue

            # 가격
            PRICE_SELECTORS = [
                "strong.price-value",
                "em.sale",
                "span.price",
                "strong[class*='price']",
            ]

            price = ""
            for selector in PRICE_SELECTORS:
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, selector)
                    price = price_elem.text.strip()
                    if price:
                        break
                except:
                    continue

            # 이미지 URL
            IMG_SELECTORS = [
                "img.search-product-wrap-img",
                "img[class*='product']",
                "img[src*='coupang']",
                "img",
            ]

            image_url = ""
            for selector in IMG_SELECTORS:
                try:
                    img_elem = item.find_element(By.CSS_SELECTOR, selector)
                    image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-img-src") or ""
                    if image_url and "thumbnail" in image_url.lower():
                        break
                    if image_url:
                        break
                except:
                    continue

            if image_url.startswith("//"):
                image_url = "https:" + image_url

            # 평점
            rating = ""
            try:
                rating_elem = item.find_element(By.CSS_SELECTOR, "em.rating, span[class*='rating']")
                rating = rating_elem.text.strip()
            except:
                pass

            # 리뷰 수
            review_count = ""
            try:
                review_elem = item.find_element(By.CSS_SELECTOR, "span.rating-total-count, span[class*='count']")
                review_count = review_elem.text.strip().strip("()")
            except:
                pass

            if not title and not image_url:
                return None

            return ProductData(
                product_id=product_id,
                title=title,
                price=price,
                image_url=image_url,
                detail_url=detail_url,
                source=self.source_name,
                rating=rating,
                review_count=review_count,
                metadata={
                    "keyword_search": True
                }
            )

        except Exception as e:
            return None

    def get_product_detail(self, product_url: str) -> ProductData | None:
        """상품 상세 정보 수집 (미구현)"""
        # 필요시 구현
        return None

    def close(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __del__(self):
        self.close()
