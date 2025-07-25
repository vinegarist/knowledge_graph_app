#!/usr/bin/env python3
"""
调试AI诊断引擎初始化
"""

import requests
import time

def test_ai_engine_status():
    """测试AI诊断引擎状态"""
    print("=== 调试AI诊断引擎初始化 ===")
    
    # 1. 测试统计信息
    print("1. 测试AI诊断统计信息...")
    try:
        response = requests.get("http://localhost:5000/api/ai-symptom-diagnosis/statistics", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
            if data.get('success'):
                print("✅ AI诊断引擎已正确初始化")
            else:
                print(f"❌ AI诊断引擎初始化失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    # 2. 测试症状列表
    print("\n2. 测试症状列表...")
    try:
        response = requests.get("http://localhost:5000/api/ai-symptom-diagnosis/symptoms", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
        else:
            print(f"❌ 请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    # 3. 测试基本诊断
    print("\n3. 测试基本诊断...")
    try:
        response = requests.post(
            "http://localhost:5000/api/ai-symptom-diagnosis/diagnose",
            json={"symptoms": ["咳嗽"]},
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {data}")
        else:
            print(f"❌ 请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def test_backend_status():
    """测试后端服务状态"""
    print("\n=== 测试后端服务状态 ===")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"后端服务状态: {response.status_code}")
    except Exception as e:
        print(f"后端服务连接失败: {e}")

if __name__ == "__main__":
    print("🚀 开始调试AI诊断引擎...")
    time.sleep(3)
    
    test_backend_status()
    test_ai_engine_status()
    
    print("\n🎉 调试完成") 