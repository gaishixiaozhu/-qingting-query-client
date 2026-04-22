# -*- coding: utf-8 -*-
"""
蜻蜓查询 - API Key验证层（客户端用）
只验证格式，不验证hash（hash由服务端验证）
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class APIKeyInfo:
    """API Key信息"""
    key_id: str
    customer: str
    rate_limit: int
    expires_at: str
    is_valid: bool
    invalid_reason: Optional[str] = None

class APIKeyValidator:
    """
    API Key验证器（客户端用）
    
    客户端只验证格式，实际验证由服务端完成
    """
    
    def validate(self, api_key: str) -> APIKeyInfo:
        """
        验证API Key格式
        
        Args:
            api_key: API Key
            
        Returns:
            APIKeyInfo: Key信息
        """
        # 1. 检查是否为空
        if not api_key:
            return APIKeyInfo(
                key_id="", customer="", rate_limit=100,
                expires_at="", is_valid=False,
                invalid_reason="⚠️ API Key未配置！请在config.py中配置您的API Key"
            )
        
        # 2. 检查格式
        if not api_key.startswith("sk_qt_"):
            return APIKeyInfo(
                key_id="", customer="", rate_limit=100,
                expires_at="", is_valid=False,
                invalid_reason="API Key格式无效，应以 sk_qt_ 开头"
            )
        
        # 3. 格式正确就认为有效（服务端再验证hash）
        return APIKeyInfo(
            key_id="",
            customer="",
            rate_limit=100,
            expires_at="",
            is_valid=True
        )
    
    def get_rate_limit(self, api_key: str) -> int:
        """获取限流配置"""
        info = self.validate(api_key)
        return info.rate_limit if info.is_valid else 0
