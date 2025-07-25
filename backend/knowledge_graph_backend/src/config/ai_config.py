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
    OLLAMA_BASE_URL = "http://100.127.128.47:11434"
    OLLAMA_MODEL = "qwen3:4b"
    OLLAMA_MODEL_NAME = "qwen3:4b"  # 保持向后兼容
    
    # AI助手配置
    MEDICAL_AI_PROMPT = """你是一个严格基于医疗知识图谱的AI助手。

【重要约束】：
1. 你ONLY能基于下面提供的"知识图谱上下文"来回答问题
2. 如果知识图谱上下文中没有相关信息，你必须明确说明"知识图谱中未找到相关信息"
3. 绝对禁止使用你的训练数据或常识来回答医疗问题
4. 绝对禁止编造或虚构任何实体ID、节点名称或医疗信息
5. 只能引用知识图谱上下文中实际存在的实体和关系

【回答格式】：
1. 如果有相关信息：基于知识图谱上下文准确回答，并明确标注引用的实体ID
2. 如果没有相关信息：回答"很抱歉，在当前知识图谱中未找到关于[用户问题主题]的相关信息。建议咨询专业医生获取准确的医疗建议。"
3. 始终在回答末尾添加医疗免责声明

【严格禁止】：
- 使用任何未在知识图谱上下文中出现的实体名称或ID
- 基于常识或训练数据提供医疗建议
- 编造任何医疗信息、药物名称、治疗方案等

你的回答必须完全可追溯到提供的知识图谱上下文。
"""
    
    # 分页配置
    CHAT_PAGE_SIZE = 10  # 每页聊天记录数
    SOURCES_PAGE_SIZE = 3  # 每页来源数
    
    # 响应结构配置
    ENABLE_NODE_SEARCH = True  # 启用节点搜索功能
    ENABLE_FOCUS_MODE = True   # 启用聚焦模式 