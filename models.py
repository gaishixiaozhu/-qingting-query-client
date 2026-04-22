# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 核心数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

class IntentType(Enum):
    """意图类型"""
    UNKNOWN = "未知"
    QUERY_MAJOR = "查专业"           # 查专业+分数
    QUERY_SCHOOL = "查院校"          # 查院校+分数
    QUERY_PLAN = "查计划"            # 查招生计划的分数
    RECOMMEND_ADMISSION = "推荐志愿"  # 推荐完整志愿表
    COMPARISON = "对比"              # 对比院校/专业
    SIMPLE_QUESTION = "简单问答"       # 简单问题，不需要触发skill

class QueryMode(Enum):
    """查询模式"""
    EXACT = "精确查询"      # 用户条件明确
    FUZZY = "模糊查询"      # 条件不完整，智能补全
    EXPAND = "扩展查询"     # 条件不足时扩展

class RiskLevel(Enum):
    """风险等级"""
    EXTREME_RISK = ("极危", ">分差+20")   # diff > +20
    SPRINT = ("冲刺", "0<分差≤+20")        # +20 >= diff > 0
    SUITABLE = ("适合", "-10<分差≤0")     # 0 >= diff > -10
    SAFE = ("稳妥", "-20<分差≤-10")       # -10 >= diff > -20
    BOTTOM = ("托底", "分差≤-20")         # diff <= -20

@dataclass
class UserCondition:
    """用户查询条件"""
    # 必填条件
    province: Optional[str] = None       # 省份代码
    province_name: Optional[str] = None   # 省份名称
    nature: Optional[str] = None        # 科类
    score: Optional[int] = None         # 考生分数
    rank: Optional[int] = None         # 考生位次
    
    # 可选条件
    year: int = 2025
    school_name: Optional[str] = None   # 院校名称
    major_name: Optional[str] = None    # 专业名称
    city: Optional[str] = None         # 城市
    school_level: Optional[str] = None  # 院校层次
    
    # 风险偏好
    risk_preference: str = "适中"
    admission_ratio: str = "3:3:4"
    
    # 排除条件
    exclude_tags: List[str] = field(default_factory=list)
    
    # 原始
    original_text: str = ""

    def to_dict(self) -> dict:
        return {
            "province": self.province,
            "province_name": self.province_name,
            "nature": self.nature,
            "score": self.score,
            "rank": self.rank,
            "year": self.year,
            "school_name": self.school_name,
            "major_name": self.major_name,
            "city": self.city,
            "school_level": self.school_level,
            "risk_preference": self.risk_preference,
            "admission_ratio": self.admission_ratio,
            "exclude_tags": self.exclude_tags
        }

@dataclass
class IntentResult:
    """意图识别结果"""
    intent: IntentType = IntentType.UNKNOWN
    query_mode: QueryMode = QueryMode.FUZZY
    confidence: float = 0.0
    
    conditions: UserCondition = field(default_factory=UserCondition)
    condition_fills: List[str] = field(default_factory=list)
    condition_warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # 是否需要触发skill
    should_trigger_skill: bool = False
    # 响应消息
    response_message: str = ""

@dataclass
class AdmissionResult:
    """录取结果"""
    school_id: int
    school_name: str
    city: str
    
    major: str
    major_note: Optional[str] = None
    
    year: int = 2025
    nature: str = ""
    
    low_score: int = 0
    low_rank: int = 0
    avg_score: float = 0.0
    plan_num: int = 0
    
    user_score: Optional[int] = None
    user_rank: Optional[int] = None
    diff_avg: float = 0.0
    risk_level: Optional[RiskLevel] = None
    
    def to_dict(self) -> dict:
        return {
            "school_id": self.school_id,
            "school_name": self.school_name,
            "city": self.city,
            "major": self.major,
            "major_note": self.major_note,
            "year": self.year,
            "nature": self.nature,
            "low_score": self.low_score,
            "low_rank": self.low_rank,
            "avg_score": self.avg_score,
            "plan_num": self.plan_num,
            "risk_level": self.risk_level.value[0] if self.risk_level else "未知",
            "diff_avg": self.diff_avg
        }

@dataclass
class AdmissionPlan:
    """志愿方案"""
    sprint_list: List[AdmissionResult] = field(default_factory=list)
    suitable_list: List[AdmissionResult] = field(default_factory=list)
    safe_list: List[AdmissionResult] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "sprint": [r.to_dict() for r in self.sprint_list[:10]],
            "suitable": [r.to_dict() for r in self.suitable_list[:10]],
            "safe": [r.to_dict() for r in self.safe_list[:10]]
        }
    
    def to_display_text(self) -> str:
        """转换为可读文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("🎯 志愿方案推荐结果")
        lines.append("=" * 60)
        
        if self.sprint_list:
            lines.append("\n🚀 冲刺院校（+20~0分差）")
            lines.append("-" * 40)
            for r in self.sprint_list[:5]:
                lines.append(f"  {r.school_name} | {r.major} | {r.low_score}分 | {r.plan_num}人")
        
        if self.suitable_list:
            lines.append("\n✅ 适合院校（0~-10分差）")
            lines.append("-" * 40)
            for r in self.suitable_list[:5]:
                lines.append(f"  {r.school_name} | {r.major} | {r.low_score}分 | {r.plan_num}人")
        
        if self.safe_list:
            lines.append("\n🛡️ 稳妥院校（<-10分差）")
            lines.append("-" * 40)
            for r in self.safe_list[:5]:
                lines.append(f"  {r.school_name} | {r.major} | {r.low_score}分 | {r.plan_num}人")
        
        lines.append("=" * 60)
        return "\n".join(lines)
