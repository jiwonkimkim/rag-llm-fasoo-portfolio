"""
네이버 쇼핑 상품 크롤러

네이버 쇼핑에서 키워드로 상품을 검색하고 정보를 수집합니다.
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
    from selenium.webdriver.common.keys import Keys
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
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        SELENIUM_AVAILABLE = True
    except ImportError:
        pass


class NaverShoppingCrawler(BaseShoppingCrawler):
    """네이버 쇼핑 상품 크롤러 (Selenium 기반)"""

    BASE_URL = "https://search.shopping.naver.com"
    SEARCH_URL = "https://search.shopping.naver.com/search/all?query={keyword}"

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
        return "naver"

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
                "보안 확인",
                "접속이 일시적으로 제한",
                "비정상적인 접근",
                "captcha",
                "보안문자",
                "자동등록방지",
                "access denied",
                "blocked",
            ]

            for keyword in security_keywords:
                if keyword in page_source or keyword in title:
                    print(f"⚠️ 보안 페이지 감지: '{keyword}' 발견")
                    return True

            # content_error 클래스 확인 (네이버 차단 페이지)
            if "content_error" in page_source:
                print("⚠️ 네이버 접속 제한 페이지 감지")
                return True

            return False
        except:
            return False

    def search_products(self, keyword: str, max_results: int = 20) -> list[ProductData]:
        """네이버 쇼핑에서 키워드 검색

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

        # 다양한 선택자 시도 (네이버 쇼핑 HTML 구조가 자주 변경됨)
        PRODUCT_SELECTORS = [
            "div[class*='product_item']",
            "div[class*='basicList_item']",
            "li[class*='product_item']",
            "div[class*='adProduct_item']",
            "ul[class*='list'] > li",
            "div.product_info_area",
        ]

        try:
            # 1. 네이버 쇼핑 홈페이지 접속
            print("네이버 쇼핑 홈페이지 접속 중...")
            self.driver.get("https://shopping.naver.com")
            self._random_delay()

            # 보안 페이지 체크
            if self._check_security_page():
                raise Exception("네이버 쇼핑 보안 확인 페이지가 감지되었습니다. IP가 일시적으로 차단된 상태입니다. VPN 사용 또는 나중에 다시 시도해주세요.")

            # 2. 검색창에 키워드 입력 후 엔터
            print(f"검색어 입력: {keyword}")
            try:
                # 검색창 찾기 (여러 선택자 시도)
                search_input = None
                SEARCH_INPUT_SELECTORS = [
                    "#input_text",
                    "input[type='search']",
                    "input[placeholder*='검색']",
                    "input[name='query']",
                ]

                for selector in SEARCH_INPUT_SELECTORS:
                    try:
                        search_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        print(f"검색창 발견: {selector}")
                        break
                    except:
                        continue

                if search_input:
                    search_input.clear()
                    search_input.send_keys(keyword)
                    self._random_delay()
                    search_input.send_keys(Keys.ENTER)
                    self._random_delay()
                    print("검색 실행 완료")
                else:
                    # 검색창을 못 찾으면 URL 직접 접근
                    print("검색창을 찾지 못해 URL 직접 접근")
                    search_url = self.SEARCH_URL.format(keyword=quote(keyword))
                    self.driver.get(search_url)
                    self._random_delay()

            except Exception as e:
                print(f"검색창 입력 실패: {e}, URL 직접 접근")
                search_url = self.SEARCH_URL.format(keyword=quote(keyword))
                self.driver.get(search_url)
                self._random_delay()

            # 검색 후 보안 페이지 체크
            if self._check_security_page():
                raise Exception("네이버 쇼핑 보안 확인 페이지가 감지되었습니다. IP가 일시적으로 차단된 상태입니다. VPN 사용 또는 나중에 다시 시도해주세요.")

            # 3. 페이지 로딩 대기 - 여러 선택자 시도
            page_loaded = False
            for selector in PRODUCT_SELECTORS:
                try:
                    WebDriverWait(self.driver, 10).until(
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

            # 상품 링크에서 ID 추출 - 여러 선택자 시도
            LINK_SELECTORS = [
                "a[href*='catalog']",
                "a[href*='smartstore']",
                "a[href*='shopping.naver']",
                "a[class*='product_link']",
                "a[class*='thumb']",
                "a",
            ]

            detail_url = ""
            product_id = ""

            for selector in LINK_SELECTORS:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, selector)
                    detail_url = link_elem.get_attribute("href") or ""
                    if detail_url and "naver" in detail_url:
                        break
                except:
                    continue

            if not detail_url:
                return None

            # URL에서 상품 ID 추출
            if "catalog/" in detail_url:
                product_id = detail_url.split("catalog/")[1].split("?")[0]
            elif "products/" in detail_url:
                product_id = detail_url.split("products/")[1].split("?")[0]
            else:
                product_id = hashlib.md5(detail_url.encode()).hexdigest()[:12]

            # 상품명 - 여러 선택자 시도
            TITLE_SELECTORS = [
                "a[class*='product_link']",
                "div[class*='title'] a",
                "a[class*='title']",
                "span[class*='title']",
                "div[class*='name']",
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

            # 가격 - 여러 선택자 시도
            PRICE_SELECTORS = [
                "span[class*='price_num']",
                "span[class*='price'] em",
                "em[class*='price']",
                "span[class*='num']",
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

            # 이미지 URL - 여러 선택자 시도
            IMG_SELECTORS = [
                "img[class*='product_img']",
                "img[class*='thumbnail']",
                "img[class*='thumb']",
                "img[src*='shopping-phinf']",
                "img",
            ]

            image_url = ""
            for selector in IMG_SELECTORS:
                try:
                    img_elem = item.find_element(By.CSS_SELECTOR, selector)
                    image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
                    if image_url and ("shopping" in image_url or "naver" in image_url):
                        break
                except:
                    continue

            if image_url.startswith("//"):
                image_url = "https:" + image_url

            # 평점
            rating = ""
            try:
                rating_elem = item.find_element(By.CSS_SELECTOR, "span[class*='grade'], span[class*='rating']")
                rating = rating_elem.text.strip()
            except:
                pass

            # 리뷰 수
            review_count = ""
            try:
                review_elem = item.find_element(By.CSS_SELECTOR, "span[class*='etc'], span[class*='review']")
                review_count = review_elem.text.strip()
            except:
                pass

            # 판매처
            seller = ""
            try:
                seller_elem = item.find_element(By.CSS_SELECTOR, "span[class*='mall'], a[class*='mall']")
                seller = seller_elem.text.strip()
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
                    "keyword_search": True,
                    "seller": seller
                }
            )

        except Exception as e:
            return None

    def get_product_detail(self, product_url: str) -> ProductData | None:
        """상품 상세 정보 수집 (미구현)"""
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
