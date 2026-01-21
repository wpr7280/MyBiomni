from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from core.database import Base

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False, default='text')
    tokens = Column(Integer, nullable=False, default=0)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class ExecutionStep(Base):
    __tablename__ = 'execution_steps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)
    step_name = Column(String(100))
    tool_name = Column(String(100))
    tool_input = Column(Text)
    tool_output = Column(Text)
    status = Column(String(20), nullable=False, default='running')
    error_message = Column(Text)
    duration_ms = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    message_count = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    total_duration_ms = Column(Integer, nullable=False, default=0)
    last_message_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)

class UserQuota(Base):
    __tablename__ = 'user_quotas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True)
    total_token_limit = Column(Integer, nullable=False, default=1000000)
    total_token_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class SystemConfig(Base):
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text)
    config_type = Column(String(20), nullable=False, default='string')
    description = Column(String(500))
    is_sensitive = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


