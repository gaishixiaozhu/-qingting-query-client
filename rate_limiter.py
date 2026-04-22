# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 限流器
基于滑动窗口算法实现
"""

import time
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib

@dataclass
class RateLimitResult:
    """限流结果"""
    allowed: bool          # 是否允许请求
    remaining: int        # 剩余请求次数
    reset_in: float       # 多少秒后重置
    total_limit: int       # 总限制次数

class RateLimiter:
    """
    滑动窗口限流器
    
    支持：
    1. 按API Key限流
    2. 全局限流
    3. 动态调整限制
    """
    
    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        """
        Args:
            default_limit: 默认每分钟限制次数
            window_seconds: 时间窗口（秒）
        """
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        
        # 存储请求时间戳
        # {"api_key": [(timestamp1, count), (timestamp2, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        
        # 全局限流
        self._global_requests: list = []
        
        # 锁
        self._lock = threading.Lock()
    
    def _get_window_start(self) -> float:
        """获取当前窗口起始时间"""
        return time.time() - self.window_seconds
    
    def _clean_old_requests(self, key: str):
        """清理过期的请求记录"""
        window_start = self._get_window_start()
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > window_start
        ]
    
    def check(self, api_key: str, limit: Optional[int] = None) -> RateLimitResult:
        """
        检查是否允许请求
        
        Args:
            api_key: API Key
            limit: 自定义限制（优先使用）
            
        Returns:
            RateLimitResult
        """
        with self._lock:
            limit = limit or self.default_limit
            window_start = self._get_window_start()
            
            # 清理旧记录
            self._clean_old_requests(api_key)
            
            # 获取当前请求数
            current_count = len(self._requests[api_key])
            
            # 检查是否超限
            if current_count >= limit:
                # 计算重置时间
                oldest = min(self._requests[api_key])
                reset_in = oldest + self.window_seconds - time.time()
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_in=max(0, reset_in),
                    total_limit=limit
                )
            
            # 记录请求
            self._requests[api_key].append(time.time())
            
            return RateLimitResult(
                allowed=True,
                remaining=limit - current_count - 1,
                reset_in=self.window_seconds,
                total_limit=limit
            )
    
    def check_global(self) -> RateLimitResult:
        """检查全局限流"""
        with self._lock:
            window_start = self._get_window_start()
            
            # 清理
            self._global_requests = [ts for ts in self._global_requests if ts > window_start]
            
            # 全局限制是单个Key的10倍
            global_limit = self.default_limit * 10
            
            current_count = len(self._global_requests)
            
            if current_count >= global_limit:
                oldest = min(self._global_requests)
                reset_in = oldest + self.window_seconds - time.time()
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_in=max(0, reset_in),
                    total_limit=global_limit
                )
            
            self._global_requests.append(time.time())
            
            return RateLimitResult(
                allowed=True,
                remaining=global_limit - current_count - 1,
                reset_in=self.window_seconds,
                total_limit=global_limit
            )
    
    def get_status(self, api_key: str, limit: Optional[int] = None) -> Dict:
        """获取状态"""
        with self._lock:
            limit = limit or self.default_limit
            self._clean_old_requests(api_key)
            
            current_count = len(self._requests[api_key])
            
            return {
                "api_key": self._hash_key(api_key),
                "current_requests": current_count,
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "window_seconds": self.window_seconds
            }
    
    def _hash_key(self, key: str) -> str:
        """Hash Key用于显示"""
        return hashlib.md5(key.encode()).hexdigest()[:8]
    
    def reset(self, api_key: Optional[str] = None):
        """重置限流记录"""
        with self._lock:
            if api_key:
                self._requests[api_key] = []
            else:
                self._requests.clear()
                self._global_requests = []

# 全局实例
_global_limiter: Optional[RateLimiter] = None

def get_limiter() -> RateLimiter:
    """获取全局限流器"""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter(default_limit=100, window_seconds=60)
    return _global_limiter
