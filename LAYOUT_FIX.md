# AI助手布局修复说明

## 问题描述

当AI回答文字过长时，右侧的来源区域会被遮挡，导致用户无法看到相关的实体信息。

## 问题原因

1. **文字宽度限制不当**：AI回答的`max-w-[80%]`设置可能导致文字换行过多
2. **布局溢出**：聊天区域没有正确的溢出处理
3. **文字换行问题**：长文字没有正确的换行处理

## 修复内容

### 1. 调整消息宽度限制

**修改前**：
```jsx
<div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
```

**修改后**：
```jsx
<div className={`${message.type === 'user' ? 'max-w-[70%]' : 'max-w-[75%]'} ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
```

- 用户消息：从80%减少到70%
- AI消息：从80%减少到75%
- 为右侧来源区域留出更多空间

### 2. 改进文字处理

**修改前**：
```jsx
<div className="whitespace-pre-wrap">{message.content}</div>
```

**修改后**：
```jsx
<div className="whitespace-pre-wrap break-words max-w-full overflow-hidden">{message.content}</div>
```

- 添加`break-words`：强制长单词换行
- 添加`max-w-full`：确保不超过容器宽度
- 添加`overflow-hidden`：防止内容溢出

### 3. 改进布局结构

**聊天区域**：
```jsx
<div className="flex-1 flex flex-col min-h-0 overflow-hidden">
```

**来源区域**：
```jsx
<div className="w-80 border-l bg-gray-50 flex flex-col flex-shrink-0 overflow-hidden">
```

- 添加`overflow-hidden`：防止内容溢出
- 确保固定宽度：`w-80`（320px）
- 使用`flex-shrink-0`：防止被压缩

## 测试方法

### 1. 使用测试页面
打开`test_layout.html`文件，查看布局效果：
```bash
# 在浏览器中打开
open test_layout.html
```

### 2. 实际测试
1. 启动前端应用
2. 在AI助手中提问一个会产生长回答的问题
3. 检查右侧来源区域是否仍然可见
4. 验证文字是否正确换行

### 3. 测试用例

**长回答测试**：
- "请详细解释感冒的病因、症状、诊断和治疗方法"
- "高血压的并发症有哪些？请详细说明"
- "糖尿病的预防措施有哪些？请提供全面的建议"

**预期结果**：
- AI回答正确换行，不会超出容器
- 右侧来源区域始终可见
- 布局保持稳定，不会出现遮挡

## 技术细节

### CSS类说明

- `whitespace-pre-wrap`：保留换行符和空格，允许自动换行
- `break-words`：强制长单词换行
- `overflow-hidden`：隐藏溢出内容
- `flex-shrink-0`：防止flex项目被压缩
- `min-h-0`：允许flex项目收缩到内容高度以下

### 布局结构

```
容器 (h-full flex flex-col)
├── 头部 (flex-shrink-0)
├── 主体 (flex-1 flex)
    ├── 聊天区域 (flex-1 flex flex-col)
    │   ├── 消息列表 (flex-1 overflow-y-auto)
    │   └── 输入区域 (flex-shrink-0)
    └── 来源区域 (w-80 flex-shrink-0)
        ├── 来源标题 (flex-shrink-0)
        └── 来源列表 (flex-1 overflow-y-auto)
```

## 注意事项

1. **响应式设计**：当前修复主要针对桌面布局，移动端可能需要额外调整
2. **文字长度**：虽然修复了布局问题，但过长的回答仍可能影响用户体验
3. **性能考虑**：长文字可能影响渲染性能，建议在AI回答中添加长度限制

## 后续优化建议

1. **添加文字长度限制**：在AI回答中添加最大字符数限制
2. **实现响应式布局**：为移动端设备优化布局
3. **添加展开/收起功能**：对于很长的回答，提供展开/收起选项
4. **优化滚动体验**：改进长回答的滚动体验 