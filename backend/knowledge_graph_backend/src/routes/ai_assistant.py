"""
AI助手API路由
"""
from flask import Blueprint, jsonify, request
from flask_cors import CORS
import json
import os
from src.ai.medical_ai import MedicalKnowledgeGraphAI
from src.routes.knowledge_graph import parse_csv_to_full_graph

ai_bp = Blueprint('ai_assistant', __name__)
CORS(ai_bp)

# 全局AI实例
ai_assistant = None

def init_ai_assistant():
    """初始化AI助手"""
    global ai_assistant
    
    # 获取知识图谱数据
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'Disease.csv'
    )
    
    try:
        if os.path.exists(csv_path):
            graph_data = parse_csv_to_full_graph(csv_path)
            ai_assistant = MedicalKnowledgeGraphAI(graph_data)
            print(f"[信息] AI助手初始化成功，加载了 {len(graph_data['nodes'])} 个节点")
        else:
            print(f"[警告] CSV文件不存在: {csv_path}")
            ai_assistant = MedicalKnowledgeGraphAI()
    except Exception as e:
        print(f"[错误] 初始化AI助手失败: {str(e)}")
        ai_assistant = MedicalKnowledgeGraphAI()

# 初始化AI助手
init_ai_assistant()

@ai_bp.route('/ai/chat', methods=['POST'])
def chat():
    """AI聊天接口"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': '缺少问题参数'}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        # 调用AI助手
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        result = ai_assistant.ask(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"[错误] AI聊天处理失败: {str(e)}")
        return jsonify({'error': f'处理请求时出错: {str(e)}'}), 500

@ai_bp.route('/ai/search', methods=['GET'])
def search_entities():
    """搜索实体接口"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': '搜索查询不能为空'}), 400
        
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        results = ai_assistant.search_entities(query, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'total': len(results)
            }
        })
        
    except Exception as e:
        print(f"[错误] 实体搜索失败: {str(e)}")
        return jsonify({'error': f'搜索时出错: {str(e)}'}), 500

@ai_bp.route('/ai/entity/<entity_id>/context', methods=['GET'])
def get_entity_context(entity_id):
    """获取实体上下文信息"""
    try:
        depth = int(request.args.get('depth', 1))
        
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        context = ai_assistant.get_entity_context(entity_id, depth)
        
        if not context:
            return jsonify({'error': '实体不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': context
        })
        
    except Exception as e:
        print(f"[错误] 获取实体上下文失败: {str(e)}")
        return jsonify({'error': f'获取上下文时出错: {str(e)}'}), 500

@ai_bp.route('/ai/sources/page', methods=['POST'])
def paginate_sources():
    """来源分页接口"""
    try:
        data = request.get_json()
        action = data.get('action', 'current')  # current, next, prev
        
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        if action == 'next':
            sources = ai_assistant.next_page()
        elif action == 'prev':
            sources = ai_assistant.prev_page()
        else:
            sources = ai_assistant._get_paginated_sources()
        
        return jsonify({
            'success': True,
            'data': sources
        })
        
    except Exception as e:
        print(f"[错误] 来源分页失败: {str(e)}")
        return jsonify({'error': f'分页时出错: {str(e)}'}), 500

@ai_bp.route('/ai/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        history = ai_assistant.get_chat_history(page, page_size)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        print(f"[错误] 获取聊天历史失败: {str(e)}")
        return jsonify({'error': f'获取历史时出错: {str(e)}'}), 500

@ai_bp.route('/ai/history', methods=['DELETE'])
def clear_chat_history():
    """清空聊天历史"""
    try:
        if ai_assistant is None:
            return jsonify({'error': 'AI助手未初始化'}), 500
        
        ai_assistant.clear_history()
        
        return jsonify({
            'success': True,
            'message': '聊天历史已清空'
        })
        
    except Exception as e:
        print(f"[错误] 清空聊天历史失败: {str(e)}")
        return jsonify({'error': f'清空历史时出错: {str(e)}'}), 500

@ai_bp.route('/ai/status', methods=['GET'])
def get_ai_status():
    """获取AI助手状态"""
    try:
        if ai_assistant is None:
            return jsonify({
                'success': False,
                'status': 'not_initialized',
                'message': 'AI助手未初始化'
            })
        
        # 检查知识图谱数据
        graph_stats = {
            'nodes_count': len(ai_assistant.knowledge_graph_data.get('nodes', [])),
            'links_count': len(ai_assistant.knowledge_graph_data.get('links', [])),
            'entities_indexed': len(ai_assistant.entity_index.get('entities', {}))
        }
        
        # 检查LLM状态
        llm_status = ai_assistant.llm
        
        return jsonify({
            'success': True,
            'status': 'ready',
            'data': {
                'graph_stats': graph_stats,
                'llm_status': llm_status,
                'chat_history_count': len(ai_assistant.chat_history),
                'current_sources_count': len(ai_assistant.current_sources)
            }
        })
        
    except Exception as e:
        print(f"[错误] 获取AI状态失败: {str(e)}")
        return jsonify({'error': f'获取状态时出错: {str(e)}'}), 500

@ai_bp.route('/ai/reload', methods=['POST'])
def reload_knowledge_graph():
    """重新加载知识图谱"""
    try:
        # 重新初始化AI助手
        init_ai_assistant()
        
        if ai_assistant is None:
            return jsonify({'error': '重新初始化失败'}), 500
        
        return jsonify({
            'success': True,
            'message': '知识图谱已重新加载',
            'data': {
                'nodes_count': len(ai_assistant.knowledge_graph_data.get('nodes', [])),
                'links_count': len(ai_assistant.knowledge_graph_data.get('links', []))
            }
        })
        
    except Exception as e:
        print(f"[错误] 重新加载知识图谱失败: {str(e)}")
        return jsonify({'error': f'重新加载时出错: {str(e)}'}), 500 