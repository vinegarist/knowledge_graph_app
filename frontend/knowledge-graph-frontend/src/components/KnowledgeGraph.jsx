import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Search, Download, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { Slider } from "@/components/ui/slider";

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

const KnowledgeGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [maxNodes, setMaxNodes] = useState(100);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const graphRef = useRef();

  // 获取图谱数据
  const fetchGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/graph?max_nodes=${maxNodes}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      // 转换数据格式以适配ForceGraph2D
      const formattedData = {
        nodes: data.nodes.map(node => ({
          ...node,
          name: node.label,
          color: getNodeColor(node.label, node.level)
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relation,
          color: '#999'
        }))
      };
      setGraphData(formattedData);
    } catch (error) {
      console.error('获取图谱数据失败:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 根据节点类型和层级获取颜色
  const getNodeColor = (label, level) => {
    if (level === 1) {
      if (label.includes('[疾病]')) return '#ff6b6b';
      if (label.includes('科室')) return '#4ecdc4';
      if (label.includes('比例') || label.includes('%')) return '#45b7d1';
      if (label.includes('人群')) return '#96ceb4';
      if (label.includes('传播') || label.includes('方式')) return '#feca57';
      return '#a8e6cf';
    }
    // 二级节点使用较浅的颜色
    if (label.includes('[疾病]')) return '#ffb3b3';
    if (label.includes('科室')) return '#b3e6e6';
    if (label.includes('比例') || label.includes('%')) return '#b3e6ff';
    if (label.includes('人群')) return '#d9f2e6';
    if (label.includes('传播') || label.includes('方式')) return '#ffe6b3';
    return '#e6f2e6';
  };

  // 展开节点
  const expandNode = async (nodeId) => {
    if (expandedNodes.has(nodeId)) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/node/expand?id=${encodeURIComponent(nodeId)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }

      // 转换新节点和边的格式
      const newNodes = data.nodes.map(node => ({
        ...node,
        name: node.label,
        color: getNodeColor(node.label, node.level)
      }));
      const newLinks = data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        label: edge.relation,
        color: '#999'
      }));

      // 更新图数据，避免重复
      const existingNodeIds = new Set(graphData.nodes.map(n => n.id));
      const existingLinkIds = new Set(graphData.links.map(l => `${l.source}-${l.target}-${l.label}`));

      setGraphData(prev => ({
        nodes: [
          ...prev.nodes,
          ...newNodes.filter(node => !existingNodeIds.has(node.id))
        ],
        links: [
          ...prev.links,
          ...newLinks.filter(link => 
            !existingLinkIds.has(`${link.source}-${link.target}-${link.label}`))
        ]
      }));

      setExpandedNodes(prev => new Set([...prev, nodeId]));
    } catch (error) {
      console.error('展开节点失败:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 处理文件上传
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      const formattedData = {
        nodes: data.nodes.map(node => ({
          id: node.id,
          name: node.label,
          type: node.type,
          color: getNodeColor(node.label, node.level)
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relation,
          color: '#999'
        }))
      };
      setGraphData(formattedData);
    } catch (error) {
      console.error('文件上传失败:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 搜索实体
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      if (data.entities.length > 0) {
        // 高亮搜索结果
        const highlightedData = {
          ...graphData,
          nodes: graphData.nodes.map(node => ({
            ...node,
            color: data.entities.some(entity => entity.id === node.id) 
              ? '#ff4757' 
              : getNodeColor(node.name, node.level)
          }))
        };
        setGraphData(highlightedData);
      }
    } catch (error) {
      console.error('搜索错误:', error);
      setError(error.message);
    }
  };

  // 节点点击事件
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    expandNode(node.id);
    // 聚焦到节点
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 1000);
      graphRef.current.zoom(2, 1000);
    }
  };

  // 缩放控制
  const handleZoom = (factor) => {
    if (graphRef.current) {
      const currentZoom = graphRef.current.zoom();
      graphRef.current.zoom(currentZoom * factor, 1000);
    }
  };

  // 重置视图
  const resetView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(1000);
    }
  };

  // 处理最大节点数变化
  const handleMaxNodesChange = (value) => {
    setMaxNodes(value[0]);
    fetchGraphData();
  };

  // 导出图谱数据
  const exportData = () => {
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'knowledge_graph.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  return (
    <div className="w-full h-screen bg-gray-50">
      {/* 顶部工具栏 */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-800">知识图谱可视化</h1>
          
          <div className="flex items-center space-x-4">
            {/* 搜索框 */}
            <div className="flex items-center space-x-2">
              <Input
                type="text"
                placeholder="搜索实体..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-64"
              />
              <Button onClick={handleSearch} size="sm">
                <Search className="w-4 h-4" />
              </Button>
            </div>

            {/* 节点数量控制 */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">显示节点数:</span>
              <div className="w-32">
                <Slider
                  value={[maxNodes]}
                  min={20}
                  max={200}
                  step={20}
                  onValueChange={handleMaxNodesChange}
                />
              </div>
              <span className="text-sm text-gray-600">{maxNodes}</span>
            </div>

            {/* 缩放控制 */}
            <div className="flex items-center space-x-2">
              <Button onClick={() => handleZoom(0.5)} size="sm" variant="outline">
                <ZoomOut className="w-4 h-4" />
              </Button>
              <Button onClick={() => handleZoom(2)} size="sm" variant="outline">
                <ZoomIn className="w-4 h-4" />
              </Button>
              <Button onClick={resetView} size="sm" variant="outline">
                <Maximize2 className="w-4 h-4" />
              </Button>
            </div>

            {/* 文件上传 */}
            <div className="relative">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Button variant="outline" size="sm">
                <Upload className="w-4 h-4 mr-2" />
                上传CSV
              </Button>
            </div>

            {/* 导出数据 */}
            <Button onClick={exportData} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              导出
            </Button>
          </div>
        </div>
      </div>

      <div className="flex h-full">
        {/* 错误提示 */}
        {error && (
          <div className="absolute top-20 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50">
            <p>{error}</p>
          </div>
        )}

        {/* 主图谱区域 */}
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
              <div className="text-lg">加载中...</div>
            </div>
          )}
          
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel="name"
            nodeColor="color"
            nodeRelSize={8}
            linkLabel="label"
            linkColor="color"
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            onNodeClick={handleNodeClick}
            width={window.innerWidth * 0.75}
            height={window.innerHeight - 80}
            backgroundColor="#f8f9fa"
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.name;
              const fontSize = 12/globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

              ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
              ctx.fillRect(
                node.x - bckgDimensions[0] / 2,
                node.y - bckgDimensions[1] / 2,
                ...bckgDimensions
              );

              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = node.color;
              ctx.fillText(label, node.x, node.y);

              node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
            }}
            nodePointerAreaPaint={(node, color, ctx) => {
              ctx.fillStyle = color;
              const bckgDimensions = node.__bckgDimensions;
              bckgDimensions && ctx.fillRect(
                node.x - bckgDimensions[0] / 2,
                node.y - bckgDimensions[1] / 2,
                ...bckgDimensions
              );
            }}
          />
        </div>

        {/* 侧边栏 */}
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">
          {selectedNode ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">节点详情</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600">名称</label>
                    <p className="text-sm text-gray-800">{selectedNode.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">类型</label>
                    <p className="text-sm text-gray-800">{selectedNode.type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">层级</label>
                    <p className="text-sm text-gray-800">{selectedNode.level === 1 ? '一级节点' : '二级节点'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">连接数</label>
                    <p className="text-sm text-gray-800">{selectedNode.connections}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">ID</label>
                    <p className="text-sm text-gray-800">{selectedNode.id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">使用说明</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>• 点击节点可以展开相关联的节点</p>
                  <p>• 使用滑块控制显示的节点数量</p>
                  <p>• 使用缩放按钮调整视图</p>
                  <p>• 深色节点为一级节点，浅色节点为二级节点</p>
                  <p>• 搜索框可以查找特定实体</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;

