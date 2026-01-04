#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patient Agent API 配置文件
"""

import os
from typing import Dict, Any

class Config:
    """基础配置类"""
    
    # API配置
    API_TITLE = "Patient Agent API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "精神科患者智能体API服务"
    
    # 服务器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 会话配置
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1小时
    MAX_SESSIONS = int(os.getenv('MAX_SESSIONS', 1000))
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-HpDITbMxP8eFnGN3cV5jy3taxkyUnqjtj8ePYxJBZ4MmD8hl')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.apicore.ai/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')
    
    # RAG配置
    RAG_ENABLED = os.getenv('RAG_ENABLED', 'True').lower() == 'true'
    VECTOR_STORE_TYPE = os.getenv('VECTOR_STORE_TYPE', 'faiss')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # 性能配置
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))  # 30秒
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境安全配置
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    
    # 测试环境使用模拟数据
    RAG_ENABLED = False

# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env: str = None) -> Config:
    """获取配置对象"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()









