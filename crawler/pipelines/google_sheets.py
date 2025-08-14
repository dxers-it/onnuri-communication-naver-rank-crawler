from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

import os

from ..settings import Env
from ..utils.common import column_index_to_letter

class GoogleSheet:

    def __init__(self, sheet_obj):
        self.service = self._init_service()
        self.sheet_obj = sheet_obj
        self.sheet_id = sheet_obj.sheet_id
        self.keyword_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.keyword_start_column}:{sheet_obj.keyword_column}'
        self.popular_theme_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.popular_theme_start_column}:{sheet_obj.popular_theme_column}'
        self.title_keyword_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.title_start_column}:{sheet_obj.title_column}'
        self.login_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.login_start_column}:{sheet_obj.login_column}'
        self.column_name_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.column_name_row}:{sheet_obj.column_name_row}'
        self.datetime_range_name = f'{sheet_obj.sheet_name}!{sheet_obj.datetime_start_column}:{sheet_obj.datetime_column}'
        self._ensure_columns()
        self._get_today_column()
    

    def get_sheet_values(self):
        self.keywords = self._fetch_sheet_values(self.keyword_range_name)
        self.popular_themes = self._fetch_sheet_values(self.popular_theme_range_name)
        self.titles = self._fetch_sheet_values(self.title_keyword_range_name)
        self.login_keywords = self._fetch_sheet_values(self.login_range_name)
        self._set_values_length()

        not_logins, logins = self._grouping_logins()
        return not_logins, logins
        

    def set_result_values(self, ranks, datetimes):
        self._update_sheet_values(f'{self.sheet_obj.sheet_name}!{self.insert_column}{self.sheet_obj.start_row}:{self.insert_column}', ranks)
        self._update_sheet_values(self.datetime_range_name, datetimes)


    def _update_sheet_values(self, range_name: str, values: list):
        body = { 'values': values }
        self.service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    

    def _fetch_sheet_values(self, range_name: str):
        if self.service == None: return []

        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.sheet_id, range=range_name, ).execute()

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
            self._update_sheet_values(f'{self.sheet_obj.sheet_name}!{self.insert_column}{self.sheet_obj.column_name_row}', [[month_day]])


    def _set_values_length(self):
        while len(self.popular_themes) < len(self.keywords): self.popular_themes.append([])
        while len(self.titles) < len(self.keywords): self.titles.append([])
        while len(self.login_keywords) < len(self.keywords): self.login_keywords.append([])

        for popular_theme in self.popular_themes:
            if len(popular_theme) == 0: popular_theme.append('')
        for title in self.titles:
            if len(title) == 0: title.append('')

    def _grouping_logins(self):
        not_logins, logins = [], []

        for index in range(0, len(self.keywords)):
            row = index + self.sheet_obj.start_row

            title = self.titles[index][0] if len(self.titles[index]) == 1 else ''
            keyword = self.keywords[index][0]
            popular_theme = self.popular_themes[index][0]
            rank = ''

            value = { 
                'row': row, 
                'title': title.replace(' ', '').replace('\r', '').replace('\n', '').replace(' ', ''), 
                'keyword': keyword, 
                'popular_theme': popular_theme.replace(' ', '').replace('\r', '').replace('\n', '').replace(' ', '') ,
                'rank': rank 
            }

            if len(self.login_keywords[index]) == 0: not_logins.append(value)
            else: logins.append(value)

        return not_logins, logins
    

    def _get_sheet_meta(self):
        meta = self.service.spreadsheets().get(
            spreadsheetId=self.sheet_id,
            fields="sheets(properties(sheetId,title,gridProperties(columnCount)))"
        ).execute()

        for sheet in meta["sheets"]:
            props = sheet["properties"]
            if props["title"] == self.sheet_obj.sheet_name:
                return props["sheetId"], props["gridProperties"]["columnCount"]
            

    def _get_last_used_column(self):
        rng = f"{self.sheet_obj.sheet_name}!{self.sheet_obj.column_name_row}:{self.sheet_obj.column_name_row}"
        response = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=rng, majorDimension="ROWS"
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
            spreadsheetId=self.sheet_id,
            body=body
        ).execute()
