#!/usr/bin/env python3
"""
测试AI驱动的症状诊断功能
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:5000/api/ai-symptom-diagnosis"

def test_ai_diagnosis():
    """测试AI诊断功能"""
    print("=== 测试AI驱动的症状诊断 ===")
    
    # 1. 测试基本诊断
    print("1. 测试基本AI诊断...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose",
            json={"symptoms": ["咳嗽", "发热", "头痛"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ AI诊断成功")
                print(f"   症状: {result.get('symptoms', [])}")
                print(f"   疾病数量: {result.get('disease_count', 0)}")
                print(f"   AI诊断分析: {result.get('ai_diagnosis', '')[:200]}...")
                
                # 显示前3个疾病
                for i, disease in enumerate(result.get('possible_diseases', [])[:3]):
                    print(f"     {i+1}. {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
            else:
                print(f"❌ AI诊断失败: {data.get('message')}")
        else:
            print(f"❌ AI诊断请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_ai_interactive_diagnosis():
    """测试AI交互式诊断"""
    print("\n2. 测试AI交互式诊断...")
    
    # 1. 开始交互式诊断
    print("   2.1 开始交互式诊断...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/interactive/start",
            json={"symptoms": ["咳嗽", "喉咙痛"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                interactive_data = data['data']
                print(f"✅ AI交互式诊断开始成功")
                print(f"   当前症状: {interactive_data['current_symptoms']}")
                print(f"   AI诊断分析: {interactive_data.get('ai_diagnosis', '')[:200]}...")
                print(f"   问题数量: {len(interactive_data.get('interactive_questions', []))}")
                
                # 显示AI生成的问题
                for i, question in enumerate(interactive_data.get('interactive_questions', [])):
                    print(f"   问题{i+1}: {question['question']}")
                
                # 2. 回答问题
                if interactive_data.get('interactive_questions'):
                    answers = {}
                    for question in interactive_data['interactive_questions']:
                        # 模拟用户回答
                        answers[question['id']] = "是的，我有这些症状"
                    
                    print(f"   2.2 回答问题...")
                    print(f"   答案: {answers}")
                    
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
                            print(f"✅ 回答AI问题成功")
                            print(f"   新增症状: {result.get('new_symptoms', [])}")
                            print(f"   当前症状: {result.get('current_symptoms', [])}")
                            print(f"   诊断改进: {result.get('diagnosis_improved', False)}")
                            print(f"   AI诊断分析: {result.get('ai_diagnosis', '')[:200]}...")
                        else:
                            print(f"❌ 回答AI问题失败: {data2.get('message')}")
                    else:
                        print(f"❌ 回答AI问题请求失败: {response2.status_code}")
                        print(f"   响应内容: {response2.text}")
            else:
                print(f"❌ AI交互式诊断失败: {data.get('message')}")
        else:
            print(f"❌ AI交互式诊断请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_ai_statistics():
    """测试AI诊断统计信息"""
    print("\n3. 测试AI诊断统计信息...")
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 获取AI诊断统计成功")
                print(f"   症状总数: {stats.get('total_symptoms', 0)}")
                print(f"   疾病总数: {stats.get('total_diseases', 0)}")
                print(f"   AI功能启用: {stats.get('ai_enabled', False)}")
            else:
                print(f"❌ 获取统计失败: {data.get('message')}")
        else:
            print(f"❌ 统计请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ai_symptoms_list():
    """测试AI症状列表"""
    print("\n4. 测试AI症状列表...")
    try:
        response = requests.get(f"{API_BASE_URL}/symptoms")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                symptoms_data = data['data']
                print(f"✅ 获取AI症状列表成功")
                print(f"   症状数量: {symptoms_data.get('count', 0)}")
                print(f"   前5个症状: {symptoms_data.get('symptoms', [])[:5]}")
            else:
                print(f"❌ 获取症状列表失败: {data.get('message')}")
        else:
            print(f"❌ 症状列表请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 开始测试AI驱动的症状诊断功能")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    test_ai_diagnosis()
    test_ai_interactive_diagnosis()
    test_ai_statistics()
    test_ai_symptoms_list()
    
    print("\n🎉 AI驱动的症状诊断功能测试完成")

if __name__ == "__main__":
    main() 