#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端服务启动脚本
"""

import sys
import os

# 添加后端路径到系统路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'knowledge_graph_backend')
sys.path.insert(0, backend_path)

try:
    # 导入并启动Flask应用
    from src.main import app
    
    print("正在启动后端服务...")
    print(f"后端服务将在 http://localhost:8080 启动")
    print("按 Ctrl+C 停止服务")
    
    # 启动应用
    app.run(host='0.0.0.0', port=8080, debug=True)
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包")
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)