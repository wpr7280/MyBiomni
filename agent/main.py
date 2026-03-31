import uvicorn
from api.app import app

if __name__ == "__main__":
    import os
    use_mock = os.getenv('USE_MOCK_AGENT', 'false').lower() == 'true'
    
    print("🚀 启动 WarpHelix Agent API 服务...")
    print("📍 服务地址: http://0.0.0.0:8000")
    print("📡 WebSocket: ws://0.0.0.0:8000/ws/chat/{conversation_id}")
    
    if use_mock:
        print("🎭 Mock 模式: 使用模拟 Agent（不需要真实 A1）")
    else:
        print("🤖 真实模式: 使用 WarpHelix A1 Agent")
    
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )
