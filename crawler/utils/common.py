from datetime import datetime

import os, json

def get_korean_datetime_string():
    dt = datetime.now()

    am_pm = '오전' if dt.hour < 12 else '오후'

    hour = dt.hour % 12
    if hour == 0:
        hour = 12

    return f"{dt.year}. {dt.month}. {dt.day} {am_pm} {hour}:{dt.minute:02d}:{dt.second:02d}"

def compare_subject(subject: str, keyword: str):
    return subject.replace(' ', '') == keyword.replace(' ', '')

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