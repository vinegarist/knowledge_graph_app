#!/usr/bin/env python3
"""
完整的AI诊断功能测试
"""

import requests
import json
import time

def test_ai_diagnosis():
    """测试AI诊断功能"""
    print("=== 测试AI诊断功能 ===")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/ai-symptom-diagnosis/diagnose",
            json={"symptoms": ["发烧", "流鼻涕", "头痛"]},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ AI诊断成功")
                print(f"   症状: {result.get('symptoms', [])}")
                print(f"   疾病数量: {result.get('disease_count', 0)}")
                
                # 显示前3个疾病
                for i, disease in enumerate(result.get('possible_diseases', [])[:3]):
                    print(f"     {i+1}. {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
                
                # 显示AI诊断分析
                ai_diagnosis = result.get('ai_diagnosis', '')
                if ai_diagnosis:
                    print(f"   AI诊断分析: {ai_diagnosis[:200]}...")
                else:
                    print("   AI诊断分析: 空")
            else:
                print(f"❌ AI诊断失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ai_interactive():
    """测试AI交互式诊断"""
    print("\n=== 测试AI交互式诊断 ===")
    
    try:
        # 开始交互式诊断
        response = requests.post(
            "http://localhost:5000/api/ai-symptom-diagnosis/interactive/start",
            json={"symptoms": ["咳嗽", "喉咙痛"]},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ AI交互式诊断开始成功")
                print(f"   当前症状: {result.get('current_symptoms', [])}")
                print(f"   问题数量: {len(result.get('interactive_questions', []))}")
                
                # 显示AI生成的问题
                for i, question in enumerate(result.get('interactive_questions', [])):
                    print(f"   问题{i+1}: {question['question']}")
                
                # 回答问题
                if result.get('interactive_questions'):
                    answers = {}
                    for question in result['interactive_questions']:
                        answers[question['id']] = "是的，我有这些症状"
                    
                    response2 = requests.post(
                        "http://localhost:5000/api/ai-symptom-diagnosis/interactive/answer",
                        json={
                            "answers": answers,
                            "current_symptoms": result['current_symptoms']
                        },
                        timeout=60
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data2.get('success'):
                            result2 = data2['data']
                            print(f"✅ 回答AI问题成功")
                            print(f"   新增症状: {result2.get('new_symptoms', [])}")
                            print(f"   诊断改进: {result2.get('diagnosis_improved', False)}")
                        else:
                            print(f"❌ 回答AI问题失败: {data2.get('message')}")
                    else:
                        print(f"❌ 回答AI问题请求失败: {response2.status_code}")
            else:
                print(f"❌ AI交互式诊断失败: {data.get('message')}")
        else:
            print(f"❌ 交互式诊断请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ai_statistics():
    """测试AI统计信息"""
    print("\n=== 测试AI统计信息 ===")
    
    try:
        response = requests.get("http://localhost:5000/api/ai-symptom-diagnosis/statistics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 获取AI统计成功")
                print(f"   症状总数: {stats.get('total_symptoms', 0)}")
                print(f"   疾病总数: {stats.get('total_diseases', 0)}")
                print(f"   AI功能启用: {stats.get('ai_enabled', False)}")
            else:
                print(f"❌ 获取统计失败: {data.get('message')}")
        else:
            print(f"❌ 统计请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 开始完整AI诊断功能测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    test_ai_diagnosis()
    test_ai_interactive()
    test_ai_statistics()
    
    print("\n🎉 AI诊断功能测试完成")

if __name__ == "__main__":
    main() 