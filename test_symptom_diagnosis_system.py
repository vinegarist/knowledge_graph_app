#!/usr/bin/env python3
"""
症状诊断系统测试脚本
测试症状查询疾病的功能
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:5000/api/symptom-diagnosis"

def test_basic_diagnosis():
    """测试基本症状诊断功能"""
    print("=== 测试基本症状诊断功能 ===")
    
    # 测试用例1：感冒相关症状
    symptoms = ["头痛", "发烧", "流鼻涕"]
    print(f"症状: {symptoms}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose",
            json={"symptoms": symptoms, "min_match_ratio": 0.3}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ 诊断成功")
                print(f"可能的疾病数量: {len(result.get('possible_diseases', []))}")
                
                for i, disease in enumerate(result.get('possible_diseases', [])[:3]):
                    print(f"  {i+1}. {disease['disease']}")
                    print(f"     匹配度: {disease['match_ratio']:.1%}")
                    print(f"     匹配症状: {disease['matched_symptoms']}")
            else:
                print(f"❌ 诊断失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_interactive_diagnosis():
    """测试交互式诊断功能"""
    print("=== 测试交互式诊断功能 ===")
    
    # 开始交互式诊断
    initial_symptoms = ["咳嗽", "喉咙痛"]
    print(f"初始症状: {initial_symptoms}")
    
    try:
        # 第一步：开始交互式诊断
        response = requests.post(
            f"{API_BASE_URL}/interactive/start",
            json={"symptoms": initial_symptoms}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                interactive_data = data['data']
                print(f"✅ 交互式诊断开始成功")
                print(f"当前症状: {interactive_data['current_symptoms']}")
                print(f"问题数量: {len(interactive_data.get('interactive_questions', []))}")
                
                # 模拟回答问题
                if interactive_data.get('interactive_questions'):
                    answers = {}
                    for question in interactive_data['interactive_questions']:
                        # 模拟选择第一个症状
                        if question['symptoms']:
                            answers[question['id']] = [question['symptoms'][0]]
                    
                    print(f"模拟答案: {answers}")
                    
                    # 第二步：回答问题
                    response2 = requests.post(
                        f"{API_BASE_URL}/interactive/answer",
                        json={
                            "answers": answers,
                            "current_symptoms": interactive_data['current_symptoms']
                        }
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data2.get('success'):
                            result = data2['data']
                            print(f"✅ 回答问题成功")
                            print(f"新增症状: {result.get('new_symptoms', [])}")
                            print(f"当前症状: {result.get('current_symptoms', [])}")
                            print(f"诊断改进: {result.get('diagnosis_improved', False)}")
                        else:
                            print(f"❌ 回答问题失败: {data2.get('message')}")
                    else:
                        print(f"❌ 回答问题请求失败: {response2.status_code}")
            else:
                print(f"❌ 交互式诊断失败: {data.get('message')}")
        else:
            print(f"❌ 交互式诊断请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_disease_details():
    """测试疾病详情功能"""
    print("=== 测试疾病详情功能 ===")
    
    disease_name = "感冒"
    print(f"查询疾病: {disease_name}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/disease/{disease_name}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                details = data['data']
                print(f"✅ 获取疾病详情成功")
                print(f"疾病: {details['disease']}")
                print(f"症状数量: {details['symptom_count']}")
                print(f"症状列表: {details['symptoms'][:5]}...")  # 只显示前5个
            else:
                print(f"❌ 获取疾病详情失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_statistics():
    """测试统计信息功能"""
    print("=== 测试统计信息功能 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 获取统计信息成功")
                print(f"症状总数: {stats['total_symptoms']}")
                print(f"疾病总数: {stats['total_diseases']}")
                print(f"平均症状数/疾病: {stats['avg_symptoms_per_disease']:.2f}")
                print(f"平均疾病数/症状: {stats['avg_diseases_per_symptom']:.2f}")
            else:
                print(f"❌ 获取统计信息失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_available_symptoms():
    """测试可用症状列表功能"""
    print("=== 测试可用症状列表功能 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/symptoms")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                symptoms_data = data['data']
                print(f"✅ 获取症状列表成功")
                print(f"症状总数: {symptoms_data['count']}")
                print(f"前10个症状: {symptoms_data['symptoms'][:10]}")
            else:
                print(f"❌ 获取症状列表失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_available_diseases():
    """测试可用疾病列表功能"""
    print("=== 测试可用疾病列表功能 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/diseases")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                diseases_data = data['data']
                print(f"✅ 获取疾病列表成功")
                print(f"疾病总数: {diseases_data['count']}")
                print(f"前10个疾病: {diseases_data['diseases'][:10]}")
            else:
                print(f"❌ 获取疾病列表失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_complex_scenarios():
    """测试复杂场景"""
    print("=== 测试复杂场景 ===")
    
    # 场景1：消化系统症状
    print("场景1：消化系统症状")
    symptoms1 = ["腹痛", "恶心", "呕吐"]
    print(f"症状: {symptoms1}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose",
            json={"symptoms": symptoms1, "min_match_ratio": 0.2}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ 诊断成功，找到 {len(result.get('possible_diseases', []))} 个可能疾病")
                for disease in result.get('possible_diseases', [])[:3]:
                    print(f"  - {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
            else:
                print(f"❌ 诊断失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()
    
    # 场景2：呼吸系统症状
    print("场景2：呼吸系统症状")
    symptoms2 = ["咳嗽", "胸闷", "气短"]
    print(f"症状: {symptoms2}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose",
            json={"symptoms": symptoms2, "min_match_ratio": 0.2}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ 诊断成功，找到 {len(result.get('possible_diseases', []))} 个可能疾病")
                for disease in result.get('possible_diseases', [])[:3]:
                    print(f"  - {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
            else:
                print(f"❌ 诊断失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始症状诊断系统测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 运行所有测试
    test_basic_diagnosis()
    test_interactive_diagnosis()
    test_disease_details()
    test_statistics()
    test_available_symptoms()
    test_available_diseases()
    test_complex_scenarios()
    
    print("🎉 症状诊断系统测试完成")

if __name__ == "__main__":
    main() 