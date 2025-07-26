@echo off
echo 正在重启医学知识图谱系统服务...

echo.
echo 1. 停止现有服务...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo 2. 启动后端服务...
cd backend\knowledge_graph_backend
start "后端服务" cmd /k "python src/main.py"

echo.
echo 3. 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo.
echo 4. 启动前端服务...
cd ..\..\frontend\knowledge-graph-frontend
start "前端服务" cmd /k "npm run dev"

echo.
echo 服务启动完成！
echo 后端服务地址: http://localhost:8080
echo 前端服务地址: http://localhost:5174
echo 外部访问地址: http://100.71.94.3:5174
echo.
echo 请等待几秒钟让服务完全启动...
pause 