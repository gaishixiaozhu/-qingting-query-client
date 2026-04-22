# -*- coding: utf-8 -*-
"""
蜻蜓查询 - API服务
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from intent_recognition import IntelligentIR
from query_engine import QingtingDB
from recommendation_engine import RecommendationEngine
from rate_limiter import get_limiter
from api_key_validator import get_validator

app = Flask(__name__)

# 配置
DB_PATH = os.environ.get("DB_PATH", "/Users/fuquanhao/.openclaw/skills/data/cache.db")
KEYS_FILE = os.environ.get("KEYS_FILE", "")  # 如果配置了Key验证文件

# 初始化组件
ir = IntelligentIR()
db = QingtingDB(DB_PATH)
recommender = RecommendationEngine(DB_PATH)
limiter = get_limiter()
validator = get_validator(KEYS_FILE if KEYS_FILE else None)

@app.route("/api/v1/query", methods=["POST"])
def query():
    """
    统一查询接口
    
    输入：
    {
        "text": "辽宁物理类520分能上什么学校",
        "api_key": "sk_qt_xxx"
    }
    """
    try:
        data = request.json
        user_text = data.get("text", "")
        api_key = data.get("api_key", "")
        
        # 1. 验证API Key
        if api_key:
            key_info = validator.validate(api_key)
            if not key_info.is_valid:
                return jsonify({
                    "success": False,
                    "error": key_info.invalid_reason
                }), 401
            
            # 2. 检查限流
            rate_result = limiter.check(api_key, key_info.rate_limit)
            if not rate_result.allowed:
                return jsonify({
                    "success": False,
                    "error": f"请求过于频繁，请{rate_result.reset_in:.0f}秒后重试",
                    "retry_after": int(rate_result.reset_in)
                }), 429
        
        # 3. 意图识别
        result = ir.recognize(user_text)
        
        # 4. 检查是否触发skill
        if not result.should_trigger_skill:
            return jsonify({
                "success": True,
                "trigger_skill": False,
                "intent": result.intent.value,
                "message": "非查询类问题，无需触发技能"
            })
        
        # 5. 检查条件完整性
        if result.condition_warnings:
            return jsonify({
                "success": False,
                "intent": result.intent.value,
                "conditions": result.conditions.to_dict(),
                "warnings": result.condition_warnings,
                "suggestions": result.suggestions
            })
        
        # 6. 执行查询
        if result.intent.value == "推荐志愿":
            plan, stats = recommender.generate_plan(result.conditions)
            return jsonify({
                "success": True,
                "trigger_skill": True,
                "intent": result.intent.value,
                "data": plan.to_dict(),
                "statistics": stats,
                "display_text": plan.to_display_text()
            })
        
        elif result.intent.value == "查专业":
            data = recommender.query_major(result.conditions)
            return jsonify({
                "success": True,
                "trigger_skill": True,
                "intent": result.intent.value,
                "data": data
            })
        
        elif result.intent.value == "查院校":
            data = recommender.query_school(result.conditions)
            return jsonify({
                "success": True,
                "trigger_skill": True,
                "intent": result.intent.value,
                "data": data
            })
        
        else:
            return jsonify({
                "success": True,
                "trigger_skill": True,
                "intent": result.intent.value,
                "conditions": result.conditions.to_dict(),
                "message": "请提供更多条件以进行查询"
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/score_to_rank", methods=["POST"])
def score_to_rank():
    """分数转位次"""
    data = request.json
    province = data.get("province")
    year = data.get("year", 2025)
    nature = data.get("nature")
    score = data.get("score")
    
    if not all([province, nature, score]):
        return jsonify({"error": "缺少参数"}), 400
    
    rank = db.score_to_rank(province, year, nature, score)
    
    return jsonify({
        "score": score,
        "rank": rank,
        "province": province,
        "year": year,
        "nature": nature
    })

@app.route("/api/v1/rank_to_score", methods=["POST"])
def rank_to_score():
    """位次转分数"""
    data = request.json
    province = data.get("province")
    year = data.get("year", 2025)
    nature = data.get("nature")
    rank = data.get("rank")
    
    if not all([province, nature, rank]):
        return jsonify({"error": "缺少参数"}), 400
    
    score = db.rank_to_score(province, year, nature, rank)
    
    return jsonify({
        "rank": rank,
        "score": score,
        "province": province,
        "year": year,
        "nature": nature
    })

@app.route("/api/v1/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "qingting-query"
    })

@app.route("/api/v1/conditions_check", methods=["POST"])
def conditions_check():
    """
    条件检查接口
    用于检测用户输入中是否包含必要的查询条件
    """
    data = request.json
    text = data.get("text", "")
    
    result = ir.recognize(text)
    
    return jsonify({
        "intent": result.intent.value,
        "should_trigger_skill": result.should_trigger_skill,
        "conditions": result.conditions.to_dict(),
        "condition_warnings": result.condition_warnings,
        "suggestions": result.suggestions,
        "condition_fills": result.condition_fills
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    app.run(host="0.0.0.0", port=port, debug=False)
