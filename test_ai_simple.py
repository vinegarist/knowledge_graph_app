#!/usr/bin/env python3
"""
简单的AI诊断测试
"""

import requests
import time

def test_ai_diagnosis():
    """测试AI诊断"""
    print("测试AI诊断功能...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/ai-symptom-diagnosis/diagnose",
            json={"symptoms": ["咳嗽", "发热"]},
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    print("开始测试...")
    time.sleep(2)
    test_ai_diagnosis()
    print("测试完成") 