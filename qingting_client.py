# 蜻蜓智能志愿查询 - Python SDK
# 通过API调用数据接口

import os
import requests
from typing import Optional, Dict, Any

class QingtingClient:
    """
    蜻蜓查询Python客户端
    
    使用示例:
    ```python
    from qingting_client import QingtingClient
    
    client = QingtingClient(
        api_key="您的API Key",
        api_url="http://localhost:5006"
    )
    
    # 查询院校
    schools = client.query_schools("ln", nature="物理类")
    
    # 查询录取计划
    plans = client.query_plans("ln", "物理类", score=520)
    ```
    """
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.environ.get("QITING_API_KEY", "")
        self.api_url = api_url or os.environ.get("QTING_API_URL", "http://localhost:5006")
        
        if not self.api_key:
            raise ValueError("API Key未配置！")
    
    def _request(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.api_url}{path}"
        headers = {"X-API-Key": self.api_key}
        
        if method == "GET":
            response = requests.get(url, params=data, headers=headers, timeout=30)
        else:
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 401:
            raise ValueError("API Key无效")
        elif response.status_code == 429:
            raise ValueError("请求过于频繁")
        elif response.status_code != 200:
            raise ValueError(f"请求失败: {response.status_code}")
        
        result = response.json()
        if not result.get("success"):
            raise ValueError(result.get("error", "未知错误"))
        
        return result
    
    def score_to_rank(self, province: str, score: int, nature: str = "物理类", year: int = 2025) -> Optional[int]:
        result = self._request("POST", "/api/v1/score_to_rank", {
            "province": province,
            "score": score,
            "nature": nature,
            "year": year
        })
        return result.get("data", {}).get("rank")
    
    def rank_to_score(self, province: str, rank: int, nature: str = "物理类", year: int = 2025) -> Optional[int]:
        result = self._request("POST", "/api/v1/rank_to_score", {
            "province": province,
            "rank": rank,
            "nature": nature,
            "year": year
        })
        return result.get("data", {}).get("score")
    
    def query_schools(self, province: str, nature: str = None, city: str = None, 
                     school_name: str = None, year: int = 2025) -> list:
        data = {"province": province, "year": year}
        if nature: data["nature"] = nature
        if city: data["city"] = city
        if school_name: data["school_name"] = school_name
        result = self._request("POST", "/api/v1/schools", data)
        return result.get("data", {}).get("schools", [])
    
    def query_plans(self, province: str, nature: str, score: int = None, rank: int = None,
                   major_name: str = None, school_name: str = None, 
                   year: int = 2025, min_plan_num: int = 2) -> list:
        data = {"province": province, "nature": nature, "year": year, "min_plan_num": min_plan_num}
        if score: data["score"] = score
        if rank: data["rank"] = rank
        if major_name: data["major_name"] = major_name
        if school_name: data["school_name"] = school_name
        result = self._request("POST", "/api/v1/plans", data)
        return result.get("data", {}).get("plans", [])
    
    def query_batch_line(self, province: str, nature: str, year: int = 2025) -> Optional[int]:
        result = self._request("GET", "/api/v1/batch_line", {
            "province": province,
            "nature": nature,
            "year": year
        })
        return result.get("data", {}).get("batch_line")
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=10)
            return response.status_code == 200
        except:
            return False

__all__ = ["QingtingClient"]
