#!/usr/bin/env python3
"""
测试AI助手来源功能的脚本
"""
import requests
import json

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

def test_ai_chat():
    """测试AI聊天功能"""
    print("=== 测试AI聊天功能 ===")
    
    # 测试问题
    test_question = "感冒的症状有哪些？"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": test_question},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ AI回答成功")
                print(f"问题: {test_question}")
                print(f"回答: {data['data']['answer'][:100]}...")
                print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                print(f"来源数据: {json.dumps(data['data'].get('sources', {}), indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ AI回答失败: {data.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_entity_search():
    """测试实体搜索功能"""
    print("\n=== 测试实体搜索功能 ===")
    
    # 测试搜索
    test_query = "感冒"
    
    try:
        response = requests.get(f"{API_BASE_URL}/ai/search?q={test_query}&limit=5")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 实体搜索成功")
                print(f"查询: {test_query}")
                print(f"结果数量: {len(data['data'].get('results', []))}")
                for i, result in enumerate(data['data'].get('results', [])[:3]):
                    print(f"  {i+1}. {result.get('label', 'N/A')} (ID: {result.get('id', 'N/A')})")
            else:
                print(f"❌ 实体搜索失败: {data.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_ai_status():
    """测试AI状态"""
    print("\n=== 测试AI状态 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/ai/status")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ AI状态正常")
                status_data = data.get('data', {})
                print(f"图谱统计: {status_data.get('graph_stats', {})}")
                print(f"聊天历史数量: {status_data.get('chat_history_count', 0)}")
                print(f"当前来源数量: {status_data.get('current_sources_count', 0)}")
            else:
                print(f"❌ AI状态异常: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    print("开始测试AI助手来源功能...")
    
    # 测试AI状态
    test_ai_status()
    
    # 测试实体搜索
    test_entity_search()
    
    # 测试AI聊天
    test_ai_chat()
    
    print("\n测试完成！") 