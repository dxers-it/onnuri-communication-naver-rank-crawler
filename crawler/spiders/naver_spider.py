from ..utils.common import get_korean_datetime_string, compare_subject, conversion_list
from ..utils.selenium_utils import set_chrome_driver, human_scroll
from ..pipelines.google_sheets import GoogleSheet
from ..settings import Constant, Env

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time, pyautogui, pyperclip

class NaverSpider:
    """
    네이버 블로그 글 순위 스파이더(크롤러):
    - 
    """
    def __init__(self):
        
        print('==================== 🤗 네이버 블로그 순위 크롤링 시작 ====================')

        self.google_sheet_instance = GoogleSheet()
        self.driver = set_chrome_driver()
        self.not_adults, self.adults = self.google_sheet_instance.get_sheet_values()
        self.count = 0
        self.size = len(self.not_adults) + len(self.adults)


    def crawl(self):
        for notAdult in self.not_adults: self._check_rank(notAdult)
        self._login()
        for adult in self.adults: self._check_rank(adult)

        ranks, datetimes = conversion_list(self.adults, self.not_adults)
        self.google_sheet_instance.set_result_values(ranks, datetimes)
        # saveJsonFile(self.not_adults, 'not_adults')
        # saveJsonFile(self.adults, 'adult')


    def _check_rank(self, obj):
        self.count += 1
        print(f'========== [{self.count} / {self.size}] ==========')

        self.driver.get(Constant.SEARCH_URL(obj['keyword']))
        time.sleep(1.2)

        human_scroll(self.driver)

        match obj['popular_theme']:
            case '' | '인기글': self._check_view(obj)
            case _: self._check_smart_view(obj)


    def _login(self):
        self.driver.get(Env.NAVER_LOGIN_URL)

        search_input = self.driver.find_element(By.ID, Constant.NAVER_ID_INPUT_ID)
        search_input.click()
        pyperclip.copy(Env.NAVER_ID)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)

        search_input = self.driver.find_element(By.ID, Constant.NAVER_PASSWORD_INPUT_ID)
        search_input.click()
        pyperclip.copy(Env.NAVER_PASSWORD)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)

        search_input.send_keys(Keys.ENTER)
        time.sleep(2)
    

    def _check_view(self, obj):
        section, selector = None, None
        selectors = [
            Constant.NAVER_POPULAR_POST_CSS_SELECTOR, 
            Constant.NAVER_NAME_POPULAR_POST_CSS_SELECTOR,
            Constant.NAVER_ADULT_CLASS
        ]

        for css_selector in selectors:
            try:
                section = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                selector = css_selector
                break
            except:
                continue

        match selector:
            case Constant.NAVER_ADULT_CLASS: obj['rank'] = '성인 인증 확인 필요'
            case Constant.NAVER_POPULAR_POST_CSS_SELECTOR: self._check_popular_post(section, obj)
            case Constant.NAVER_NAME_POPULAR_POST_CSS_SELECTOR: self._check_name_popular_post(section, obj)
            case _: self._check_other_block(obj)

        obj['datetime'] = get_korean_datetime_string()


    def _check_popular_post(self, section, obj):
        list_view = section.find_element(By.CLASS_NAME, 'lst_view')
        lis = list_view.find_elements(By.CLASS_NAME, '_slog_visible')

        rank = 0
        for index in range(0, len(lis)):
            li = lis[index]
            title = li.find_element(By.CLASS_NAME, 'title_area').text
            if title == obj['title']:
                rank = index + 1
                break
        
        obj['rank'] = '' if rank == 0 else (f'{rank}위')


    def _check_name_popular_post(self, section, obj):

        fds_ugc_block_mod_list = section.find_elements(
            By.CSS_SELECTOR,
            ".fds-ugc-block-mod-list > div:not(.fds-ugc-cross-keyword)"
        )

        rank = 0
        for index in range(0, len(fds_ugc_block_mod_list)):
            fds_ugc_block_mod = fds_ugc_block_mod_list[index]
            title = fds_ugc_block_mod.find_element(By.CLASS_NAME, 'fds-comps-right-image-text-title').text
            if title == obj['title']: 
                rank = index + 1
                break

        obj['rank'] = '' if rank == 0 else (f'{rank}위')


    def _check_smart_view(self, obj):
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
                section = self.driver.find_element(By.CSS_SELECTOR, css_selector)
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
            if title == obj['title']: 
                rank = index + 1
                break

        obj['rank'] = '' if rank == 0 else (f'{rank}위')

    def _check_other_block(self, obj):
        elements = []
        spw_reranks = self.driver.find_elements(By.CLASS_NAME, 'spw_rerank')

        for spw_rerank in spw_reranks:
            elements = spw_rerank.find_elements(
                By.XPATH,
                '//*[@class="sp_nreview" or @data-slog-container="rrB_hdR"]'
            )
            elements.append('elements')

        title_classes = ['title_area', 'sds-comps-text-type-headline1']
        rank = 0

        for index in range(0, len(elements)):
            title = ''
            for title_class in title_classes:
                try:
                    title = elements[index].find_element(By.CLASS_NAME, title_class)
                    break
                except:
                    continue
            if title == obj['title']: 
                rank = index + 1
                break
        
        obj['rank'] = '' if rank == 0 else (f'{rank}위')
