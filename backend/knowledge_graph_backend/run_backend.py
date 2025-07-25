#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务启动脚本
修复导入路径问题
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# 切换到src目录
os.chdir(src_path)

if __name__ == '__main__':
    try:
        # 导入并运行Flask应用
        from main import app
        print("[启动] 后端服务正在启动...")
        print("[启动] 服务地址: http://localhost:8080")
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        import traceback
        traceback.print_exc()