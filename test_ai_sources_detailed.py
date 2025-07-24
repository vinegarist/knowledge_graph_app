#!/usr/bin/env python3
"""
详细测试AI助手来源功能的脚本
"""
import requests
import json
import time

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

def test_ai_chat_detailed():
    """详细测试AI聊天功能"""
    print("=== 详细测试AI聊天功能 ===")
    
    # 测试问题列表
    test_questions = [
        "感冒的症状有哪些？",
        "高血压的治疗方法",
        "糖尿病的并发症",
        "不存在的疾病测试",  # 测试没有相关实体的情况
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- 测试 {i}: {question} ---")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ AI回答成功")
                    print(f"问题: {question}")
                    print(f"回答长度: {len(data['data']['answer'])} 字符")
                    print(f"回答前100字符: {data['data']['answer'][:100]}...")
                    print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                    print(f"知识图谱覆盖: {data['data'].get('knowledge_graph_coverage', False)}")
                    
                    # 检查来源数据
                    sources = data['data'].get('sources', {})
                    print(f"来源数据结构: {list(sources.keys()) if isinstance(sources, dict) else 'Not a dict'}")
                    print(f"来源数组长度: {len(sources.get('sources', []))}")
                    print(f"当前页: {sources.get('current_page', 'N/A')}")
                    print(f"总页数: {sources.get('total_pages', 'N/A')}")
                    
                    # 显示前3个相关实体
                    entities = data['data'].get('related_entities', [])
                    if entities:
                        print("相关实体:")
                        for j, entity in enumerate(entities[:3], 1):
                            print(f"  {j}. {entity.get('label', 'N/A')} (ID: {entity.get('id', 'N/A')}, 匹配类型: {entity.get('match_type', 'N/A')})")
                    else:
                        print("没有找到相关实体")
                        
                else:
                    print(f"❌ AI回答失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        # 等待一下再测试下一个问题
        time.sleep(1)

def test_entity_search_detailed():
    """详细测试实体搜索功能"""
    print("\n=== 详细测试实体搜索功能 ===")
    
    # 测试搜索列表
    test_queries = [
        "感冒",
        "高血压", 
        "糖尿病",
        "不存在的疾病",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 搜索测试 {i}: {query} ---")
        
        try:
            response = requests.get(f"{API_BASE_URL}/ai/search?q={query}&limit=5")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 实体搜索成功")
                    print(f"查询: {query}")
                    results = data['data'].get('results', [])
                    print(f"结果数量: {len(results)}")
                    
                    for j, result in enumerate(results[:3], 1):
                        print(f"  {j}. {result.get('label', 'N/A')} (ID: {result.get('id', 'N/A')}, 匹配类型: {result.get('match_type', 'N/A')}, 分数: {result.get('match_score', 'N/A')})")
                        
                else:
                    print(f"❌ 实体搜索失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        time.sleep(1)

def test_source_pagination():
    """测试来源分页功能"""
    print("\n=== 测试来源分页功能 ===")
    
    # 先发送一个问题获取来源
    try:
        response = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": "感冒的症状有哪些？"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data['data'].get('sources', {}).get('sources'):
                print("✅ 获取到来源数据，测试分页...")
                
                # 测试下一页
                pagination_response = requests.post(
                    f"{API_BASE_URL}/ai/sources/page",
                    json={"action": "next"},
                    headers={"Content-Type": "application/json"}
                )
                
                if pagination_response.status_code == 200:
                    pagination_data = pagination_response.json()
                    if pagination_data.get('success'):
                        print(f"✅ 分页成功")
                        print(f"分页数据: {json.dumps(pagination_data['data'], indent=2, ensure_ascii=False)}")
                    else:
                        print(f"❌ 分页失败: {pagination_data.get('error')}")
                else:
                    print(f"❌ 分页HTTP错误: {pagination_response.status_code}")
            else:
                print("❌ 没有获取到来源数据，无法测试分页")
        else:
            print(f"❌ 获取来源数据失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 分页测试失败: {str(e)}")

if __name__ == "__main__":
    print("开始详细测试AI助手来源功能...")
    
    # 测试AI聊天
    test_ai_chat_detailed()
    
    # 测试实体搜索
    test_entity_search_detailed()
    
    # 测试来源分页
    test_source_pagination()
    
    print("\n详细测试完成！") 