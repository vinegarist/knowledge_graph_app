#!/usr/bin/env python3
"""
简单的症状诊断测试脚本
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:5000/api/symptom-diagnosis"

def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 1. 测试统计信息
    print("1. 测试统计信息...")
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()
    
    # 2. 测试症状列表
    print("2. 测试症状列表...")
    try:
        response = requests.get(f"{API_BASE_URL}/symptoms")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"症状数量: {data.get('data', {}).get('count', 0)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()
    
    # 3. 测试疾病列表
    print("3. 测试疾病列表...")
    try:
        response = requests.get(f"{API_BASE_URL}/diseases")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"疾病数量: {data.get('data', {}).get('count', 0)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()

def test_diagnosis():
    """测试诊断功能"""
    print("=== 测试诊断功能 ===")
    
    symptoms = ["头痛", "发烧"]
    print(f"症状: {symptoms}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose",
            json={"symptoms": symptoms, "min_match_ratio": 0.2}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"诊断成功: {data.get('success')}")
            if data.get('success'):
                result = data.get('data', {})
                print(f"可能疾病数量: {len(result.get('possible_diseases', []))}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()

def test_cache_management():
    """测试缓存管理"""
    print("=== 测试缓存管理 ===")
    
    # 1. 清除缓存
    print("1. 清除缓存...")
    try:
        response = requests.post(f"{API_BASE_URL}/cache/clear")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"清除结果: {data.get('message')}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()
    
    # 2. 重新构建
    print("2. 重新构建映射...")
    try:
        response = requests.post(f"{API_BASE_URL}/cache/rebuild")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"重建结果: {data.get('message')}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print()

def main():
    """主函数"""
    print("🚀 开始简单症状诊断测试")
    print("=" * 40)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    test_basic_functionality()
    test_diagnosis()
    test_cache_management()
    
    print("🎉 测试完成")

if __name__ == "__main__":
    main() 