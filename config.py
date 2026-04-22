# 蜻蜓查询客户端配置
# 客户端不需要数据库，只通过API访问数据

import os

# API Key配置（从开发者处获取）
# 方式1: 直接在这里填写
API_KEY = ""

# 方式2: 通过环境变量配置
if not API_KEY:
    API_KEY = os.environ.get("QINGTING_API_KEY", "")

# API服务地址
# 本地调试: http://localhost:5006
# 外网访问: https://12335pm0oq770.vicp.fun
API_BASE_URL = os.environ.get("QTING_API_URL", "http://localhost:5006")
