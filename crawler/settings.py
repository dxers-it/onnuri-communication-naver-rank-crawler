import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Env:
    SCOPE_FILENAME = os.getenv('SCOPE_FILENAME', 'token.json')
    SCOPES = [os.getenv('SCOPE', 'https://www.googleapis.com/auth/spreadsheets')]
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME')
    START_ROW = int(os.getenv('START_ROW'))
    KEYWORD_COLUMN = os.getenv('KEYWORD_COLUMN')
    KEYWORD_START_COLUMN = os.getenv('KEYWORD_COLUMN') + os.getenv('START_ROW')
    POPULAR_THEME_COLUMN = os.getenv('POPULAR_THEME_COLUMN')
    POPULAR_THEME_START_COLUMN = os.getenv('POPULAR_THEME_COLUMN') + os.getenv('START_ROW')
    TITLE_COLUMN = os.getenv('TITLE_COLUMN')
    TITLE_START_COLUMN = os.getenv('TITLE_COLUMN') + os.getenv('START_ROW')
    ADULT_KEYWORD_COLUMN = os.getenv('ADULT_KEYWORD_COLUMN')
    ADULT_KEYWORD_START_COLUMN = os.getenv('ADULT_KEYWORD_COLUMN') + os.getenv('START_ROW')
    DATETIME_COLUMN = os.getenv('DATETIME_COLUMN')
    DATETIME_START_COLUMN = os.getenv('DATETIME_COLUMN') + os.getenv('START_ROW')
    COLUMN_NAME_ROW = os.getenv('COLUMN_NAME_ROW')
    NAVER_LOGIN_URL = os.getenv('NAVER_LOGIN_URL')
    NAVER_ID = os.getenv('NAVER_ID')
    NAVER_PASSWORD = os.getenv('NAVER_PASSWORD')

class Constant:

    NAVER_ID_INPUT_ID = 'id'
    NAVER_PASSWORD_INPUT_ID = 'pw'

    NAVER_POPULAR_POST_CSS_SELECTOR = '[data-slog-container="ugB_bsR"]'
    NAVER_NAME_POPULAR_POST_CSS_SELECTOR = '[data-slog-container="ugB_qpR"]'
    NAVER_SMART_BLOCK_1_CSS_SELECTOR = '[data-slog-container="ugB_b1R"]'
    NAVER_SMART_BLOCK_2_CSS_SELECTOR = '[data-slog-container="ugB_b2R"]'
    NAVER_SMART_BLOCK_3_CSS_SELECTOR = '[data-slog-container="ugB_b3R"]'
    NAVER_SMART_BLOCK_4_CSS_SELECTOR = '[data-slog-container="ugB_b3R"]'
    NAVER_SMART_BLOCK_5_CSS_SELECTOR = '[data-slog-container="ugB_b3R"]'
    NAVER_ADULT_CLASS = 'group_adult'
    
    NAVER_OTHERS_BLOCK_CLASS = 'spw_rerank'
    
    @classmethod
    def SEARCH_URL(cls, keyword):
        return f'https://m.search.naver.com/search.naver?&query={quote_plus(keyword)}'
