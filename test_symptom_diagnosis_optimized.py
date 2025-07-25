#!/usr/bin/env python3
"""
优化后的症状诊断系统测试脚本
测试缓存功能和性能优化
"""

import requests
import json
import time
import os

# API基础URL
API_BASE_URL = "http://localhost:5000/api/symptom-diagnosis"

def test_cache_performance():
    """测试缓存性能"""
    print("=== 测试缓存性能 ===")
    
    # 第一次启动（构建缓存）
    print("第一次启动 - 构建缓存...")
    start_time = time.time()
    
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 统计信息获取成功")
                print(f"症状总数: {stats['total_symptoms']}")
                print(f"疾病总数: {stats['total_diseases']}")
                print(f"缓存状态: {'启用' if stats['cache_enabled'] else '禁用'}")
                print(f"缓存文件: {stats['cache_file']}")
            else:
                print(f"❌ 获取统计信息失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    first_load_time = time.time() - start_time
    print(f"第一次加载耗时: {first_load_time:.3f}s")
    
    # 等待一下
    time.sleep(2)
    
    # 第二次启动（从缓存加载）
    print("\n第二次启动 - 从缓存加载...")
    start_time = time.time()
    
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 统计信息获取成功")
                print(f"症状总数: {stats['total_symptoms']}")
                print(f"疾病总数: {stats['total_diseases']}")
                print(f"缓存状态: {'启用' if stats['cache_enabled'] else '禁用'}")
                print(f"缓存文件: {stats['cache_file']}")
            else:
                print(f"❌ 获取统计信息失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    second_load_time = time.time() - start_time
    print(f"第二次加载耗时: {second_load_time:.3f}s")
    
    # 计算性能提升
    if first_load_time > 0 and second_load_time > 0:
        improvement = (first_load_time - second_load_time) / first_load_time * 100
        print(f"性能提升: {improvement:.1f}%")
    
    print()

def test_cache_management():
    """测试缓存管理功能"""
    print("=== 测试缓存管理功能 ===")
    
    # 1. 获取当前统计信息
    print("1. 获取当前统计信息...")
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print(f"✅ 当前缓存文件: {stats['cache_file']}")
            else:
                print(f"❌ 获取统计信息失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 2. 清除缓存
    print("\n2. 清除缓存...")
    try:
        response = requests.post(f"{API_BASE_URL}/cache/clear")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 缓存清除成功: {data.get('message')}")
            else:
                print(f"❌ 缓存清除失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 3. 重新构建映射
    print("\n3. 重新构建映射...")
    start_time = time.time()
    try:
        response = requests.post(f"{API_BASE_URL}/cache/rebuild")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                rebuild_time = time.time() - start_time
                print(f"✅ 映射重建成功: {data.get('message')}")
                print(f"重建耗时: {rebuild_time:.3f}s")
                print(f"症状数量: {stats['total_symptoms']}")
                print(f"疾病数量: {stats['total_diseases']}")
            else:
                print(f"❌ 映射重建失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_diagnosis_with_cache():
    """测试带缓存的诊断功能"""
    print("=== 测试带缓存的诊断功能 ===")
    
    # 测试用例
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
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试 {test_case['name']}")
        print(f"症状: {test_case['symptoms']}")
        
        start_time = time.time()
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
                    diagnosis_time = time.time() - start_time
                    print(f"✅ 诊断成功，耗时: {diagnosis_time:.3f}s")
                    print(f"找到 {len(result.get('possible_diseases', []))} 个可能疾病")
                    
                    # 显示前3个结果
                    for j, disease in enumerate(result.get('possible_diseases', [])[:3]):
                        print(f"  {j+1}. {disease['disease']} (匹配度: {disease['match_ratio']:.1%})")
                else:
                    print(f"❌ 诊断失败: {data.get('message')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print()

def test_interactive_diagnosis_with_cache():
    """测试带缓存的交互式诊断"""
    print("=== 测试带缓存的交互式诊断 ===")
    
    initial_symptoms = ["咳嗽", "喉咙痛"]
    print(f"初始症状: {initial_symptoms}")
    
    try:
        # 开始交互式诊断
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/interactive/start",
            json={"symptoms": initial_symptoms}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                interactive_data = data['data']
                start_time_total = time.time() - start_time
                print(f"✅ 交互式诊断开始成功，耗时: {start_time_total:.3f}s")
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
                    
                    # 回答问题
                    answer_start_time = time.time()
                    response2 = requests.post(
                        f"{API_BASE_URL}/interactive/answer",
                        json={
                            "answers": answers,
                            "current_symptoms": interactive_data['current_symptoms']
                        }
                    )
                    
                    if response2.status_code == 200:
                        data2 = response.json()
                        if data2.get('success'):
                            result = data2['data']
                            answer_time = time.time() - answer_start_time
                            print(f"✅ 回答问题成功，耗时: {answer_time:.3f}s")
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

def check_cache_files():
    """检查缓存文件"""
    print("=== 检查缓存文件 ===")
    
    cache_dir = os.path.join(os.path.dirname(__file__), 'knowledge_graph_app', 'backend', 'knowledge_graph_backend', 'cache')
    
    if os.path.exists(cache_dir):
        print(f"缓存目录: {cache_dir}")
        files = os.listdir(cache_dir)
        for file in files:
            file_path = os.path.join(cache_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  {file}: {file_size} bytes")
    else:
        print("缓存目录不存在")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始优化后的症状诊断系统测试")
    print("=" * 60)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 运行所有测试
    check_cache_files()
    test_cache_performance()
    test_cache_management()
    test_diagnosis_with_cache()
    test_interactive_diagnosis_with_cache()
    
    print("🎉 优化后的症状诊断系统测试完成")

if __name__ == "__main__":
    main() 