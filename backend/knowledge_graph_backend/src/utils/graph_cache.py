"""
知识图谱缓存和优化模块
解决性能瓶颈，大幅提升加载和搜索速度
"""
import csv
import os
import time
import json
import hashlib
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

class KnowledgeGraphCache:
    """知识图谱缓存管理器"""
    
    def __init__(self):
        self._graph_cache: Optional[Dict[str, Any]] = None
        self._search_index: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._file_hash: Optional[str] = None
        self._csv_file_path: Optional[str] = None
        
    def _get_file_hash(self, file_path: str) -> str:
        """获取文件哈希值，用于检测文件变化"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 只读取前1MB来计算哈希，提升性能
                chunk = f.read(1024 * 1024)
                hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _is_cache_valid(self, file_path: str) -> bool:
        """检查缓存是否有效"""
        if (self._graph_cache is None or 
            self._file_hash is None or 
            self._csv_file_path != file_path):
            return False
        
        current_hash = self._get_file_hash(file_path)
        return current_hash == self._file_hash
    
    def load_graph(self, csv_file_path: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载知识图谱，使用智能缓存
        
        Args:
            csv_file_path: CSV文件路径
            force_reload: 是否强制重新加载
            
        Returns:
            包含nodes和edges的字典
        """
        # 检查缓存
        if not force_reload and self._is_cache_valid(csv_file_path):
            print(f"[缓存] 使用缓存的知识图谱数据")
            return self._graph_cache
        
        print(f"[加载] 开始加载知识图谱: {csv_file_path}")
        start_time = time.time()
        
        try:
            # 快速解析CSV
            graph_data = self._parse_csv_optimized(csv_file_path)
            
            # 构建搜索索引
            self._build_search_index(graph_data)
            
            # 更新缓存
            self._graph_cache = graph_data
            self._csv_file_path = csv_file_path
            self._file_hash = self._get_file_hash(csv_file_path)
            self._cache_timestamp = time.time()
            
            end_time = time.time()
            print(f"[加载] 完成! 耗时 {end_time - start_time:.2f}s, "
                  f"节点: {len(graph_data['nodes'])}, 边: {len(graph_data['edges'])}")
            
            return graph_data
            
        except Exception as e:
            print(f"[错误] 加载知识图谱失败: {str(e)}")
            return {'nodes': [], 'edges': []}
    
    def _parse_csv_optimized(self, csv_file_path: str) -> Dict[str, Any]:
        """
        优化的CSV解析器
        - 单次读取
        - 批量处理
        - 内存优化
        """
        nodes_dict = {}
        edges = []
        node_connections = defaultdict(int)
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            row_count = 0
            
            for row in reader:
                if len(row) >= 3:
                    source = row[0].strip()
                    relation = row[1].strip()
                    target = row[2].strip()
                    
                    if not source or not target:  # 跳过空值
                        continue
                    
                    # 统计连接数
                    node_connections[source] += 1
                    node_connections[target] += 1
                    
                    # 存储边信息
                    edges.append({
                        'source': source,
                        'target': target,
                        'relation': relation,
                        'label': relation
                    })
                    
                    row_count += 1
                    
                    # 进度显示
                    if row_count % 50000 == 0:
                        print(f"[解析] 已处理 {row_count} 行")
        
        # 构建节点字典
        for edge in edges:
            source, target = edge['source'], edge['target']
            
            if source not in nodes_dict:
                nodes_dict[source] = {
                    'id': source,
                    'label': source,
                    'type': 'entity',
                    'connections': node_connections[source]
                }
            
            if target not in nodes_dict:
                nodes_dict[target] = {
                    'id': target,
                    'label': target,
                    'type': 'entity',
                    'connections': node_connections[target]
                }
        
        return {
            'nodes': list(nodes_dict.values()),
            'edges': edges
        }
    
    def _build_search_index(self, graph_data: Dict[str, Any]) -> None:
        """构建搜索索引"""
        start_time = time.time()
        print(f"[索引] 开始构建搜索索引...")
        
        # 初始化索引结构
        self._search_index = {
            'entities': {},      # 实体ID -> 实体信息
            'exact': {},         # 精确匹配
            'prefix': defaultdict(list),  # 前缀索引
            'token': defaultdict(list),   # 词语索引
            'relations': defaultdict(list),  # 关系索引: 疾病ID -> [(关系, 目标ID)]
            'disease_relations': defaultdict(list),  # 疾病名称 -> [(关系, 目标ID)]
            'relation_targets': defaultdict(list),   # 关系类型 -> [(疾病ID, 目标ID)]
        }
        
        # 医疗同义词映射
        medical_synonyms = {
            '感冒': ['感冒', '普通感冒', '上呼吸道感染'],
            '发烧': ['发热', '发烧', '体温升高'],
            '咳嗽': ['咳嗽', '咳痰', '干咳'],
            '头痛': ['头痛', '头疼', '偏头痛']
        }
        
        # 构建实体索引
        for node in graph_data['nodes']:
            entity_id = node['id']
            label = node['label'].lower()
            
            # 存储实体信息
            self._search_index['entities'][entity_id] = node
            
            # 精确匹配索引
            self._search_index['exact'][label] = entity_id
            
            # 前缀索引（前3-6个字符）
            for i in range(2, min(len(label) + 1, 7)):
                prefix = label[:i]
                self._search_index['prefix'][prefix].append(entity_id)
            
            # 词语分割索引
            tokens = label.split()
            for token in tokens:
                if len(token) > 1:
                    self._search_index['token'][token].append(entity_id)
            
            # 同义词索引
            for term, synonyms in medical_synonyms.items():
                if term in label:
                    for synonym in synonyms:
                        self._search_index['exact'][synonym.lower()] = entity_id
        
        # 构建关系索引
        print(f"[索引] 构建关系索引...")
        for edge in graph_data['edges']:
            source_id = edge.get('source')
            target_id = edge.get('target')
            relation = edge.get('relation', '')
            
            if source_id and target_id and relation:
                # 关系索引
                self._search_index['relations'][source_id].append((relation, target_id))
                
                # 关系目标索引
                self._search_index['relation_targets'][relation].append((source_id, target_id))
                
                # 疾病关系索引（通过实体标签）
                source_entity = self._search_index['entities'].get(source_id)
                if source_entity:
                    source_label = source_entity.get('label', '').lower()
                    # 检查是否是疾病实体
                    if any(disease in source_label for disease in ['感冒', '发烧', '咳嗽', '头痛', '高血压', '糖尿病']):
                        self._search_index['disease_relations'][source_label].append((relation, target_id))
        
        end_time = time.time()
        print(f"[索引] 索引构建完成, 耗时 {end_time - start_time:.2f}s")
        print(f"[索引] 实体数量: {len(self._search_index['entities'])}")
        print(f"[索引] 关系数量: {len(self._search_index['relations'])}")
        print(f"[索引] 疾病关系数量: {len(self._search_index['disease_relations'])}")
    
    def search_entities_fast(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        快速实体搜索
        时间复杂度从 O(E×Q×W) 降低到 O(log N)
        """
        if not query.strip() or not self._search_index:
            return []
        
        query_lower = query.lower().strip()
        results = []
        seen_ids = set()
        
        # 1. 精确匹配 (最高优先级)
        if query_lower in self._search_index['exact']:
            entity_id = self._search_index['exact'][query_lower]
            if entity_id in self._search_index['entities']:
                entity = self._search_index['entities'][entity_id].copy()
                entity['match_type'] = 'exact'
                entity['match_score'] = 100
                results.append(entity)
                seen_ids.add(entity_id)
        
        # 2. 前缀匹配
        for prefix_len in range(len(query_lower), 1, -1):
            prefix = query_lower[:prefix_len]
            if prefix in self._search_index['prefix']:
                for entity_id in self._search_index['prefix'][prefix]:
                    if entity_id not in seen_ids and len(results) < limit:
                        entity = self._search_index['entities'][entity_id].copy()
                        entity['match_type'] = 'prefix'
                        entity['match_score'] = 80 + prefix_len  # 前缀越长分数越高
                        results.append(entity)
                        seen_ids.add(entity_id)
        
        # 3. 词语匹配
        tokens = query_lower.split()
        for token in tokens:
            if token in self._search_index['token']:
                for entity_id in self._search_index['token'][token]:
                    if entity_id not in seen_ids and len(results) < limit:
                        entity = self._search_index['entities'][entity_id].copy()
                        entity['match_type'] = 'token'
                        entity['match_score'] = 60
                        results.append(entity)
                        seen_ids.add(entity_id)
        
        # 按分数和连接数排序
        results.sort(key=lambda x: (x['match_score'], x.get('connections', 0)), reverse=True)
        
        return results[:limit]
    
    def search_by_relation_fast(self, disease: str, relation: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        快速关系搜索
        时间复杂度: O(1) 到 O(log N)
        """
        if not disease or not relation or not self._search_index:
            return []
        
        print(f"[快速关系搜索] 疾病={disease}, 关系={relation}")
        start_time = time.time()
        
        results = []
        seen_ids = set()
        
        # 1. 通过疾病关系索引快速查找
        disease_lower = disease.lower()
        if disease_lower in self._search_index['disease_relations']:
            relations = self._search_index['disease_relations'][disease_lower]
            for rel, target_id in relations:
                if relation in rel and target_id not in seen_ids:
                    target_entity = self._search_index['entities'].get(target_id)
                    if target_entity:
                        result = {
                            **target_entity,
                            "match_type": "relation",
                            "match_score": 95,
                            "relation": rel,
                            "source_disease": disease,
                            "search_method": "disease_relations_index"
                        }
                        results.append(result)
                        seen_ids.add(target_id)
                        if len(results) >= limit:
                            break
        
        # 2. 通过关系目标索引查找
        if len(results) < limit and relation in self._search_index['relation_targets']:
            relation_pairs = self._search_index['relation_targets'][relation]
            for source_id, target_id in relation_pairs:
                if target_id not in seen_ids:
                    source_entity = self._search_index['entities'].get(source_id)
                    target_entity = self._search_index['entities'].get(target_id)
                    
                    if (source_entity and target_entity and 
                        disease in source_entity.get('label', '').lower()):
                        result = {
                            **target_entity,
                            "match_type": "relation",
                            "match_score": 90,
                            "relation": relation,
                            "source_disease": source_entity.get('label'),
                            "search_method": "relation_targets_index"
                        }
                        results.append(result)
                        seen_ids.add(target_id)
                        if len(results) >= limit:
                            break
        
        # 3. 通过实体ID查找疾病实体，然后查找关系
        if len(results) < limit:
            for entity_id, entity in self._search_index['entities'].items():
                if disease in entity.get('label', '').lower():
                    relations = self._search_index['relations'].get(entity_id, [])
                    for rel, target_id in relations:
                        if relation in rel and target_id not in seen_ids:
                            target_entity = self._search_index['entities'].get(target_id)
                            if target_entity:
                                result = {
                                    **target_entity,
                                    "match_type": "relation",
                                    "match_score": 85,
                                    "relation": rel,
                                    "source_disease": entity.get('label'),
                                    "search_method": "entity_relations_index"
                                }
                                results.append(result)
                                seen_ids.add(target_id)
                                if len(results) >= limit:
                                    break
                    if len(results) >= limit:
                        break
        
        end_time = time.time()
        print(f"[快速关系搜索] 找到 {len(results)} 个结果, 耗时 {end_time - start_time:.3f}s")
        
        # 按分数排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:limit]
    
    def get_cached_graph(self) -> Optional[Dict[str, Any]]:
        """获取缓存的图谱数据"""
        return self._graph_cache
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._graph_cache = None
        self._search_index = None
        self._cache_timestamp = None
        self._file_hash = None
        self._csv_file_path = None
        print("[缓存] 知识图谱缓存已清除")

# 全局缓存实例
graph_cache = KnowledgeGraphCache() 