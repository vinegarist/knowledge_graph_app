"""
症状诊断模块
实现症状查询疾病的功能，包括症状输入、疾病匹配、交集计算和进一步询问
"""

import time
import os
import pickle
import hashlib
from typing import List, Dict, Any, Set, Optional
from collections import defaultdict
import concurrent.futures
from ai.medical_ai import MedicalKnowledgeGraphAI
from utils import graph_cache


def ensure_json_serializable(obj):
    """确保对象可以被JSON序列化"""
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)


class SymptomDiagnosisEngine:
    """症状诊断引擎"""
    
    def __init__(self, medical_ai: MedicalKnowledgeGraphAI):
        self.medical_ai = medical_ai
        self.knowledge_graph_data = medical_ai.knowledge_graph_data
        self._use_cache = True
        
        # 症状-疾病映射缓存
        self._symptom_disease_cache = {}
        self._disease_symptom_cache = {}
        
        # 缓存文件路径
        self._cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cache')
        self._cache_file = os.path.join(self._cache_dir, 'symptom_diagnosis_cache.pkl')
        self._cache_meta_file = os.path.join(self._cache_dir, 'symptom_diagnosis_meta.json')
        
        # 确保缓存目录存在
        os.makedirs(self._cache_dir, exist_ok=True)
        
        # 构建症状-疾病映射
        self._build_symptom_disease_mapping()
    
    def _get_data_hash(self) -> str:
        """计算知识图谱数据的哈希值，用于缓存验证"""
        try:
            # 使用节点和边的数量作为简单的数据标识
            nodes_count = len(self.knowledge_graph_data.get("nodes", []))
            edges_count = len(self.knowledge_graph_data.get("edges", []))
            
            # 计算前100个节点的哈希作为数据指纹
            nodes_sample = self.knowledge_graph_data.get("nodes", [])[:100]
            nodes_str = str(sorted([(n.get('id', ''), n.get('label', '')) for n in nodes_sample]))
            
            data_str = f"{nodes_count}_{edges_count}_{nodes_str}"
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            print(f"[症状诊断] 计算数据哈希失败: {e}")
            return "unknown"
    
    def _load_cache(self) -> bool:
        """从本地缓存加载症状-疾病映射"""
        try:
            if not os.path.exists(self._cache_file) or not os.path.exists(self._cache_meta_file):
                print("[症状诊断] 缓存文件不存在，需要重新构建")
                return False
            
            # 检查数据哈希
            import json
            with open(self._cache_meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            current_hash = self._get_data_hash()
            if meta.get('data_hash') != current_hash:
                print("[症状诊断] 数据已更新，缓存失效，需要重新构建")
                return False
            
            # 加载缓存数据
            with open(self._cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self._symptom_disease_cache = cache_data.get('symptom_disease_cache', {})
            self._disease_symptom_cache = cache_data.get('disease_symptom_cache', {})
            
            print(f"[症状诊断] 从缓存加载成功")
            print(f"[症状诊断] 症状数量: {len(self._symptom_disease_cache)}")
            print(f"[症状诊断] 疾病数量: {len(self._disease_symptom_cache)}")
            
            return True
            
        except Exception as e:
            print(f"[症状诊断] 加载缓存失败: {e}")
            return False
    
    def _save_cache(self):
        """保存症状-疾病映射到本地缓存"""
        try:
            cache_data = {
                'symptom_disease_cache': self._symptom_disease_cache,
                'disease_symptom_cache': self._disease_symptom_cache,
                'timestamp': time.time()
            }
            
            # 保存缓存数据
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            # 保存元数据
            import json
            meta_data = {
                'data_hash': self._get_data_hash(),
                'timestamp': time.time(),
                'symptom_count': len(self._symptom_disease_cache),
                'disease_count': len(self._disease_symptom_cache)
            }
            
            with open(self._cache_meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            print(f"[症状诊断] 缓存保存成功: {self._cache_file}")
            
        except Exception as e:
            print(f"[症状诊断] 保存缓存失败: {e}")
    
    def _build_symptom_disease_mapping(self):
        """构建症状-疾病映射关系"""
        print("[症状诊断] 开始构建症状-疾病映射...")
        start_time = time.time()
        
        # 尝试从缓存加载
        if self._use_cache and self._load_cache():
            end_time = time.time()
            print(f"[症状诊断] 缓存加载完成，耗时 {end_time - start_time:.3f}s")
            return
        
        # 清空缓存
        self._symptom_disease_cache.clear()
        self._disease_symptom_cache.clear()
        
        # 从知识图谱中提取症状-疾病关系
        edges = self.knowledge_graph_data.get("edges", [])
        total_edges = len(edges)
        
        print(f"[症状诊断] 处理 {total_edges} 条边关系...")
        
        # 批量处理边关系
        batch_size = 1000
        processed_count = 0
        
        for i in range(0, total_edges, batch_size):
            batch_edges = edges[i:i + batch_size]
            
            for edge in batch_edges:
                relation = edge.get('relation', '').lower()
                
                # 查找症状关系
                if '症状' in relation:
                    source_id = edge.get('source')
                    target_id = edge.get('target')
                    
                    # 获取实体信息
                    source_entity = self._get_entity_by_id(source_id)
                    target_entity = self._get_entity_by_id(target_id)
                    
                    if source_entity and target_entity:
                        source_label = source_entity.get('label', '')
                        target_label = target_entity.get('label', '')
                        
                        # 判断哪个是疾病，哪个是症状
                        if '[疾病]' in source_label:
                            disease = source_label.replace('[疾病]', '')
                            symptom = target_label.replace('[症状]', '') if '[症状]' in target_label else target_label
                            
                            # 添加到映射
                            if symptom not in self._symptom_disease_cache:
                                self._symptom_disease_cache[symptom] = set()
                            self._symptom_disease_cache[symptom].add(disease)
                            
                            if disease not in self._disease_symptom_cache:
                                self._disease_symptom_cache[disease] = set()
                            self._disease_symptom_cache[disease].add(symptom)
                        
                        elif '[疾病]' in target_label:
                            disease = target_label.replace('[疾病]', '')
                            symptom = source_label.replace('[症状]', '') if '[症状]' in source_label else source_label
                            
                            # 添加到映射
                            if symptom not in self._symptom_disease_cache:
                                self._symptom_disease_cache[symptom] = set()
                            self._symptom_disease_cache[symptom].add(disease)
                            
                            if disease not in self._disease_symptom_cache:
                                self._disease_symptom_cache[disease] = set()
                            self._disease_symptom_cache[disease].add(symptom)
            
            processed_count += len(batch_edges)
            if processed_count % 5000 == 0:
                print(f"[症状诊断] 已处理 {processed_count}/{total_edges} 条边...")
        
        # 保存到缓存
        if self._use_cache:
            self._save_cache()
        
        end_time = time.time()
        print(f"[症状诊断] 症状-疾病映射构建完成，耗时 {end_time - start_time:.3f}s")
        print(f"[症状诊断] 症状数量: {len(self._symptom_disease_cache)}")
        print(f"[症状诊断] 疾病数量: {len(self._disease_symptom_cache)}")
    
    def _get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取实体"""
        for node in self.knowledge_graph_data.get("nodes", []):
            if node.get('id') == entity_id:
                return node
        return None
    
    def clear_cache(self):
        """清除本地缓存"""
        try:
            if os.path.exists(self._cache_file):
                os.remove(self._cache_file)
            if os.path.exists(self._cache_meta_file):
                os.remove(self._cache_meta_file)
            print("[症状诊断] 本地缓存已清除")
        except Exception as e:
            print(f"[症状诊断] 清除缓存失败: {e}")
    
    def rebuild_mapping(self):
        """重新构建症状-疾病映射"""
        print("[症状诊断] 重新构建症状-疾病映射...")
        self.clear_cache()
        self._build_symptom_disease_mapping()
    
    def diagnose_by_symptoms(self, symptoms: List[str], min_match_ratio: float = 0.3) -> Dict[str, Any]:
        """
        根据症状进行疾病诊断
        
        Args:
            symptoms: 症状列表
            min_match_ratio: 最小匹配比例（症状匹配数/疾病总症状数）
        
        Returns:
            诊断结果
        """
        print(f"[症状诊断] 开始诊断，症状: {symptoms}")
        start_time = time.time()
        
        # 1. 为每个症状找到可能的疾病
        symptom_diseases = {}
        for symptom in symptoms:
            diseases = self._find_diseases_by_symptom(symptom)
            symptom_diseases[symptom] = diseases
            print(f"[症状诊断] 症状 '{symptom}' 匹配疾病: {list(diseases)[:5]}...")
        
        # 2. 计算疾病交集
        if not symptom_diseases:
            return {
                "success": False,
                "message": "未找到相关疾病",
                "possible_diseases": [],
                "symptom_analysis": {},
                "further_questions": []
            }
        
        # 获取所有疾病
        all_diseases = set()
        for diseases in symptom_diseases.values():
            all_diseases.update(diseases)
        
        # 计算每个疾病的匹配分数
        disease_scores = {}
        for disease in all_diseases:
            matched_symptoms = []
            total_symptoms = len(self._disease_symptom_cache.get(disease, set()))
            
            for symptom in symptoms:
                if disease in symptom_diseases.get(symptom, set()):
                    matched_symptoms.append(symptom)
            
            match_ratio = len(matched_symptoms) / total_symptoms if total_symptoms > 0 else 0
            
            if match_ratio >= min_match_ratio:
                disease_scores[disease] = {
                    "matched_symptoms": matched_symptoms,
                    "total_symptoms": total_symptoms,
                    "match_ratio": match_ratio,
                    "score": len(matched_symptoms) * match_ratio  # 综合分数
                }
        
        # 3. 按分数排序
        sorted_diseases = sorted(
            disease_scores.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        # 4. 生成进一步询问的问题
        further_questions = self._generate_further_questions(sorted_diseases[:5], symptoms)
        
        end_time = time.time()
        
        return {
            "success": True,
            "symptoms": symptoms,
            "possible_diseases": [
                {
                    "disease": disease,
                    "matched_symptoms": list(info["matched_symptoms"]),  # 转换为list
                    "total_symptoms": info["total_symptoms"],
                    "match_ratio": info["match_ratio"],
                    "score": info["score"]
                }
                for disease, info in sorted_diseases[:10]  # 返回前10个
            ],
            "symptom_analysis": {k: list(v) for k, v in symptom_diseases.items()},  # 转换为list
            "further_questions": further_questions,
            "diagnosis_time": end_time - start_time
        }
    
    def _find_diseases_by_symptom(self, symptom: str) -> Set[str]:
        """根据症状查找疾病"""
        diseases = set()
        
        # 直接匹配
        if symptom in self._symptom_disease_cache:
            diseases.update(self._symptom_disease_cache[symptom])
        
        # 模糊匹配
        for cached_symptom, cached_diseases in self._symptom_disease_cache.items():
            if symptom in cached_symptom or cached_symptom in symptom:
                diseases.update(cached_diseases)
        
        return diseases
    
    def _generate_further_questions(self, top_diseases: List[tuple], current_symptoms: List[str]) -> List[Dict[str, Any]]:
        """生成进一步询问的问题"""
        questions = []
        
        for disease, info in top_diseases:
            disease_symptoms = self._disease_symptom_cache.get(disease, set())
            missing_symptoms = disease_symptoms - set(current_symptoms)
            
            if missing_symptoms:
                # 选择最重要的症状进行询问
                important_symptoms = self._select_important_symptoms(list(missing_symptoms)[:3])
                
                questions.append({
                    "disease": disease,
                    "question": f"您是否还有以下症状？",
                    "symptoms": important_symptoms,
                    "reason": f"这些症状在{disease}中比较常见"
                })
        
        return questions[:5]  # 最多返回5个问题
    
    def _select_important_symptoms(self, symptoms: List[str]) -> List[str]:
        """选择重要的症状"""
        # 这里可以根据症状的重要性进行排序
        # 暂时返回前3个
        return symptoms[:3]
    
    def interactive_diagnosis(self, initial_symptoms: List[str]) -> Dict[str, Any]:
        """
        交互式诊断
        
        Args:
            initial_symptoms: 初始症状列表
        
        Returns:
            交互式诊断结果
        """
        print(f"[交互式诊断] 开始，初始症状: {initial_symptoms}")
        
        current_symptoms = initial_symptoms.copy()
        diagnosis_history = []
        
        # 第一轮诊断
        result = self.diagnose_by_symptoms(current_symptoms)
        diagnosis_history.append({
            "round": 1,
            "symptoms": current_symptoms.copy(),
            "result": result
        })
        
        # 生成交互式问题
        interactive_questions = []
        for question_info in result.get("further_questions", []):
            interactive_questions.append({
                "id": f"q_{len(interactive_questions)}",
                "disease": question_info["disease"],
                "question": question_info["question"],
                "symptoms": question_info["symptoms"],
                "type": "symptom_check"
            })
        
        # 确保possible_diseases中的set类型被转换为list
        possible_diseases = result.get("possible_diseases", [])
        for disease in possible_diseases:
            if "matched_symptoms" in disease and isinstance(disease["matched_symptoms"], set):
                disease["matched_symptoms"] = list(disease["matched_symptoms"])
        
        return {
            "success": True,
            "current_symptoms": current_symptoms,
            "possible_diseases": possible_diseases,
            "interactive_questions": interactive_questions,
            "diagnosis_history": diagnosis_history,
            "next_step": "answer_questions"
        }
    
    def answer_questions(self, answers: Dict[str, List[str]], current_symptoms: List[str]) -> Dict[str, Any]:
        """
        回答交互式问题，更新诊断结果
        
        Args:
            answers: 问题答案，格式为 {"q_0": ["症状1", "症状2"], ...}
            current_symptoms: 当前症状列表
        
        Returns:
            更新后的诊断结果
        """
        print(f"[交互式诊断] 回答问题，当前症状: {current_symptoms}")
        print(f"[交互式诊断] 答案: {answers}")
        
        # 更新症状列表
        updated_symptoms = current_symptoms.copy()
        for question_id, new_symptoms in answers.items():
            updated_symptoms.extend(new_symptoms)
        
        # 去重
        updated_symptoms = list(set(updated_symptoms))
        
        # 重新诊断
        result = self.diagnose_by_symptoms(updated_symptoms)
        
        # 确保possible_diseases中的set类型被转换为list
        possible_diseases = result.get("possible_diseases", [])
        for disease in possible_diseases:
            if "matched_symptoms" in disease and isinstance(disease["matched_symptoms"], set):
                disease["matched_symptoms"] = list(disease["matched_symptoms"])
        
        return {
            "success": True,
            "previous_symptoms": current_symptoms,
            "new_symptoms": [s for s in updated_symptoms if s not in current_symptoms],
            "current_symptoms": updated_symptoms,
            "possible_diseases": possible_diseases,
            "diagnosis_improved": len(possible_diseases) > 0,
            "next_step": "continue_or_finish"
        }
    
    def get_disease_details(self, disease: str) -> Dict[str, Any]:
        """获取疾病详细信息"""
        symptoms = list(self._disease_symptom_cache.get(disease, set()))
        
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
            "avg_symptoms_per_disease": sum(len(symptoms) for symptoms in self._disease_symptom_cache.values()) / len(self._disease_symptom_cache) if self._disease_symptom_cache else 0,
            "avg_diseases_per_symptom": sum(len(diseases) for diseases in self._symptom_disease_cache.values()) / len(self._symptom_disease_cache) if self._symptom_disease_cache else 0,
            "cache_enabled": self._use_cache,
            "cache_file": self._cache_file if os.path.exists(self._cache_file) else None
        }