from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

import os

from ..settings import Env
from ..utils.common import column_index_to_letter

class GoogleSheet:

    def __init__(self):
        self.service = self._init_service()
        self.keyword_range_name = f'{Env.SPREADSHEET_NAME}!{Env.KEYWORD_START_COLUMN}:{Env.KEYWORD_COLUMN}'
        self.popular_theme_range_name = f'{Env.SPREADSHEET_NAME}!{Env.POPULAR_THEME_START_COLUMN}:{Env.POPULAR_THEME_COLUMN}'
        self.title_keyword_range_name = f'{Env.SPREADSHEET_NAME}!{Env.TITLE_START_COLUMN}:{Env.TITLE_COLUMN}'
        self.adult_keyword_range_name = f'{Env.SPREADSHEET_NAME}!{Env.ADULT_KEYWORD_START_COLUMN}:{Env.ADULT_KEYWORD_COLUMN}'
        self.column_name_range_name = f'{Env.SPREADSHEET_NAME}!{Env.COLUMN_NAME_ROW}:{Env.COLUMN_NAME_ROW}'
        self.datetime_range_name = f'{Env.SPREADSHEET_NAME}!{Env.DATETIME_START_COLUMN}:{Env.DATETIME_COLUMN}'
        self._ensure_columns()
        self._get_today_column()
    

    def get_sheet_values(self):
        self.keywords = self._fetch_sheet_values(self.keyword_range_name)
        self.popular_themes = self._fetch_sheet_values(self.popular_theme_range_name)
        self.titles = self._fetch_sheet_values(self.title_keyword_range_name)
        self.adult_keywords = self._fetch_sheet_values(self.adult_keyword_range_name)
        self._set_values_length()

        not_adults, adults = self._grouping_adults()
        return not_adults, adults
        

    def set_result_values(self, ranks, datetimes):
        self._update_sheet_values(f'{Env.SPREADSHEET_NAME}!{self.insert_column}{Env.START_ROW}:{self.insert_column}', ranks)
        self._update_sheet_values(self.datetime_range_name, datetimes)


    def _update_sheet_values(self, range_name: str, values: list):
        body = { 'values': values }
        self.service.spreadsheets().values().update(
            spreadsheetId=Env.SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    

    def _fetch_sheet_values(self, range_name: str):
        if self.service == None: return []

        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=Env.SPREADSHEET_ID, range=range_name, ).execute()

        return result.get('values', [])
    

    def _init_service(self):
        credentials = None

        if os.path.exists(Env.SCOPE_FILENAME):
            credentials = Credentials.from_authorized_user_file(Env.SCOPE_FILENAME, Env.SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = flow = InstalledAppFlow.from_client_secrets_file('cred.json', Env.SCOPES)
                credentials = flow.run_local_server(port=0)

            with open(Env.SCOPE_FILENAME, 'w', encoding='utf-8') as token_file:
                token_file.write(credentials.to_json())
        
        return build('sheets', 'v4', credentials=credentials)
    
    
    def _get_today_column(self):
        month_day = f"{datetime.now().month}/{datetime.now().day}"
        column_names = self._fetch_sheet_values(self.column_name_range_name)
        
        index = column_names[0].index(month_day) if month_day in column_names[0] else -1

        if index != -1: self.insert_column = column_index_to_letter(index + 1)
        else: 
            self.insert_column = column_index_to_letter(len(column_names[0]) + 1)
            self._update_sheet_values(f'{Env.SPREADSHEET_NAME}!{self.insert_column}{Env.COLUMN_NAME_ROW}', [[month_day]])


    def _set_values_length(self):
        while len(self.popular_themes) < len(self.keywords): self.popular_themes.append([])
        while len(self.titles) < len(self.keywords): self.titles.append([])
        while len(self.adult_keywords) < len(self.keywords): self.adult_keywords.append([])

        for popular_theme in self.popular_themes:
            if len(popular_theme) == 0: popular_theme.append('')
        for title in self.titles:
            if len(title) == 0: title.append('')

    def _grouping_adults(self):
        notAdults, adults = [], []

        for index in range(0, len(self.keywords)):
            row = index + Env.START_ROW

            title = self.titles[index][0] if len(self.titles[index]) == 1 else ''
            keyword = self.keywords[index][0]
            popular_theme = self.popular_themes[index][0]
            rank = ''

            value = { 
                'row': row, 
                'title': title, 
                'keyword': keyword, 
                'popular_theme': popular_theme, 
                'rank': rank 
            }

            if len(self.adult_keywords[index]) == 0: notAdults.append(value)
            else: adults.append(value)

        return notAdults, adults
    

    def _get_sheet_meta(self):
        meta = self.service.spreadsheets().get(
            spreadsheetId=Env.SPREADSHEET_ID,
            fields="sheets(properties(sheetId,title,gridProperties(columnCount)))"
        ).execute()

        for sheet in meta["sheets"]:
            props = sheet["properties"]
            if props["title"] == Env.SPREADSHEET_NAME:
                return props["sheetId"], props["gridProperties"]["columnCount"]
            

    def _get_last_used_column(self):
        rng = f"{Env.SPREADSHEET_NAME}!{Env.COLUMN_NAME_ROW}:{Env.COLUMN_NAME_ROW}"
        response = self.service.spreadsheets().values().get(
            spreadsheetId=Env.SPREADSHEET_ID, range=rng, majorDimension="ROWS"
        ).execute()
        values = response.get("values", [[]])
        row = values[0] if values else []

        last = 0
        for index in range(len(row), 0, -1):
            if str(row[index-1]).strip() != "":
                last =index
                break
        return last
    

    def _ensure_columns(self, grow_by: int = 10):
        last_used = self._get_last_used_column()
        next_column = (last_used + 1) if last_used > 0 else 1

        sheet_id, col_count = self._get_sheet_meta()

        if next_column <= col_count:
            return

        add_length = (next_column + grow_by) - col_count
        body = {
            "requests": [{
                "appendDimension": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "length": add_length
                }
            }]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=Env.SPREADSHEET_ID,
            body=body
        ).execute()
