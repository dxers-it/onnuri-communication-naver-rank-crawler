import os
from dotenv import load_dotenv
load_dotenv()

def env_required(key: str, cast=str):
    value = os.getenv(key)
    if value is None:
        raise KeyError(f'Missing env: {key}')
    try:
        return cast(value) if cast else value
    except Exception as e:
        raise ValueError(f'{key}={value!r} cannot be cast to {cast.__name__}') from e

class SheetObject:

    def __init__(self, name: str):
        key = lambda string: f'{name}_{string}'

        self.sheet_id = env_required(key('SPREADSHEET_ID'))
        self.sheet_name = env_required(key('SHEET_NAME'))
        self.start_row = env_required(key('START_ROW'), int)
        self.column_name_row = env_required(key('COLUMN_NAME_ROW'), int)

        self.keyword_column = env_required(key('KEYWORD_COLUMN'))
        self.popular_theme_column = env_required(key('POPULAR_THEME_COLUMN'))
        self.title_column = env_required(key('TITLE_COLUMN'))
        self.login_column = env_required(key('LOGIN_COLUMN'))
        self.datetime_column = env_required(key('DATETIME_COLUMN'))

        self.keyword_start_column = f'{self.keyword_column}{self.start_row}'
        self.popular_theme_start_column = f'{self.popular_theme_column}{self.start_row}'
        self.title_start_column = f'{self.title_column}{self.start_row}'
        self.login_start_column = f'{self.login_column}{self.start_row}'
        self.datetime_start_column = f'{self.datetime_column}{self.start_row}'
