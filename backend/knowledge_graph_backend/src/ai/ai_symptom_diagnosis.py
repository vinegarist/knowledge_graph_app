"""
AI驱动的症状诊断模块
使用LangChain和Ollama模型进行智能症状诊断
"""

import time
import os
import json
from typing import List, Dict, Any, Optional
from collections import defaultdict
import requests
from .medical_ai import MedicalKnowledgeGraphAI
from ..config.ai_config import AIConfig


class AISymptomDiagnosisEngine:
    """AI驱动的症状诊断引擎"""
    
    def __init__(self, medical_ai: MedicalKnowledgeGraphAI):
        self.medical_ai = medical_ai
        self.knowledge_graph_data = medical_ai.knowledge_graph_data
        self._symptom_disease_cache = {}
        self._disease_symptom_cache = {}
        self._build_symptom_disease_mapping()
        
    def _build_symptom_disease_mapping(self):
        """构建症状-疾病映射关系"""
        print("[AI症状诊断] 开始构建症状-疾病映射...")
        start_time = time.time()
        
        # 从知识图谱中提取症状-疾病关系
        for edge in self.knowledge_graph_data.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation", "")
            
            # 如果关系是"症状"，则source是疾病，target是症状
            if relation == "症状":
                disease = source
                symptom = target
                
                # 添加到疾病-症状映射
                if disease not in self._disease_symptom_cache:
                    self._disease_symptom_cache[disease] = set()
                self._disease_symptom_cache[disease].add(symptom)
                
                # 添加到症状-疾病映射
                if symptom not in self._symptom_disease_cache:
                    self._symptom_disease_cache[symptom] = set()
                self._symptom_disease_cache[symptom].add(disease)
        
        print(f"[AI症状诊断] 映射构建完成，耗时: {time.time() - start_time:.2f}s")
        print(f"   症状数量: {len(self._symptom_disease_cache)}")
        print(f"   疾病数量: {len(self._disease_symptom_cache)}")
    
    def _call_ollama_ai(self, prompt: str, system_prompt: str = None) -> str:
        """调用Ollama AI模型"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                f"{AIConfig.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": AIConfig.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                timeout=(10, 60),
                proxies={'http': '', 'https': ''}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                print(f"[AI症状诊断] Ollama调用失败: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"[AI症状诊断] Ollama调用异常: {e}")
            return ""
    
    def _get_disease_symptoms(self, disease: str) -> List[str]:
        """获取疾病的症状列表"""
        return list(self._disease_symptom_cache.get(disease, set()))
    
    def _get_symptom_diseases(self, symptom: str) -> List[str]:
        """获取症状相关的疾病列表"""
        return list(self._symptom_disease_cache.get(symptom, set()))
    
    def _find_related_diseases(self, symptoms: List[str]) -> Dict[str, Any]:
        """基于症状查找相关疾病"""
        disease_scores = defaultdict(lambda: {"matched_symptoms": set(), "total_symptoms": 0, "score": 0})
        
        for symptom in symptoms:
            related_diseases = self._get_symptom_diseases(symptom)
            for disease in related_diseases:
                disease_scores[disease]["matched_symptoms"].add(symptom)
                disease_scores[disease]["total_symptoms"] = len(self._get_disease_symptoms(disease))
                disease_scores[disease]["score"] += 1
        
        # 计算匹配度
        for disease, info in disease_scores.items():
            if info["total_symptoms"] > 0:
                info["match_ratio"] = len(info["matched_symptoms"]) / info["total_symptoms"]
            else:
                info["match_ratio"] = 0
        
        return disease_scores
    
    def diagnose_by_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
        """AI驱动的症状诊断"""
        print(f"[AI症状诊断] 开始诊断症状: {symptoms}")
        
        if not symptoms:
            return {
                "success": False,
                "message": "请提供症状信息"
            }
        
        # 1. 基于知识图谱查找相关疾病
        disease_scores = self._find_related_diseases(symptoms)
        
        # 2. 构建AI诊断提示
        system_prompt = """你是一个专业的医疗AI助手，专门进行症状诊断。请基于提供的症状和疾病信息，进行专业的诊断分析。

诊断要求：
1. 分析症状与疾病的匹配程度
2. 考虑症状的严重程度和组合
3. 提供可能的诊断结果和置信度
4. 建议进一步的检查或注意事项
5. 始终提醒用户咨询专业医生

请用中文回答，格式要清晰易读。"""
        
        # 构建疾病信息
        disease_info = []
        for disease, info in sorted(disease_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]:
            all_symptoms = self._get_disease_symptoms(disease)
            disease_info.append({
                "疾病": disease,
                "匹配症状": list(info["matched_symptoms"]),
                "所有症状": all_symptoms,
                "匹配度": f"{info['match_ratio']:.1%}",
                "匹配分数": info["score"]
            })
        
        prompt = f"""请基于以下症状进行诊断分析：

患者症状：{', '.join(symptoms)}

相关疾病信息：
{json.dumps(disease_info, ensure_ascii=False, indent=2)}

请提供：
1. 最可能的诊断结果（按可能性排序）
2. 每个诊断的置信度分析
3. 建议的进一步检查
4. 注意事项和就医建议

请用中文回答，格式要清晰易读。"""
        
        # 3. 调用AI进行诊断
        ai_diagnosis = self._call_ollama_ai(prompt, system_prompt)
        
        # 4. 构建返回结果
        possible_diseases = []
        for disease, info in sorted(disease_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]:
            possible_diseases.append({
                "disease": disease,
                "matched_symptoms": list(info["matched_symptoms"]),
                "total_symptoms": info["total_symptoms"],
                "match_ratio": info["match_ratio"],
                "score": info["score"]
            })
        
        return {
            "success": True,
            "symptoms": symptoms,
            "ai_diagnosis": ai_diagnosis,
            "possible_diseases": possible_diseases,
            "disease_count": len(possible_diseases),
            "diagnosis_time": time.time()
        }
    
    def interactive_diagnosis(self, initial_symptoms: List[str]) -> Dict[str, Any]:
        """AI驱动的交互式诊断"""
        print(f"[AI症状诊断] 开始交互式诊断，初始症状: {initial_symptoms}")
        
        # 1. 初始诊断
        initial_result = self.diagnose_by_symptoms(initial_symptoms)
        
        # 2. 生成AI交互问题
        system_prompt = """你是一个专业的医疗AI助手，正在进行交互式诊断。请基于患者的症状和可能的疾病，生成有针对性的问题来进一步了解病情。

问题要求：
1. 问题要具体且有针对性
2. 避免重复已知症状
3. 重点关注关键症状
4. 问题要简洁明了
5. 每次最多生成3个问题

请用中文回答，格式要清晰易读。"""
        
        prompt = f"""患者当前症状：{', '.join(initial_symptoms)}

可能的疾病：
{json.dumps([d['disease'] for d in initial_result.get('possible_diseases', [])[:5]], ensure_ascii=False)}

请生成3个有针对性的问题来进一步了解患者病情，帮助更准确诊断。问题应该关注：
1. 症状的详细特征（如疼痛性质、持续时间等）
2. 相关症状（如发热、乏力等）
3. 病史和诱因

请直接列出问题，每个问题一行。"""
        
        ai_questions = self._call_ollama_ai(prompt, system_prompt)
        
        # 解析AI生成的问题
        questions = []
        for i, line in enumerate(ai_questions.strip().split('\n')):
            if line.strip():
                questions.append({
                    "id": f"q_{i}",
                    "question": line.strip(),
                    "type": "ai_generated"
                })
        
        return {
            "success": True,
            "current_symptoms": initial_symptoms,
            "ai_diagnosis": initial_result.get("ai_diagnosis", ""),
            "possible_diseases": initial_result.get("possible_diseases", []),
            "interactive_questions": questions,
            "next_step": "answer_questions"
        }
    
    def answer_questions(self, answers: Dict[str, str], current_symptoms: List[str]) -> Dict[str, Any]:
        """回答AI交互问题，更新诊断"""
        print(f"[AI症状诊断] 回答问题，当前症状: {current_symptoms}")
        print(f"[AI症状诊断] 答案: {answers}")
        
        # 1. 更新症状列表（从答案中提取新症状）
        updated_symptoms = current_symptoms.copy()
        new_symptoms = []
        
        for question_id, answer in answers.items():
            # 使用AI提取答案中的症状
            system_prompt = """你是一个医疗AI助手，请从患者的回答中提取症状信息。

要求：
1. 只提取明确的症状描述
2. 忽略非症状信息
3. 用简洁的词语描述症状
4. 如果有多个症状，用逗号分隔

请直接返回症状列表，用逗号分隔。如果没有症状，返回"无"。"""
            
            prompt = f"""患者回答：{answer}

请提取其中的症状信息："""
            
            extracted_symptoms = self._call_ollama_ai(prompt, system_prompt)
            if extracted_symptoms and extracted_symptoms.strip() != "无":
                symptoms_from_answer = [s.strip() for s in extracted_symptoms.split(',') if s.strip()]
                new_symptoms.extend(symptoms_from_answer)
                updated_symptoms.extend(symptoms_from_answer)
        
        # 去重
        updated_symptoms = list(set(updated_symptoms))
        new_symptoms = list(set(new_symptoms))
        
        # 2. 重新诊断
        updated_result = self.diagnose_by_symptoms(updated_symptoms)
        
        return {
            "success": True,
            "previous_symptoms": current_symptoms,
            "new_symptoms": new_symptoms,
            "current_symptoms": updated_symptoms,
            "ai_diagnosis": updated_result.get("ai_diagnosis", ""),
            "possible_diseases": updated_result.get("possible_diseases", []),
            "diagnosis_improved": len(updated_result.get("possible_diseases", [])) > 0,
            "next_step": "continue_or_finish"
        }
    
    def get_disease_details(self, disease: str) -> Dict[str, Any]:
        """获取疾病详细信息"""
        symptoms = self._get_disease_symptoms(disease)
        
        # 获取疾病实体信息
        disease_entity = None
        for node in self.knowledge_graph_data.get("nodes", []):
            if disease in node.get('label', ''):
                disease_entity = node
                break
        
        return {
            "disease": disease,
            "symptoms": symptoms,
            "entity_info": disease_entity,
            "symptom_count": len(symptoms)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取诊断引擎统计信息"""
        return {
            "total_symptoms": len(self._symptom_disease_cache),
            "total_diseases": len(self._disease_symptom_cache),
            "avg_symptoms_per_disease": sum(len(self._get_disease_symptoms(d)) for d in self._disease_symptom_cache.keys()) / len(self._disease_symptom_cache) if self._disease_symptom_cache else 0,
            "avg_diseases_per_symptom": sum(len(self._get_symptom_diseases(s)) for s in self._symptom_disease_cache.keys()) / len(self._symptom_disease_cache) if self._symptom_disease_cache else 0,
            "ai_enabled": True
        } 