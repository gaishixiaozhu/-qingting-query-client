# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 志愿推荐引擎
"""

from typing import List, Tuple, Dict
from models import AdmissionResult, AdmissionPlan, RiskLevel, UserCondition, IntentResult, IntentType
from query_engine import QingtingDB

class RecommendationEngine:
    """
    志愿推荐引擎
    
    按照MEMORY.md规则：
    - 冲刺:适合:稳妥 = 3:3:4（默认）
    - 风险等级判定基于等位分法
    """
    
    def __init__(self, db_path: str = "/Users/fuquanhao/.openclaw/skills/data/cache.db"):
        self.db = QingtingDB(db_path)
    
    def generate_plan(self, conditions: UserCondition, 
                    ratio: str = "3:3:4") -> Tuple[AdmissionPlan, Dict]:
        """
        生成志愿方案
        
        Args:
            conditions: 用户条件
            ratio: 冲刺:适合:稳妥比例
            
        Returns:
            (志愿方案, 统计信息)
        """
        plan = AdmissionPlan()
        
        # 查询录取数据
        results = self.db.query_admission_plans(conditions)
        
        if not results:
            return plan, {
                "total": 0,
                "message": "未找到符合条件的院校"
            }
        
        # 按风险等级分类
        sprint_list = []
        suitable_list = []
        safe_list = []
        
        for r in results:
            if r.risk_level == RiskLevel.EXTREME_RISK:
                sprint_list.append(r)
            elif r.risk_level == RiskLevel.SPRINT:
                sprint_list.append(r)
            elif r.risk_level == RiskLevel.SUITABLE:
                suitable_list.append(r)
            elif r.risk_level == RiskLevel.SAFE:
                safe_list.append(r)
            elif r.risk_level == RiskLevel.BOTTOM:
                safe_list.append(r)
        
        # 按分差排序
        sprint_list.sort(key=lambda x: x.diff_avg, reverse=True)
        suitable_list.sort(key=lambda x: x.diff_avg, reverse=True)
        safe_list.sort(key=lambda x: x.diff_avg, reverse=True)
        
        # 根据比例分配
        plan.sprint_list = sprint_list
        plan.suitable_list = suitable_list
        plan.safe_list = safe_list
        
        # 统计信息
        stats = {
            "total": len(results),
            "sprint_count": len(sprint_list),
            "suitable_count": len(suitable_list),
            "safe_count": len(safe_list),
            "user_score": conditions.score,
            "user_rank": conditions.rank,
            "province": conditions.province,
            "province_name": conditions.province_name,
            "nature": conditions.nature,
            "batch_line": self.db.query_batch_line(
                conditions.province, 
                conditions.year, 
                conditions.nature
            )
        }
        
        return plan, stats
    
    def query_school(self, conditions: UserCondition) -> Dict:
        """
        查询院校历年数据
        
        Returns:
            {
                "school_name": str,
                "history": [{year, nature, low_score, avg_score, plan_num}, ...],
                "statistics": {...}
            }
        """
        # 先获取院校ID
        schools = self.db.query_schools(conditions.province, conditions)
        
        if not schools:
            return {"error": "未找到该院校"}
        
        # 获取第一个匹配的结果
        school = schools[0]
        
        # 查询历年数据（简化版，直接查表）
        with self.db.get_connection() as conn:
            table = self.db.province_tables.get(conditions.province)
            if not table:
                return {"error": "不支持该省份"}
            
            sql = f"""
            SELECT year, nature, pro, low_real, avg_real, plan_num
            FROM {table}
            WHERE school_id = ? AND nature = ?
            ORDER BY year DESC, low_real DESC
            LIMIT 50
            """
            cursor = conn.execute(sql, [school['id'], conditions.nature])
            rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "year": row['year'],
                "nature": row['nature'],
                "major": row['pro'],
                "low_score": int(row['low_real']) if row['low_real'] else 0,
                "avg_score": float(row['avg_real']) if row['avg_real'] else 0.0,
                "plan_num": int(row['plan_num']) if row['plan_num'] else 0
            })
        
        return {
            "school_id": school['id'],
            "school_name": school['school'],
            "city": school['city'],
            "history": history
        }
    
    def query_major(self, conditions: UserCondition) -> Dict:
        """
        查询专业录取情况
        
        Returns:
            专业列表及录取情况
        """
        results = self.db.query_admission_plans(conditions)
        
        if not results:
            return {"error": "未找到符合条件的专业"}
        
        # 按院校分组
        by_school = {}
        for r in results:
            if r.school_name not in by_school:
                by_school[r.school_name] = []
            by_school[r.school_name].append(r.to_dict())
        
        return {
            "total": len(results),
            "schools": list(by_school.keys())[:20],
            "data": by_school
        }
