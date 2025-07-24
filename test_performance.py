#!/usr/bin/env python3
"""
性能测试脚本
"""
import requests
import json
import time
import statistics
from typing import List, Dict, Any

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'

def test_search_performance():
    """测试搜索性能"""
    print("=== 搜索性能测试 ===")
    
    # 测试查询列表
    test_queries = [
        "感冒应该吃什么？",
        "感冒吃什么药？",
        "感冒有什么症状？",
        "感冒需要做什么检查？",
        "如何预防感冒？",
        "感冒的并发症有哪些？",
        "发烧应该吃什么？",
        "咳嗽吃什么药？",
        "头痛有什么症状？",
        "高血压需要做什么检查？"
    ]
    
    performance_data = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试 {i}: {query} ---")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": query},
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 查询成功")
                    print(f"响应时间: {response_time:.3f}s")
                    print(f"相关实体数量: {len(data['data'].get('related_entities', []))}")
                    print(f"知识图谱覆盖: {data['data'].get('knowledge_graph_coverage', False)}")
                    
                    # 记录性能数据
                    performance_data.append({
                        'query': query,
                        'response_time': response_time,
                        'entities_count': len(data['data'].get('related_entities', [])),
                        'success': True
                    })
                    
                    # 显示搜索方法信息
                    entities = data['data'].get('related_entities', [])
                    if entities:
                        search_methods = set()
                        for entity in entities:
                            if 'search_method' in entity:
                                search_methods.add(entity['search_method'])
                        if search_methods:
                            print(f"搜索方法: {', '.join(search_methods)}")
                        
                else:
                    print(f"❌ 查询失败: {data.get('error')}")
                    performance_data.append({
                        'query': query,
                        'response_time': response_time,
                        'entities_count': 0,
                        'success': False,
                        'error': data.get('error')
                    })
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                performance_data.append({
                    'query': query,
                    'response_time': response_time,
                    'entities_count': 0,
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            performance_data.append({
                'query': query,
                'response_time': 0,
                'entities_count': 0,
                'success': False,
                'error': str(e)
            })
        
        # 等待一下再测试下一个查询
        time.sleep(0.5)
    
    # 分析性能数据
    print("\n=== 性能分析 ===")
    
    successful_queries = [p for p in performance_data if p['success']]
    failed_queries = [p for p in performance_data if not p['success']]
    
    if successful_queries:
        response_times = [p['response_time'] for p in successful_queries]
        entity_counts = [p['entities_count'] for p in successful_queries]
        
        print(f"成功查询数量: {len(successful_queries)}")
        print(f"失败查询数量: {len(failed_queries)}")
        print(f"平均响应时间: {statistics.mean(response_times):.3f}s")
        print(f"最快响应时间: {min(response_times):.3f}s")
        print(f"最慢响应时间: {max(response_times):.3f}s")
        print(f"响应时间标准差: {statistics.stdev(response_times):.3f}s")
        print(f"平均实体数量: {statistics.mean(entity_counts):.1f}")
        
        # 性能评级
        avg_time = statistics.mean(response_times)
        if avg_time < 0.5:
            rating = "优秀"
        elif avg_time < 1.0:
            rating = "良好"
        elif avg_time < 2.0:
            rating = "一般"
        else:
            rating = "需要优化"
        
        print(f"性能评级: {rating}")
        
        # 显示最慢的查询
        slowest_queries = sorted(successful_queries, key=lambda x: x['response_time'], reverse=True)[:3]
        print("\n最慢的3个查询:")
        for i, query_data in enumerate(slowest_queries, 1):
            print(f"  {i}. {query_data['query']} - {query_data['response_time']:.3f}s")
    
    if failed_queries:
        print(f"\n失败的查询:")
        for query_data in failed_queries:
            print(f"  - {query_data['query']}: {query_data.get('error', '未知错误')}")

def test_cache_performance():
    """测试缓存性能"""
    print("\n=== 缓存性能测试 ===")
    
    # 测试相同查询的缓存效果
    query = "感冒应该吃什么？"
    
    print(f"测试查询: {query}")
    
    # 第一次查询（冷启动）
    print("\n--- 第一次查询（冷启动）---")
    try:
        start_time = time.time()
        response1 = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": query},
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        time1 = end_time - start_time
        
        if response1.status_code == 200:
            data1 = response1.json()
            if data1.get('success'):
                print(f"响应时间: {time1:.3f}s")
                print(f"实体数量: {len(data1['data'].get('related_entities', []))}")
            else:
                print(f"查询失败: {data1.get('error')}")
        else:
            print(f"HTTP错误: {response1.status_code}")
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return
    
    # 等待一下
    time.sleep(1)
    
    # 第二次查询（缓存）
    print("\n--- 第二次查询（缓存）---")
    try:
        start_time = time.time()
        response2 = requests.post(
            f"{API_BASE_URL}/ai/chat",
            json={"question": query},
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        time2 = end_time - start_time
        
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get('success'):
                print(f"响应时间: {time2:.3f}s")
                print(f"实体数量: {len(data2['data'].get('related_entities', []))}")
                
                # 计算性能提升
                if time1 > 0:
                    improvement = ((time1 - time2) / time1) * 100
                    print(f"性能提升: {improvement:.1f}%")
                    
                    if improvement > 20:
                        print("✅ 缓存效果显著")
                    elif improvement > 10:
                        print("✅ 缓存效果良好")
                    else:
                        print("⚠️ 缓存效果有限")
            else:
                print(f"查询失败: {data2.get('error')}")
        else:
            print(f"HTTP错误: {response2.status_code}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_concurrent_performance():
    """测试并发性能"""
    print("\n=== 并发性能测试 ===")
    
    # 并发查询测试
    queries = [
        "感冒应该吃什么？",
        "感冒吃什么药？",
        "感冒有什么症状？",
        "发烧应该吃什么？",
        "咳嗽吃什么药？"
    ]
    
    print(f"并发测试 {len(queries)} 个查询...")
    
    start_time = time.time()
    
    # 使用线程池进行并发请求
    import concurrent.futures
    
    def make_request(query):
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"question": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'query': query,
                    'success': data.get('success', False),
                    'entities_count': len(data['data'].get('related_entities', [])) if data.get('success') else 0
                }
            else:
                return {
                    'query': query,
                    'success': False,
                    'entities_count': 0
                }
        except Exception as e:
            return {
                'query': query,
                'success': False,
                'entities_count': 0,
                'error': str(e)
            }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, query) for query in queries]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"并发总耗时: {total_time:.3f}s")
    print(f"平均每个查询: {total_time / len(queries):.3f}s")
    
    successful = [r for r in results if r['success']]
    print(f"成功查询: {len(successful)}/{len(queries)}")
    
    if successful:
        avg_entities = statistics.mean([r['entities_count'] for r in successful])
        print(f"平均实体数量: {avg_entities:.1f}")

if __name__ == "__main__":
    print("开始性能测试...")
    
    # 测试搜索性能
    test_search_performance()
    
    # 测试缓存性能
    test_cache_performance()
    
    # 测试并发性能
    test_concurrent_performance()
    
    print("\n性能测试完成！") 