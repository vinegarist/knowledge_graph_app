#!/usr/bin/env python3
"""
症状诊断功能测试脚本
"""
import requests
import json
import time

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

def test_symptom_diagnosis():
    """测试症状诊断功能"""
    print("=== 症状诊断功能测试 ===")
    
    # 测试查询列表
    test_queries = [
        # 感冒相关症状
        "我有点感冒，发烧，流鼻涕，可能是什么病？",
        "我有感冒症状，发烧，咳嗽，可能是什么病？",
        "我出现感冒，头痛，乏力，可能是什么病？",
        
        # 发烧相关症状
        "我发烧了，头痛，全身酸痛，可能是什么病？",
        "我有发烧，咳嗽，胸闷，可能是什么病？",
        "我出现发烧，流鼻涕，打喷嚏，可能是什么病？",
        
        # 咳嗽相关症状
        "我咳嗽，喉咙痛，可能是什么病？",
        "我有咳嗽，胸闷，气短，可能是什么病？",
        "我出现咳嗽，发烧，乏力，可能是什么病？",
        
        # 头痛相关症状
        "我头痛，恶心，可能是什么病？",
        "我有头痛，发烧，可能是什么病？",
        "我出现头痛，头晕，可能是什么病？",
        
        # 消化系统症状
        "我腹痛，恶心，呕吐，可能是什么病？",
        "我有腹泻，腹痛，可能是什么病？",
        "我出现腹胀，食欲不振，可能是什么病？",
        
        # 其他症状
        "我失眠，多梦，可能是什么病？",
        "我有心悸，胸闷，可能是什么病？",
        "我出现皮疹，瘙痒，可能是什么病？",
        
        # 非症状诊断查询（对比测试）
        "感冒应该吃什么？",
        "发烧吃什么药？",
        "咳嗽有什么症状？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}: {query} ---")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 查询成功")
                    print(f"回答长度: {len(data['data']['answer'])} 字符")
                    print(f"回答前200字符: {data['data']['answer'][:200]}...")
                    print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                    print(f"知识图谱覆盖: {data['data'].get('knowledge_graph_coverage', False)}")
                    
                    # 显示相关实体
                    entities = data['data'].get('related_entities', [])
                    if entities:
                        print("相关实体:")
                        for j, entity in enumerate(entities[:3], 1):
                            match_type = entity.get('match_type', 'N/A')
                            match_score = entity.get('match_score', 'N/A')
                            matched_symptoms = entity.get('matched_symptoms', [])
                            search_method = entity.get('search_method', 'N/A')
                            
                            print(f"  {j}. {entity.get('label', 'N/A')}")
                            print(f"     匹配类型: {match_type}, 分数: {match_score}")
                            if matched_symptoms:
                                print(f"     匹配症状: {matched_symptoms}")
                            print(f"     搜索方法: {search_method}")
                    else:
                        print("没有找到相关实体")
                        
                else:
                    print(f"❌ 查询失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        # 等待一下再测试下一个查询
        time.sleep(1)

def test_specific_symptom_queries():
    """测试特定的症状诊断场景"""
    print("\n=== 特定症状诊断场景测试 ===")
    
    # 测试感冒症状诊断
    print("\n--- 测试感冒症状诊断 ---")
    try:
        response = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": "我有点感冒，发烧，流鼻涕，可能是什么病？"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 感冒症状诊断成功")
                print(f"回答: {data['data']['answer'][:300]}...")
                
                # 检查是否找到了相关实体
                entities = data['data'].get('related_entities', [])
                if entities:
                    print("找到的相关实体:")
                    for entity in entities:
                        print(f"  - {entity.get('label')} (匹配类型: {entity.get('match_type', 'N/A')})")
                        if entity.get('matched_symptoms'):
                            print(f"    匹配症状: {entity.get('matched_symptoms')}")
                else:
                    print("没有找到相关实体")
            else:
                print(f"❌ 查询失败: {data.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_symptom_extraction():
    """测试症状提取功能"""
    print("\n=== 症状提取功能测试 ===")
    
    # 测试不同的症状描述
    symptom_tests = [
        "我有点感冒，发烧，流鼻涕",
        "我有咳嗽，喉咙痛，胸闷",
        "我出现头痛，恶心，呕吐",
        "我有腹痛，腹泻，食欲不振",
        "我出现失眠，多梦，心悸",
        "我有皮疹，瘙痒，红肿",
        "我出现头晕，耳鸣，视力模糊",
        "我有口干，口苦，口臭",
        "我出现牙痛，牙龈出血",
        "我有声音嘶哑，失声"
    ]
    
    for i, symptoms in enumerate(symptom_tests, 1):
        print(f"\n--- 症状提取测试 {i}: {symptoms} ---")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": f"{symptoms}，可能是什么病？"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 症状提取成功")
                    print(f"回答前100字符: {data['data']['answer'][:100]}...")
                    print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                    
                    # 显示匹配的症状
                    entities = data['data'].get('related_entities', [])
                    if entities:
                        for entity in entities:
                            if entity.get('matched_symptoms'):
                                print(f"匹配症状: {entity.get('matched_symptoms')}")
                else:
                    print(f"❌ 查询失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    print("开始症状诊断功能测试...")
    
    # 测试症状诊断功能
    test_symptom_diagnosis()
    
    # 测试特定场景
    test_specific_symptom_queries()
    
    # 测试症状提取
    test_symptom_extraction()
    
    print("\n症状诊断功能测试完成！") 