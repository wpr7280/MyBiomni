from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.websocket import router as websocket_router
from api.upload import router as upload_router
from core.config import settings

app = FastAPI(
    title="Biomni Agent API",
    description="Biomni Agent WebSocket 服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
app.include_router(upload_router, prefix="/api", tags=["Upload"])

# Also expose execution-status under /api for REST access
from api.websocket import router as ws_router
app.include_router(ws_router, prefix="/api", tags=["Execution"], include_in_schema=False)

@app.get("/")
async def root():
    return {"message": "Biomni Agent API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
