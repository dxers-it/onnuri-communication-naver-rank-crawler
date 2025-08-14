from .spiders.naver_spider import NaverSpider
from .settings import Env
import time

def main():
    start_time = time.time()

    spiders = [NaverSpider(Env.INST_OBJ), NaverSpider(Env.NEWTRI_OBJ)]
    for spider in spiders: spider.crawl()

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"총 실행 시간: {elapsed_time // 60}분 {(elapsed_time % 60):.4f}초")

if __name__ == '__main__':
    main()