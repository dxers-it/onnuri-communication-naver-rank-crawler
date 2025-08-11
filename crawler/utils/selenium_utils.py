from selenium import webdriver

import random, time

def set_chrome_driver() -> webdriver.Chrome:
    """
    ChromeDriver 의 기본 옵션을 설정해서 반환합니다.
    - 자동화 탐지 방지 플래그
    - 로그 레벨, 시크릿 모드, 캐시 비활성화 등
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--log-level=3")
    options.add_argument("--incognito")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--disable-application-cache")
    return webdriver.Chrome(options=options)

def human_scroll(driver):
    height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(random.randint(2, 4)):
        delta = random.randint(height // 4, height // 2)
        driver.execute_script(f"window.scrollBy(0, {delta});")
        time.sleep(random.uniform(0.3, 0.6))