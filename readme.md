# Patient Agent - 精神科患者智能体

一个基于RAG（检索增强生成）技术的精神科患者模拟系统，支持通过REST API进行患者对话模拟。

## 项目特性

- 🤖 **智能患者模拟**: 基于LangGraph的RAG工作流生成个性化患者
- 🧠 **多维度人格**: 支持信任度、配合度、情绪反应等多维度患者行为模拟
- 📋 **完整病历生成**: 自动生成符合临床规范的8部分结构病历
- 🔄 **多会话管理**: 支持同时管理多个患者会话
- 🌐 **REST API**: 提供完整的HTTP API接口
- 🐳 **容器化部署**: 支持Docker和Docker Compose部署

## 目录结构

```
patient_agent_full_v3_backend/
├── app.py                    # Flask API 主应用
├── run_server.py            # 服务器启动脚本
├── config.py                # 配置文件
├── test_api.py              # API测试脚本
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker Compose配置
├── API_DOCUMENTATION.md     # API文档
├── Part1.py                 # RAG 工作流（检索与病历生成）
├── Part1RAG/                # DSM-5/知识库 Markdown 文档
├── patient_agent/           # 患者智能体核心模块
│   ├── cli.py              # 命令行交互（保留）
│   ├── server.py           # FastAPI + WebSocket 服务（保留）
│   ├── policy.py           # 患者对话策略链
│   ├── prompts.py          # 提示词模板
│   ├── record_generator.py # 调用 Part1 并解析病历
│   ├── schemas.py          # Pydantic 数据结构
│   └── state.py            # 默认会话/Persona/Profile
└── requirements.txt         # 项目依赖
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd patient_agent_full_v3_backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.apicore.ai/v1"
export SECRET_KEY="your-secret-key"
```

### 3. 启动服务

#### 开发模式
```bash
python app.py
# 或
python run_server.py --mode dev --debug
```

#### 生产模式
```bash
python run_server.py --mode prod --host 0.0.0.0 --port 5000
```

### 4. 测试API

```bash
# 运行测试套件
python test_api.py

# 或手动测试
curl http://localhost:5000/health
```

## API 使用示例

### 创建患者会话

```bash
curl -X POST http://localhost:5000/api/v1/patients/create \
  -H "Content-Type: application/json" \
  -d '{
    "age": "25",
    "gender": "女",
    "diagnosis": "精神分裂症",
    "severity": "中度"
  }'
```

### 与患者对话

```bash
curl -X POST http://localhost:5000/api/v1/patients/{session_id}/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下你的情况"
  }'
```

## Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key"
export SECRET_KEY="your-secret-key"

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 使用 Docker

```bash
# 构建镜像
docker build -t patient-agent-api .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -e OPENAI_API_KEY="your-api-key" \
  -e SECRET_KEY="your-secret-key" \
  --name patient-agent \
  patient-agent-api
```

## 原有CLI功能（保留）

项目仍支持原有的命令行交互模式：

```bash
# 完整链路
python -m patient_agent.cli --age 40 --gender 女 --diagnosis 精神分裂症 --severity 重度

# 跳过 RAG（仅验证策略链路）
python -m patient_agent.cli --no-rag
```

CLI 内部命令：
- `/stage opening|information_gathering|explanation_planning|closing` 切换会话阶段
- `/persona` 查看当前 Persona
- `/profile` 查看当前 Profile
- `/regen` 用当前四参重新生成病历（覆盖 Profile/Persona）
- `/quit` 退出

## 依赖说明

主要依赖包：
- **Flask**: Web框架
- **LangChain**: LLM应用框架
- **LangGraph**: 工作流编排
- **Pydantic**: 数据验证
- **FAISS**: 向量数据库
- **OpenAI**: LLM API

完整依赖列表请查看 `requirements.txt`

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务器主机地址 |
| `PORT` | `5000` | 服务器端口 |
| `DEBUG` | `False` | 调试模式 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `OPENAI_API_KEY` | - | OpenAI API密钥 |
| `OPENAI_API_BASE` | `https://api.apicore.ai/v1` | OpenAI API基础URL |
| `SECRET_KEY` | - | Flask密钥（生产环境必需） |

### 配置文件

详细配置选项请查看 `config.py`

## 故障排除

### 常见问题

1. **RAG生成失败**
   - 检查API密钥配置
   - 确认网络连接正常
   - 查看日志获取详细错误信息

2. **依赖安装失败**
   - 确保Python版本 >= 3.9
   - 在Windows上，FAISS可能需要Visual Studio Build Tools

3. **端口占用**
   - 修改 `--port` 参数使用其他端口
   - 或使用 `lsof -i :5000` 查找占用进程

### 日志查看

```bash
# 开发模式日志
python app.py

# Docker日志
docker-compose logs -f patient-agent-api
```

## 开发指南

### 添加新功能

1. 在 `patient_agent/` 模块中添加业务逻辑
2. 在 `app.py` 中添加新的API端点
3. 更新 `test_api.py` 添加测试用例
4. 更新 `API_DOCUMENTATION.md` 文档

### 代码规范

- 使用类型注解
- 遵循PEP 8代码风格
- 添加适当的错误处理
- 编写单元测试

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 添加Flask REST API支持
- 实现多会话管理
- 添加Docker部署支持
- 完善API文档和测试