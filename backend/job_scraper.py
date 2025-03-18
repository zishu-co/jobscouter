# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import time

from selenium.common.exceptions import  TimeoutException
import urllib.parse

class JobScraper:
    _instance = None
    _request_count = 0
    MAX_REQUESTS = 100  # 最大请求次数
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            print("初始化 JobScraper 实例...")
            self._setup_driver()
            self._initialized = True
            
            # 添加延时配置
            self.min_delay = 5  # 最小延时秒数
            self.max_delay = 10  # 最大延时秒数
    
    def _setup_driver(self):
        """初始化或重新初始化Chrome驱动"""
        self.chrome_options = Options()
        #self.chrome_options.add_argument('--headless=new')  # 使用新的无头模式
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--remote-debugging-pipe')
        # self.chrome_options.add_argument('--proxy-server=http://222.219.133.18:8008')

        # 添加更多必要的参数
        # self.chrome_options.add_argument('--disable-extensions')
        # self.chrome_options.add_argument('--disable-setuid-sandbox')
        # self.chrome_options.add_argument('--disable-infobars')
        # self.chrome_options.add_argument('--remote-debugging-port=9222')
        # self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # self.chrome_options.add_argument('--start-maximized')
        
        # 添加必要的属性
        self.base_url = "https://www.zhipin.com/web/geek/job"
        
        try:
            if hasattr(self, '_driver'):
                self._driver.quit()
            
            # 使用系统安装的 ChromeDriver
            service = webdriver.ChromeService()
            self._driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options
            )
            print(f"Chrome驱动初始化完成")
            self._request_count = 0
        except Exception as e:
            print(f"Chrome驱动初始化失败: {str(e)}")
            raise
    
    def _init_page_settings(self):
        """初始化页面设置"""
        try:
            # 设置 localStorage
            self._driver.execute_script("""
                window.localStorage.setItem('_bl_uid', '5Lkgj4ROm6q2XwvXs9Uw8j9gFzOL');
            """)
        except Exception as e:
            print(f"设置 localStorage 失败: {str(e)}")
    
    def _check_driver_health(self):
        """检查驱动是否需要重启"""
        self._request_count += 1
        if self._request_count >= self.MAX_REQUESTS:
            print(f"请求次数达到{self.MAX_REQUESTS}次，重启Chrome驱动...")
            self._setup_driver()
    
   
    
    
    def fetch_jobs_by_page(self, url):
        """获取单页职位信息"""
        try:
            # 访问页面
            self._driver.get(url)
            
            # 设置等待时间
            wait = WebDriverWait(self._driver, timeout=15, poll_frequency=0.5)
            
            try:
                # 先等待职位列表或空结果出现
                wait.until(lambda driver: 
                    len(driver.find_elements(By.CLASS_NAME, "job-card-wrapper")) > 0 or 
                    len(driver.find_elements(By.CLASS_NAME, "job-empty-wrapper")) > 0 or
                    len(driver.find_elements(By.CLASS_NAME, "wrap-verify-slider")) > 0
                )
                
                # 检查是否出现验证码
                verify_sliders = self._driver.find_elements(By.CLASS_NAME, "wrap-verify-slider")
                if verify_sliders and len(verify_sliders) > 0:
                    print("检测到验证码，需要人工验证")
                    return { "status": "verify", "data": [] }
                
                # 检查是否有职位列表
                job_cards = self._driver.find_elements(By.CLASS_NAME, "job-card-wrapper")
                if job_cards and len(job_cards) > 0:
                    # 提取职位数据
                    jobs_data = self._driver.execute_script("""
                        return Array.from(document.querySelectorAll('.job-card-wrapper')).map(card => ({
                            title: card.querySelector('.job-name').textContent.trim(),
                            salary: card.querySelector('.salary').textContent.trim(),
                            company: card.querySelector('.company-name').textContent.trim(),
                            location: card.querySelector('.job-area').textContent.trim(),
                            tags: Array.from(card.querySelector('.tag-list').querySelectorAll('li')).map(li => li.textContent.trim()),
                            job_link: card.querySelector('a.job-card-left').href
                        }));
                    """)
                    
                    return { "status": "success", "data": jobs_data }
                
                # 如果没有职位列表，检查是否是无数据
                empty_results = self._driver.find_elements(By.CLASS_NAME, "job-empty-wrapper")
                if empty_results and len(empty_results) > 0:
                    print("没有找到相关职位")
                    return { "status": "empty", "data": [] }
                
            except TimeoutException:
                print(f"页面加载超时: {url}")
                return { "status": "timeout", "data": [] }
            except Exception as e:
                print(f"获取职位列表失败: {str(e)}")
                return { "status": "error", "data": [] }
            
        except Exception as e:
            print(f"访问页面失败: {str(e)}")
            return { "status": "error", "data": [] }
    
    def fetch_jobs(self, keyword, city, max_pages=10):
        """获取多页职位信息"""
        all_jobs = []
        
        try:
            # 构建基础URL
            encoded_query = urllib.parse.quote(keyword)
            base_url = f"{self.base_url}?query={encoded_query}&city={city}"
            print(f"开始获取职位列表，基础URL: {base_url}")
            
            self._check_driver_health()  # 检查驱动健康状况
            
            # 遍历指定页数
            for page in range(1, max_pages + 1):
                page_url = f"{base_url}&page={page}"
                print(f"正在获取第 {page} 页: {page_url}")
                
                try:
                    # 使用现有的fetch_jobs_by_page方法获取单页数据
                    result = self.fetch_jobs_by_page(page_url)
                    
                    # 根据状态处理结果
                    if result["status"] == "success":
                        jobs_data = result["data"]
                        all_jobs.extend(jobs_data)
                        print(f"第 {page} 页获取到 {len(jobs_data)} 个职位")
                        
                        # 如果当前页职位数小于30，说明已到最后一页
                        if len(jobs_data) < 30:
                            print("职位数量不足30，已到最后一页")
                            break
                            
                    elif result["status"] == "empty":
                        print(f"第 {page} 页没有找到相关职位")
                        break  # 如果某页无数据，停止获取后续页面
                    elif result["status"] == "timeout":
                        print(f"第 {page} 页加载超时，跳过")
                        continue  # 超时则跳过当前页，继续获取下一页
                    else:  # error 或其他状态
                        print(f"第 {page} 页获取失败: {result['status']}")
                        continue
                    
                    # 添加随机延迟，避免被反爬
                    delay = random.uniform(self.min_delay, self.max_delay)
                    print(f"等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"获取第 {page} 页失败: {str(e)}")
                    continue
                
            print(f"总共获取到 {len(all_jobs)} 个职位")
            return all_jobs
            
        except Exception as e:
            print(f"获取职位列表失败: {str(e)}")
            return []
    
    def __del__(self):
        if hasattr(self, '_driver'):
            try:
                self._driver.quit()
            except:
                pass