from ..utils.common import get_korean_datetime_string, compare_title, compare_subject, conversion_list, chunked, saveJsonFile
from ..utils.selenium_utils import set_chrome_driver, human_scroll, fake_paste_events
from ..pipelines.google_sheets import GoogleSheet
from ..settings import Constant, Env

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import shutil

import time, random

class NaverSpider:
    """
    네이버 블로그 글 순위 스파이더(크롤러):
    - 
    """
    def __init__(self):
        
        print('==================== 🤗 네이버 블로그 순위 크롤링 시작 ====================')

        self.google_sheet_instance = GoogleSheet()
        self.not_adults, self.adults = self.google_sheet_instance.get_sheet_values()
        self.count = 0
        self.size = len(self.not_adults) + len(self.adults)


    def crawl(self):

        not_adults_chunks = chunked(self.not_adults)
        adult_chunks = chunked(self.adults)
        
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
           
            futures += [
                executor.submit(self._each_task, index, chunk)
                for index, chunk in enumerate(not_adults_chunks)
            ]
            futures += [
                executor.submit(self._each_task, index, chunk, self._login)
                for index, chunk in enumerate(adult_chunks, start=len(not_adults_chunks))
            ]

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        if all(results):
            ranks, datetimes = conversion_list(self.adults, self.not_adults)
            self.google_sheet_instance.set_result_values(ranks, datetimes)


    def _each_task(self, chunk_index, chunk_list, _login = None):
        tmp_profile = tempfile.mkdtemp(prefix=f"selenium_profile_{chunk_index}_")
        driver = set_chrome_driver(user_data_dir=tmp_profile, remote_debugging_port=9222 + chunk_index)
        if _login: _login(driver)

        try:
            for item in chunk_list: 
                self._check_rank(driver, item)
            return True
        except:
            return False
        finally:
            if driver:
                driver.quit()
            try:
                shutil.rmtree(tmp_profile, ignore_errors=True)
            except Exception:
                pass


    def _check_rank(self, driver, obj):

        driver.get(Constant.SEARCH_URL(obj['keyword']))

        human_scroll(driver)

        if obj['popular_theme'] == '' or obj['popular_theme'] == '인기글': self._check_view(obj, driver)
        elif obj['popular_theme'].replace(' ', '') == '인기카페글': self._check_cafe_view(obj, driver)
        elif '인플루언서콘텐츠' in obj['popular_theme'].replace(' ', ''): self._check_influencer_view(obj, driver)
        else: self._check_smart_view(obj, driver)



    def _login(self, driver):
        driver.get(Env.NAVER_LOGIN_URL)

        wait = WebDriverWait(driver, 10)

        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, Constant.NAVER_ID_INPUT_ELEMENT)))
        search_input.click()
        time.sleep(random.uniform(0.1, 0.3))

        fake_paste_events(driver, search_input, Env.NAVER_ID)

        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, Constant.NAVER_PASSWORD_INPUT_ELEMENT)))
        search_input.click()
        time.sleep(random.uniform(0.1, 0.3))

        fake_paste_events(driver, search_input, Env.NAVER_PASSWORD)

        search_input.send_keys(Keys.ENTER)
        time.sleep(2)
    

    def _check_view(self, obj, driver):

        section, selector = None, None
        selectors = [
            Constant.NAVER_POPULAR_POST_CSS_SELECTOR, 
            Constant.NAVER_NAME_POPULAR_POST_CSS_SELECTOR,
            Constant.NAVER_ADULT_CLASS
        ]

        for css_selector in selectors:
            try:
                section = driver.find_element(By.CSS_SELECTOR, css_selector)
                selector = css_selector
                break
            except:
                continue

        match selector:
            case Constant.NAVER_ADULT_CLASS: obj['rank'] = '성인 인증 확인 필요'
            case Constant.NAVER_POPULAR_POST_CSS_SELECTOR: self._check_popular_post(section, obj)
            case Constant.NAVER_NAME_POPULAR_POST_CSS_SELECTOR: self._check_name_popular_post(section, obj)
            case _: self._check_other_block(obj, driver)

        obj['datetime'] = get_korean_datetime_string()


    def _check_cafe_view(self, obj, driver):
        section, selector = None, None
        selectors = [
            Constant.NAVER_POPULAR_CAFE_POST_CSS_SELECTOR, 
            Constant.NAVER_ADULT_CLASS
        ]

        for css_selector in selectors:
            try:
                section = driver.find_element(By.CSS_SELECTOR, css_selector)
                selector = css_selector
                break
            except:
                continue

        match selector:
            case Constant.NAVER_ADULT_CLASS: obj['rank'] = '성인 인증 확인 필요'
            case Constant.NAVER_POPULAR_CAFE_POST_CSS_SELECTOR: self._check_name_popular_post(section, obj)

        obj['datetime'] = get_korean_datetime_string()


    def _check_influencer_view(self, obj, driver):
        section, selector = None, None
        selectors = [
            Constant.NAVER_POPULAR_INFLUENCER_POST_CSS_SELECTOR, 
            Constant.NAVER_ADULT_CLASS
        ]

        for css_selector in selectors:
            try:
                section = driver.find_element(By.CSS_SELECTOR, css_selector)
                selector = css_selector
                break
            except:
                continue

        match selector:
            case Constant.NAVER_ADULT_CLASS: obj['rank'] = '성인 인증 확인 필요'
            case Constant.NAVER_POPULAR_INFLUENCER_POST_CSS_SELECTOR: self._check_influencer_post(section, obj)

        obj['datetime'] = get_korean_datetime_string()


    def _check_popular_post(self, section, obj):
        
        list_view = section.find_element(By.CLASS_NAME, 'lst_view')
        lis = list_view.find_elements(By.CLASS_NAME, '_slog_visible')

        rank = 0
        for index in range(0, len(lis)):
            li = lis[index]
            title = li.find_element(By.CLASS_NAME, 'title_area').text
            if compare_title(title, obj):
                rank = index + 1
                break
        
        obj['rank'] = '' if rank == 0 else (f'{rank}')


    def _check_name_popular_post(self, section, obj):


        fds_ugc_block_mod_list = section.find_elements(
            By.CSS_SELECTOR,
            ".fds-ugc-block-mod-list > div:not(.fds-ugc-cross-keyword)"
        )

        rank = 0
        for index in range(0, len(fds_ugc_block_mod_list)):
            fds_ugc_block_mod = fds_ugc_block_mod_list[index]
            title = fds_ugc_block_mod.find_element(By.CLASS_NAME, 'fds-comps-right-image-text-title').text
        
            if compare_title(title, obj): 
                rank = index + 1
                break

        obj['rank'] = '' if rank == 0 else (f'{rank}')


    def _check_influencer_post(self, section, obj):
        ugcItemMo_list = section.find_elements(
            By.CSS_SELECTOR,
            '[data-template-id="ugcItemMo"]'
        )

        rank = 0
        for index in range(0, len(ugcItemMo_list)):
            ugcItemMo = ugcItemMo_list[index]

            title = ugcItemMo.find_element(By.CSS_SELECTOR, '.fds-comps-text.t0Gnpaae9B2Qr5RidZYS.ellipsis2').text
            
            if compare_title(title, obj): 
                rank = index + 1
                break

        obj['rank'] = '' if rank == 0 else (f'{rank}')


    def _check_smart_view(self, obj, driver):
        section, selector = None, None

        selectors = [
            Constant.NAVER_SMART_BLOCK_1_CSS_SELECTOR,
            Constant.NAVER_SMART_BLOCK_2_CSS_SELECTOR,
            Constant.NAVER_SMART_BLOCK_3_CSS_SELECTOR,
            Constant.NAVER_SMART_BLOCK_4_CSS_SELECTOR,
            Constant.NAVER_SMART_BLOCK_5_CSS_SELECTOR
        ]

        for css_selector in selectors:
            try:
                section = driver.find_element(By.CSS_SELECTOR, css_selector)
                subject = section.find_element(By.CLASS_NAME, 'fds-comps-header-headline').text
                if compare_subject(subject, obj['popular_theme']):
                    selector = css_selector
                    break
            except:
                continue
        
        match selector:
            case None: obj['rank'] = '블록X'
            case _: self._check_smart_block(section, obj)

        obj['datetime'] = get_korean_datetime_string()


    def _check_smart_block(self, section, obj):
        fds_ugc_block_mod_list = section.find_elements(
            By.CSS_SELECTOR,
            ".fds-ugc-block-mod-list > div:not(.fds-ugc-cross-keyword)"
        )

        rank = 0
        for index in range(0, len(fds_ugc_block_mod_list)):
            fds_ugc_block_mod = fds_ugc_block_mod_list[index]
            title = fds_ugc_block_mod.find_element(By.CLASS_NAME, 'fds-comps-right-image-text-title').text
            if compare_title(title, obj): 
                rank = index + 1
                break

        obj['rank'] = '' if rank == 0 else (f'{rank}')

    def _check_other_block(self, obj, driver):
        elements = []
        spw_reranks = driver.find_elements(By.CLASS_NAME, 'spw_rerank')

        for spw_rerank in spw_reranks:
            element_items = spw_rerank.find_elements(
                By.CSS_SELECTOR,
                '.sp_nreview, [data-slog-container="rrB_hdR"]'
            )
            elements.extend(element_items)

        title_classes = ['title_area', 'sds-comps-text-type-headline1']
        rank = 0

        for index in range(0, len(elements)):
            title = ''
            for title_class in title_classes:
                try:
                    title = elements[index].find_element(By.CLASS_NAME, title_class).text
                    break
                except:
                    continue
            if compare_title(title, obj): 
                rank = index + 1
                break
        
        obj['rank'] = '' if rank == 0 else (f'{rank}')
