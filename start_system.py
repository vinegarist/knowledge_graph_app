#!/usr/bin/env python3
"""
知识图谱AI助手系统启动脚本
"""
import os
import sys
import subprocess
import time
import requests
import signal
import threading
from pathlib import Path

def check_port(port, service_name=None, host='localhost'):
    """检查端口是否被占用"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            if result == 0:
                if service_name:
                    print(f"✓ {service_name} 正在端口 {port} 上运行")
                return True
            else:
                if service_name:
                    print(f"✗ {service_name} 未在端口 {port} 上运行")
                return False
    except Exception as e:
        if service_name:
            print(f"✗ 检查端口 {port} 时出错: {e}")
        return False

def check_ollama_service():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_backend_service():
    """检查后端服务是否运行"""
    try:
        response = requests.get('http://localhost:5000/api/ai/status', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """启动Ollama服务"""
    print("🚀 启动Ollama服务...")
    
    if check_ollama_service():
        print("✅ Ollama服务已在运行")
        return None
    
    try:
        # 尝试启动Ollama
        process = subprocess.Popen(['ollama', 'serve'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        # 等待服务启动
        for i in range(30):
            if check_ollama_service():
                print("✅ Ollama服务启动成功")
                return process
            time.sleep(1)
            print(f"⏳ 等待Ollama服务启动... ({i+1}/30)")
        
        print("❌ Ollama服务启动超时")
        return None
    except FileNotFoundError:
        print("❌ 未找到Ollama，请先安装：")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        return None
    except Exception as e:
        print(f"❌ 启动Ollama失败: {e}")
        return None

def start_backend():
    """启动后端服务"""
    print("\n=== 启动后端服务 ===")
    
    # 检查后端是否已经在运行
    if check_port(8080, "后端服务"):
        print("后端服务已在运行，跳过启动")
        return True
    
    backend_dir = Path(__file__).parent / "backend" / "knowledge_graph_backend"
    
    if not backend_dir.exists():
        print(f"❌ 后端目录不存在: {backend_dir}")
        return None
    
    try:
        # 切换到后端目录并启动
        process = subprocess.Popen([sys.executable, "src/main.py"], 
                                   cwd=backend_dir,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        # 等待服务启动
        for i in range(30):
            if check_port(8080):
                print("✅ 后端服务启动成功")
                return process
            time.sleep(1)
            print(f"⏳ 等待后端服务启动... ({i+1}/30)")
        
        print("❌ 后端服务启动超时")
        return None
    except Exception as e:
        print(f"❌ 启动后端失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    
    if check_port(5174):  # Vite默认端口
        print("✅ 前端服务已在运行")
        return None
    
    frontend_dir = Path(__file__).parent / "frontend" / "knowledge-graph-frontend"
    
    if not frontend_dir.exists():
        print(f"❌ 前端目录不存在: {frontend_dir}")
        return None
    
    try:
        # 检查是否已安装依赖
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("📦 安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # 启动前端开发服务器
        process = subprocess.Popen(["npm", "run", "dev"], 
                                   cwd=frontend_dir,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        # 等待服务启动
        for i in range(30):
            if check_port(5174):
                print("✅ 前端服务启动成功")
                return process
            time.sleep(1)
            print(f"⏳ 等待前端服务启动... ({i+1}/30)")
        
        print("❌ 前端服务启动超时")
        return None
    except FileNotFoundError:
        print("❌ 未找到npm，请先安装Node.js")
        return None
    except Exception as e:
        print(f"❌ 启动前端失败: {e}")
        return None

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查系统依赖...")
    
    # 检查Python依赖
    required_packages = ['flask', 'flask_cors', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少Python包: {missing_packages}")
        print("💡 请运行: pip install -r backend/knowledge_graph_backend/requirements_ai.txt")
        return False
    
    # 检查Node.js
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
    except:
        print("❌ 未找到Node.js，请先安装")
        return False
    
    print("✅ 依赖检查通过")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🏥 知识图谱AI助手系统启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    processes = []
    
    try:
        # 启动Ollama服务
        ollama_process = start_ollama()
        if ollama_process:
            processes.append(ollama_process)
        
        # 启动后端服务
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
        
        # 启动前端服务
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        print("\n" + "=" * 60)
        print("🎉 系统启动完成！")
        print("=" * 60)
        print("\n=== 系统状态检查 ===")
        ollama_running = check_port(11434, "Ollama服务")
        backend_running = check_port(8080, "后端服务")
        frontend_running = check_port(5174, "前端服务")
        print("📊 知识图谱系统: http://localhost:5174")
        print("🤖 AI助手API: http://localhost:8080/api/ai/status")
        print("🛠️ Ollama服务: http://localhost:11434")
        print("=" * 60)
        print("💡 使用说明:")
        print("   - 在浏览器中访问 http://localhost:5174")
        print("   - 点击顶部'AI助手'标签使用AI功能")
        print("   - 按Ctrl+C退出所有服务")
        print("=" * 60)
        
        # 等待用户中断
        def signal_handler(sig, frame):
            print("\n🛑 正在关闭服务...")
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            print("✅ 所有服务已关闭")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在关闭服务...")
    except Exception as e:
        print(f"\n❌ 启动过程中出错: {e}")
    finally:
        # 清理进程
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass

if __name__ == "__main__":
    main()