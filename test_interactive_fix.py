#!/usr/bin/env python3
"""
测试交互式诊断修复
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:5000/api/symptom-diagnosis"

def test_interactive_diagnosis():
    """测试交互式诊断"""
    print("=== 测试交互式诊断修复 ===")
    
    # 1. 开始交互式诊断
    print("1. 开始交互式诊断...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/interactive/start",
            json={"symptoms": ["咳嗽", "喉咙痛"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                interactive_data = data['data']
                print(f"✅ 交互式诊断开始成功")
                print(f"   当前症状: {interactive_data['current_symptoms']}")
                print(f"   问题数量: {len(interactive_data.get('interactive_questions', []))}")
                
                # 2. 回答问题
                if interactive_data.get('interactive_questions'):
                    answers = {}
                    for question in interactive_data['interactive_questions']:
                        if question['symptoms']:
                            # 只选择第一个症状
                            answers[question['id']] = [question['symptoms'][0]]
                    
                    print(f"2. 回答问题...")
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
                            print(f"✅ 回答问题成功")
                            print(f"   新增症状: {result.get('new_symptoms', [])}")
                            print(f"   当前症状: {result.get('current_symptoms', [])}")
                            print(f"   诊断改进: {result.get('diagnosis_improved', False)}")
                            print(f"   可能疾病数量: {len(result.get('possible_diseases', []))}")
                            
                            # 显示前3个疾病
                            for i, disease in enumerate(result.get('possible_diseases', [])[:3]):
                                print(f"     {i+1}. {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
                        else:
                            print(f"❌ 回答问题失败: {data2.get('message')}")
                    else:
                        print(f"❌ 回答问题请求失败: {response2.status_code}")
                        print(f"   响应内容: {response2.text}")
            else:
                print(f"❌ 交互式诊断失败: {data.get('message')}")
        else:
            print(f"❌ 交互式诊断请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 开始测试交互式诊断修复")
    print("=" * 40)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    test_interactive_diagnosis()
    
    print("🎉 测试完成")

if __name__ == "__main__":
    main() 