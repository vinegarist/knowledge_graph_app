# 网络错误问题修复说明

## 问题描述
当从 `http://100.71.94.3:5174` 访问系统时，登录功能出现"网络错误，请稍后重试"的问题，但从 `http://localhost:5174` 访问时正常。

## 问题原因
1. **CORS配置限制**：后端CORS配置只允许特定的本地地址访问
2. **API URL硬编码**：前端代码中所有API调用都硬编码为 `http://localhost:8080`

## 修复方案

### 1. 后端CORS配置修复
**文件**: `backend/knowledge_graph_backend/src/main.py`

**修改前**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174", "http://127.0.0.1:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**修改后**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 允许所有来源
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 2. 前端API配置动态化
**新增文件**: `frontend/knowledge-graph-frontend/src/config/api.js`

```javascript
// API配置文件
const getApiBaseUrl = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  // 如果是本地开发环境
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8080/api';
  }
  
  // 如果是其他IP地址，使用相同的IP地址但端口为8080
  return `${protocol}//${hostname}:8080/api`;
};

export const API_BASE_URL = getApiBaseUrl();
```

### 3. 组件API调用更新
更新了以下组件的API调用：

- `LoginPage.jsx` - 登录注册功能
- `App.jsx` - 主应用组件
- `KnowledgeGraph.jsx` - 知识图谱组件
- `AIAssistant.jsx` - AI助手组件
- `SymptomDiagnosis.jsx` - 症状诊断组件
- `SymptomDiagnosisPage.jsx` - 症状诊断页面
- `AISymptomDiagnosisPage.jsx` - AI症状诊断页面

## 修复效果
1. **跨域问题解决**：允许从任何IP地址访问系统
2. **API调用正确**：前端会根据当前访问的域名自动调整API地址
3. **网络错误消除**：登录功能在所有访问地址下都能正常工作

## 使用方法

### 方法1: 使用重启脚本
```bash
# 在项目根目录运行
restart_services.bat
```

### 方法2: 手动重启
```bash
# 1. 停止现有服务
# 2. 启动后端
cd backend/knowledge_graph_backend
python src/main.py

# 3. 启动前端
cd frontend/knowledge-graph-frontend
npm run dev
```

## 访问地址
- 本地访问: http://localhost:5174
- 外部访问: http://100.71.94.3:5174
- 后端API: http://100.71.94.3:8080

## 注意事项
1. 确保防火墙允许8080端口访问
2. 确保后端服务绑定到 `0.0.0.0:8080`
3. 确保前端服务绑定到 `0.0.0.0:5174`

## 安全建议
在生产环境中，建议：
1. 限制CORS origins为特定的域名
2. 使用HTTPS协议
3. 配置适当的防火墙规则 