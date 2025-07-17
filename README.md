# 知识图谱可视化网站

一个基于Python Flask后端和React前端的知识图谱可视化系统，支持实体-关系-实体CSV文件的可视化展示。

## 项目特性

- 🔍 **CSV数据解析**: 支持实体-关系-实体格式的CSV文件导入
- 📊 **交互式可视化**: 基于D3.js和ForceGraph2D的动态图谱展示
- 🔎 **实体搜索**: 支持实体名称搜索和高亮显示
- 📤 **文件上传**: 支持在线上传CSV文件更新图谱数据
- 💾 **数据导出**: 支持将图谱数据导出为JSON格式
- 🎨 **响应式设计**: 适配桌面和移动设备的现代化界面

## 项目结构

```
knowledge_graph_app/
├── backend/                    # Python Flask后端
│   └── knowledge_graph_backend/
│       ├── src/
│       │   ├── routes/         # API路由
│       │   │   ├── user.py
│       │   │   └── knowledge_graph.py
│       │   ├── models/         # 数据模型
│       │   └── main.py         # 主入口文件
│       ├── venv/               # Python虚拟环境
│       ├── sample_data.csv     # 示例数据文件
│       └── requirements.txt    # Python依赖
└── frontend/                   # React前端
    └── knowledge-graph-frontend/
        ├── src/
        │   ├── components/     # React组件
        │   │   ├── ui/         # UI组件库
        │   │   └── KnowledgeGraph.jsx
        │   ├── App.jsx         # 主应用组件
        │   └── main.jsx        # 入口文件
        ├── public/             # 静态资源
        └── package.json        # 前端依赖
```

## 技术栈

### 后端
- **Python 3.11**: 主要编程语言
- **Flask**: Web框架
- **Flask-CORS**: 跨域资源共享支持
- **CSV**: 数据文件格式解析

### 前端
- **React 19**: 前端框架
- **Vite**: 构建工具
- **Tailwind CSS**: 样式框架
- **shadcn/ui**: UI组件库
- **D3.js**: 数据可视化库
- **react-force-graph-2d**: 图谱可视化组件
- **Lucide React**: 图标库

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 20+
- pnpm

### 后端启动

1. 进入后端目录：
```bash
cd backend/knowledge_graph_backend
```

2. 激活虚拟环境


3. 安装依赖（如需要）：
```bash
pip install -r requirements.txt
```

1. 启动后端服务：
```bash
python src/main.py
```

后端服务将在 `http://localhost:5000` 启动。

### 前端启动

1. 进入前端目录：
```bash
cd frontend/knowledge-graph-frontend
```

2. 安装依赖（如需要，如果无法启动，就删了所有环境重新安装）：
```bash
npm install -g pnpm
pnpm install
```

3. 启动开发服务器：
```bash
pnpm run dev --host
```

前端服务将在 `http://localhost:5173` 启动。

## API接口

### 获取图谱数据
```
GET /api/graph
```
返回当前图谱的节点和边数据。

### 上传CSV文件
```
POST /api/upload
```
上传CSV文件并返回解析后的图谱数据。

### 搜索实体
```
GET /api/search?q={query}
```
根据查询字符串搜索匹配的实体。

## CSV数据格式

系统支持以下格式的CSV文件：

```csv
实体1,关系,实体2
百日咳[疾病],一级科室分类,疾病
百日咳[疾病],二级科室分类,儿科
百日咳[疾病],三级科室分类,小儿内科
百日咳[疾病],医保疾病,否
百日咳[疾病],患病比例,0.50%
百日咳[疾病],易感人群,多见于小儿
百日咳[疾病],传染方式,呼吸道传播
```

每行包含三列：
- **第一列**: 源实体
- **第二列**: 关系类型
- **第三列**: 目标实体

## 使用说明

1. **查看图谱**: 启动应用后，系统会自动加载示例数据并显示知识图谱
2. **交互操作**: 
   - 点击节点查看详细信息
   - 拖拽节点调整位置
   - 滚轮缩放图谱
3. **搜索功能**: 在搜索框中输入关键词，匹配的实体会高亮显示
4. **上传数据**: 点击"上传CSV"按钮选择本地CSV文件更新图谱
5. **导出数据**: 点击"导出"按钮将当前图谱数据保存为JSON文件

## 部署说明

### 开发环境部署
按照"快速开始"部分的说明分别启动后端和前端服务。

### 生产环境部署
1. 构建前端：
```bash
cd frontend/knowledge-graph-frontend
pnpm run build
```

2. 将构建产物复制到后端静态目录：
```bash
cp -r dist/* ../backend/knowledge_graph_backend/src/static/
```

3. 启动后端服务：
```bash
cd backend/knowledge_graph_backend
source venv/bin/activate
python src/main.py
```

访问 `http://localhost:5000` 即可使用完整应用。

## 开发说明

### 添加新的API接口
在 `backend/knowledge_graph_backend/src/routes/knowledge_graph.py` 中添加新的路由函数。

### 修改前端界面
主要的可视化组件位于 `frontend/knowledge-graph-frontend/src/components/KnowledgeGraph.jsx`。

### 自定义样式
在 `frontend/knowledge-graph-frontend/src/App.css` 中添加自定义CSS样式。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

