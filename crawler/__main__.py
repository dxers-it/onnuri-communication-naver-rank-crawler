from .spiders.naver_spider import NaverSpider
import time

def main():
    start_time = time.time()

    spider = NaverSpider()
    spider.crawl()

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"총 실행 시간: {elapsed_time:.4f}초")

if __name__ == '__main__':
    main()