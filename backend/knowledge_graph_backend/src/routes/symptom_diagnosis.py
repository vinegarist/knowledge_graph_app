"""
症状诊断API路由
提供症状查询疾病的功能
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Any
import traceback
from ai.symptom_diagnosis import SymptomDiagnosisEngine
from ai.medical_ai import MedicalKnowledgeGraphAI

# 创建蓝图
symptom_diagnosis_bp = Blueprint('symptom_diagnosis', __name__)

# 全局诊断引擎实例
diagnosis_engine = None

def init_diagnosis_engine(medical_ai: MedicalKnowledgeGraphAI):
    """初始化诊断引擎"""
    global diagnosis_engine
    diagnosis_engine = SymptomDiagnosisEngine(medical_ai)

@symptom_diagnosis_bp.route('/diagnose', methods=['POST'])
def diagnose_symptoms():
    """根据症状进行疾病诊断"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据不能为空"
            }), 400
        
        symptoms = data.get('symptoms', [])
        min_match_ratio = data.get('min_match_ratio', 0.3)
        
        if not symptoms:
            return jsonify({
                "success": False,
                "message": "症状列表不能为空"
            }), 400
        
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 进行诊断
        result = diagnosis_engine.diagnose_by_symptoms(symptoms, min_match_ratio)
        
        # 确保结果可以被JSON序列化
        def ensure_serializable(obj):
            if isinstance(obj, dict):
                return {k: ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        serializable_result = ensure_serializable(result)
        
        return jsonify({
            "success": True,
            "data": serializable_result
        })
        
    except Exception as e:
        print(f"[症状诊断API] 错误: {str(e)}")
        print(f"[症状诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"诊断失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/interactive/start', methods=['POST'])
def start_interactive_diagnosis():
    """开始交互式诊断"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据不能为空"
            }), 400
        
        initial_symptoms = data.get('symptoms', [])
        
        if not initial_symptoms:
            return jsonify({
                "success": False,
                "message": "初始症状不能为空"
            }), 400
        
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 开始交互式诊断
        result = diagnosis_engine.interactive_diagnosis(initial_symptoms)
        
        # 确保结果可以被JSON序列化
        def ensure_serializable(obj):
            if isinstance(obj, dict):
                return {k: ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        serializable_result = ensure_serializable(result)
        
        return jsonify({
            "success": True,
            "data": serializable_result
        })
        
    except Exception as e:
        print(f"[交互式诊断API] 错误: {str(e)}")
        print(f"[交互式诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"交互式诊断失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/interactive/answer', methods=['POST'])
def answer_interactive_questions():
    """回答交互式问题"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据不能为空"
            }), 400
        
        answers = data.get('answers', {})
        current_symptoms = data.get('current_symptoms', [])
        
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 回答问题
        result = diagnosis_engine.answer_questions(answers, current_symptoms)
        
        # 确保结果可以被JSON序列化
        def ensure_serializable(obj):
            if isinstance(obj, dict):
                return {k: ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        serializable_result = ensure_serializable(result)
        
        return jsonify({
            "success": True,
            "data": serializable_result
        })
        
    except Exception as e:
        print(f"[交互式诊断API] 错误: {str(e)}")
        print(f"[交互式诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"回答问题失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/disease/<disease_name>', methods=['GET'])
def get_disease_details(disease_name: str):
    """获取疾病详细信息"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 获取疾病详情
        details = diagnosis_engine.get_disease_details(disease_name)
        
        return jsonify({
            "success": True,
            "data": details
        })
        
    except Exception as e:
        print(f"[疾病详情API] 错误: {str(e)}")
        print(f"[疾病详情API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取疾病详情失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取诊断引擎统计信息"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 获取统计信息
        stats = diagnosis_engine.get_statistics()
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        print(f"[统计信息API] 错误: {str(e)}")
        print(f"[统计信息API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取统计信息失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/symptoms', methods=['GET'])
def get_available_symptoms():
    """获取所有可用的症状列表"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 获取所有症状
        symptoms = list(diagnosis_engine._symptom_disease_cache.keys())
        
        return jsonify({
            "success": True,
            "data": {
                "symptoms": symptoms,
                "count": len(symptoms)
            }
        })
        
    except Exception as e:
        print(f"[症状列表API] 错误: {str(e)}")
        print(f"[症状列表API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取症状列表失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/diseases', methods=['GET'])
def get_available_diseases():
    """获取所有可用的疾病列表"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 获取所有疾病
        diseases = list(diagnosis_engine._disease_symptom_cache.keys())
        
        return jsonify({
            "success": True,
            "data": {
                "diseases": diseases,
                "count": len(diseases)
            }
        })
        
    except Exception as e:
        print(f"[疾病列表API] 错误: {str(e)}")
        print(f"[疾病列表API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取疾病列表失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/cache/clear', methods=['POST'])
def clear_diagnosis_cache():
    """清除症状诊断缓存"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 清除缓存
        diagnosis_engine.clear_cache()
        
        return jsonify({
            "success": True,
            "message": "症状诊断缓存已清除"
        })
        
    except Exception as e:
        print(f"[缓存清除API] 错误: {str(e)}")
        print(f"[缓存清除API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"清除缓存失败: {str(e)}"
        }), 500

@symptom_diagnosis_bp.route('/cache/rebuild', methods=['POST'])
def rebuild_diagnosis_mapping():
    """重新构建症状-疾病映射"""
    try:
        if not diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "诊断引擎未初始化"
            }), 500
        
        # 重新构建映射
        diagnosis_engine.rebuild_mapping()
        
        # 获取统计信息
        stats = diagnosis_engine.get_statistics()
        
        return jsonify({
            "success": True,
            "message": "症状-疾病映射已重新构建",
            "data": stats
        })
        
    except Exception as e:
        print(f"[映射重建API] 错误: {str(e)}")
        print(f"[映射重建API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"重新构建映射失败: {str(e)}"
        }), 500