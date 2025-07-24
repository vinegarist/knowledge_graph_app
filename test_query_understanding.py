#!/usr/bin/env python3
"""
测试查询理解功能的脚本
"""
import requests
import json
import time

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

def test_query_understanding():
    """测试查询理解功能"""
    print("=== 测试查询理解功能 ===")
    
    # 测试查询列表
    test_queries = [
        # 饮食相关
        "感冒应该吃什么？",
        "感冒吃什么食物好？",
        "感冒的饮食建议",
        
        # 药物相关
        "感冒吃什么药？",
        "感冒用什么药物治疗？",
        "感冒的用药建议",
        
        # 症状相关
        "感冒有什么症状？",
        "感冒的表现有哪些？",
        "感冒的征兆",
        
        # 检查相关
        "感冒需要做什么检查？",
        "感冒的检查项目",
        "感冒的诊断方法",
        
        # 预防相关
        "如何预防感冒？",
        "感冒的预防措施",
        "避免感冒的方法",
        
        # 并发症相关
        "感冒的并发症有哪些？",
        "感冒会有什么后果？",
        "感冒的影响",
        
        # 非结构化查询
        "感冒是什么？",
        "感冒的原因",
        "感冒的治疗",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}: {query} ---")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 查询成功")
                    print(f"问题: {query}")
                    print(f"回答长度: {len(data['data']['answer'])} 字符")
                    print(f"回答前100字符: {data['data']['answer'][:100]}...")
                    print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                    print(f"知识图谱覆盖: {data['data'].get('knowledge_graph_coverage', False)}")
                    
                    # 显示相关实体
                    entities = data['data'].get('related_entities', [])
                    if entities:
                        print("相关实体:")
                        for j, entity in enumerate(entities[:3], 1):
                            relation_info = f", 关系: {entity.get('relation', 'N/A')}" if entity.get('relation') else ""
                            source_info = f", 来源疾病: {entity.get('source_disease', 'N/A')}" if entity.get('source_disease') else ""
                            print(f"  {j}. {entity.get('label', 'N/A')} (ID: {entity.get('id', 'N/A')}, 匹配类型: {entity.get('match_type', 'N/A')}{relation_info}{source_info})")
                    else:
                        print("没有找到相关实体")
                        
                else:
                    print(f"❌ 查询失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        # 等待一下再测试下一个查询
        time.sleep(1)

def test_specific_queries():
    """测试特定的查询场景"""
    print("\n=== 测试特定查询场景 ===")
    
    # 测试感冒饮食查询
    print("\n--- 测试感冒饮食查询 ---")
    try:
        response = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": "感冒应该吃什么？"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 感冒饮食查询成功")
                print(f"回答: {data['data']['answer'][:200]}...")
                
                # 检查是否找到了相关实体
                entities = data['data'].get('related_entities', [])
                if entities:
                    print("找到的相关实体:")
                    for entity in entities:
                        print(f"  - {entity.get('label')} (关系: {entity.get('relation', 'N/A')})")
                else:
                    print("没有找到相关实体")
            else:
                print(f"❌ 查询失败: {data.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    print("开始测试查询理解功能...")
    
    # 测试查询理解
    test_query_understanding()
    
    # 测试特定查询
    test_specific_queries()
    
    print("\n测试完成！") 