#!/usr/bin/env python3
"""
启动后端服务器并测试AI助手来源功能的脚本
"""
import subprocess
import time
import requests
import sys
import os

def start_backend_server():
    """启动后端服务器"""
    print("正在启动后端服务器...")
    
    # 切换到后端目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend', 'knowledge_graph_backend')
    os.chdir(backend_dir)
    
    # 启动服务器
    try:
        process = subprocess.Popen(
            [sys.executable, 'src/main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(10)
        
        # 检查服务器是否启动
        try:
            response = requests.get('http://localhost:5000/api/ai/status', timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务器启动成功！")
                return process
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ 无法连接到服务器")
            return None
            
    except Exception as e:
        print(f"❌ 启动服务器失败: {str(e)}")
        return None

def run_tests():
    """运行测试"""
    print("\n开始运行测试...")
    
    # 切换到项目根目录
    os.chdir(os.path.dirname(__file__))
    
    # 运行详细测试
    try:
        result = subprocess.run([sys.executable, 'test_ai_sources_detailed.py'], 
                              capture_output=True, text=True)
        print("测试输出:")
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
    except Exception as e:
        print(f"运行测试失败: {str(e)}")

def main():
    """主函数"""
    print("=== AI助手来源功能测试 ===")
    
    # 启动服务器
    server_process = start_backend_server()
    
    if server_process:
        try:
            # 运行测试
            run_tests()
        finally:
            # 停止服务器
            print("\n正在停止服务器...")
            server_process.terminate()
            server_process.wait()
            print("服务器已停止")
    else:
        print("无法启动服务器，测试终止")

if __name__ == "__main__":
    main() 