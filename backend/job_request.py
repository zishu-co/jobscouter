# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import urllib.parse
from job_scraper import JobScraper
from models import User, Subscription, Log
from database import SessionLocal, init_db
import json
from scheduler import JobScheduler
from tenacity import retry, stop_after_attempt, wait_exponential
from mail import EmailSender
from datetime import datetime

send_email = EmailSender().send_email
app = FastAPI()

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加主页路由
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>工作搜索与订阅系统 API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .endpoint { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>工作搜索与订阅系统 API</h1>
            <div class="endpoint">
                <h3>API 文档</h3>
                <p><a href="/docs">Swagger UI 文档</a></p>
            </div>
            <div class="endpoint">
                <h3>可用接口：</h3>
                <ul>
                    <li><code>POST /api/jobs/search</code> - 搜索职位</li>
                    <li><code>POST /api/jobs/subscribe</code> - 订阅职位</li>
                    <li><code>GET /api/jobs/subscriptions</code> - 获取订阅列表</li>
                </ul>
            </div>
        </body>
    </html>
    """

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 订阅请求模型
class SubscribeRequest(BaseModel):
    search_params: dict
    email_list: List[str]

class JobSearchRequest(BaseModel):
    query: str
    city: str
    page: Optional[int] = 1

class JobSearchResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: list = []

# 创建全局的JobScraper实例
job_scraper = JobScraper()

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@app.post("/api/jobs/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    try:
        # URL编码处理查询参数
        encoded_query = urllib.parse.quote(request.query)
        
        # 构建请求URL
        base_url = "https://www.zhipin.com/web/geek/job"
        url = f"{base_url}?query={encoded_query}&city={request.city}"
        
        if request.page > 1:
            url += f"&page={request.page}"
        
        print(f"搜索URL: {url}")
        
        # 使用全局的JobScraper实例
        result = job_scraper.fetch_jobs_by_page(url)
        
        # 如果需要验证，返回特殊状态
        if result["status"] == "verify":
            return JobSearchResponse(
                code=403,  # 使用403表示需要验证
                message="verify",
                data=[]
            )
        
        return JobSearchResponse(
            code=200,
            message=result["status"],
            data=result["data"]
        )
        
    except Exception as e:
        print(f"搜索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )

@app.post("/api/jobs/subscribe")
async def subscribe_jobs(request: SubscribeRequest, db: Session = Depends(get_db)):
    try:
        # 使用固定用户ID=1
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                username="default_user",
                email_list=request.email_list
            )
            db.add(user)
            db.flush()
        else:
            user.email_list = request.email_list
            db.flush()

        # 获取搜索参数并构建URL
        query = request.search_params["query"]
        city = request.search_params["city"]
        encoded_query = urllib.parse.quote(query)
        base_url = "https://www.zhipin.com/web/geek/job"
        url = f"{base_url}?query={encoded_query}&city={city}"
        if request.search_params.get('position'):
            url += f"&position={request.search_params['position']}"

        # 通过 user_id 和 search_url 检查是否存在相同订阅
        existing_subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.search_url == url
        ).first()

        # 获取初始职位列表
        scraper = JobScraper()
        jobs = scraper.fetch_jobs(
            keyword=query,
            city=city,
            max_pages=3
        )

        if existing_subscription:
            # 更新现有订阅
            db.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.search_url == url
            ).update({
                "search_params": request.search_params,
                "email_list": request.email_list,
                "updated_at": datetime.utcnow()
            })
            subscription = existing_subscription
            action = "更新"
        else:
            # 创建新订阅
            subscription = Subscription(
                user_id=user.id,
                search_params=request.search_params,
                search_url=url,
                email_list=request.email_list
            )
            db.add(subscription)
            action = "创建"
        
        db.flush()
        
        # 记录初始job keys
        if jobs:
            job_keys = [job['job_link'].split('?')[0] for job in jobs]
            log = Log(
                subscription_id=subscription.id,
                job_key=json.dumps(job_keys),
                email_title=f"{query}职位订阅{action}",
                email_content=f"订阅{action}成功，已记录当前职位列表"
            )
            db.add(log)

            # 发送订阅邮件
            email_content = f"""
            <h2>订阅{action}成功通知</h2>
            <p>您已成功{action}以下职位搜索：</p>
            <ul>
                <li>搜索关键词：{query}</li>
                <li>城市：{city}</li>
                <li>当前职位数量：{len(jobs)}</li>
            </ul>
            <p>我们会定期检查新职位，如有更新会及时通过邮件通知您。</p>
            <p>祝您求职顺利！</p>
            """
            
            try:
                for email in request.email_list:
                    await send_email(
                        to_email=email,
                        subject=f"{query}职位订阅{action}成功",
                        content=email_content
                    )
                print(f"订阅{action}邮件已发送至: {', '.join(request.email_list)}")
            except Exception as mail_error:
                print(f"发送订阅{action}邮件失败: {str(mail_error)}")

        db.commit()
        JobScheduler.reload_subscriptions()  # 重新加载订阅列表
        return {
            "code": 200, 
            "message": f"订阅{action}成功",
            "action": action  # 返回操作类型给前端
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"订阅失败: {str(e)}"
        )

# 添加健康检查接口
@app.get("/health")
async def health_check():
    try:
        # 检查数据库连接
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    finally:
        db.close()

    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "scheduler": "running" if scheduler._initialized else "not running"
    }

# 创建调度器实例
scheduler = JobScheduler()

# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    scheduler.start()  # 启动定时任务

# 在应用关闭时清理资源
@app.on_event("shutdown")
async def shutdown_event():
    global job_scraper
    if job_scraper:
        del job_scraper

# 添加新的响应模型
class SubscriptionResponse(BaseModel):
    id: int
    search_params: dict
    search_url: str
    email_list: List[str]
    created_at: str

@app.get("/api/jobs/subscriptions")
async def get_subscriptions(db: Session = Depends(get_db)):
    """获取用户的所有订阅"""
    try:
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == 1  # 固定用户ID
        ).all()
        
        return {
            "code": 200,
            "message": "success",
            "data": [{
                "id": sub.id,
                "search_params": sub.search_params,
                "search_url": sub.search_url,
                "email_list": sub.email_list,
                "created_at": sub.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for sub in subscriptions]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取订阅列表失败: {str(e)}"
        )

@app.delete("/api/jobs/subscription/{subscription_id}")
async def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """删除指定订阅"""
    try:
        result = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == 1  # 固定用户ID
        ).delete()
        
        if result == 0:
            raise HTTPException(status_code=404, detail="订阅不存在")
            
        db.commit()
        JobScheduler.reload_subscriptions()  # 重新加载订阅列表
        return {"code": 200, "message": "删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除订阅失败: {str(e)}"
        )

@app.put("/api/jobs/subscription/{subscription_id}/emails")
async def update_subscription_emails(
    subscription_id: int, 
    email_list: List[str], 
    db: Session = Depends(get_db)
):
    """更新订阅的邮箱列表"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == 1
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="订阅不存在")
            
        subscription.email_list = email_list
        db.commit()
        
        return {"code": 200, "message": "邮箱更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新邮箱失败: {str(e)}"
        )

# 添加服务启动代码
if __name__ == "__main__":
    import uvicorn
    # 启动服务，host="0.0.0.0" 允许外部访问，port=8000 指定端口号
    uvicorn.run(app, host="0.0.0.0", port=8000)
