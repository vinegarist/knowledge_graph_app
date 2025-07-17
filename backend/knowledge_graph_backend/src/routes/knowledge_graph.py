import csv
import os
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from collections import defaultdict

knowledge_graph_bp = Blueprint('knowledge_graph', __name__)
CORS(knowledge_graph_bp)

# 默认CSV文件路径
DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'Disease.csv'
)

def parse_csv_to_graph(csv_file_path, max_nodes=100):
    """解析CSV文件为知识图谱数据结构"""
    nodes = {}
    edges = []
    node_connections = defaultdict(int)  # 记录节点的连接数
    
    # 第一遍扫描：统计节点的连接数
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                source = row[0].strip()
                target = row[2].strip()
                node_connections[source] += 1
                node_connections[target] += 1
    
    # 找出连接数最多的节点作为一级节点
    important_nodes = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
    important_node_ids = {node[0] for node in important_nodes}
    
    # 第二遍扫描：构建图
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                source = row[0].strip()
                relation = row[1].strip()
                target = row[2].strip()
                
                # 判断节点层级
                source_level = 1 if source in important_node_ids else 2
                target_level = 1 if target in important_node_ids else 2
                
                # 添加节点
                if source not in nodes:
                    nodes[source] = {
                        'id': source,
                        'label': source,
                        'type': 'entity',
                        'level': source_level,
                        'connections': node_connections[source]
                    }
                
                if target not in nodes:
                    nodes[target] = {
                        'id': target,
                        'label': target,
                        'type': 'entity',
                        'level': target_level,
                        'connections': node_connections[target]
                    }
                
                # 添加边
                edges.append({
                    'source': source,
                    'target': target,
                    'relation': relation,
                    'label': relation
                })
    
    return {
        'nodes': list(nodes.values()),
        'edges': edges
    }

@knowledge_graph_bp.route('/graph', methods=['GET'])
def get_graph():
    """获取知识图谱数据"""
    try:
        level = int(request.args.get('level', 1))  # 默认只显示一级节点
        max_nodes = int(request.args.get('max_nodes', 100))  # 默认最多显示100个节点
        
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        full_graph = parse_csv_to_graph(DEFAULT_CSV_PATH, max_nodes)
        
        if level == 1:
            # 只返回一级节点和它们之间的边
            level_one_nodes = [node for node in full_graph['nodes'] if node['level'] == 1]
            level_one_node_ids = {node['id'] for node in level_one_nodes}
            level_one_edges = [
                edge for edge in full_graph['edges']
                if edge['source'] in level_one_node_ids and edge['target'] in level_one_node_ids
            ]
            return jsonify({
                'nodes': level_one_nodes,
                'edges': level_one_edges
            })
        
        return jsonify(full_graph)
    
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
            
        full_graph = parse_csv_to_graph(DEFAULT_CSV_PATH)
        
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

@knowledge_graph_bp.route('/upload', methods=['POST'])
def upload_csv():
    """上传CSV文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and file.filename.endswith('.csv'):
            # 保存文件
            upload_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'uploaded_data.csv'
            )
            file.save(upload_path)
            
            # 解析并返回图谱数据
            graph_data = parse_csv_to_graph(upload_path)
            return jsonify(graph_data)
        
        return jsonify({'error': '请上传CSV文件'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge_graph_bp.route('/search', methods=['GET'])
def search_entities():
    """搜索实体"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'entities': []})
        
        if not os.path.exists(DEFAULT_CSV_PATH):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        graph_data = parse_csv_to_graph(DEFAULT_CSV_PATH)
        
        # 搜索匹配的实体
        matching_entities = []
        for node in graph_data['nodes']:
            if query.lower() in node['label'].lower():
                matching_entities.append(node)
        
        return jsonify({'entities': matching_entities})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

