# 蜻蜓智能志愿查询系统 - 客户端

基于OpenClaw的智能志愿填报推荐系统，采用等位分法算法。

---

## 📦 安装步骤

### 第一步：克隆仓库

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/gaishixiaozhu/-qingting-query-client.git qingting-query
```

### 第二步：安装依赖

```bash
cd qingting-query/client
pip install flask requests
```

### 第三步：配置

**方式一：使用配置向导（推荐）**

```bash
python3 setup_config.py
```

按提示输入：
1. API Key（联系开发者获取）
2. 数据库路径（如有需要）

**方式二：手动配置**

编辑 `config.py`：

```python
API_KEY = "您的API Key"
DB_PATH = "/path/to/your/database.db"  # 可选
```

**方式三：环境变量**

```bash
export QITING_API_KEY="您的API Key"
export QTING_DB_PATH="/path/to/database.db"
export QTING_API_URL="http://localhost:5006"
```

### 第四步：启动服务

```bash
python3 api_server.py
# 或使用启动脚本
./start.sh
```

### 第五步：验证

```bash
curl http://localhost:5006/api/v1/health
```

返回 `{"status": "ok"}` 表示成功。

---

## ⚠️ 常见问题

### 1. API Key未配置

**错误**: `API Key未配置！请联系开发者购买API Key`

**解决**: 编辑 `config.py`，填写您的API Key：
```python
API_KEY = "sk_qt_您的Key"
```

### 2. 数据库文件不存在

**错误**: `数据库文件不存在`

**解决**: 
1. 联系开发者获取数据库文件
2. 或确认数据库路径后配置到 `config.py`

### 3. 启动失败

```bash
# 检查端口是否被占用
lsof -i :5006

# 使用其他端口
PORT=5007 python3 api_server.py
```

---

## 📡 API接口

### 主查询接口

```bash
curl -X POST http://localhost:5006/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"text": "辽宁物理类520分能上什么学校"}'
```

### 健康检查

```bash
curl http://localhost:5006/api/v1/health
```

---

## 🔧 配置说明

| 配置项 | 环境变量 | 说明 |
|-------|---------|------|
| API_KEY | QITING_API_KEY | API密钥（必填） |
| DB_PATH | QTING_DB_PATH | 数据库路径 |
| API_BASE_URL | QTING_API_URL | API服务地址 |
| PORT | PORT | 服务端口（默认5006） |

---

## 📚 相关文档

- [接口设计文档](./docs/API设计文档.md)
- [意图识别设计文档](./docs/意图识别设计文档.md)

---

## 📞 获取帮助

请联系开发者获取：
1. API Key
2. 数据库文件
3. 技术支持
