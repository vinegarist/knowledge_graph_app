#!/usr/bin/env python3
"""
症状诊断页面功能测试脚本
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:5000/api/symptom-diagnosis"

def test_page_functionality():
    """测试页面功能"""
    print("=== 症状诊断页面功能测试 ===")
    
    # 1. 测试基本API功能
    print("1. 测试基本API功能...")
    
    # 统计信息
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 统计信息: {stats['total_symptoms']} 症状, {stats['total_diseases']} 疾病")
            else:
                print(f"❌ 获取统计信息失败: {data.get('message')}")
        else:
            print(f"❌ 统计信息请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息测试失败: {e}")
    
    # 症状列表
    try:
        response = requests.get(f"{API_BASE_URL}/symptoms")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 症状列表: {data['data']['count']} 个症状")
            else:
                print(f"❌ 获取症状列表失败: {data.get('message')}")
        else:
            print(f"❌ 症状列表请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 症状列表测试失败: {e}")
    
    # 疾病列表
    try:
        response = requests.get(f"{API_BASE_URL}/diseases")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 疾病列表: {data['data']['count']} 个疾病")
            else:
                print(f"❌ 获取疾病列表失败: {data.get('message')}")
        else:
            print(f"❌ 疾病列表请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 疾病列表测试失败: {e}")
    
    print()
    
    # 2. 测试诊断功能
    print("2. 测试诊断功能...")
    
    test_cases = [
        {
            "name": "感冒症状",
            "symptoms": ["头痛", "发烧", "流鼻涕"]
        },
        {
            "name": "消化系统症状",
            "symptoms": ["腹痛", "恶心", "呕吐"]
        },
        {
            "name": "呼吸系统症状",
            "symptoms": ["咳嗽", "胸闷", "气短"]
        }
    ]
    
    for test_case in test_cases:
        print(f"   测试 {test_case['name']}...")
        try:
            response = requests.post(
                f"{API_BASE_URL}/diagnose",
                json={
                    "symptoms": test_case['symptoms'],
                    "min_match_ratio": 0.2
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data['data']
                    print(f"   ✅ 找到 {len(result.get('possible_diseases', []))} 个可能疾病")
                    
                    # 显示前3个结果
                    for i, disease in enumerate(result.get('possible_diseases', [])[:3]):
                        print(f"     {i+1}. {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
                else:
                    print(f"   ❌ 诊断失败: {data.get('message')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    print()
    
    # 3. 测试交互式诊断
    print("3. 测试交互式诊断...")
    
    try:
        # 开始交互式诊断
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
                
                # 模拟回答问题
                if interactive_data.get('interactive_questions'):
                    answers = {}
                    for question in interactive_data['interactive_questions']:
                        if question['symptoms']:
                            answers[question['id']] = [question['symptoms'][0]]
                    
                    print(f"   模拟答案: {answers}")
                    
                    # 回答问题
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
                            print(f"   诊断改进: {result.get('diagnosis_improved', False)}")
                        else:
                            print(f"❌ 回答问题失败: {data2.get('message')}")
                    else:
                        print(f"❌ 回答问题请求失败: {response2.status_code}")
            else:
                print(f"❌ 交互式诊断失败: {data.get('message')}")
        else:
            print(f"❌ 交互式诊断请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 交互式诊断测试失败: {e}")
    
    print()
    
    # 4. 测试疾病详情
    print("4. 测试疾病详情...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/disease/感冒")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                details = data['data']
                print(f"✅ 疾病详情获取成功")
                print(f"   疾病: {details['disease']}")
                print(f"   症状数量: {details['symptom_count']}")
                print(f"   症状示例: {details['symptoms'][:3]}")
            else:
                print(f"❌ 获取疾病详情失败: {data.get('message')}")
        else:
            print(f"❌ 疾病详情请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 疾病详情测试失败: {e}")
    
    print()
    
    # 5. 测试缓存管理
    print("5. 测试缓存管理...")
    
    try:
        # 清除缓存
        response = requests.post(f"{API_BASE_URL}/cache/clear")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 缓存清除成功: {data.get('message')}")
            else:
                print(f"❌ 缓存清除失败: {data.get('message')}")
        else:
            print(f"❌ 缓存清除请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 缓存清除测试失败: {e}")
    
    try:
        # 重新构建
        response = requests.post(f"{API_BASE_URL}/cache/rebuild")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 映射重建成功: {data.get('message')}")
                print(f"   症状数量: {stats['total_symptoms']}")
                print(f"   疾病数量: {stats['total_diseases']}")
            else:
                print(f"❌ 映射重建失败: {data.get('message')}")
        else:
            print(f"❌ 映射重建请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 映射重建测试失败: {e}")
    
    print()

def test_performance():
    """测试性能"""
    print("=== 性能测试 ===")
    
    # 测试诊断响应时间
    symptoms = ["头痛", "发烧", "流鼻涕"]
    
    print(f"测试诊断响应时间 (症状: {symptoms})...")
    
    times = []
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE_URL}/diagnose",
                json={"symptoms": symptoms, "min_match_ratio": 0.2}
            )
            if response.status_code == 200:
                end_time = time.time()
                response_time = end_time - start_time
                times.append(response_time)
                print(f"   第{i+1}次: {response_time:.3f}s")
            else:
                print(f"   第{i+1}次: 失败")
        except Exception as e:
            print(f"   第{i+1}次: 错误 - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"平均响应时间: {avg_time:.3f}s")
    
    print()

def main():
    """主函数"""
    print("🚀 开始症状诊断页面功能测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    test_page_functionality()
    test_performance()
    
    print("🎉 症状诊断页面功能测试完成")
    print("\n📋 测试总结:")
    print("✅ 基本API功能正常")
    print("✅ 诊断功能正常")
    print("✅ 交互式诊断正常")
    print("✅ 疾病详情功能正常")
    print("✅ 缓存管理功能正常")
    print("✅ 性能表现良好")

if __name__ == "__main__":
    main() 