import csv
import os
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from collections import defaultdict
import math
import time
import pickle

knowledge_graph_bp = Blueprint('knowledge_graph', __name__)
CORS(knowledge_graph_bp)

# 默认CSV文件路径
DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'Disease.csv'
)

# 全局缓存
_graph_cache = None
_cache_timestamp = None
_csv_file_path = DEFAULT_CSV_PATH

def _get_file_mtime(file_path):
    """获取文件修改时间"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0

def _is_cache_valid():
    """检查缓存是否有效"""
    global _cache_timestamp
    if _graph_cache is None or _cache_timestamp is None:
        return False
    
    current_mtime = _get_file_mtime(_csv_file_path)
    return current_mtime <= _cache_timestamp

def parse_csv_to_full_graph_optimized(csv_file_path):
    """优化的CSV解析器 - 使用缓存和单次读取"""
    global _graph_cache, _cache_timestamp, _csv_file_path
    
    # 更新文件路径
    _csv_file_path = csv_file_path
    
    # 检查缓存
    if _is_cache_valid():
        print(f"[缓存] 使用缓存的知识图谱数据")
        return _graph_cache
    
    print(f"[解析] 开始解析CSV文件: {csv_file_path}")
    start_time = time.time()
    
    nodes = {}
    edges = []
    node_connections = defaultdict(int)
    
    # 单次读取，同时统计连接数和构建图
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            row_count = 0
            
            for row in reader:
                if len(row) >= 3:
                    source = row[0].strip()
                    relation = row[1].strip()
                    target = row[2].strip()
                    
                    # 统计连接数
                    node_connections[source] += 1
                    node_connections[target] += 1
                    
                    # 临时存储边信息
                    edges.append({
                        'source': source,
                        'target': target,
                        'relation': relation,
                        'label': relation
                    })
                    
                    row_count += 1
                    
                    # 批量进度显示
                    if row_count % 10000 == 0:
                        print(f"[解析] 已处理 {row_count} 行")
        
        # 构建节点（只需一次循环）
        for edge in edges:
            source, target = edge['source'], edge['target']
            
            if source not in nodes:
                nodes[source] = {
                    'id': source,
                    'label': source,
                    'type': 'entity',
                    'connections': node_connections[source]
                }
            
            if target not in nodes:
                nodes[target] = {
                    'id': target,
                    'label': target,
                    'type': 'entity',
                    'connections': node_connections[target]
                }
        
        result = {
            'nodes': list(nodes.values()),
            'edges': edges
        }
        
        # 更新缓存
        _graph_cache = result
        _cache_timestamp = time.time()
        
        end_time = time.time()
        print(f"[解析] 完成! 耗时 {end_time - start_time:.2f}s, "
              f"节点: {len(result['nodes'])}, 边: {len(result['edges'])}")
        
        return result
        
    except Exception as e:
        print(f"[错误] CSV解析失败: {str(e)}")
        return {'nodes': [], 'edges': []}

def parse_csv_to_full_graph(csv_file_path):
    """保持向后兼容的接口"""
    return parse_csv_to_full_graph_optimized(csv_file_path)

def invalidate_cache():
    """手动清除缓存"""
    global _graph_cache, _cache_timestamp
    _graph_cache = None
    _cache_timestamp = None
    print("[缓存] 已清除知识图谱缓存")

def get_paginated_graph(full_graph, page=1, page_size=50):
    """获取分页的图谱数据"""
    # 按连接数排序节点
    sorted_nodes = sorted(full_graph['nodes'], key=lambda x: x['connections'], reverse=True)
    
    # 计算分页
    total_nodes = len(sorted_nodes)
    total_pages = math.ceil(total_nodes / page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # 获取当前页的节点
    current_page_nodes = sorted_nodes[start_idx:end_idx]
    current_node_ids = {node['id'] for node in current_page_nodes}
    
    # 获取这些节点之间的边
    current_page_edges = [
        edge for edge in full_graph['edges']
        if edge['source'] in current_node_ids and edge['target'] in current_node_ids
    ]
    
    return {
        'nodes': current_page_nodes,
        'edges': current_page_edges,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'page_size': page_size,
            'total_nodes': total_nodes
        }
    }

@knowledge_graph_bp.route('/graph', methods=['GET'])
def get_graph():
    """获取知识图谱数据（支持分页）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        paginated_data = get_paginated_graph(full_graph, page, page_size)
        
        return jsonify(paginated_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/graph/info', methods=['GET'])
def get_graph_info():
    """获取图谱基本信息"""
    try:
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
            
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        
        if not full_graph or 'nodes' not in full_graph or 'edges' not in full_graph:
            return jsonify({'error': '无法加载知识图谱数据'}), 500
        
        nodes = full_graph['nodes']
        edges = full_graph['edges']
        
        return jsonify({
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'max_connections': max(node['connections'] for node in nodes) if nodes else 0,
            'min_connections': min(node['connections'] for node in nodes) if nodes else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/node/expand', methods=['GET'])
def expand_node():
    """展开指定节点的相关节点"""
    try:
        node_id = request.args.get('id')
        if not node_id:
            return jsonify({'error': '未指定节点ID'}), 400
            
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
            
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        
        if not full_graph or 'nodes' not in full_graph or 'edges' not in full_graph:
            return jsonify({'error': '无法加载知识图谱数据'}), 500
        
        # 找出与指定节点直接相连的所有节点和边
        related_node_ids = {node_id}
        related_edges = []
        
        for edge in full_graph['edges']:
            if edge['source'] == node_id or edge['target'] == node_id:
                related_edges.append(edge)
                related_node_ids.add(edge['source'])
                related_node_ids.add(edge['target'])
        
        related_nodes = [
            node for node in full_graph['nodes']
            if node['id'] in related_node_ids
        ]
        
        return jsonify({
            'nodes': related_nodes,
            'edges': related_edges
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/node/neighbors', methods=['GET'])
def get_node_neighbors():
    """获取指定节点及其直接邻居节点"""
    try:
        node_id = request.args.get('id')
        if not node_id:
            return jsonify({'error': '未指定节点ID'}), 400
            
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
            
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        
        if not full_graph or 'nodes' not in full_graph or 'edges' not in full_graph:
            return jsonify({'error': '无法加载知识图谱数据'}), 500
        
        # 找出与指定节点直接相连的所有节点和边
        neighbor_node_ids = {node_id}  # 包含目标节点本身
        neighbor_edges = []
        
        # 查找所有相关的边
        for edge in full_graph['edges']:
            if edge['source'] == node_id:
                neighbor_edges.append(edge)
                neighbor_node_ids.add(edge['target'])
            elif edge['target'] == node_id:
                neighbor_edges.append(edge)
                neighbor_node_ids.add(edge['source'])
        
        # 获取所有相关节点
        neighbor_nodes = [
            node for node in full_graph['nodes']
            if node['id'] in neighbor_node_ids
        ]
        
        return jsonify({
            'nodes': neighbor_nodes,
            'edges': neighbor_edges,
            'center_node': node_id,
            'neighbor_count': len(neighbor_nodes) - 1  # 减去中心节点本身
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/upload', methods=['POST'])
def upload_csv():
    """上传CSV文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '' or file.filename is None:
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and file.filename and file.filename.endswith('.csv'):
            # 保存文件
            upload_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'uploaded_data.csv'
            )
            file.save(upload_path)
            
            # 解析并返回图谱数据
            full_graph = parse_csv_to_full_graph(upload_path)
            paginated_data = get_paginated_graph(full_graph, 1, 50)
            return jsonify(paginated_data)
        
        return jsonify({'error': '请上传CSV文件'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/search', methods=['GET'])
def search_entities():
    """搜索实体（支持跨页搜索）"""
    try:
        query = request.args.get('q', '').strip()
        page_size = int(request.args.get('page_size', 50))
        
        if not query:
            return jsonify({'entities': [], 'pages': []})
        
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        
        if not full_graph or 'nodes' not in full_graph:
            return jsonify({'error': '无法加载知识图谱数据'}), 500
        
        # 搜索匹配的实体
        matching_entities = []
        for node in full_graph['nodes']:
            if query.lower() in node['label'].lower():
                matching_entities.append(node)
        
        # 按连接数排序（与分页逻辑保持一致）
        sorted_nodes = sorted(full_graph['nodes'], key=lambda x: x['connections'], reverse=True)
        
        # 计算每个匹配实体在哪一页
        entity_pages = []
        for entity in matching_entities:
            # 找到该实体在排序列表中的位置
            for idx, node in enumerate(sorted_nodes):
                if node['id'] == entity['id']:
                    page_number = (idx // page_size) + 1
                    entity_pages.append({
                        'entity': entity,
                        'page': page_number,
                        'position': idx + 1
                    })
                    break
        
        return jsonify({
            'entities': matching_entities,
            'entity_pages': entity_pages,
            'total_matches': len(matching_entities)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/search/navigate', methods=['GET'])
def search_and_navigate():
    """搜索并导航到包含实体的页面"""
    try:
        query = request.args.get('q', '').strip()
        page_size = int(request.args.get('page_size', 50))
        entity_index = int(request.args.get('entity_index', 0))  # 选择第几个匹配的实体
        
        if not query:
            return jsonify({'error': '搜索查询不能为空'}), 400
        
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        full_graph = parse_csv_to_full_graph(DEFAULT_CSV_PATH)
        
        if not full_graph or 'nodes' not in full_graph:
            return jsonify({'error': '无法加载知识图谱数据'}), 500
        
        # 搜索匹配的实体
        matching_entities = []
        for node in full_graph['nodes']:
            if query.lower() in node['label'].lower():
                matching_entities.append(node)
        
        if not matching_entities:
            return jsonify({'error': '未找到匹配的实体'}), 404
            
        if entity_index >= len(matching_entities):
            return jsonify({'error': '实体索引超出范围'}), 400
        
        target_entity = matching_entities[entity_index]
        
        # 按连接数排序（与分页逻辑保持一致）
        sorted_nodes = sorted(full_graph['nodes'], key=lambda x: x['connections'], reverse=True)
        
        # 找到目标实体在排序列表中的位置
        target_position = None
        for idx, node in enumerate(sorted_nodes):
            if node['id'] == target_entity['id']:
                target_position = idx
                break
        
        if target_position is None:
            return jsonify({'error': '无法定位目标实体'}), 404
        
        # 计算目标页码
        target_page = (target_position // page_size) + 1
        
        # 获取该页的数据
        paginated_data = get_paginated_graph(full_graph, target_page, page_size)
        
        # 标记搜索结果
        for node in paginated_data['nodes']:
            if node['id'] == target_entity['id']:
                node['is_search_result'] = True
                break
        
        return jsonify({
            **paginated_data,
            'search_result': {
                'entity': target_entity,
                'page': target_page,
                'position': target_position + 1,
                'total_matches': len(matching_entities)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

