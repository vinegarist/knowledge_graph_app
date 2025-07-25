#!/usr/bin/env python3
"""
测试意图识别功能的脚本
"""
import sys
import os

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'knowledge_graph_backend', 'src'))

from ai.medical_ai import MedicalKnowledgeGraphAI

def test_intent_recognition():
    """测试意图识别功能"""
    print("=== 测试意图识别功能 ===")
    
    # 创建AI实例（不需要实际数据）
    ai = MedicalKnowledgeGraphAI()
    
    # 测试查询列表
    test_queries = [
        "感冒应该吃什么？",
        "感冒应该吃什么药？", 
        "感冒吃什么食物好？",
        "感冒吃什么药好？",
        "感冒的症状有哪些？",
        "感冒需要做什么检查？",
        "如何预防感冒？",
        "感冒的并发症有哪些？"
    ]
    
    for query in test_queries:
        print(f"\n--- 测试查询: {query} ---")
        intent = ai._parse_query_intent(query)
        print(f"原始查询: {intent['original_query']}")
        print(f"识别意图: {intent['intent']}")
        print(f"检测疾病: {intent['disease']}")
        print(f"关系类型: {intent['relation']}")
        print(f"目标类型: {intent['target_type']}")
        print(f"结构化查询: {intent['is_structured_query']}")

if __name__ == "__main__":
    test_intent_recognition() 