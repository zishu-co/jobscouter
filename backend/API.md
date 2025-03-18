# API 文档

## 基础信息
- 基础URL: `http://localhost:8000`
- 所有请求和响应均使用 JSON 格式
- 所有时间字段使用 ISO 8601 格式

## 接口列表

### 1. 搜索职位
搜索指定条件的职位信息。

- **URL**: `/api/jobs/search`
- **方法**: POST
- **请求体**:
```json
{
    "query": "前端开发",
    "city": "101010100",
    "position": "100101",  // 可选
    "page": 1  // 可选，默认为1
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "title": "高级前端开发工程师",
            "salary": "25-35K",
            "company": "某科技公司",
            "location": "北京",
            "tags": ["React", "Vue", "3年经验"],
            "job_link": "https://www.zhipin.com/job_detail/xxx"
        }
    ]
}
```

- **curl示例**:
```bash
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "前端开发",
    "city": "101010100",
    "position": "100101"
  }'
```

### 2. 订阅职位
订阅指定搜索条件的职位更新。

- **URL**: `/api/jobs/subscribe`
- **方法**: POST
- **请求体**:
```json
{
    "search_params": {
        "query": "前端开发",
        "city": "101010100",
        "position": "100101"
    },
    "email_list": ["user@example.com"]
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "订阅成功"
}
```

- **curl示例**:
```bash
curl -X POST http://localhost:8000/api/jobs/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "search_params": {
        "query": "前端开发",
        "city": "101010100",
        "position": "100101"
    },
    "email_list": ["user@example.com"]
  }'
```

### 3. 健康检查
检查服务是否正常运行。

- **URL**: `/health`
- **方法**: GET
- **响应**:
```json
{
    "status": "ok"
}
```

- **curl示例**:
```bash
curl http://localhost:8000/health
```

## 错误响应
所有接口在发生错误时会返回以下格式：

```json
{
    "detail": "错误信息描述"
}
```

## 状态码说明
- 200: 请求成功
- 400: 请求参数错误
- 500: 服务器内部错误

## 城市编码对照表
| 城市 | 编码 |
|------|------|
| 全国 | 100010000 |
| 北京 | 101010100 |
| 上海 | 101020100 |
| 广州 | 101280100 |
| 深圳 | 101280600 |
| 杭州 | 101210100 |

## 注意事项
1. 订阅接口会自动创建或更新用户邮箱列表
2. 职位更新检查间隔为20分钟
3. 每个邮箱地址需要符合标准邮箱格式
4. 订阅成功后会立即记录当前职位列表作为基准
```

这个API文档包含了：
1. 所有接口的详细说明
2. 请求和响应示例
3. curl命令示例
4. 错误处理说明
5. 状态码说明
6. 城市编码对照表
7. 使用注意事项

文档采用 Markdown 格式，便于阅读和维护。每个接口都包含了完整的请求和响应示例，以及对应的 curl 命令，方便开发者测试和集成。
