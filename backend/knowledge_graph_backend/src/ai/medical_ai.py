"""
医疗知识图谱AI助手模块
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import re
import requests
from collections import defaultdict
import time # Added for timing in _search_by_relation
import asyncio
import concurrent.futures

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
        
        print(f"[调试] 搜索查询: {query}, 限制: {limit}") # 调试信息
        
        # 优先使用缓存的快速搜索
        if self._use_cache and graph_cache.get_cached_graph():
            results = graph_cache.search_entities_fast(query, limit)
            print(f"[调试] 缓存搜索结果数量: {len(results)}") # 调试信息
            return results
        
        # 备用：原始搜索算法
        results = self._search_entities_fallback(query, limit)
        print(f"[调试] 备用搜索结果数量: {len(results)}") # 调试信息
        return results
    
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
                "sources": self._get_paginated_sources(),
                "medical_disclaimer": True
            }
        
        # 解析查询意图
        query_intent = self._parse_query_intent(question)
        print(f"[调试] 查询意图: {query_intent}")
        
        # 使用并发搜索提升性能
        related_entities = self._search_concurrent(query_intent, limit=8)
        
        # 如果没有找到相关实体，直接返回标准回答
        if not related_entities:
            answer = self._generate_no_knowledge_response(question)
            # 清空当前来源
            self.current_sources = []
            self.current_page = 0
            
            return {
                "answer": answer,
                "related_entities": [],
                "suggested_focus": None,
                "sources": self._get_paginated_sources(),
                "medical_disclaimer": True,
                "context_used": "未找到相关实体",
                "knowledge_graph_coverage": False
            }
        
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
        
        # 调试信息
        print(f"[调试] 相关实体数量: {len(related_entities)}")
        print(f"[调试] 当前来源数量: {len(self.current_sources)}")
        print(f"[调试] 分页来源: {self._get_paginated_sources()}")
        
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
                full_prompt += "⚠️ 重要约束：\n"
                full_prompt += "1. 只能使用上述知识图谱中的实体和信息\n"
                full_prompt += "2. 严禁编造或推测任何不在知识图谱中的实体\n"
                full_prompt += "3. 如果知识图谱中没有相关信息，明确说明'知识图谱中未找到相关信息'\n"
                full_prompt += "4. 回答中提到的每个实体都必须在上述列表中\n"
                full_prompt += "5. 不要使用任何训练数据或常识知识\n\n"
            else:
                full_prompt += "知识图谱上下文：无相关实体\n\n"
                full_prompt += "⚠️ 重要约束：\n"
                full_prompt += "1. 知识图谱中未找到相关实体\n"
                full_prompt += "2. 严禁编造或推测任何实体\n"
                full_prompt += "3. 明确告知用户知识图谱中没有相关信息\n\n"
            
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
                answer = result.get("response", "抱歉，AI暂时无法回答您的问题。")
                
                # 额外验证：检查回答中是否包含未授权的实体
                if entities:
                    valid_labels = set(entity['label'] for entity in entities)
                    valid_ids = set(entity['id'] for entity in entities)
                    
                    # 简单的实体检测（可以进一步优化）
                    import re
                    # 检测可能的实体ID模式
                    id_pattern = r'\b[A-Z]\d+\b'
                    found_ids = re.findall(id_pattern, answer)
                    
                    # 检查是否有未授权的实体ID
                    unauthorized_ids = [found_id for found_id in found_ids if found_id not in valid_ids]
                    if unauthorized_ids:
                        answer = f"⚠️ 检测到未授权的实体引用，已移除。\n\n{answer}"
                
                return answer
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

    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """解析查询意图，提取疾病、关系和目标"""
        query_lower = query.lower().strip()
        
        # 定义查询模式
        patterns = {
            # 饮食相关
            'diet': {
                'keywords': ['吃什么', '饮食', '食物', '菜', '汤', '粥', '水果', '蔬菜', '营养'],
                'relation': '推荐食谱',
                'target_type': 'food'
            },
            # 药物相关
            'medicine': {
                'keywords': ['吃什么药', '药物', '药品', '药', '治疗', '用药', '处方'],
                'relation': '常用药品',
                'target_type': 'medicine'
            },
            # 症状相关
            'symptoms': {
                'keywords': ['症状', '表现', '征兆', '感觉', '不适'],
                'relation': '症状',
                'target_type': 'symptom'
            },
            # 检查相关
            'examination': {
                'keywords': ['检查', '化验', '检测', '诊断', '筛查'],
                'relation': '检查项目',
                'target_type': 'examination'
            },
            # 预防相关
            'prevention': {
                'keywords': ['预防', '避免', '防止', '预防措施'],
                'relation': '预防措施',
                'target_type': 'prevention'
            },
            # 并发症相关
            'complications': {
                'keywords': ['并发症', '后果', '影响', '恶化'],
                'relation': '并发症',
                'target_type': 'complication'
            },
            # 症状诊断相关
            'diagnosis': {
                'keywords': ['可能是什么病', '什么病', '诊断', '什么原因', '怎么回事'],
                'relation': '症状',
                'target_type': 'diagnosis'
            }
        }
        
        # 检测查询意图
        detected_intent = None
        for intent, pattern in patterns.items():
            if any(keyword in query_lower for keyword in pattern['keywords']):
                detected_intent = intent
                break
        
        # 提取疾病名称
        disease_keywords = ['感冒', '发烧', '咳嗽', '头痛', '高血压', '糖尿病', '心脏病', '肺炎', '胃炎', '肝炎']
        detected_disease = None
        for disease in disease_keywords:
            if disease in query_lower:
                detected_disease = disease
                break
        
        # 检查是否是症状诊断查询
        is_symptom_diagnosis = self._is_symptom_diagnosis_query(query_lower)
        
        return {
            'original_query': query,
            'intent': detected_intent,
            'disease': detected_disease,
            'relation': patterns[detected_intent]['relation'] if detected_intent else None,
            'target_type': patterns[detected_intent]['target_type'] if detected_intent else None,
            'is_structured_query': detected_intent is not None and detected_disease is not None,
            'is_symptom_diagnosis': is_symptom_diagnosis,
            'symptoms': self._extract_symptoms(query_lower) if is_symptom_diagnosis else []
        }
    
    def _is_symptom_diagnosis_query(self, query_lower: str) -> bool:
        """判断是否是症状诊断查询"""
        # 诊断相关关键词
        diagnosis_keywords = [
            '可能是什么病', '什么病', '诊断', '什么原因', '怎么回事',
            '我有点', '我有', '我出现', '我得了', '我患了',
            '症状', '表现', '征兆', '感觉', '不适'
        ]
        
        # 症状关键词
        symptom_keywords = [
            '感冒', '发烧', '发热', '咳嗽', '头痛', '头疼', '流鼻涕', '鼻塞',
            '喉咙痛', '咽痛', '嗓子疼', '打喷嚏', '乏力', '疲劳', '食欲不振',
            '恶心', '呕吐', '腹泻', '腹痛', '腹胀', '便秘', '失眠', '多梦',
            '心悸', '胸闷', '气短', '呼吸困难', '胸痛', '背痛', '关节痛',
            '肌肉酸痛', '皮疹', '瘙痒', '红肿', '水肿', '头晕', '眩晕',
            '耳鸣', '视力模糊', '眼痛', '眼红', '流泪', '口干', '口苦',
            '口臭', '牙龈出血', '牙痛', '口腔溃疡', '声音嘶哑', '失声'
        ]
        
        # 检查是否包含诊断关键词和症状关键词
        has_diagnosis_keyword = any(keyword in query_lower for keyword in diagnosis_keywords)
        has_symptom_keyword = any(keyword in query_lower for keyword in symptom_keywords)
        
        return has_diagnosis_keyword and has_symptom_keyword
    
    def _extract_symptoms(self, query_lower: str) -> List[str]:
        """提取症状关键词"""
        # 症状映射表
        symptom_mapping = {
            '感冒': ['感冒', '上呼吸道感染'],
            '发烧': ['发烧', '发热', '体温升高'],
            '咳嗽': ['咳嗽', '咳痰', '干咳'],
            '头痛': ['头痛', '头疼', '偏头痛'],
            '流鼻涕': ['流鼻涕', '鼻涕', '鼻塞'],
            '喉咙痛': ['喉咙痛', '咽痛', '嗓子疼'],
            '打喷嚏': ['打喷嚏', '喷嚏'],
            '乏力': ['乏力', '疲劳', '无力'],
            '食欲不振': ['食欲不振', '不想吃饭', '没胃口'],
            '恶心': ['恶心', '想吐'],
            '呕吐': ['呕吐', '吐'],
            '腹泻': ['腹泻', '拉肚子'],
            '腹痛': ['腹痛', '肚子疼'],
            '腹胀': ['腹胀', '肚子胀'],
            '便秘': ['便秘', '大便干燥'],
            '失眠': ['失眠', '睡不着'],
            '心悸': ['心悸', '心跳快'],
            '胸闷': ['胸闷', '胸口闷'],
            '气短': ['气短', '呼吸困难'],
            '胸痛': ['胸痛', '胸口疼'],
            '背痛': ['背痛', '后背疼'],
            '关节痛': ['关节痛', '关节疼'],
            '肌肉酸痛': ['肌肉酸痛', '肌肉疼'],
            '皮疹': ['皮疹', '红疹'],
            '瘙痒': ['瘙痒', '痒'],
            '红肿': ['红肿', '红'],
            '水肿': ['水肿', '肿'],
            '头晕': ['头晕', '晕'],
            '眩晕': ['眩晕', '天旋地转'],
            '耳鸣': ['耳鸣', '耳朵响'],
            '视力模糊': ['视力模糊', '看不清'],
            '眼痛': ['眼痛', '眼睛疼'],
            '眼红': ['眼红', '眼睛红'],
            '流泪': ['流泪', '眼泪'],
            '口干': ['口干', '嘴巴干'],
            '口苦': ['口苦', '嘴巴苦'],
            '口臭': ['口臭', '口气'],
            '牙龈出血': ['牙龈出血', '牙龈'],
            '牙痛': ['牙痛', '牙齿疼'],
            '口腔溃疡': ['口腔溃疡', '溃疡'],
            '声音嘶哑': ['声音嘶哑', '嘶哑'],
            '失声': ['失声', '说不出话']
        }
        
        extracted_symptoms = []
        for symptom, keywords in symptom_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                extracted_symptoms.append(symptom)
        
        return extracted_symptoms
    
    def _search_by_relation(self, disease: str, relation: str, limit: int = 10) -> List[Dict[str, Any]]:
        """根据疾病和关系搜索相关实体"""
        if not disease or not relation:
            return []
        
        print(f"[调试] 关系搜索: 疾病={disease}, 关系={relation}")
        start_time = time.time()
        
        # 优先使用缓存的快速关系搜索
        if self._use_cache and graph_cache.get_cached_graph():
            results = graph_cache.search_by_relation_fast(disease, relation, limit)
            end_time = time.time()
            print(f"[调试] 快速关系搜索完成, 耗时 {end_time - start_time:.3f}s")
            return results
        
        # 备用：原始搜索算法
        results = []
        
        # 查找疾病实体
        disease_entities = []
        for node in self.knowledge_graph_data.get("nodes", []):
            if disease in node.get("label", ""):
                disease_entities.append(node)
        
        print(f"[调试] 找到疾病实体数量: {len(disease_entities)}")
        
        for disease_entity in disease_entities:
            # 查找相关关系
            for edge in self.knowledge_graph_data.get("edges", []):
                if edge.get('source') == disease_entity['id']:
                    edge_relation = edge.get('relation', '')
                    # 灵活的关系匹配
                    if (relation in edge_relation or 
                        edge_relation in relation or
                        any(keyword in edge_relation for keyword in relation.split())):
                        
                        # 找到目标实体
                        target_id = edge.get('target')
                        for node in self.knowledge_graph_data.get("nodes", []):
                            if node.get('id') == target_id:
                                result = {
                                    **node,
                                    "match_type": "relation",
                                    "match_score": 90,
                                    "relation": edge_relation,
                                    "source_disease": disease_entity['label'],
                                    "edge_id": edge.get('id'),
                                    "search_method": "fallback_search"
                                }
                                results.append(result)
                                break
        
        end_time = time.time()
        print(f"[调试] 关系搜索结果数量: {len(results)}, 耗时 {end_time - start_time:.3f}s")
        return results[:limit] 

    def _search_by_symptoms(self, symptoms: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """根据症状搜索可能的疾病"""
        if not symptoms:
            return []
        
        print(f"[调试] 症状诊断搜索: 症状={symptoms}")
        start_time = time.time()
        
        results = []
        seen_ids = set()
        
        # 优先使用缓存
        if self._use_cache and graph_cache.get_cached_graph():
            cached_graph = graph_cache.get_cached_graph()
            
            # 通过症状关键词搜索相关疾病
            for symptom in symptoms:
                # 搜索包含症状关键词的实体
                for node in cached_graph.get('nodes', []):
                    node_label = node.get('label', '').lower()
                    
                    # 检查是否是疾病实体且包含症状信息
                    if (symptom in node_label and 
                        any(disease_keyword in node_label for disease_keyword in ['感冒', '发烧', '咳嗽', '头痛', '肺炎', '胃炎', '肝炎', '高血压', '糖尿病'])):
                        
                        if node.get('id') not in seen_ids:
                            result = {
                                **node,
                                "match_type": "symptom_diagnosis",
                                "match_score": 85,
                                "matched_symptoms": [symptom],
                                "search_method": "symptom_disease_match"
                            }
                            results.append(result)
                            seen_ids.add(node.get('id'))
                            if len(results) >= limit:
                                break
                
                if len(results) >= limit:
                    break
            
            # 如果症状匹配不够，搜索症状相关的实体
            if len(results) < limit:
                for symptom in symptoms:
                    for node in cached_graph.get('nodes', []):
                        node_label = node.get('label', '').lower()
                        
                        if symptom in node_label and node.get('id') not in seen_ids:
                            result = {
                                **node,
                                "match_type": "symptom_entity",
                                "match_score": 70,
                                "matched_symptoms": [symptom],
                                "search_method": "symptom_entity_match"
                            }
                            results.append(result)
                            seen_ids.add(node.get('id'))
                            if len(results) >= limit:
                                break
                    
                    if len(results) >= limit:
                        break
        else:
            # 备用搜索
            for symptom in symptoms:
                for node in self.knowledge_graph_data.get("nodes", []):
                    node_label = node.get('label', '').lower()
                    
                    if symptom in node_label and node.get('id') not in seen_ids:
                        # 判断是否是疾病实体
                        is_disease = any(disease_keyword in node_label for disease_keyword in ['感冒', '发烧', '咳嗽', '头痛', '肺炎', '胃炎', '肝炎', '高血压', '糖尿病'])
                        
                        result = {
                            **node,
                            "match_type": "symptom_diagnosis" if is_disease else "symptom_entity",
                            "match_score": 85 if is_disease else 70,
                            "matched_symptoms": [symptom],
                            "search_method": "fallback_symptom_search"
                        }
                        results.append(result)
                        seen_ids.add(node.get('id'))
                        if len(results) >= limit:
                            break
                
                if len(results) >= limit:
                    break
        
        end_time = time.time()
        print(f"[调试] 症状诊断搜索结果数量: {len(results)}, 耗时 {end_time - start_time:.3f}s")
        
        # 按分数排序
        results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return results[:limit]
    
    def _search_concurrent(self, query_intent: Dict[str, Any], limit: int = 8) -> List[Dict[str, Any]]:
        """并发搜索相关实体"""
        # 如果是症状诊断查询，使用症状搜索
        if query_intent.get('is_symptom_diagnosis') and query_intent.get('symptoms'):
            print(f"[调试] 症状诊断查询: 症状={query_intent['symptoms']}")
            return self._search_by_symptoms(query_intent['symptoms'], limit)
        
        # 如果是非结构化查询，使用通用搜索
        if not query_intent['is_structured_query']:
            return self.search_entities(query_intent['original_query'], limit)
        
        start_time = time.time()
        print(f"[并发搜索] 开始并发搜索: 疾病={query_intent['disease']}, 关系={query_intent['relation']}")
        
        # 使用线程池进行并发搜索
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # 提交多个搜索任务
            future_relation = executor.submit(
                self._search_by_relation, 
                query_intent['disease'], 
                query_intent['relation'], 
                limit
            )
            
            future_entities = executor.submit(
                self.search_entities, 
                query_intent['disease'], 
                limit // 2
            )
            
            future_keywords = executor.submit(
                self.search_entities, 
                query_intent['relation'], 
                limit // 2
            )
            
            # 收集结果
            results = []
            seen_ids = set()
            
            # 关系搜索结果（最高优先级）
            try:
                relation_results = future_relation.result(timeout=2.0)
                for result in relation_results:
                    if result.get('id') not in seen_ids:
                        results.append(result)
                        seen_ids.add(result.get('id'))
            except concurrent.futures.TimeoutError:
                print("[并发搜索] 关系搜索超时")
            
            # 疾病实体搜索结果
            try:
                entity_results = future_entities.result(timeout=1.0)
                for result in entity_results:
                    if result.get('id') not in seen_ids and len(results) < limit:
                        result['match_score'] = result.get('match_score', 0) * 0.8  # 降低分数
                        results.append(result)
                        seen_ids.add(result.get('id'))
            except concurrent.futures.TimeoutError:
                print("[并发搜索] 实体搜索超时")
            
            # 关系关键词搜索结果
            try:
                keyword_results = future_keywords.result(timeout=1.0)
                for result in keyword_results:
                    if result.get('id') not in seen_ids and len(results) < limit:
                        result['match_score'] = result.get('match_score', 0) * 0.6  # 进一步降低分数
                        results.append(result)
                        seen_ids.add(result.get('id'))
            except concurrent.futures.TimeoutError:
                print("[并发搜索] 关键词搜索超时")
        
        end_time = time.time()
        print(f"[并发搜索] 完成, 找到 {len(results)} 个结果, 耗时 {end_time - start_time:.3f}s")
        
        # 按分数排序
        results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return results[:limit] 