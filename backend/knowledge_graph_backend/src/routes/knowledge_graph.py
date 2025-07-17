import csv
import os
from flask import Blueprint, jsonify, request
from flask_cors import CORS

knowledge_graph_bp = Blueprint('knowledge_graph', __name__)
CORS(knowledge_graph_bp)

def parse_csv_to_graph(csv_file_path):
    """解析CSV文件为知识图谱数据结构"""
    nodes = {}
    edges = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                source = row[0].strip()
                relation = row[1].strip()
                target = row[2].strip()
                
                # 添加节点
                if source not in nodes:
                    nodes[source] = {
                        'id': source,
                        'label': source,
                        'type': 'entity'
                    }
                
                if target not in nodes:
                    nodes[target] = {
                        'id': target,
                        'label': target,
                        'type': 'entity'
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
        # 获取CSV文件路径
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'sample_data.csv'
        )
        
        if not os.path.exists(csv_file_path):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        graph_data = parse_csv_to_graph(csv_file_path)
        return jsonify(graph_data)
    
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
        
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'sample_data.csv'
        )
        
        if not os.path.exists(csv_file_path):
            return jsonify({'error': 'CSV文件不存在'}), 404
        
        graph_data = parse_csv_to_graph(csv_file_path)
        
        # 搜索匹配的实体
        matching_entities = []
        for node in graph_data['nodes']:
            if query.lower() in node['label'].lower():
                matching_entities.append(node)
        
        return jsonify({'entities': matching_entities})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

