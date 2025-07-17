"""
医疗知识图谱AI助手模块
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import re
import requests
from collections import defaultdict

from src.config.ai_config import AIConfig, ModelType
from src.utils.graph_cache import graph_cache

class MedicalKnowledgeGraphAI:
    """医疗知识图谱AI助手"""
    
    def __init__(self, knowledge_graph_data: Optional[Dict[str, Any]] = None):
        """
        初始化医疗AI助手
        
        Args:
            knowledge_graph_data: 知识图谱数据，包含nodes和links
        """
        if knowledge_graph_data:
            self.knowledge_graph_data = knowledge_graph_data
        else:
            self.knowledge_graph_data = {"nodes": [], "links": []}
            
        self.chat_history = []
        self.current_sources = []
        self.current_page = 0
        self.sources_per_page = AIConfig.SOURCES_PAGE_SIZE
        
        # 使用优化的缓存系统
        self._use_cache = True
        
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
            # 检查Ollama服务可用性（禁用代理）
            response = requests.get(
                f"{AIConfig.OLLAMA_BASE_URL}/api/tags", 
                timeout=5,
                proxies={'http': '', 'https': ''}
            )
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
        """
        构建实体索引用于快速搜索
        注意：此方法已废弃，现在使用graph_cache中的优化索引系统
        """
        print("[警告] _build_entity_index方法已废弃，请使用graph_cache优化索引系统")
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
        """
        快速搜索实体 - 使用优化的索引算法
        时间复杂度从 O(E×Q×W) 降低到 O(log N)
        """
        if not query.strip():
            return []
        
        # 优先使用缓存的快速搜索
        if self._use_cache and graph_cache.get_cached_graph():
            return graph_cache.search_entities_fast(query, limit)
        
        # 备用：原始搜索算法
        return self._search_entities_fallback(query, limit)
    
    def _search_entities_fallback(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """备用搜索算法 - 当缓存不可用时使用"""
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        scored_results = []
        
        # 简化的医疗术语映射
        medical_terms = {
            '感冒': ['感冒', '普通感冒', '上呼吸道感染'],
            '发烧': ['发热', '发烧', '体温升高'],
            '咳嗽': ['咳嗽', '咳痰', '干咳'],
            '头痛': ['头痛', '头疼', '偏头痛']
        }
        
        # 扩展查询词
        expanded_queries = [query_lower]
        for term, synonyms in medical_terms.items():
            if term in query_lower:
                expanded_queries.extend(synonyms)
        
        # 快速匹配评分
        for node in self.knowledge_graph_data.get("nodes", []):
            entity_label = node.get("label", "").lower()
            score = 0
            match_type = "none"
            
            # 精确匹配
            if query_lower == entity_label:
                score = 100
                match_type = "exact"
            # 包含匹配
            elif query_lower in entity_label or entity_label in query_lower:
                score = 80
                match_type = "contains"
            # 词语匹配
            else:
                query_words = set(query_lower.split())
                entity_words = set(entity_label.split())
                intersection = query_words & entity_words
                if intersection:
                    score = 60 * len(intersection) / len(query_words)
                    match_type = "partial"
            
            if score > 0:
                result_entity = {
                    **node,
                    "match_type": match_type,
                    "match_score": score
                }
                scored_results.append(result_entity)
        
        # 排序并返回
        scored_results.sort(key=lambda x: (x["match_score"], x.get("connections", 0)), reverse=True)
        return scored_results[:limit]
    
    def get_entity_context(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """获取实体的上下文信息"""
        # 优先使用缓存的实体信息
        if self._use_cache and graph_cache.get_cached_graph():
            cached_graph = graph_cache.get_cached_graph()
            if not cached_graph:
                return {}
                
            entity = None
            
            # 查找实体
            for node in cached_graph.get('nodes', []):
                if node.get('id') == entity_id:
                    entity = node
                    break
            
            if not entity:
                return {}
            
            context = {
                "entity": entity,
                "relationships": [],
                "neighbors": []
            }
            
            # 获取关系
            for edge in cached_graph.get('edges', []):
                if edge['source'] == entity_id:
                    # 查找目标节点
                    for node in cached_graph.get('nodes', []):
                        if node.get('id') == edge['target']:
                            context["relationships"].append({
                                "relation": edge['relation'],
                                "direction": "outgoing",
                                "neighbor": node
                            })
                            context["neighbors"].append(node)
                            break
                elif edge['target'] == entity_id:
                    # 查找源节点
                    for node in cached_graph.get('nodes', []):
                        if node.get('id') == edge['source']:
                            context["relationships"].append({
                                "relation": edge['relation'],
                                "direction": "incoming",
                                "neighbor": node
                            })
                            context["neighbors"].append(node)
                            break
            
            return context
        
        # 备用：直接从知识图谱数据查找
        entity = None
        for node in self.knowledge_graph_data.get('nodes', []):
            if node.get('id') == entity_id:
                entity = node
                break
        
        if not entity:
            return {}
        
        context = {
            "entity": entity,
            "relationships": [],
            "neighbors": []
        }
        
        # 获取关系（简化版本）
        for edge in self.knowledge_graph_data.get('edges', []):
            if edge['source'] == entity_id or edge['target'] == entity_id:
                neighbor_id = edge['target'] if edge['source'] == entity_id else edge['source']
                direction = "outgoing" if edge['source'] == entity_id else "incoming"
                
                # 查找邻居节点
                for node in self.knowledge_graph_data.get('nodes', []):
                    if node.get('id') == neighbor_id:
                        context["relationships"].append({
                            "relation": edge['relation'],
                            "direction": direction,
                            "neighbor": node
                        })
                        context["neighbors"].append(node)
                        break
        
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
            
            # 调用Ollama API（禁用代理）
            response = requests.post(
                f"{AIConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": AIConfig.OLLAMA_MODEL_NAME,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30,
                proxies={'http': '', 'https': ''}  # 禁用代理
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
        related_entities = self.search_entities(question, limit=8)
        
        # 构建详细的上下文信息
        context_info = []
        if related_entities:
            context_info.append("=== 知识图谱上下文 ===")
            for entity in related_entities:
                entity_context = self.get_entity_context(entity["id"])
                context_info.append(f"\n实体: {entity['label']}")
                context_info.append(f"ID: {entity['id']}")
                context_info.append(f"类型: {entity.get('type', '未知')}")
                context_info.append(f"连接数: {entity.get('connections', 0)}")
                
                # 添加关系信息
                relationships = entity_context.get("relationships", [])
                if relationships:
                    context_info.append("关系:")
                    for rel in relationships[:5]:  # 限制关系数量
                        direction_symbol = "→" if rel['direction'] == 'outgoing' else "←"
                        context_info.append(f"  {direction_symbol} {rel['relation']}: {rel['neighbor']['label']} (ID: {rel['neighbor']['id']})")
                else:
                    context_info.append("关系: 无直接关系")
                    
            context_info.append("\n=== 上下文结束 ===")
        
        context_text = "\n".join(context_info) if context_info else "未找到相关实体"
        
        # 调用AI模型
        if AIConfig.MODEL_TYPE == ModelType.OLLAMA:
            answer = self._call_ollama_strict(question, context_text, related_entities)
        else:
            answer = "OpenAI模型暂未实现"
        
        # 如果没有找到相关实体，提供标准回答
        if not related_entities:
            answer = self._generate_no_knowledge_response(question)
        
        # 验证AI回答中的实体引用
        validated_answer = self._validate_entity_references(answer, related_entities)
        
        # 建议聚焦的节点（选择最相关的实体）
        suggested_focus = related_entities[0]["id"] if related_entities else None
        
        # 保存到聊天历史
        self.chat_history.append({
            "question": question,
            "answer": validated_answer,
            "related_entities": related_entities,
            "context_used": context_text,
            "timestamp": self._get_timestamp()
        })
        
        # 更新当前来源
        self.current_sources = related_entities
        self.current_page = 0
        
        return {
            "answer": validated_answer,
            "related_entities": related_entities,
            "suggested_focus": suggested_focus,
            "sources": self._get_paginated_sources(),
            "medical_disclaimer": True,
            "context_used": context_text,
            "knowledge_graph_coverage": len(related_entities) > 0
        }

    def _call_ollama_strict(self, prompt: str, context: str = "", entities: Optional[List[Dict]] = None) -> str:
        """严格调用Ollama模型，强化知识图谱约束"""
        if not self.llm.get("available", False):
            return "AI服务暂时不可用，请稍后再试。"
        
        try:
            # 构建严格的提示词
            full_prompt = f"{AIConfig.MEDICAL_AI_PROMPT}\n\n"
            
            if context and entities:
                full_prompt += f"{context}\n\n"
                full_prompt += "【可引用的实体ID列表】：\n"
                for entity in entities:
                    full_prompt += f"- {entity['label']} (ID: {entity['id']})\n"
                full_prompt += "\n"
            else:
                full_prompt += "知识图谱上下文：无相关实体\n\n"
            
            full_prompt += f"用户问题：{prompt}\n\n"
            full_prompt += "请严格按照上述约束回答，只能使用上述上下文中的信息和实体ID。如果没有相关信息，明确说明知识图谱中未找到相关信息。"
            
            # 调用Ollama API（禁用代理）
            response = requests.post(
                f"{AIConfig.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": AIConfig.OLLAMA_MODEL_NAME,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # 降低温度，减少创造性
                        "top_p": 0.8,
                        "top_k": 10
                    }
                },
                timeout=30,
                proxies={'http': '', 'https': ''}  # 禁用代理
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "抱歉，AI暂时无法回答您的问题。")
            else:
                return f"AI服务错误（状态码：{response.status_code}）"
                
        except Exception as e:
            print(f"[错误] 调用Ollama失败: {str(e)}")
            return "抱歉，AI服务出现错误，请稍后再试。"

    def _validate_entity_references(self, answer: str, valid_entities: List[Dict]) -> str:
        """验证AI回答中的实体引用，移除无效的实体ID"""
        if not valid_entities:
            return answer
        
        # 提取有效的实体ID
        valid_ids = set(entity['id'] for entity in valid_entities)
        valid_labels = set(entity['label'] for entity in valid_entities)
        
        # 检查回答中是否包含无效的实体ID模式
        import re
        
        # 查找可能的实体ID模式（如 D123, F456, B001 等）
        id_pattern = r'\b[A-Z]\d+\b'
        found_ids = re.findall(id_pattern, answer)
        
        # 移除无效的实体ID
        validated_answer = answer
        for found_id in found_ids:
            if found_id not in valid_ids:
                # 移除无效的实体ID引用
                validated_answer = re.sub(rf'\([^)]*{re.escape(found_id)}[^)]*\)', '', validated_answer)
                validated_answer = re.sub(rf'\b{re.escape(found_id)}\b', '', validated_answer)
        
        # 如果回答中没有引用任何有效实体且原本有相关实体，添加提示
        has_valid_reference = any(entity['label'] in answer or entity['id'] in answer for entity in valid_entities)
        if valid_entities and not has_valid_reference and '知识图谱中未找到' not in answer:
            validated_answer += f"\n\n💡 相关实体：基于您的问题，在知识图谱中找到了相关实体：{', '.join([e['label'] for e in valid_entities[:3]])}，您可以点击查看详情。"
        
        return validated_answer
    
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
    
    def get_chat_history(self, page: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
        """获取分页的聊天历史"""
        # 确保page_size是int类型
        actual_page_size: int = page_size if page_size is not None else AIConfig.CHAT_PAGE_SIZE
        
        start_idx = (page - 1) * actual_page_size
        end_idx = start_idx + actual_page_size
        
        page_history = self.chat_history[start_idx:end_idx]
        total_pages = (len(self.chat_history) + actual_page_size - 1) // actual_page_size
        
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
        # 不再使用entity_index，改用缓存系统
        print(f"[信息] 知识图谱已更新，包含 {len(graph_data.get('nodes', []))} 个节点") 

    def update_knowledge_graph_from_file(self, csv_file_path: str, force_reload: bool = False):
        """从CSV文件更新知识图谱，使用缓存优化"""
        try:
            # 使用优化的缓存加载
            graph_data = graph_cache.load_graph(csv_file_path, force_reload)
            self.knowledge_graph_data = graph_data
            print(f"[信息] 知识图谱已更新，包含 {len(graph_data.get('nodes', []))} 个节点")
        except Exception as e:
            print(f"[错误] 更新知识图谱失败: {str(e)}")
            self.knowledge_graph_data = {"nodes": [], "links": []}

    def _generate_no_knowledge_response(self, question: str) -> str:
        """生成知识图谱中没有相关信息时的标准回答"""
        return f"""很抱歉，在当前医疗知识图谱中未找到关于"{question}"的相关信息。

当前知识图谱主要包含以下类型的医疗信息：
- 疾病相关信息
- 症状描述
- 治疗方法
- 药物信息
- 检查项目
- 身体部位

建议您：
1. 尝试使用更具体的医疗术语重新提问
2. 咨询专业医生获取准确的医疗建议

⚠️ 医疗免责声明：本系统仅提供基于知识图谱的信息参考，不能替代专业医疗诊断和治疗建议。如有健康问题，请及时就医。""" 