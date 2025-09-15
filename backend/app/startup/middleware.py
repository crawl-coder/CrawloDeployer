# /backend/app/startup/middleware.py
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_cors(app):
    """配置CORS中间件"""
    # 处理Pydantic AnyHttpUrl自动添加斜杠的问题
    origins = [str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS]
    logger.info(f"✅ CORS configured with origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
