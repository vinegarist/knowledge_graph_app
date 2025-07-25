"""
AI驱动的症状诊断路由
"""

from flask import Blueprint, request, jsonify
import traceback
from ai.ai_symptom_diagnosis import AISymptomDiagnosisEngine
from ai.medical_ai import MedicalKnowledgeGraphAI

ai_symptom_diagnosis_bp = Blueprint('ai_symptom_diagnosis', __name__)
ai_diagnosis_engine = None

def init_ai_diagnosis_engine(medical_ai: MedicalKnowledgeGraphAI):
    """初始化AI诊断引擎"""
    global ai_diagnosis_engine
    ai_diagnosis_engine = AISymptomDiagnosisEngine(medical_ai)
    print(f"[AI症状诊断] AI诊断引擎初始化成功")

@ai_symptom_diagnosis_bp.route('/diagnose', methods=['POST'])
def ai_diagnose_symptoms():
    """AI驱动的症状诊断"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据不能为空"
            }), 400
        
        symptoms = data.get('symptoms', [])
        
        if not symptoms:
            return jsonify({
                "success": False,
                "message": "请提供症状信息"
            }), 400
        
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 进行AI诊断
        result = ai_diagnosis_engine.diagnose_by_symptoms(symptoms)
        
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
        print(f"[AI症状诊断API] 错误: {str(e)}")
        print(f"[AI症状诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"AI诊断失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/interactive/start', methods=['POST'])
def start_ai_interactive_diagnosis():
    """开始AI交互式诊断"""
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
                "message": "请提供初始症状"
            }), 400
        
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 开始AI交互式诊断
        result = ai_diagnosis_engine.interactive_diagnosis(initial_symptoms)
        
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
        print(f"[AI交互式诊断API] 错误: {str(e)}")
        print(f"[AI交互式诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"开始AI交互式诊断失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/interactive/answer', methods=['POST'])
def answer_ai_interactive_questions():
    """回答AI交互式问题"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "请求数据不能为空"
            }), 400
        
        answers = data.get('answers', {})
        current_symptoms = data.get('current_symptoms', [])
        
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 回答AI问题
        result = ai_diagnosis_engine.answer_questions(answers, current_symptoms)
        
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
        print(f"[AI交互式诊断API] 错误: {str(e)}")
        print(f"[AI交互式诊断API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"回答AI问题失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/disease/<disease_name>', methods=['GET'])
def get_ai_disease_details(disease_name: str):
    """获取疾病详细信息"""
    try:
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 获取疾病详情
        details = ai_diagnosis_engine.get_disease_details(disease_name)
        
        return jsonify({
            "success": True,
            "data": details
        })
        
    except Exception as e:
        print(f"[AI疾病详情API] 错误: {str(e)}")
        print(f"[AI疾病详情API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取疾病详情失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/statistics', methods=['GET'])
def get_ai_statistics():
    """获取AI诊断引擎统计信息"""
    try:
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 获取统计信息
        stats = ai_diagnosis_engine.get_statistics()
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        print(f"[AI统计信息API] 错误: {str(e)}")
        print(f"[AI统计信息API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取统计信息失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/symptoms', methods=['GET'])
def get_ai_available_symptoms():
    """获取所有可用的症状列表"""
    try:
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 获取所有症状
        symptoms = list(ai_diagnosis_engine._symptom_disease_cache.keys())
        
        return jsonify({
            "success": True,
            "data": {
                "symptoms": symptoms,
                "count": len(symptoms)
            }
        })
        
    except Exception as e:
        print(f"[AI症状列表API] 错误: {str(e)}")
        print(f"[AI症状列表API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取症状列表失败: {str(e)}"
        }), 500

@ai_symptom_diagnosis_bp.route('/diseases', methods=['GET'])
def get_ai_available_diseases():
    """获取所有可用的疾病列表"""
    try:
        if not ai_diagnosis_engine:
            return jsonify({
                "success": False,
                "message": "AI诊断引擎未初始化"
            }), 500
        
        # 获取所有疾病
        diseases = list(ai_diagnosis_engine._disease_symptom_cache.keys())
        
        return jsonify({
            "success": True,
            "data": {
                "diseases": diseases,
                "count": len(diseases)
            }
        })
        
    except Exception as e:
        print(f"[AI疾病列表API] 错误: {str(e)}")
        print(f"[AI疾病列表API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取疾病列表失败: {str(e)}"
        }), 500