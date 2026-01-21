"""
配置管理服务
从数据库加载 Agent 配置
"""

from sqlalchemy.orm import Session
from models.models import SystemConfig
import os


class ConfigService:
    """配置管理服务"""
    
    @staticmethod
    def get_agent_config(db: Session) -> dict:
        """从数据库加载 Agent 配置
        
        Returns:
            dict: Agent 配置字典，包含所有参数
        """
        # 查询所有 agent.* 和 llm.* 配置
        configs = db.query(SystemConfig).filter(
            (SystemConfig.config_key.like('agent.%')) | 
            (SystemConfig.config_key.like('llm.%'))
        ).all()
        
        config = {}
        llm_credentials = {}
        
        for c in configs:
            if c.config_key.startswith('agent.'):
                # Agent 配置
                key = c.config_key.replace('agent.', '')
                value = ConfigService._parse_value(c.config_value, c.config_type)
                config[key] = value
            elif c.config_key.startswith('llm.'):
                # LLM 凭证配置
                key = c.config_key.replace('llm.', '')
                llm_credentials[key] = c.config_value
        
        # 根据 source 设置对应的环境变量
        source = config.get('source', 'Anthropic')
        ConfigService._set_llm_env_vars(source, llm_credentials)
        
        return config
    
    @staticmethod
    def _parse_value(value: str, config_type: str):
        """解析配置值"""
        if not value:
            return None
        
        if config_type == 'int':
            return int(value)
        elif config_type == 'float':
            return float(value)
        elif config_type == 'bool':
            return value.lower() in ('true', '1', 'yes')
        elif config_type == 'json':
            import json
            return json.loads(value)
        else:
            return value
    
    @staticmethod
    def _set_llm_env_vars(source: str, credentials: dict):
        """根据 LLM 提供商设置环境变量"""
        if source == 'OpenAI':
            if credentials.get('openai_api_key'):
                os.environ['OPENAI_API_KEY'] = credentials['openai_api_key']
        
        elif source == 'Anthropic':
            if credentials.get('anthropic_api_key'):
                os.environ['ANTHROPIC_API_KEY'] = credentials['anthropic_api_key']
        
        elif source == 'Gemini':
            if credentials.get('gemini_api_key'):
                os.environ['GEMINI_API_KEY'] = credentials['gemini_api_key']
        
        elif source == 'Groq':
            if credentials.get('groq_api_key'):
                os.environ['GROQ_API_KEY'] = credentials['groq_api_key']
        
        elif source == 'AzureOpenAI':
            if credentials.get('azure_api_key'):
                os.environ['OPENAI_API_KEY'] = credentials['azure_api_key']
            if credentials.get('azure_endpoint'):
                os.environ['OPENAI_ENDPOINT'] = credentials['azure_endpoint']
        
        elif source == 'Bedrock':
            if credentials.get('aws_region'):
                os.environ['AWS_REGION'] = credentials['aws_region']
            if credentials.get('aws_access_key_id'):
                os.environ['AWS_ACCESS_KEY_ID'] = credentials['aws_access_key_id']
            if credentials.get('aws_secret_access_key'):
                os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['aws_secret_access_key']
            if credentials.get('aws_bearer_token'):
                os.environ['AWS_BEARER_TOKEN_BEDROCK'] = credentials['aws_bearer_token']
