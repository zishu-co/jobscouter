import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "job_request:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
        workers=1     # 工作进程数
    ) 