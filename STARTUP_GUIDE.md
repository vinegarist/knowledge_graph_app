# 医学知识图谱系统启动指南

## 系统修改说明

本次修改已完成以下功能：

### 1. 后端端口修改
- 后端服务端口从 `5000` 改为 `8080`
- 所有前端组件的API调用已更新为新端口

### 2. 登录注册功能
- 新增用户认证系统，支持JWT令牌
- 创建了登录注册页面 (`LoginPage.jsx`)
- 用户模型增加了密码哈希和认证功能
- 所有API接口现在需要认证访问

### 3. 知识图谱数据缓存
- 登录成功后自动加载知识图谱数据
- 数据缓存在前端状态中，提高访问速度

### 4. 前端服务器配置
- Vite配置为对外可访问 (`host: '0.0.0.0'`)
- 前端端口保持 `5174`

## 手动启动步骤

### 步骤1: 安装后端依赖
```bash
cd backend/knowledge_graph_backend
pip install -r requirements.txt
```

### 步骤2: 启动后端服务
```bash
cd backend/knowledge_graph_backend
python src/main.py
```
后端将在 http://localhost:8080 启动

### 步骤3: 安装前端依赖
```bash
cd frontend/knowledge-graph-frontend
npm install
```

### 步骤4: 启动前端服务
```bash
cd frontend/knowledge-graph-frontend
npm run dev
```
前端将在 http://localhost:5174 启动

## 使用说明

1. **首次访问**: 打开 http://localhost:5174，会看到登录页面
2. **注册账户**: 点击"注册"标签，填写用户名、邮箱和密码
3. **登录系统**: 使用注册的账户登录
4. **自动缓存**: 登录成功后，系统会自动加载知识图谱数据
5. **功能访问**: 登录后可以访问所有功能模块

## 新增API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/verify` - 验证令牌

### 认证要求
所有API请求现在需要在请求头中包含认证令牌：
```
Authorization: Bearer <your-jwt-token>
```

## 数据库
- 使用SQLite数据库存储用户信息
- 数据库文件：`knowledge_graph.db`
- 首次启动时会自动创建数据库表

## 安全特性
- 密码使用Werkzeug进行哈希加密
- JWT令牌24小时过期
- CORS配置限制访问来源
- 所有敏感操作需要认证

## 故障排除

### 端口冲突
如果端口被占用，请检查：
- 后端端口 8080 是否被其他服务占用
- 前端端口 5174 是否被其他服务占用

### 依赖问题
确保安装了所有必需的依赖：
- 后端：Flask, PyJWT, SQLAlchemy等
- 前端：React, Vite, Tailwind CSS等

### 数据库问题
如果遇到数据库错误，删除 `knowledge_graph.db` 文件重新启动后端服务。

## 开发说明

- 后端使用Flask框架，端口8080
- 前端使用React + Vite，端口5174
- 数据库使用SQLite
- 认证使用JWT令牌
- UI使用Tailwind CSS + shadcn/ui组件