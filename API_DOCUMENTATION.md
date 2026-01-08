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

### 8. 评估对话并生成文档

**POST** `/api/v1/patients/{session_id}/evaluate`

对指定会话的对话记录进行评估，生成评分和反馈，并返回完整的对话文档。

该端点会调用两个 LangChain Agent：
- **评分 Agent**：依据结构化量表从三大类别（原则态度20分、基本技巧50分、效果印象30分）共15个子项进行客观评分（满分100分）
- **反馈 Agent**：基于沟通技能标签列表提供详细的主观反馈，包括整体评估和针对每个技能标签的情境化分析与指导

#### 响应示例

```json
{
    "success": true,
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "evaluation": {
        "scoring": {
            "原则态度": {
                "A1 尊重并理解患者": {
                    "score": 3.5,
                    "comment": "称呼得体，对患者处境表现理解"
                },
                "A2 态度真诚和蔼": {
                    "score": 4,
                    "comment": "语气温和，表达关怀"
                },
                "A3 以患者为中心的交流方式": {
                    "score": 3.5,
                    "comment": "优先关注患者主诉"
                },
                "A4 知情同意": {
                    "score": 2,
                    "comment": "对话未体现知情同意流程"
                },
                "A5 伦理与纠纷风险控制": {
                    "score": 4,
                    "comment": "无违背伦理的言语"
                },
                "小计": 17
            },
            "基本技巧": {
                "B1 倾听与反应": {
                    "score": 8,
                    "comment": "对关键内容有回应，体现倾听"
                },
                "B2 鼓励表达": {
                    "score": 4,
                    "comment": "使用鼓励语，留白适当"
                },
                "B3 提问结构（开放→封闭）": {
                    "score": 7.5,
                    "comment": "先开放后聚焦，转换自然"
                },
                "B4 重要信息与解释核实": {
                    "score": 6,
                    "comment": "部分核实，可加强"
                },
                "B5 具体建议": {
                    "score": 3,
                    "comment": "建议较空泛"
                },
                "B6 医生意见表达": {
                    "score": 4,
                    "comment": "表达清晰"
                },
                "B7 总结（阶段/结束）": {
                    "score": 3,
                    "comment": "对话未体现总结"
                },
                "小计": 35.5
            },
            "效果印象": {
                "C1 沟通目的达成度": {
                    "score": 8,
                    "comment": "访谈目标清晰，关键问题得到推进"
                },
                "C2 患者舒适与被理解": {
                    "score": 7.5,
                    "comment": "患者情绪被接住，表达较充分"
                },
                "C3 总体沟通能力印象": {
                    "score": 8,
                    "comment": "整体结构清晰，专业且有人情味"
                },
                "小计": 23.5
            },
            "总分": 76,
            "主要亮点": ["开场自然，建立关系良好", "提问结构合理，先开放后聚焦"],
            "主要问题": ["未体现知情同意流程", "缺少阶段性总结"],
            "可操作的改进建议": ["在访谈开始时说明目的和流程", "在关键节点进行阶段性小结"]
        },
        "feedback": "【优点与亮点】\n1. 开场自然，能够快速建立与患者的信任关系...\n\n【需要改进的地方】\n1. 在信息收集阶段可以更加系统化...\n\n【专业建议】\n1. 对于精神分裂症患者，需要特别关注...\n\n【学习要点】\n1. 精神科问诊的核心技巧..."
    },
    "document": "================================================================================\n精神科问诊对话记录\n================================================================================\n\n生成时间：2024-01-15 10:30:00\n会话ID：123e4567-e89b-12d3-a456-426614174000\n\n...完整文档内容...",
    "formatted_dialog": "第1轮：\n医生：你好，请介绍一下你的情况\n患者：医生您好，我最近感觉有些不对劲...\n...",
    "patient_info": "姓名：李某\n性别：女\n年龄：25\n职业：学生\n诊断：精神分裂症\n严重程度：中度\n主诉：情绪异常，出现幻觉"
}
```

#### 注意事项

- 该端点需要调用 LLM 进行评估，可能需要较长时间（通常10-30秒）
- 如果会话中没有对话记录，将返回错误
- 评分结果以 JSON 格式返回，包含各维度分数和总分
- 反馈结果以自然语言文本返回，包含详细的专业建议

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

# 4. 评估对话并生成文档
response = requests.post(f"{BASE_URL}/api/v1/patients/{session_id}/evaluate")
evaluation = response.json()
if evaluation.get('success'):
    print(f"总分: {evaluation['evaluation']['scoring'].get('总分', 'N/A')}")
    print(f"反馈: {evaluation['evaluation']['feedback'][:200]}...")  # 显示前200字符
    # 可以保存文档到文件
    with open(f"dialog_report_{session_id}.txt", "w", encoding="utf-8") as f:
        f.write(evaluation['document'])
    print("文档已保存到文件")
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









