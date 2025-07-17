# 知识图谱AI助手集成指南

## 功能特性

✅ **医疗领域专业AI助手**
- 基于医疗知识图谱数据回答用户问题
- 专业的医疗领域提示词和约束
- 自动添加医疗免责声明

✅ **智能实体搜索与聚焦**
- 实时搜索医疗实体（疾病、症状、药物等）
- 支持精确匹配和模糊匹配
- 一键聚焦相关节点到知识图谱

✅ **分页式交互体验**
- 聊天历史分页浏览
- 参考来源分页显示
- 响应式界面设计

✅ **双模式用户界面**
- 知识图谱可视化模式
- AI助手对话模式
- 无缝切换和数据联动

## 系统架构

```
知识图谱可视化系统
├── 前端 (React + Vite)
│   ├── 知识图谱组件 (原有功能)
│   └── AI助手组件 (新增)
├── 后端 (Flask)
│   ├── 知识图谱API (原有)
│   ├── AI助手API (新增)
│   └── 医疗AI模块 (新增)
└── AI服务
    ├── Ollama (本地部署)
    └── OpenAI (可选)
```

## 快速部署

### 1. 后端部署

```bash
cd backend/knowledge_graph_backend

# 安装基础依赖
pip install -r requirements.txt

# 安装AI功能依赖
pip install -r requirements_ai.txt

# 启动后端服务
python src/main.py
```

### 2. 前端部署

```bash
cd frontend/knowledge-graph-frontend

# 安装依赖
npm install

# 启动前端服务
npm run dev
```

### 3. AI服务配置

#### 方案一：使用Ollama（推荐）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen3:4b
ollama pull nomic-embed-text

# 启动服务（默认端口11434）
ollama serve
```

#### 方案二：使用OpenAI

编辑 `backend/knowledge_graph_backend/src/config/ai_config.py`：

```python
class AIConfig:
    MODEL_TYPE = ModelType.OPENAI
    OPENAI_API_KEY = "your-openai-api-key"
    OPENAI_MODEL = "gpt-3.5-turbo"
```

## API接口文档

### AI助手接口

#### 1. 聊天接口
```http
POST /api/ai/chat
Content-Type: application/json

{
  "question": "什么是高血压？"
}
```

#### 2. 实体搜索接口
```http
GET /api/ai/search?q=高血压&limit=10
```

#### 3. 实体上下文接口
```http
GET /api/ai/entity/{entity_id}/context?depth=1
```

#### 4. 来源分页接口
```http
POST /api/ai/sources/page
Content-Type: application/json

{
  "action": "next"  // "prev", "current", "next"
}
```

#### 5. 聊天历史接口
```http
GET /api/ai/history?page=1&page_size=10
DELETE /api/ai/history
```

#### 6. AI状态检查
```http
GET /api/ai/status
```

## 使用说明

### 基本操作

1. **启动系统**：分别启动后端、前端和AI服务
2. **切换模式**：点击顶部"知识图谱"/"AI助手"标签切换
3. **AI对话**：在AI助手模式下输入医疗问题
4. **节点聚焦**：点击相关实体按钮可聚焦到图谱节点
5. **实体搜索**：使用搜索功能查找图谱中的实体

### AI助手功能

- **医疗问答**：回答疾病、症状、治疗相关问题
- **实体关联**：自动识别并关联知识图谱实体
- **智能搜索**：支持实体名称的精确和模糊搜索
- **聚焦模式**：一键跳转到相关图谱节点
- **分页浏览**：支持聊天历史和参考来源分页

### 医疗约束

AI助手具有以下医疗领域约束：
- 仅基于知识图谱数据回答问题
- 自动添加医疗免责声明
- 强调咨询专业医生的重要性
- 不提供具体诊断或治疗建议

## 配置说明

### AI配置文件

位置：`backend/knowledge_graph_backend/src/config/ai_config.py`

```python
class AIConfig:
    # 模型选择
    MODEL_TYPE = ModelType.OLLAMA  # OLLAMA 或 OPENAI
    
    # Ollama配置
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL_NAME = "qwen3:4b"
    
    # 分页配置
    CHAT_PAGE_SIZE = 10
    SOURCES_PAGE_SIZE = 3
    
    # 功能开关
    ENABLE_NODE_SEARCH = True
    ENABLE_FOCUS_MODE = True
```

### 医疗提示词

系统使用专门的医疗领域提示词，确保AI回答的专业性和安全性：

```python
MEDICAL_AI_PROMPT = """你是一个专业的医疗知识图谱AI助手...
知识图谱包含以下类型的医疗实体和关系：
- 疾病（Disease）
- 症状（Symptom）
- 药物（Drug）
- 治疗方法（Treatment）
...
"""
```

## 故障排除

### 常见问题

1. **AI服务连接失败**
   - 检查Ollama服务是否启动
   - 验证模型是否已下载
   - 确认端口配置正确

2. **前端标签页不显示**
   - 检查`tabs.jsx`组件是否存在
   - 验证导入路径是否正确

3. **实体搜索无结果**
   - 确认知识图谱数据已加载
   - 检查CSV文件格式是否正确

4. **AI回答质量差**
   - 调整提示词内容
   - 更换更强大的AI模型
   - 检查知识图谱数据质量

### 日志调试

后端服务会输出详细的调试信息：

```bash
# 启动时的日志
[信息] AI助手初始化成功，加载了 1000 个节点
[信息] Ollama服务可用: http://localhost:11434

# 运行时的日志
[信息] 处理问题: 什么是高血压？
[调试] 搜索到相关实体: ['高血压', '血压', '心血管疾病']
```

## 扩展开发

### 添加新的AI模型

1. 在`ai_config.py`中添加新的模型类型
2. 在`medical_ai.py`中实现对应的初始化和调用方法
3. 更新路由处理逻辑

### 自定义提示词

修改`AIConfig.MEDICAL_AI_PROMPT`可以调整AI的回答风格和专业领域。

### 添加新的API接口

在`ai_assistant.py`中添加新的路由函数，并注册到Flask应用中。

## 性能优化

1. **缓存机制**：可添加Redis缓存频繁查询的结果
2. **模型优化**：使用更小但高效的本地模型
3. **分页加载**：大型知识图谱的分页处理
4. **索引优化**：构建更高效的实体搜索索引

## 安全考虑

1. **输入验证**：对用户输入进行严格验证
2. **访问控制**：可添加用户认证和权限管理
3. **数据隐私**：本地部署保护医疗数据隐私
4. **免责声明**：确保医疗免责声明的显著展示

---

**注意**：此系统仅用于演示和研究目的，不能替代专业医疗建议。在生产环境中使用时，请确保遵循相关的医疗数据保护法规。 