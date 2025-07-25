# 部署指南

本文档详细说明了知识图谱可视化网站的部署方法。

## 部署方式

### 方式一：开发环境部署（推荐用于开发和测试）

#### 1. 启动后端服务

```bash
# 进入后端目录
cd backend/knowledge_graph_backend

# 激活虚拟环境
source venv/bin/activate

# 启动Flask服务
python src/main.py
```

后端服务将在 `http://localhost:5000` 启动。

#### 2. 启动前端服务

```bash
# 新开一个终端，进入前端目录
cd frontend/knowledge-graph-frontend

# 启动开发服务器
pnpm run dev --host
```

前端服务将在 `http://localhost:5174` 启动。

#### 3. 访问应用

打开浏览器访问 `http://localhost:5174` 即可使用应用。

### 方式二：生产环境部署

#### 1. 构建前端

```bash
cd frontend/knowledge-graph-frontend
pnpm run build
```

#### 2. 复制前端构建产物到后端

```bash
# 确保后端静态目录存在
mkdir -p ../backend/knowledge_graph_backend/src/static

# 复制构建产物
cp -r dist/* ../backend/knowledge_graph_backend/src/static/
```

#### 3. 启动后端服务

```bash
cd ../backend/knowledge_graph_backend
source venv/bin/activate
python src/main.py
```

#### 4. 访问应用

打开浏览器访问 `http://localhost:5000` 即可使用完整应用。

## 环境要求

### 系统要求
- 操作系统：Linux/macOS/Windows
- Python 3.11+
- Node.js 20+
- pnpm 包管理器

### Python依赖
```
blinker==1.9.0
click==8.2.1
Flask==3.1.1
Flask-Cors==6.0.0
Flask-SQLAlchemy==3.1.1
greenlet==3.1.1
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
SQLAlchemy==2.0.36
typing_extensions==4.12.2
Werkzeug==3.1.3
```

### 前端依赖
主要依赖包括：
- React 19
- Vite
- Tailwind CSS
- D3.js
- react-force-graph-2d
- shadcn/ui

## 配置说明

### 后端配置

#### 端口配置
在 `backend/knowledge_graph_backend/src/main.py` 中修改：
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

#### CORS配置
CORS已在 `src/main.py` 中配置，允许所有来源的跨域请求：
```python
from flask_cors import CORS
CORS(app)
```

#### 数据文件路径
示例数据文件位于 `backend/knowledge_graph_backend/sample_data.csv`，可以修改此文件来更改默认数据。

### 前端配置

#### API基础URL
前端使用相对路径调用API，无需额外配置。如需修改，可在组件中更改API调用路径。

#### 开发服务器配置
在 `frontend/knowledge-graph-frontend/vite.config.js` 中可以配置开发服务器选项。

## 故障排除

### 常见问题

#### 1. 后端启动失败
- 检查Python版本是否为3.11+
- 确认虚拟环境已激活
- 检查依赖是否正确安装：`pip install -r requirements.txt`

#### 2. 前端启动失败
- 检查Node.js版本是否为20+
- 确认pnpm已安装：`npm install -g pnpm`
- 重新安装依赖：`pnpm install`

#### 3. API调用失败
- 确认后端服务正在运行
- 检查CORS配置是否正确
- 查看浏览器控制台错误信息

#### 4. 图谱不显示
- 检查CSV数据格式是否正确
- 确认API返回数据格式正确
- 查看浏览器控制台是否有JavaScript错误

#### 5. 文件上传失败
- 确认上传的是CSV格式文件
- 检查文件大小是否过大
- 确认后端有写入权限

### 日志查看

#### 后端日志
Flask应用的日志会直接输出到终端。

#### 前端日志
打开浏览器开发者工具查看控制台日志。

## 性能优化

### 后端优化
1. 使用生产级WSGI服务器（如Gunicorn）替代Flask开发服务器
2. 添加数据缓存机制
3. 优化CSV解析性能

### 前端优化
1. 启用生产构建：`pnpm run build`
2. 使用CDN加速静态资源
3. 实现图谱数据的懒加载

## 安全考虑

1. **文件上传安全**：限制上传文件类型和大小
2. **输入验证**：对用户输入进行验证和清理
3. **HTTPS**：生产环境建议使用HTTPS
4. **访问控制**：根据需要添加用户认证和授权

## 扩展功能

### 可能的扩展方向
1. 添加用户认证系统
2. 支持更多数据格式（JSON、XML等）
3. 实现图谱数据的持久化存储
4. 添加图谱分析功能（路径查找、社区发现等）
5. 支持大规模图谱的分页加载
6. 添加图谱编辑功能

### 技术栈升级
1. 后端可考虑使用FastAPI替代Flask
2. 前端可添加状态管理（Redux、Zustand等）
3. 数据库可使用PostgreSQL或Neo4j
4. 部署可使用Docker容器化

