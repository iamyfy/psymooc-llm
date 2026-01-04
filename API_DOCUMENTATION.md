# Patient Agent API 文档

## 概述

Patient Agent API 是一个基于Flask的REST API服务，提供精神科患者模拟和对话功能。该API将原有的CLI患者智能体改造为Web服务，支持多会话管理和实时对话。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 3. 健康检查

```bash
curl http://localhost:5000/health
```

## API 端点

### 基础信息

- **基础URL**: `http://localhost:5000`
- **API版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1. 创建患者会话

**POST** `/api/v1/patients/create`

创建新的患者会话，通过RAG生成个性化病历。

#### 请求参数

```json
{
    "age": "25",
    "gender": "女", 
    "diagnosis": "精神分裂症",
    "severity": "中度"
}
```

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "patient_profile": {
        "demographics": {
            "name": "李某",
            "gender": "女",
            "age": "25"
        },
        "chief_complaint": "情绪异常，出现幻觉",
        "diagnosis": "精神分裂症",
        "severity": "中度"
    },
    "patient_persona": {
        "traits": ["内向", "敏感"],
        "insight_level": 0.6,
        "trust_toward_clinician": 0.5
    },
    "medical_record": "完整的病历文本..."
}
```

### 2. 获取患者信息

**GET** `/api/v1/patients/{session_id}`

获取指定会话的患者信息。

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "patient_profile": { ... },
    "patient_persona": { ... },
    "current_stage": "opening",
    "dialog_count": 0
}
```

### 3. 与患者对话

**POST** `/api/v1/patients/{session_id}/chat`

向患者发送消息并获取回复。

#### 请求参数

```json
{
    "message": "你好，请介绍一下你的情况"
}
```

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "doctor_message": "你好，请介绍一下你的情况",
    "patient_reply": "医生您好，我最近感觉有些不对劲...",
    "current_stage": "information_gathering"
}
```

### 4. 获取对话历史

**GET** `/api/v1/patients/{session_id}/history`

获取指定会话的完整对话历史。

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "dialog_history": [
        {
            "speaker": "doctor",
            "text": "你好，请介绍一下你的情况"
        },
        {
            "speaker": "patient", 
            "text": "医生您好，我最近感觉有些不对劲..."
        }
    ],
    "total_turns": 2
}
```

### 5. 更新对话阶段

**PUT** `/api/v1/patients/{session_id}/stage`

更新患者的对话阶段。

#### 请求参数

```json
{
    "stage": "information_gathering"
}
```

#### 有效阶段值

- `opening`: 开场阶段
- `information_gathering`: 信息收集阶段  
- `explanation_planning`: 解释规划阶段
- `closing`: 结束阶段

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "old_stage": "opening",
    "new_stage": "information_gathering"
}
```

### 6. 重新生成病历

**POST** `/api/v1/patients/{session_id}/regenerate`

使用当前患者信息重新生成病历。

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "new_profile": { ... },
    "new_persona": { ... },
    "medical_record": "重新生成的病历文本..."
}
```

### 7. 删除会话

**DELETE** `/api/v1/patients/{session_id}`

删除指定的患者会话。

#### 响应示例

```json
{
    "success": true,
    "message": "会话 123e4567-e89b-12d3-a456-426614174000 已删除"
}
```

## 错误处理

所有API端点都返回统一的错误格式：

```json
{
    "success": false,
    "error": "错误描述信息"
}
```

### 常见HTTP状态码

- `200`: 成功
- `400`: 请求参数错误
- `404`: 会话不存在
- `500`: 服务器内部错误

## 使用示例

### Python客户端示例

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:5000"

# 1. 创建患者会话
create_data = {
    "age": "25",
    "gender": "女",
    "diagnosis": "精神分裂症", 
    "severity": "中度"
}

response = requests.post(f"{BASE_URL}/api/v1/patients/create", json=create_data)
session_data = response.json()
session_id = session_data["session_id"]

print(f"创建会话成功: {session_id}")

# 2. 开始对话
chat_data = {"message": "你好，请介绍一下你的情况"}
response = requests.post(f"{BASE_URL}/api/v1/patients/{session_id}/chat", json=chat_data)
chat_result = response.json()

print(f"患者回复: {chat_result['patient_reply']}")

# 3. 获取对话历史
response = requests.get(f"{BASE_URL}/api/v1/patients/{session_id}/history")
history = response.json()
print(f"对话轮数: {history['total_turns']}")
```

### cURL示例

```bash
# 创建会话
curl -X POST http://localhost:5000/api/v1/patients/create \
  -H "Content-Type: application/json" \
  -d '{"age":"25","gender":"女","diagnosis":"精神分裂症","severity":"中度"}'

# 发送消息
curl -X POST http://localhost:5000/api/v1/patients/{session_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，请介绍一下你的情况"}'
```

## 配置说明

### 环境变量

可以通过环境变量配置API密钥：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.apicore.ai/v1"
```

### 日志配置

API使用Python标准logging模块，日志级别为INFO。生产环境建议配置更详细的日志记录。

## 部署建议

### 开发环境

```bash
python app.py
```

### 生产环境

建议使用Gunicorn部署：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 注意事项

1. **会话管理**: 当前使用内存存储会话，重启服务会丢失所有会话数据
2. **并发限制**: 建议在生产环境中添加请求限流和并发控制
3. **安全性**: 生产环境需要添加身份验证和授权机制
4. **数据持久化**: 建议使用Redis或数据库存储会话数据
5. **监控**: 建议添加性能监控和错误追踪

## 故障排除

### 常见问题

1. **RAG生成失败**: 检查API密钥配置和网络连接
2. **会话不存在**: 确认session_id正确且会话未过期
3. **参数错误**: 检查请求参数格式和必需字段

### 调试模式

启动时设置debug=True可以获取详细的错误信息：

```python
app.run(debug=True)
```









