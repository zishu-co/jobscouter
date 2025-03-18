from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

class SeleniumCrawler:
    def __init__(self):
        # 配置Chrome选项
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # 添加随机User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # 设置显式等待时间为10秒

    def fetch_data(self, url):
        try:
            self.driver.get(url)
            
            # 等待页面加载完成（这里需要根据实际网页调整等待条件）
            # 例如等待某个特定元素出现
            # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'target-class')))
            
            # 随机等待1-3秒
            time.sleep(random.uniform(1, 3))
            
            # 这里添加数据提取逻辑
            # 例如：
            # elements = self.driver.find_elements(By.CLASS_NAME, 'target-class')
            # data = [element.text for element in elements]
            
            print("数据获取成功!")
            return True
            
        except Exception as e:
            print(f"爬取失败: {str(e)}")
            return False
        
    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    crawler = SeleniumCrawler()
    try:
        # 这里替换成您要爬取的网址
        # url = "https://www.zhipin.com/web/geek/job?query=字节跳动&city=100010000&position=100101"
        url = "https://www.baidu.com/"
        crawler.fetch_data(url)
        print(crawler)
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 