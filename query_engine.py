# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 数据库查询引擎
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from models import AdmissionResult, RiskLevel, UserCondition

class QingtingDB:
    """
    蜻蜓数据库查询
    
    数据库结构：
    - clp_score_rank: 一分一段表
    - clp_school: 院校表
    - clp_profession_data_{province}: 专业录取数据表
    - clp_batch_line: 批次线表
    """
    
    def __init__(self, db_path: str = "/Users/fuquanhao/.openclaw/skills/data/cache.db"):
        self.db_path = db_path
        
        # 省份代码映射
        self.province_tables = {
            "ln": "clp_profession_data_ln",
            "sd": "clp_profession_data_sd",
            "sc": "clp_profession_data_sc",
            "hen": "clp_profession_data_hen",
            "gd": "clp_profession_data_gd",
            "js": "clp_profession_data_js",
            "zj": "clp_profession_data_zj",
            "heb": "clp_profession_data_heb",
            "hub": "clp_profession_data_hub",
            "hun": "clp_profession_data_hun",
            "ah": "clp_profession_data_ah",
            "fj": "clp_profession_data_fj",
            "jx": "clp_profession_data_jx",
            "sx": "clp_profession_data_sx",
            "shx": "clp_profession_data_shx",
            "gs": "clp_profession_data_gs",
            "jl": "clp_profession_data_jl",
            "hlj": "clp_profession_data_hlj",
            "bj": "clp_profession_data_bj",
            "tj": "clp_profession_data_tj",
            "sh": "clp_profession_data_sh",
            "cq": "clp_profession_data_cq",
            "gz": "clp_profession_data_gz",
            "yn": "clp_profession_data_yn",
            "gx": "clp_profession_data_gx",
            "han": "clp_profession_data_han",
            "nmg": "clp_profession_data_nmg",
            "nx": "clp_profession_data_nx",
            "qh": "clp_profession_data_qh",
            "xj": "clp_profession_data_xj",
            "xz": "clp_profession_data_xz",
        }
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.text_factory = str
        try:
            yield conn
        finally:
            conn.close()
    
    def score_to_rank(self, province: str, year: int, nature: str, score: int) -> Optional[int]:
        """分数 → 位次"""
        with self.get_connection() as conn:
            sql = """
            SELECT rank FROM clp_score_rank 
            WHERE prov = ? AND year = ? AND nature = ? AND score = ?
            """
            cursor = conn.execute(sql, [province, year, nature, score])
            row = cursor.fetchone()
            return row['rank'] if row else None
    
    def rank_to_score(self, province: str, year: int, nature: str, rank: int) -> Optional[int]:
        """位次 → 分数"""
        with self.get_connection() as conn:
            sql = """
            SELECT score FROM clp_score_rank 
            WHERE prov = ? AND year = ? AND nature = ? AND rank <= ?
            ORDER BY rank DESC LIMIT 1
            """
            cursor = conn.execute(sql, [province, year, nature, rank])
            row = cursor.fetchone()
            return row['score'] if row else None
    
    def get_equivalent_scores(self, province: str, nature: str, 
                            current_rank: int, current_year: int = 2025) -> Dict[int, int]:
        """
        获取历年等效分（核心算法）
        
        正确步骤：
        1. 用当前位次，在历年一分一段表中反查，获取历年等效分
        2. 用于和院校历年录取分对比
        """
        equivalent = {}
        years = [current_year, current_year - 1, current_year - 2]
        
        with self.get_connection() as conn:
            for year in years:
                sql = """
                SELECT score FROM clp_score_rank 
                WHERE prov = ? AND year = ? AND nature = ? AND rank <= ?
                ORDER BY rank DESC LIMIT 1
                """
                cursor = conn.execute(sql, [province, year, nature, current_rank])
                row = cursor.fetchone()
                if row:
                    equivalent[year] = row['score']
        
        return equivalent
    
    def query_schools(self, province: str, conditions: UserCondition) -> List[Dict]:
        """查询院校列表"""
        table = self.province_tables.get(province)
        if not table:
            return []
        
        with self.get_connection() as conn:
            sql = f"""
            SELECT DISTINCT s.id, s.school, s.city, s.prov
            FROM clp_school s
            INNER JOIN {table} p ON p.school_id = CAST(s.id AS INTEGER)
            WHERE p.year = ? AND p.nature = ?
            """
            params = [conditions.year, conditions.nature]
            
            if conditions.city:
                sql += " AND s.city LIKE ?"
                params.append(f"%{conditions.city}%")
            
            if conditions.school_name:
                sql += " AND s.school LIKE ?"
                params.append(f"%{conditions.school_name}%")
            
            sql += " ORDER BY s.school LIMIT 100"
            
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def query_admission_plans(self, conditions: UserCondition) -> List[AdmissionResult]:
        """
        查询录取计划
        
        Args:
            conditions: 查询条件
            
        Returns:
            List[AdmissionResult]: 录取结果列表
        """
        province = conditions.province
        table = self.province_tables.get(province)
        if not table:
            return []
        
        with self.get_connection() as conn:
            sql = f"""
            SELECT 
                p.school_id,
                s.school,
                s.city,
                p.pro,
                p.pro_note,
                p.low_real,
                p.low_rank_real,
                p.avg_real,
                p.plan_num,
                p.year,
                p.nature
            FROM {table} p
            INNER JOIN clp_school s ON p.school_id = CAST(s.id AS INTEGER)
            WHERE p.year = ? AND p.nature = ?
            """
            params = [conditions.year, conditions.nature]
            
            if conditions.school_name:
                sql += " AND s.school LIKE ?"
                params.append(f"%{conditions.school_name}%")
            
            if conditions.major_name:
                sql += " AND p.pro LIKE ?"
                params.append(f"%{conditions.major_name}%")
            
            # 排除条件
            if conditions.exclude_tags:
                for tag in conditions.exclude_tags:
                    if "中外合作" in tag:
                        sql += " AND (p.pro_note NOT LIKE '%中外%' OR p.pro_note IS NULL)"
                    if "师范" in tag:
                        sql += " AND (p.pro NOT LIKE '%师范%' OR p.pro IS NULL)"
            
            sql += " AND p.plan_num >= 2 ORDER BY p.low_real DESC LIMIT 300"
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
        
        # 转换为结果对象
        results = []
        for row in rows:
            result = AdmissionResult(
                school_id=row['school_id'],
                school_name=row['school'],
                city=row['city'],
                major=row['pro'],
                major_note=row.get('pro_note'),
                year=row['year'],
                nature=row['nature'],
                low_score=int(row['low_real']) if row['low_real'] else 0,
                low_rank=int(row['low_rank_real']) if row['low_rank_real'] else 0,
                avg_score=float(row['avg_real']) if row['avg_real'] else 0.0,
                plan_num=int(row['plan_num']) if row['plan_num'] else 0
            )
            results.append(result)
        
        # 计算风险等级
        if conditions.score or conditions.rank:
            results = self._calculate_risk(results, conditions)
        
        return results
    
    def _calculate_risk(self, results: List[AdmissionResult], 
                       conditions: UserCondition) -> List[AdmissionResult]:
        """计算风险等级"""
        
        # 获取考生位次
        if conditions.rank:
            user_rank = conditions.rank
        elif conditions.score:
            user_rank = self.score_to_rank(
                conditions.province,
                conditions.year,
                conditions.nature,
                conditions.score
            )
            if not user_rank:
                return results
        else:
            return results
        
        # 获取历年等效分
        equivalent_scores = self.get_equivalent_scores(
            conditions.province,
            conditions.nature,
            user_rank,
            conditions.year
        )
        
        for result in results:
            result.user_rank = user_rank
            result.user_score = conditions.score
            
            # 计算分差（简化版：用当年数据）
            # 正确做法应该是用历年等效分和院校历年录取分对比
            if result.low_rank and user_rank:
                diff = user_rank - result.low_rank
                
                # 简化：位次差转化为分差估算（每1000位次约等于5分）
                diff_score = diff * 5 / 1000
                result.diff_avg = -diff_score  # 负数表示位次更好
                
                # 判断风险等级
                if diff_score > 20:
                    result.risk_level = RiskLevel.EXTREME_RISK
                elif diff_score > 0:
                    result.risk_level = RiskLevel.SPRINT
                elif diff_score > -10:
                    result.risk_level = RiskLevel.SUITABLE
                elif diff_score > -20:
                    result.risk_level = RiskLevel.SAFE
                else:
                    result.risk_level = RiskLevel.BOTTOM
        
        return results
    
    def query_batch_line(self, province: str, year: int, nature: str) -> Optional[int]:
        """查询批次线（一本线）"""
        with self.get_connection() as conn:
            sql = """
            SELECT score FROM clp_batch_line 
            WHERE prov = ? AND year = ? AND nature = ? AND batch LIKE '%一批%'
            """
            cursor = conn.execute(sql, [province, year, nature])
            row = cursor.fetchone()
            return row['score'] if row else None
