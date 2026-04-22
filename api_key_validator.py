# -*- coding: utf-8 -*-
"""
蜻蜓查询 - API Key验证层（客户端用）
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
    rate_limit: int
    expires_at: str
    is_valid: bool
    invalid_reason: Optional[str] = None

class APIKeyValidator:
    """
    API Key验证器
    """
    
    def __init__(self, keys_file: Optional[str] = None, salt: Optional[str] = None):
        self.keys_file = keys_file
        self._keys = self._load_keys()
        self._salt = salt or self._get_salt()
    
    def _get_salt(self) -> str:
        """获取盐值"""
        # 优先从环境变量获取
        if os.environ.get("QINGTING_API_SALT"):
            return os.environ["QINGTING_API_SALT"]
        
        # 尝试从配置文件获取
        config_file = Path(__file__).parent / "config.py"
        if config_file.exists():
            for line in config_file.read_text().split('\n'):
                if line.startswith('SALT'):
                    return line.split('=')[1].strip().strip('"\'')
        
        return "default_salt_change_me"
    
    def _load_keys(self) -> dict:
        """加载Key数据"""
        if self.keys_file and os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"keys": []}
    
    def _hash_key(self, api_key: str) -> str:
        """Hash Key"""
        return hmac.new(
            self._salt.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()[:64]
    
    def validate(self, api_key: str) -> APIKeyInfo:
        if not api_key or not api_key.startswith("sk_qt_"):
            return APIKeyInfo(
                key_id="", customer="", rate_limit=100,
                expires_at="", is_valid=False,
                invalid_reason="API Key格式无效，应以 sk_qt_ 开头"
            )
        
        if not self._keys.get("keys"):
            return APIKeyInfo(
                key_id="", customer="", rate_limit=100,
                expires_at="", is_valid=False,
                invalid_reason="⚠️ API Key未配置！请在config.py中配置您的API Key"
            )
        
        key_hash = self._hash_key(api_key)
        
        for key_info in self._keys.get("keys", []):
            if key_info.get("key_hash") == key_hash:
                if not key_info.get("is_active", True):
                    return APIKeyInfo(
                        key_id=key_info.get("key_id", ""),
                        customer=key_info.get("customer", ""),
                        rate_limit=key_info.get("rate_limit", 100),
                        expires_at=key_info.get("expires_at", ""),
                        is_valid=False,
                        invalid_reason="API Key已被撤销"
                    )
                
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
                
                return APIKeyInfo(
                    key_id=key_info.get("key_id", ""),
                    customer=key_info.get("customer", ""),
                    rate_limit=key_info.get("rate_limit", 100),
                    expires_at=expires_at,
                    is_valid=True
                )
        
        return APIKeyInfo(
            key_id="", customer="", rate_limit=100,
            expires_at="", is_valid=False,
            invalid_reason="API Key无效，请检查是否输入正确"
        )
