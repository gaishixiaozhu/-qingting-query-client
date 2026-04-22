# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 智能意图识别层
"""

import re
from typing import Dict, List, Optional, Tuple
from models import IntentType, QueryMode, UserCondition, IntentResult

class IntelligentIR:
    """
    智能意图识别
    
    判断逻辑：
    1. 如果用户只是简单问答（问候、闲聊、通用问题）→ 不触发skill
    2. 如果用户询问志愿、分数、院校、专业 → 触发skill
    """
    
    # 省份映射
    PROVINCE_MAP = {
        "辽宁": "ln", "大连": "ln", "沈阳": "ln",
        "山东": "sd", "青岛": "sd", "济南": "sd",
        "四川": "sc", "成都": "sc",
        "河南": "hen", "郑州": "hen",
        "广东": "gd", "广州": "gd", "深圳": "gd",
        "江苏": "js", "南京": "js", "苏州": "js",
        "浙江": "zj", "杭州": "zj",
        "河北": "heb", "石家庄": "heb",
        "湖北": "hub", "武汉": "hub",
        "湖南": "hun", "长沙": "hun",
        "安徽": "ah", "合肥": "ah",
        "福建": "fj", "福州": "fj", "厦门": "fj",
        "江西": "jx", "南昌": "jx",
        "山西": "sx", "太原": "sx",
        "陕西": "shx", "西安": "shx",
        "甘肃": "gs", "兰州": "gs",
        "吉林": "jl", "长春": "jl",
        "黑龙江": "hlj", "哈尔滨": "hlj",
        "北京": "bj",
        "天津": "tj",
        "上海": "sh",
        "重庆": "cq",
        "贵州": "gz", "贵阳": "gz",
        "云南": "yn", "昆明": "yn",
        "广西": "gx", "南宁": "gx",
        "海南": "han", "海口": "han",
        "内蒙古": "nmg", "呼和浩特": "nmg",
        "宁夏": "nx", "银川": "nx",
        "青海": "qh", "西宁": "qh",
        "新疆": "xj", "乌鲁木齐": "xj",
        "西藏": "xz", "拉萨": "xz",
    }
    
    # 科类映射
    NATURE_MAP = {
        "物理": "物理类", "物理类": "物理类", "理科": "理科",
        "历史": "历史类", "历史类": "历史类", "文科": "文科",
        "首选物理": "物理类", "首选历史": "历史类",
    }
    
    # 简单问答关键词（不触发skill）
    SIMPLE_QUESTION_PATTERNS = [
        r"^(你好|您好|嗨|hi|hello|hi)$",
        r"^(谢谢|谢谢!|感谢)$",
        r"^(好的|收到|明白|了解)$",
        r"^(你是谁|你是|叫什么名字)",
        r"^(有什么用|能做什么|功能)",
        r"^(怎么用|如何使用|帮助|help)",
        r"^(多少钱|价格|收费|免费)",
        r"^(再见|拜拜|下次见)",
    ]
    
    # 触发skill的关键词
    SKILL_TRIGGER_PATTERNS = [
        # 查分数/位次
        r"\d{3}分", r"位次", r"分数", r"排名", r"多少名",
        # 查院校
        r"学校", r"大学", r"学院", r"院校", r"能上",
        # 查专业
        r"专业", r"院系", r"方向",
        # 查计划
        r"招生", r"计划", r"名额", r"招人",
        # 志愿相关
        r"志愿", r"填报", r"推荐", r"方案", r"报考",
        # 录取相关
        r"录取", r"投档", r"分数线",
    ]
    
    # 意图识别模式
    INTENT_PATTERNS = {
        "推荐志愿": [r"推荐志愿", r"帮我报志愿", r"志愿方案", r"怎么填", r"报什么", r"志愿填报", r"给我选"],
        "查专业": [r"专业", r"哪些学校.*计算机", r"录取.*专业", r"专业.*分数"],
        "查院校": [r"能上.*吗", r"多少分.*大学", r"考上.*要", r"院校.*录取"],
        "查计划": [r"招生", r"计划", r"名额", r"招.*人"],
        "简单问答": [r"是什么", r"什么意思", r"解释", r"讲讲", r"介绍一下"],
    }
    
    def __init__(self):
        pass
    
    def recognize(self, text: str, context: Optional[IntentResult] = None) -> IntentResult:
        """
        识别意图
        
        Returns:
            IntentResult: 包含意图类型和是否触发skill的标志
        """
        result = IntentResult(
            conditions=UserCondition(original_text=text)
        )
        
        # 清理文本
        text = self._clean_text(text)
        result.conditions.original_text = text
        
        # 1. 先判断是否简单问答
        if self._is_simple_question(text):
            result.intent = IntentType.SIMPLE_QUESTION
            result.should_trigger_skill = False
            result.response_message = None  # 不拦截，正常回答
            return result
        
        # 2. 判断是否触发skill
        if not self._should_trigger_skill(text):
            result.intent = IntentType.SIMPLE_QUESTION
            result.should_trigger_skill = False
            return result
        
        # 3. 识别具体意图
        result.intent, result.confidence = self._recognize_intent(text)
        result.should_trigger_skill = True
        
        # 4. 提取条件
        self._extract_conditions(text, result, context)
        
        # 5. 检查条件完整性
        self._check_conditions(result)
        
        # 6. 生成建议
        self._generate_suggestions(result)
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        text = text.strip()
        text = text.replace(" ", "").replace("，", ",").replace("。", ".")
        return text
    
    def _is_simple_question(self, text: str) -> bool:
        """判断是否简单问答"""
        for pattern in self.SIMPLE_QUESTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _should_trigger_skill(self, text: str) -> bool:
        """判断是否应该触发skill"""
        for pattern in self.SKILL_TRIGGER_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
    
    def _recognize_intent(self, text: str) -> Tuple[IntentType, float]:
        """识别具体意图"""
        best_intent = IntentType.UNKNOWN
        best_score = 0.0
        
        for intent_name, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    score = 0.6 + (0.1 * len(patterns))
                    if score > best_score:
                        best_score = score
                        if intent_name == "推荐志愿":
                            best_intent = IntentType.RECOMMEND_ADMISSION
                        elif intent_name == "查专业":
                            best_intent = IntentType.QUERY_MAJOR
                        elif intent_name == "查院校":
                            best_intent = IntentType.QUERY_SCHOOL
                        elif intent_name == "查计划":
                            best_intent = IntentType.QUERY_PLAN
                        elif intent_name == "简单问答":
                            best_intent = IntentType.SIMPLE_QUESTION
        
        # 如果没有匹配，根据关键词判断
        if best_intent == IntentType.UNKNOWN:
            if re.search(r"\d{3}分", text):
                best_intent = IntentType.QUERY_MAJOR
                best_score = 0.5
            elif re.search(r"学校|大学", text):
                best_intent = IntentType.QUERY_SCHOOL
                best_score = 0.5
        
        return best_intent, best_score
    
    def _extract_conditions(self, text: str, result: IntentResult, context: Optional[IntentResult]):
        """提取查询条件"""
        c = result.conditions
        
        # 从上下文继承
        if context:
            pc = context.conditions
            if not c.province and pc.province:
                c.province = pc.province
                c.province_name = pc.province_name
                result.condition_fills.append(f"继承省份：{pc.province_name}")
            if not c.nature and pc.nature:
                c.nature = pc.nature
                result.condition_fills.append(f"继承科类：{pc.nature}")
            if not c.score and not c.rank and (pc.score or pc.rank):
                c.score = pc.score
                c.rank = pc.rank
                result.condition_fills.append("继承分数/位次")
        
        # 省份
        for name, code in self.PROVINCE_MAP.items():
            if name in text:
                c.province = code
                c.province_name = name
                break
        
        # 科类
        for keyword, nature in self.NATURE_MAP.items():
            if keyword in text:
                c.nature = nature
                break
        
        # 分数
        score_match = re.search(r"(\d{3})分", text)
        if score_match:
            c.score = int(score_match.group(1))
        
        # 位次
        rank_match = re.search(r"第(\d+)名|全省第?(\d+)名|位次(\d+)", text)
        if rank_match:
            c.rank = int(rank_match.group(1) or rank_match.group(2) or rank_match.group(3))
        
        # 年份
        year_match = re.search(r"(20\d{2})年?", text)
        if year_match:
            year = int(year_match.group(1))
            if 2020 <= year <= 2026:
                c.year = year
        
        # 风险偏好
        if re.search(r"冲|激进", text):
            c.risk_preference = "激进"
        elif re.search(r"稳|保守", text):
            c.risk_preference = "保守"
    
    def _check_conditions(self, result: IntentResult):
        """检查条件完整性"""
        c = result.conditions
        
        # 推荐志愿必须有分数/位次
        if result.intent == IntentType.RECOMMEND_ADMISSION:
            if not c.score and not c.rank:
                result.condition_warnings.append("缺少分数或位次信息，请提供")
            if not c.province:
                result.condition_warnings.append("缺少省份信息，请提供")
            if not c.nature:
                result.condition_warnings.append("缺少科类信息（物理类/历史类），请提供")
    
    def _generate_suggestions(self, result: IntentResult):
        """生成建议"""
        c = result.conditions
        
        if not c.province:
            result.suggestions.append("请告诉我您想查询的省份，如：辽宁、山东")
        if not c.nature:
            result.suggestions.append("请告诉我您的科类，如：物理类、历史类")
        if not c.score and not c.rank:
            result.suggestions.append("请提供您的分数或位次")
        
        # 推荐志愿的格式建议
        if result.intent == IntentType.RECOMMEND_ADMISSION:
            if c.province and c.nature and (c.score or c.rank):
                result.suggestions.append(f"格式参考：帮我生成{c.province_name}{c.nature}{c.score or c.rank}分的志愿方案")
