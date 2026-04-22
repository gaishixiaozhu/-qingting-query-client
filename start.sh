#!/bin/bash
# 蜻蜓查询API服务启动脚本

# 配置
export PORT=${PORT:-5006}
export DB_PATH=${DB_PATH:-"/Users/fuquanhao/.openclaw/skills/data/cache.db"}

# API Key验证配置（可选）
# export KEYS_FILE="/path/to/your/api_keys.json"

echo "=========================================="
echo "  蜻蜓智能志愿查询 API 服务"
echo "=========================================="
echo ""
echo "配置信息："
echo "  端口: $PORT"
echo "  数据库: $DB_PATH"
echo ""

# 检查数据库
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 错误：数据库文件不存在: $DB_PATH"
    exit 1
fi

echo "✅ 数据库检查通过"
echo ""

# 启动服务
echo "正在启动服务..."
echo ""

cd "$(dirname "$0")"
python3 api_server.py
