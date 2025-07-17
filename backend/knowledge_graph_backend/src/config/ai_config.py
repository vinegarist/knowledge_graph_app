"""
AI配置模块 - 医疗知识图谱AI系统配置
"""
import os
from enum import Enum

# 枚举类型定义
class ModelType(Enum):
    OLLAMA = "ollama"          # Ollama 本地模型
    OPENAI = "openai"          # OpenAI API

class AIConfig:
    # 模型配置
    MODEL_TYPE = ModelType.OLLAMA  # 默认使用Ollama
    
    # OpenAI 配置
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Ollama 配置
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL_NAME = "qwen3:4b"
    
    # AI助手配置
    MEDICAL_AI_PROMPT = """你是一个专业的医疗知识图谱AI助手。你的任务是基于医疗知识图谱数据回答用户问题。

知识图谱包含以下类型的医疗实体和关系：
- 疾病（Disease）
- 症状（Symptom）
- 药物（Drug）
- 治疗方法（Treatment）
- 检查项目（Examination）
- 身体部位（BodyPart）

你需要：
1. 理解用户的医疗相关问题
2. 基于知识图谱数据提供准确的医疗信息
3. 当涉及具体实体时，提供相关的图谱节点ID以便用户查看
4. 始终强调这只是参考信息，具体诊断和治疗请咨询专业医生

回答格式要求：
- 提供清晰的医疗解释
- 包含相关实体的节点ID（如果有）
- 添加适当的医疗免责声明
"""
    
    # 分页配置
    CHAT_PAGE_SIZE = 10  # 每页聊天记录数
    SOURCES_PAGE_SIZE = 3  # 每页来源数
    
    # 响应结构配置
    ENABLE_NODE_SEARCH = True  # 启用节点搜索功能
    ENABLE_FOCUS_MODE = True   # 启用聚焦模式 