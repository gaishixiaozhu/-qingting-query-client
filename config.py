# 蜻蜓查询客户端配置
# 请在此处填写您的API Key

import os
import pathlib

# API Key配置（从开发者处获取）
# 方式1: 直接在这里填写
API_KEY = ""

# Salt配置（与服务器保持一致，自动从环境变量或配置文件读取）
SALT = os.environ.get("QINGTING_API_SALT", "cb86d1a32cb94865ae3deda0650d0400ef2d59a675490f73efcadbc8c51bbfd5")

# 方式2: 通过环境变量 QINGTING_API_KEY 配置
if not API_KEY:
    API_KEY = os.environ.get("QINGTING_API_KEY", "")

# 数据库路径配置
# 方式1: 直接在这里填写
DB_PATH = ""

# 方式2: 通过环境变量 QTING_DB_PATH 配置
if not DB_PATH:
    DB_PATH = os.environ.get("QTING_DB_PATH", "")

# 自动检测数据库位置
if not DB_PATH:
    # 常见的数据库位置
    possible_paths = [
        pathlib.Path.home() / ".openclaw/skills/data/cache.db",
        pathlib.Path.home() / ".openclaw/skills/data/qingting_cache.db",
        pathlib.Path("/data/cache.db"),
        pathlib.Path("/app/data/cache.db"),
    ]
    
    for p in possible_paths:
        if p.exists():
            DB_PATH = str(p)
            break

# 服务地址
API_BASE_URL = os.environ.get("QTING_API_URL", "http://localhost:5006")
