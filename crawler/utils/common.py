from datetime import datetime
from ..settings import Constant

import os, json

def get_korean_datetime_string():
    dt = datetime.now()

    am_pm = '오전' if dt.hour < 12 else '오후'

    hour = dt.hour % 12
    if hour == 0:
        hour = 12

    return f"{dt.year}. {dt.month}. {dt.day} {am_pm} {hour}:{dt.minute:02d}:{dt.second:02d}"

def compare_title(title, obj):
    return title.replace(' ', '').replace('"', '').replace("'", '') ==  normalize_text(obj['title']).replace(' ', '').replace('\r', '').replace('\n', '').replace(' ', '').replace('"', '').replace("'", '')

def compare_subject(subject: str, keyword: str):
    return subject.replace(' ', '').replace('"', '').replace("'", '') == normalize_text(keyword).replace(' ', '').replace('\r', '').replace('\n', '').replace(' ', '').replace('"', '').replace("'", '')

def saveJsonFile(obj, name):
    os.path.join('data', f'{name}.json')
    with open(f'{name}.json', 'w', encoding='utf-8') as f:
        json.dump(
            obj,
            f,
            ensure_ascii=False,
            indent=2
        )

def column_index_to_letter(index: int):
    letters = ''
    while index > 0:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters

def conversion_list(adults, not_adults):
    results = adults + not_adults
    start_row = min(result['row'] for result in results)
    end_row   = max(result['row'] for result in results)
    size = end_row - start_row + 1

    ranks, datetimes = [[''] for _ in range(size)], [[''] for _ in range(size)]

    for result in results:
        index = result['row'] - start_row
        ranks[index][0] = result['rank']
        datetimes[index][0] = result['datetime']

    return ranks, datetimes

def chunked(list):
    return [list[index: index + Constant.CHUNK_SIZE] for index in range(0, len(list), Constant.CHUNK_SIZE)]

import re
import unicodedata

ZERO_WIDTH = dict.fromkeys(map(ord, [
    "\u200b",  # zero width space
    "\u200c",  # zero width non-joiner
    "\u200d",  # zero width joiner
    "\ufeff",  # BOM
]), None)

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)

    # 1) 유니코드 정규화 (한글 조합 차이 제거)
    s = unicodedata.normalize("NFC", s)

    # 2) NBSP -> 일반 공백
    s = s.replace("\u00a0", " ")

    # 3) zero-width 제거
    s = s.translate(ZERO_WIDTH)

    # 4) 줄바꿈/탭 포함된 공백 정리
    s = re.sub(r"\s+", " ", s).strip()

    return s