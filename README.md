# 工作搜索与订阅系统

## 功能特性

### 1. 基础搜索功能
- 支持按关键词搜索职位
- 支持城市筛选
- 实时展示搜索结果

### 2. 工作订阅功能
- 用户可订阅特定搜索条件的职位更新
- 支持多邮箱订阅
- 系统每20分钟自动检查更新
- 发现新职位自动发送邮件通知

### 3. 邮箱管理
- 支持添加/编辑/删除订阅邮箱
- 支持多邮箱配置
- 订阅前检查邮箱配置

### 4. 日志管理
- 记录用户订阅信息
- 记录邮件发送历史
- 统计订阅触发次数
- 详细的任务执行日志
- 错误追踪和监控

## 技术实现

### 前端
- Vue 3 + Element Plus
- 响应式界面设计
- 实时数据更新

### 后端
- FastAPI
- APScheduler 定时任务
- SQLite 数据存储
- Selenium 网页爬虫
- OpenCV 图像处理
- SMTP 邮件服务

### 依赖要求
- Python 3.8+
- Chrome浏览器
- ChromeDriver

## 数据库设计

### 用户表(users)
- id: 主键
- username: 用户名
- email_list: 订阅邮箱列表(JSON)
- created_at: 创建时间

### 订阅表(subscriptions)
- id: 主键
- user_id: 用户ID
- search_params: 搜索参数(JSON)
- search_url: 订阅URL
- status: 订阅状态
- created_at: 创建时间

### 日志表(logs)
- id: 主键
- subscription_id: 订阅ID
- job_key: 职位缓存key
- email_title: 邮件标题
- email_content: 邮件内容
- sent_at: 发送时间

## 更新记录

### 2024-03-xx
- 新增城市选择功能
  - 支持热门城市快速选择
  - 支持按字母索引选择城市
- 优化搜索体验
  - 城市选择弹窗交互优化
  - 搜索参数同步更新

## 部署文档

### 1. 环境准备
```bash
# 安装Python 3.8+

# 安装Chrome浏览器
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# 安装ChromeDriver
# 注意版本要与Chrome浏览器版本匹配
wget https://chromedriver.storage.googleapis.com/[version]/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```

### 2. 项目部署
```bash
# 克隆项目
git clone [项目地址]
cd [项目目录]

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置邮箱
cp .env.example .env
# 编辑 .env 文件，填入邮箱配置
```

### 3. 前端部署
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产环境代码
npm run build
```

### 4. 启动服务
```bash
# 启动后端服务
cd backend
python job_request.py

# 启动前端服务（开发环境）
cd frontend
npm run dev

# 或使用生产环境部署
# 将 frontend/dist 目录下的文件部署到 Nginx 等 Web 服务器
```

### 5. 注意事项
- 确保 Chrome 和 ChromeDriver 版本匹配
- 配置正确的邮箱 SMTP 服务器信息
- 建议使用 supervisor 等工具管理后端进程
- 生产环境建议使用 Nginx 反向代理
- 定时任务默认每小时执行一次，可在 scheduler.py 中调整

### 6. 常见问题
1. ChromeDriver 启动失败
   - 检查 Chrome 和 ChromeDriver 版本是否匹配
   - 确保有适当的系统权限

2. 邮件发送失败
   - 检查 SMTP 配置是否正确
   - 确认邮箱是否开启 SMTP 服务

3. 定时任务未执行
   - 检查系统日志
   - 确认程序是否正常运行

### 7. 监控维护
- 检查 logs 目录下的日志文件
- 监控邮件发送状态
- 定期检查数据库大小
- 及时更新 Chrome 和 ChromeDriver


