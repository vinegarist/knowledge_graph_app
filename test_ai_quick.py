import requests
import json

print("快速测试AI诊断功能...")

try:
    # 测试基本诊断
    response = requests.post(
        "http://localhost:5000/api/ai-symptom-diagnosis/diagnose",
        json={"symptoms": ["发烧", "流鼻涕"]},
        timeout=60
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ AI诊断成功!")
        print(f"症状: {data.get('data', {}).get('symptoms', [])}")
        print(f"疾病数量: {data.get('data', {}).get('disease_count', 0)}")
        
        # 显示AI诊断分析的前100个字符
        ai_diagnosis = data.get('data', {}).get('ai_diagnosis', '')
        if ai_diagnosis:
            print(f"AI诊断分析: {ai_diagnosis[:100]}...")
        else:
            print("AI诊断分析: 空")
            
    else:
        print(f"❌ 请求失败: {response.text}")
        
except Exception as e:
    print(f"❌ 错误: {e}") 