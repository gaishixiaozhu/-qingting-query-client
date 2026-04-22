# -*- coding: utf-8 -*-
"""
蜻蜓查询 - OpenClaw集成接口

通过此模块可以将蜻蜓查询集成到OpenClaw的技能系统中
"""

import json
import os
import sys
from pathlib import Path

# 添加client路径
sys.path.insert(0, str(Path(__file__).parent))

from intent_recognition import IntelligentIR
from query_engine import QingtingDB
from recommendation_engine import RecommendationEngine
from api_key_validator import get_validator
from rate_limiter import get_limiter

class QingtingSkill:
    """
    蜻蜓查询OpenClaw技能封装
    
    用于OpenClaw的意图识别和查询处理
    """
    
    def __init__(self, db_path: str = None, api_key: str = None):
        """
        初始化
        
        Args:
            db_path: 数据库路径
            api_key: API Key（可选）
        """
        self.db_path = db_path or "/Users/fuquanhao/.openclaw/skills/data/cache.db"
        self.api_key = api_key or os.environ.get("QINGTING_API_KEY", "")
        
        self.ir = IntelligentIR()
        self.db = QingtingDB(self.db_path)
        self.recommender = RecommendationEngine(self.db_path)
        self.validator = get_validator()
        self.limiter = get_limiter()
    
    def check_api_key(self) -> dict:
        """检查API Key状态"""
        if not self.api_key:
            return {
                "valid": False,
                "message": "⚠️ API Key未配置！请联系开发者购买API Key。\n\n购买后配置您的API Key即可使用本技能。"
            }
        
        result = self.validator.validate(self.api_key)
        if not result.is_valid:
            return {
                "valid": False,
                "message": result.invalid_reason
            }
        
        return {
            "valid": True,
            "key_id": result.key_id,
            "customer": result.customer
        }
    
    def process(self, user_text: str) -> dict:
        """
        处理用户输入
        
        Args:
            user_text: 用户输入文本
            
        Returns:
            处理结果字典
        """
        # 1. 检查API Key
        if self.api_key:
            key_result = self.check_api_key()
            if not key_result["valid"]:
                return {
                    "success": False,
                    "should_trigger": False,
                    "error": key_result["message"]
                }
            
            # 2. 检查限流
            key_info = self.validator.validate(self.api_key)
            rate_result = self.limiter.check(self.api_key, key_info.rate_limit)
            if not rate_result.allowed:
                return {
                    "success": False,
                    "should_trigger": False,
                    "error": f"请求过于频繁，请{int(rate_result.reset_in)}秒后重试"
                }
        
        # 3. 意图识别
        result = self.ir.recognize(user_text)
        
        # 4. 如果是简单问答，不触发skill
        if not result.should_trigger_skill:
            return {
                "success": True,
                "should_trigger": False,
                "intent": result.intent.value,
                "message": None
            }
        
        # 5. 检查条件完整性
        if result.condition_warnings:
            return {
                "success": False,
                "should_trigger": True,
                "intent": result.intent.value,
                "conditions": result.conditions.to_dict(),
                "warnings": result.condition_warnings,
                "suggestions": result.suggestions
            }
        
        # 6. 执行查询
        try:
            if result.intent.value == "推荐志愿":
                plan, stats = self.recommender.generate_plan(result.conditions)
                return {
                    "success": True,
                    "should_trigger": True,
                    "intent": result.intent.value,
                    "data": plan.to_dict(),
                    "statistics": stats,
                    "display_text": plan.to_display_text()
                }
            
            elif result.intent.value == "查专业":
                data = self.recommender.query_major(result.conditions)
                return {
                    "success": True,
                    "should_trigger": True,
                    "intent": result.intent.value,
                    "data": data
                }
            
            elif result.intent.value == "查院校":
                data = self.recommender.query_school(result.conditions)
                return {
                    "success": True,
                    "should_trigger": True,
                    "intent": result.intent.value,
                    "data": data
                }
            
            else:
                return {
                    "success": True,
                    "should_trigger": True,
                    "intent": result.intent.value,
                    "conditions": result.conditions.to_dict(),
                    "message": "请提供更多条件以进行查询"
                }
        
        except Exception as e:
            return {
                "success": False,
                "should_trigger": True,
                "error": str(e)
            }


# 全局实例
_skill_instance = None

def get_skill(db_path: str = None, api_key: str = None) -> QingtingSkill:
    """获取技能实例"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = QingtingSkill(db_path, api_key)
    return _skill_instance


# CLI入口
if __name__ == "__main__":
    skill = get_skill()
    
    # 测试
    test_inputs = [
        "你好",
        "辽宁物理类520分能上什么学校",
        "计算机专业多少分",
        "帮我推荐志愿"
    ]
    
    for text in test_inputs:
        print(f"\n{'='*60}")
        print(f"输入: {text}")
        print(f"{'='*60}")
        result = skill.process(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
