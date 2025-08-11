# 네이버 랭크 크롤러

## 📖 프로젝트 Overview
(주)온누리커뮤니케이션의 네이버 키워드에 따른 블로그 순위 확인 크롤러  
Version: 1.0.0

---

## 🚀 실행

### Prerequisites
- Python 3.8 이상

### 설치
```bash
# 
git clone https://github.com/dxersit/onnuri-communication-naver-rank-crawler.git
cd onnuri-communication-naver-rank-crawler

# 의존성 설치
pip install -r requirements.txt
# or
pip install python-dotenv selenium pyautogui pyperclip google-auth google-auth-oauthlib google-api-python-client


```

---

## ⚙️ 환경 변수
`.env` 파일을 프로젝트 루트에 생성하고 다음 예시를 참고하여 환경변수를 설정하세요.
```env
## 스프레드 시트 아이디 ##
SPREADSHEET_ID='스프레드 시트 아이디'
## 스프레드 시트 이름 ##
SPREADSHEET_NAME='스프레드 시트 이름'

## 컬럼 이름 행 번호 ##
COLUMN_NAME_ROW=컬럼 이름 행 번호
## 데이터 입력 첫 행 번호 ##
START_ROW=데이터 입력 첫 행 번호
## 검색 키워드 열 이름 ##
KEYWORD_COLUMN='검색 키워드 열 이름'
## 인기 주제 열 이름 ##
POPULAR_THEME_COLUMN='인기 주제 열 이름'
## 제목 열 이름 ##
TITLE_COLUMN='제목 열 이름'
## 성인키 열 이름 ##
ADULT_KEYWORD_COLUMN='성인키 열 이름'
## 확인시각 열 이름 ##
DATETIME_COLUMN='확인시각 열 이름'

## 네이버 아이디 ##
NAVER_ID='네이버 아이디'
## 네이버 비밀번호 ##
NAVER_PASSWORD='네이버 비밀번호'


#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
VERSION='1.0.0'
SCOPE_FILENAME='token.json'
SCOPE='https://www.googleapis.com/auth/spreadsheets'
NAVER_LOGIN_URL='https://nid.naver.com/nidlogin.login'
#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
#################### DO NOT CHANGE ####################
```

---

## 🏃‍♀️ 크롤러 실행
```bash
python -m crawler
```

---

## 📂 프로젝트 구조
```
crawler_project/
├── crawler/
│   ├── spiders/
│   ├── pipelines/
│   └── settings.py
├── logs/
├── requirements.txt
└── README.md
```

---

## 📈 출력
- `logs/` 디렉터리에 크롤링 로그 저장  

---

## 📄 라이센스
[MIT](https://opensource.org/licenses/MIT)
