# 蜻蜓智能志愿查询技能

## ⚠️ 首次使用配置

**首次安装本技能需要配置两个内容：**

### 1. API Key（必填）

请联系开发者获取API Key，然后编辑 `config.py`：
```python
API_KEY = "您的API Key"
```

或设置环境变量：
```bash
export QITING_API_KEY="您的API Key"
```

### 2. 数据库路径（可选）

如果数据库不在默认位置，编辑 `config.py`：
```python
DB_PATH = "/path/to/your/database.db"
```

或设置环境变量：
```bash
export QTING_DB_PATH="/path/to/database.db"
```

---

## 🚀 启动服务

```bash
cd ~/.openclaw/workspace/skills/qingting-query/
python3 client/api_server.py
```

或使用启动脚本：
```bash
./client/start.sh
```

---

## 📖 功能说明

### 支持的查询类型

| 输入示例 | 识别意图 |
|---------|---------|
| 辽宁物理类520分能上什么学校 | 推荐志愿 |
| 计算机专业多少分 | 查专业 |
| 能上大连理工吗 | 查院校 |
| 帮我推荐志愿 | 推荐志愿 |

### 查询格式

```
省份 + 科类 + 分数/位次
```

示例：
- 辽宁物理类520分
- 山东历史类560分全省5000名

---

## ❓ 常见问题

**Q: 提示"API Key未配置"**
A: 请编辑 `config.py` 配置您的API Key

**Q: 提示"数据库不存在"**
A: 请联系开发者获取数据库文件，并配置正确路径

**Q: 如何获取API Key**
A: 请联系开发者购买

---

## 🔗 相关链接

- 客户端仓库: https://github.com/gaishixiaozhu/-qingting-query-client
- 管理端仓库: https://github.com/gaishixiaozhu/-qingting-query-admin
