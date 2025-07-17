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
        """构建优化的搜索索引"""
        print("[索引] 构建搜索索引...")
        start_time = time.time()
        
        # 多级索引结构
        self._search_index = {
            'exact': {},           # 精确匹配
            'prefix': defaultdict(list),  # 前缀匹配
            'token': defaultdict(list),   # 词语匹配
            'entities': {}         # 实体映射
        }
        
        # 医疗术语预处理
        medical_synonyms = {
            '感冒': ['感冒', '普通感冒', '上呼吸道感染', '流感'],
            '发烧': ['发热', '发烧', '体温升高', '高热'],
            '咳嗽': ['咳嗽', '咳痰', '干咳'],
            '头痛': ['头痛', '头疼', '偏头痛']
        }
        
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
        
        end_time = time.time()
        print(f"[索引] 索引构建完成, 耗时 {end_time - start_time:.2f}s")
    
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