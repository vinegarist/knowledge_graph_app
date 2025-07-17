"""
医疗知识图谱AI助手模块
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import re
import requests
from collections import defaultdict

from src.config.ai_config import AIConfig, ModelType

class MedicalKnowledgeGraphAI:
    """医疗知识图谱AI助手"""
    
    def __init__(self, knowledge_graph_data: Dict[str, Any] = None):
        """
        初始化医疗AI助手
        
        Args:
            knowledge_graph_data: 知识图谱数据，包含nodes和links
        """
        self.knowledge_graph_data = knowledge_graph_data or {"nodes": [], "links": []}
        self.chat_history = []
        self.current_sources = []
        self.current_page = 0
        self.sources_per_page = AIConfig.SOURCES_PAGE_SIZE
        
        # 构建实体索引用于快速查找
        self.entity_index = self._build_entity_index()
        
        # 初始化LLM
        self.llm = self._init_llm()
    
    def _init_llm(self):
        """初始化语言模型"""
        if AIConfig.MODEL_TYPE == ModelType.OLLAMA:
            return self._init_ollama()
        else:
            return self._init_openai()
    
    def _init_ollama(self):
        """初始化Ollama模型"""
        try:
            # 检查Ollama服务可用性
            response = requests.get(f"{AIConfig.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"[信息] Ollama服务可用: {AIConfig.OLLAMA_BASE_URL}")
                return {"type": "ollama", "available": True}
            else:
                print(f"[警告] Ollama服务不可用，状态码: {response.status_code}")
                return {"type": "ollama", "available": False}
        except Exception as e:
            print(f"[错误] 无法连接到Ollama服务: {str(e)}")
            return {"type": "ollama", "available": False}
    
    def _init_openai(self):
        """初始化OpenAI模型"""
        # 这里可以添加OpenAI的初始化逻辑
        return {"type": "openai", "available": True}
    
    def _build_entity_index(self) -> Dict[str, Any]:
        """构建实体索引用于快速搜索"""
        index = {
            "entities": {},  # 实体ID到实体信息的映射
            "relationships": defaultdict(list),  # 实体间关系
            "search_index": {}  # 搜索索引（实体名称到ID的映射）
        }
        
        # 构建节点索引
        for node in self.knowledge_graph_data.get("nodes", []):
            entity_id = node.get("id")
            entity_label = node.get("label", "")
            
            index["entities"][entity_id] = {
                "id": entity_id,
                "label": entity_label,
                "type": node.get("type", "entity"),
                "connections": node.get("connections", 0)
            }
            
            # 构建搜索索引
            if entity_label:
                # 支持模糊搜索
                label_lower = entity_label.lower()
                index["search_index"][label_lower] = entity_id
                
                # 添加部分匹配
                words = label_lower.split()
                for word in words:
                    if len(word) > 1:  # 避免单字符索引
                        if word not in index["search_index"]:
                            index["search_index"][word] = []
                        if isinstance(index["search_index"][word], list):
                            index["search_index"][word].append(entity_id)
                        else:
                            index["search_index"][word] = [index["search_index"][word], entity_id]
        
        # 构建关系索引
        for link in self.knowledge_graph_data.get("links", []):
            source = link.get("source")
            target = link.get("target")
            relation = link.get("label", "相关")
            
            if source and target:
                index["relationships"][source].append({
                    "target": target,
                    "relation": relation,
                    "direction": "outgoing"
                })
                index["relationships"][target].append({
                    "target": source,
                    "relation": relation,
                    "direction": "incoming"
                })
        
        return index
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索实体"""
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        results = []
        
        # 精确匹配
        if query_lower in self.entity_index["search_index"]:
            entity_id = self.entity_index["search_index"][query_lower]
            if isinstance(entity_id, str):
                entity_info = self.entity_index["entities"].get(entity_id)
                if entity_info:
                    results.append({**entity_info, "match_type": "exact"})
        
        # 部分匹配
        for key, entity_ids in self.entity_index["search_index"].items():
            if query_lower in key and len(results) < limit:
                if isinstance(entity_ids, list):
                    for entity_id in entity_ids:
                        entity_info = self.entity_index["entities"].get(entity_id)
                        if entity_info and entity_info not in results:
                            results.append({**entity_info, "match_type": "partial"})
                            if len(results) >= limit:
                                break
                elif isinstance(entity_ids, str):
                    entity_info = self.entity_index["entities"].get(entity_ids)
                    if entity_info and entity_info not in results:
                        results.append({**entity_info, "match_type": "partial"})
        
        return results[:limit]
    
    def get_entity_context(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """获取实体的上下文信息"""
        entity = self.entity_index["entities"].get(entity_id)
        if not entity:
            return {}
        
        context = {
            "entity": entity,
            "relationships": [],
            "neighbors": []
        }
        
        # 获取直接关系
        relationships = self.entity_index["relationships"].get(entity_id, [])
        for rel in relationships:
            neighbor_id = rel["target"]
            neighbor = self.entity_index["entities"].get(neighbor_id)
            if neighbor:
                context["relationships"].append({
                    "relation": rel["relation"],
                    "direction": rel["direction"],
                    "neighbor": neighbor
                })
                context["neighbors"].append(neighbor)
        
        return context
    
    def _call_ollama(self, prompt: str, context: str = "") -> str:
        """调用Ollama模型"""
        if not self.llm.get("available", False):
            return "AI服务暂时不可用，请稍后再试。"
        
        try:
            # 构建完整的提示词
            full_prompt = f"{AIConfig.MEDICAL_AI_PROMPT}\n\n"
            if context:
                full_prompt += f"知识图谱上下文：\n{context}\n\n"
            full_prompt += f"用户问题：{prompt}\n\n请基于上述信息回答用户问题。"
            
            # 调用Ollama API
            response = requests.post(
                f"{AIConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": AIConfig.OLLAMA_MODEL_NAME,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "抱歉，AI暂时无法回答您的问题。")
            else:
                return f"AI服务错误（状态码：{response.status_code}）"
                
        except Exception as e:
            print(f"[错误] 调用Ollama失败: {str(e)}")
            return "抱歉，AI服务出现错误，请稍后再试。"
    
    def ask(self, question: str) -> Dict[str, Any]:
        """处理用户问题并返回回答"""
        if not question.strip():
            return {
                "answer": "请输入您的医疗问题。",
                "related_entities": [],
                "suggested_focus": None,
                "sources": [],
                "medical_disclaimer": True
            }
        
        # 搜索相关实体
        related_entities = self.search_entities(question, limit=5)
        
        # 构建上下文信息
        context_info = []
        for entity in related_entities:
            entity_context = self.get_entity_context(entity["id"])
            context_info.append(f"实体：{entity['label']} (ID: {entity['id']})")
            
            # 添加关系信息
            for rel in entity_context.get("relationships", [])[:3]:  # 限制关系数量
                context_info.append(f"  - {rel['relation']}: {rel['neighbor']['label']}")
        
        context_text = "\n".join(context_info) if context_info else "未找到直接相关的实体"
        
        # 调用AI模型
        if AIConfig.MODEL_TYPE == ModelType.OLLAMA:
            answer = self._call_ollama(question, context_text)
        else:
            answer = "OpenAI模型暂未实现"
        
        # 从答案中提取可能的实体引用
        referenced_entities = self._extract_entity_references(answer, related_entities)
        
        # 建议聚焦的节点（选择最相关的实体）
        suggested_focus = related_entities[0]["id"] if related_entities else None
        
        # 添加医疗免责声明
        if not any(word in answer.lower() for word in ["免责", "咨询医生", "专业医生"]):
            answer += "\n\n⚠️ 医疗免责声明：以上信息仅供参考，不能替代专业医疗建议。如有健康问题，请及时咨询专业医生。"
        
        # 保存到聊天历史
        self.chat_history.append({
            "question": question,
            "answer": answer,
            "related_entities": related_entities,
            "timestamp": self._get_timestamp()
        })
        
        # 更新当前来源
        self.current_sources = related_entities
        self.current_page = 0
        
        return {
            "answer": answer,
            "related_entities": related_entities,
            "suggested_focus": suggested_focus,
            "sources": self._get_paginated_sources(),
            "medical_disclaimer": True,
            "context_used": context_text
        }
    
    def _extract_entity_references(self, text: str, entities: List[Dict]) -> List[str]:
        """从文本中提取实体引用"""
        referenced = []
        for entity in entities:
            if entity["label"].lower() in text.lower():
                referenced.append(entity["id"])
        return referenced
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_paginated_sources(self) -> Dict[str, Any]:
        """获取分页的来源信息"""
        start_idx = self.current_page * self.sources_per_page
        end_idx = start_idx + self.sources_per_page
        
        page_sources = self.current_sources[start_idx:end_idx]
        total_pages = (len(self.current_sources) + self.sources_per_page - 1) // self.sources_per_page
        
        return {
            "sources": page_sources,
            "current_page": self.current_page + 1,
            "total_pages": total_pages,
            "total_sources": len(self.current_sources),
            "has_next": end_idx < len(self.current_sources),
            "has_prev": self.current_page > 0
        }
    
    def next_page(self) -> Dict[str, Any]:
        """翻到下一页来源"""
        if (self.current_page + 1) * self.sources_per_page < len(self.current_sources):
            self.current_page += 1
        return self._get_paginated_sources()
    
    def prev_page(self) -> Dict[str, Any]:
        """翻到上一页来源"""
        if self.current_page > 0:
            self.current_page -= 1
        return self._get_paginated_sources()
    
    def get_chat_history(self, page: int = 1, page_size: int = None) -> Dict[str, Any]:
        """获取分页的聊天历史"""
        if page_size is None:
            page_size = AIConfig.CHAT_PAGE_SIZE
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_history = self.chat_history[start_idx:end_idx]
        total_pages = (len(self.chat_history) + page_size - 1) // page_size
        
        return {
            "history": page_history,
            "current_page": page,
            "total_pages": total_pages,
            "total_chats": len(self.chat_history),
            "has_next": end_idx < len(self.chat_history),
            "has_prev": page > 1
        }
    
    def clear_history(self):
        """清空聊天历史"""
        self.chat_history = []
        self.current_sources = []
        self.current_page = 0
    
    def update_knowledge_graph(self, graph_data: Dict[str, Any]):
        """更新知识图谱数据"""
        self.knowledge_graph_data = graph_data
        self.entity_index = self._build_entity_index()
        print(f"[信息] 知识图谱已更新，包含 {len(graph_data.get('nodes', []))} 个节点") 