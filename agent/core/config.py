from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT 配置（与 Spring Boot 共享）
    JWT_SECRET_KEY: str = "your-shared-secret-key-here"
    JWT_ALGORITHM: str = "HS512"  # 改为 HS512，与 Spring Boot 一致
    
    # Spring Boot API（可选，暂时不用）
    SPRING_BOOT_URL: str = "http://localhost:8083"
    INTERNAL_SECRET: str = "your-internal-api-secret"
    
    # 数据库
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/biomni_app"
    
    # Agent 配置
    AGENT_DATA_PATH: str = "./data"
    AGENT_UPLOAD_DATA_PATH: str = "./upload"

    DEFAULT_LLM: str = "claude-sonnet-4-5"
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Mock 模式
    USE_MOCK_AGENT: bool = False
    
    # CORS
    CORS_ORIGINS: list = ["http://127.0.0.1"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的字段

settings = Settings()
