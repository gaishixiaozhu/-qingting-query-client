# -*- coding: utf-8 -*-
"""
蜻蜓查询 - API Key验证层
"""

import hashlib
import hmac
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class APIKeyInfo:
    """API Key信息"""
    key_id: str
    customer: str
    rate_limit: int  # 每分钟限制
    expires_at: str
    is_valid: bool
    invalid_reason: Optional[str] = None

class APIKeyValidator:
    """
    API Key验证器
    
    功能：
    1. 验证API Key有效性
    2. 检查过期时间
    3. 获取Key对应的限流配置
    """
    
    def __init__(self, keys_file: Optional[str] = None):
        """
        Args:
            keys_file: Key文件路径，默认使用内置的验证配置
        """
        self.keys_file = keys_file
        self._keys = self._load_keys()
    
    def _load_keys(self) -> dict:
        """加载Key数据"""
        if self.keys_file and os.path.exists(self.keys_file):
            with open(self.keys_file, 'r') as f:
                return json.load(f)
        
        # 默认返回空配置（需要配置API Key）
        return {"keys": []}
    
    def _get_salt(self) -> str:
        """获取盐值"""
        # 默认盐值（实际应该从环境变量或配置文件获取）
        return os.environ.get("QINGTING_API_SALT", "default_salt_change_me")
    
    def _hash_key(self, api_key: str) -> str:
        """Hash Key"""
        salt = self._get_salt()
        return hmac.new(
            salt.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()[:64]
    
    def validate(self, api_key: str) -> APIKeyInfo:
        """
        验证API Key
        
        Args:
            api_key: API Key
            
        Returns:
            APIKeyInfo: Key信息，包含是否有效
        """
        # 1. 检查格式
        if not api_key or not api_key.startswith("sk_qt_"):
            return APIKeyInfo(
                key_id="",
                customer="",
                rate_limit=100,
                expires_at="",
                is_valid=False,
                invalid_reason="API Key格式无效，应以 sk_qt_ 开头"
            )
        
        # 2. 检查Key是否配置
        if not self._keys.get("keys"):
            return APIKeyInfo(
                key_id="",
                customer="",
                rate_limit=100,
                expires_at="",
                is_valid=False,
                invalid_reason="⚠️ API Key未配置！请联系开发者购买API Key。\n\n配置方法：\n1. 联系开发者获取API Key\n2. 配置您的API Key后即可使用"
            )
        
        # 3. 查找Key
        key_hash = self._hash_key(api_key)
        for key_info in self._keys.get("keys", []):
            if key_info.get("key_hash") == key_hash:
                # 4. 检查是否激活
                if not key_info.get("is_active", True):
                    return APIKeyInfo(
                        key_id=key_info.get("key_id", ""),
                        customer=key_info.get("customer", ""),
                        rate_limit=key_info.get("rate_limit", 100),
                        expires_at=key_info.get("expires_at", ""),
                        is_valid=False,
                        invalid_reason="API Key已被撤销"
                    )
                
                # 5. 检查过期
                expires_at = key_info.get("expires_at", "")
                if expires_at:
                    try:
                        exp_date = datetime.fromisoformat(expires_at)
                        if datetime.now() > exp_date:
                            return APIKeyInfo(
                                key_id=key_info.get("key_id", ""),
                                customer=key_info.get("customer", ""),
                                rate_limit=key_info.get("rate_limit", 100),
                                expires_at=expires_at,
                                is_valid=False,
                                invalid_reason=f"API Key已于 {expires_at[:10]} 过期"
                            )
                    except:
                        pass
                
                # 有效
                return APIKeyInfo(
                    key_id=key_info.get("key_id", ""),
                    customer=key_info.get("customer", ""),
                    rate_limit=key_info.get("rate_limit", 100),
                    expires_at=expires_at,
                    is_valid=True
                )
        
        # Key不存在
        return APIKeyInfo(
            key_id="",
            customer="",
            rate_limit=100,
            expires_at="",
            is_valid=False,
            invalid_reason="API Key无效，请检查是否输入正确或联系开发者"
        )
    
    def get_rate_limit(self, api_key: str) -> int:
        """获取Key对应的限流配置"""
        info = self.validate(api_key)
        if info.is_valid:
            return info.rate_limit
        return 0  # 无效Key返回0，禁止访问


# 全局实例
_validator: Optional[APIKeyValidator] = None

def get_validator(keys_file: Optional[str] = None) -> APIKeyValidator:
    """获取验证器实例"""
    global _validator
    if _validator is None:
        _validator = APIKeyValidator(keys_file)
    return _validator
