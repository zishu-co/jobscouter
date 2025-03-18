# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from models import Subscription, Log
from job_scraper import JobScraper
from mail import EmailSender
from database import SessionLocal, init_db
import json
from apscheduler.executors.pool import ThreadPoolExecutor
import time
from sqlalchemy.orm import joinedload
import urllib.parse

class JobScheduler:
    _instance = None
    _subscriptions = None  # 静态变量存储订阅列表
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.scheduler = BackgroundScheduler()
            self.scraper = JobScraper()
            self.email_sender = EmailSender()
            
            # 初始化订阅列表
            self.reload_subscriptions()
            
            # 添加定时任务，每小时检查一次
            self.scheduler.add_job(self.check_jobs, 'interval', hours=1)
            self._initialized = True
    
    @classmethod
    def reload_subscriptions(cls):
        """重新加载订阅列表"""
        db = SessionLocal()
        try:
            cls._subscriptions = db.query(Subscription).filter(
                Subscription.status == True
            ).all()
            print(f"已重新加载 {len(cls._subscriptions)} 个订阅")
        except Exception as e:
            print(f"重新加载订阅失败: {str(e)}")
        finally:
            db.close()
    
    def start(self):
        self.scheduler.start()
        print("定时任务已启动")
    
    def check_jobs(self):
        """检查所有订阅的职位更新"""
        if not self._subscriptions:
            print("没有活跃的订阅")
            return
            
        db = SessionLocal()
        try:
            for subscription in self._subscriptions:
                try:
                    print(f"处理订阅 ID: {subscription.id}")
                    print(f"订阅URL: {subscription.search_url}")
                    print(f"订阅参数: {subscription.search_params}")
                    
                    # 获取新的职位列表（多页）
                    jobs = self.scraper.fetch_jobs(
                        keyword=subscription.search_params['query'],
                        city=subscription.search_params['city'],
                        max_pages=10  
                    )
                    
                    # 添加测试用的假数据
                    fake_jobs = [
                        {
                            "title": f"测试职位_{int(time.time())}_{i}",
                            "salary": "20-35K",
                            "company": f"测试公司_{i}",
                            "location": "长春",
                            "tags": ["Python", "后端开发", "5-10年"],
                            "job_link": f"https://www.zhipin.com/job_detail/{int(time.time())}_{i}"
                        } for i in range(1, 2)
                    ]
                    
                    jobs = fake_jobs + jobs
                    print(f"获取到 {len(jobs)} 个职位")
                    
                    if not jobs:
                        continue
                    
                    # 获取最新的日志记录
                    latest_log = db.query(Log).filter(
                        Log.subscription_id == subscription.id
                    ).order_by(Log.sent_at.desc()).first()
                    
                    # 如果没有历史记录，创建初始记录
                    if not latest_log:
                        job_keys = [job['job_link'].split('?')[0] for job in jobs]
                        log = Log(
                            subscription_id=subscription.id,
                            job_key=json.dumps(job_keys),
                            email_title=f"{subscription.search_params['query']}职位订阅初始化",
                            email_content="订阅初始化，记录当前职位列表"
                        )
                        db.add(log)
                        db.commit()
                        continue
                    
                    # 获取历史职位key
                    old_job_keys = set(json.loads(latest_log.job_key))
                    new_job_keys = {job['job_link'].split('?')[0] for job in jobs}
                    
                    # 找出新增的职位
                    new_jobs = [
                        job for job in jobs 
                        if job['job_link'].split('?')[0] not in old_job_keys
                    ]
                    
                    if new_jobs:
                        print(f"发现 {len(new_jobs)} 个新职位")
                        
                        # 构建邮件内容
                        email_content = f"""
                        <h2>发现新职位</h2>
                        <p>您订阅的"{subscription.search_params['query']}"有新的职位发布：</p>
                        <ul>
                        """
                        
                        for job in new_jobs:
                            email_content += f"""
                            <li>
                                <p><strong>{job['title']}</strong> | {job['salary']}</p>
                                <p>公司：{job['company']}</p>
                                <p>地点：{job['location']}</p>
                                <p>标签：{', '.join(job['tags'])}</p>
                                <p><a href="{job['job_link']}" target="_blank">查看详情</a></p>
                            </li>
                            """
                        
                        email_content += """
                        </ul>
                        <p>祝您求职顺利！</p>
                        """
                        
                        # 发送邮件通知
                        for email in subscription.email_list:
                            self.email_sender.send_email(
                                [email],
                                f"【职位更新】{subscription.search_params['query']} - 发现{len(new_jobs)}个新职位",
                                email_content
                            )
                        
                        # 记录新的职位列表
                        log = Log(
                            subscription_id=subscription.id,
                            job_key=json.dumps(list(new_job_keys)),
                            email_title=f"{subscription.search_params['query']}职位更新 - 发现{len(new_jobs)}个新职位",
                            email_content=email_content
                        )
                        db.add(log)
                        db.commit()
                    
                except Exception as e:
                    print(f"处理订阅失败: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"检查任务失败: {str(e)}")
        finally:
            db.close()

def main():
    """
    测试定时任务功能
    """
    print("开始测试定时任务...")
    
    # 初始化数据库
    print("初始化数据库...")
    init_db()
    
    # 创建调度器实例
    scheduler = JobScheduler()
    
    try:
        # 手动执行一次检查
        print("\n执行立即检查...")
        db = SessionLocal()
        # 同样使用 joinedload 预加载用户信息
        subscriptions = (
            db.query(Subscription)
            .options(joinedload(Subscription.user))
            .filter_by(status=True)
            .all()
        )
        
        if not subscriptions:
            print("没有找到活跃的订阅")
        else:
            print(f"找到 {len(subscriptions)} 个活跃订阅")
            for sub in subscriptions:
                try:
                    print(f"\n处理订阅 {sub.id}...")
                    scheduler.check_jobs()
                except Exception as e:
                    print(f"处理订阅 {sub.id} 失败: {str(e)}")
        
        # 启动定时任务
        print("\n启动定时任务...")
        scheduler.start()
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到终止信号，正在停止...")
            scheduler.scheduler.shutdown()
            print("定时任务已停止")
    
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 