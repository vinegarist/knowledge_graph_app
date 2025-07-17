import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Search, Download, ZoomIn, ZoomOut, Maximize2, ChevronLeft, ChevronRight, Info, Target, RotateCcw } from 'lucide-react';
import { Slider } from "@/components/ui/slider";

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

const KnowledgeGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [originalGraphData, setOriginalGraphData] = useState({ nodes: [], links: [] }); // 保存原始数据
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [pagination, setPagination] = useState({});
  const [graphInfo, setGraphInfo] = useState({});
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [focusMode, setFocusMode] = useState(false); // 焦点模式状态
  const [focusNode, setFocusNode] = useState(null); // 当前焦点节点
  const graphRef = useRef();

  // 获取图谱基本信息
  const fetchGraphInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/graph/info`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setGraphInfo(data);
    } catch (error) {
      console.error('获取图谱信息失败:', error);
    }
  };

  // 获取图谱数据
  const fetchGraphData = async (page = currentPage, size = pageSize) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/graph?page=${page}&page_size=${size}`);
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
          color: getNodeColor(node.label, node.connections)
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relation,
          color: '#999'
        }))
      };
      
      setGraphData(formattedData);
      setOriginalGraphData(formattedData); // 保存原始数据
      setPagination(data.pagination);
      setCurrentPage(page);
      setExpandedNodes(new Set()); // 重置展开状态
      setFocusMode(false); // 重置焦点模式
      setFocusNode(null);
    } catch (error) {
      console.error('获取图谱数据失败:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 根据节点连接数获取颜色
  const getNodeColor = (label, connections, isFocus = false, isNeighbor = false) => {
    // 焦点模式下的特殊颜色
    if (isFocus) {
      return '#ff4757'; // 红色表示焦点节点
    }
    if (focusMode && !isNeighbor) {
      return 'rgba(200, 200, 200, 0.3)'; // 灰色表示非相关节点
    }
    
    // 根据连接数确定颜色深度
    const intensity = Math.min(connections / 10, 1); // 连接数越多颜色越深
    
    if (label.includes('[疾病]')) {
      return `rgba(255, 107, 107, ${0.5 + intensity * 0.5})`;
    }
    if (label.includes('科室')) {
      return `rgba(78, 205, 196, ${0.5 + intensity * 0.5})`;
    }
    if (label.includes('比例') || label.includes('%')) {
      return `rgba(69, 183, 209, ${0.5 + intensity * 0.5})`;
    }
    if (label.includes('人群')) {
      return `rgba(150, 206, 180, ${0.5 + intensity * 0.5})`;
    }
    if (label.includes('传播') || label.includes('方式')) {
      return `rgba(254, 202, 87, ${0.5 + intensity * 0.5})`;
    }
    return `rgba(168, 230, 207, ${0.5 + intensity * 0.5})`;
  };

  // 进入焦点模式
  const enterFocusMode = async (nodeId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/node/neighbors?id=${encodeURIComponent(nodeId)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }

      // 转换数据格式
      const neighborNodeIds = new Set(data.nodes.map(n => n.id));
      const focusData = {
        nodes: data.nodes.map(node => ({
          ...node,
          name: node.label,
          color: getNodeColor(
            node.label, 
            node.connections, 
            node.id === nodeId, // 是否为焦点节点
            true // 都是邻居节点
          )
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relation,
          color: '#999'
        }))
      };

      setGraphData(focusData);
      setFocusMode(true);
      setFocusNode(nodeId);
      
      // 聚焦到中心节点
      setTimeout(() => {
        if (graphRef.current) {
          graphRef.current.zoomToFit(1000);
        }
      }, 100);

    } catch (error) {
      console.error('进入焦点模式失败:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 退出焦点模式
  const exitFocusMode = () => {
    setGraphData(originalGraphData);
    setFocusMode(false);
    setFocusNode(null);
    setSelectedNode(null);
  };

  // 展开节点（仅在非焦点模式下有效）
  const expandNode = async (nodeId) => {
    if (focusMode || expandedNodes.has(nodeId)) return;
    
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
        color: getNodeColor(node.label, node.connections)
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

      const updatedData = {
        nodes: [
          ...graphData.nodes,
          ...newNodes.filter(node => !existingNodeIds.has(node.id))
        ],
        links: [
          ...graphData.links,
          ...newLinks.filter(link => 
            !existingLinkIds.has(`${link.source}-${link.target}-${link.label}`))
        ]
      };

      setGraphData(updatedData);
      setOriginalGraphData(updatedData); // 同时更新原始数据
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
          ...node,
          name: node.label,
          color: getNodeColor(node.label, node.connections)
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relation,
          color: '#999'
        }))
      };
      setGraphData(formattedData);
      setOriginalGraphData(formattedData);
      setPagination(data.pagination);
      setCurrentPage(1);
      setFocusMode(false);
      setFocusNode(null);
      await fetchGraphInfo();
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
        const currentData = focusMode ? graphData : originalGraphData;
        const highlightedData = {
          ...currentData,
          nodes: currentData.nodes.map(node => ({
            ...node,
            color: data.entities.some(entity => entity.id === node.id) 
              ? '#ff4757' 
              : getNodeColor(node.name, node.connections, node.id === focusNode, focusMode)
          }))
        };
        setGraphData(highlightedData);
        if (!focusMode) {
          setOriginalGraphData(highlightedData);
        }
      }
    } catch (error) {
      console.error('搜索错误:', error);
      setError(error.message);
    }
  };

  // 节点点击事件
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    
    if (focusMode) {
      // 在焦点模式下，双击可以切换焦点
      if (node.id === focusNode) {
        exitFocusMode();
      } else {
        enterFocusMode(node.id);
      }
    } else {
      // 在普通模式下，单击进入焦点模式
      enterFocusMode(node.id);
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

  // 分页控制
  const goToPage = (page) => {
    if (page >= 1 && page <= pagination.total_pages) {
      fetchGraphData(page, pageSize);
    }
  };

  // 改变页面大小
  const handlePageSizeChange = (value) => {
    const newSize = value[0];
    setPageSize(newSize);
    fetchGraphData(1, newSize);
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
    fetchGraphInfo();
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

            {/* 焦点模式控制 */}
            {focusMode && (
              <div className="flex items-center space-x-2">
                <Button onClick={exitFocusMode} size="sm" variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  退出焦点模式
                </Button>
              </div>
            )}

            {/* 页面大小控制（仅在非焦点模式下显示） */}
            {!focusMode && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">每页节点数:</span>
                <div className="w-32">
                  <Slider
                    value={[pageSize]}
                    min={20}
                    max={100}
                    step={10}
                    onValueChange={handlePageSizeChange}
                  />
                </div>
                <span className="text-sm text-gray-600">{pageSize}</span>
              </div>
            )}

            {/* 分页控制（仅在非焦点模式下显示） */}
            {!focusMode && (
              <div className="flex items-center space-x-2">
                <Button 
                  onClick={() => goToPage(currentPage - 1)} 
                  size="sm" 
                  variant="outline"
                  disabled={currentPage <= 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="text-sm text-gray-600">
                  {currentPage} / {pagination.total_pages || 1}
                </span>
                <Button 
                  onClick={() => goToPage(currentPage + 1)} 
                  size="sm" 
                  variant="outline"
                  disabled={currentPage >= (pagination.total_pages || 1)}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}

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

        {/* 焦点模式提示 */}
        {focusMode && (
          <div className="absolute top-20 left-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded z-50">
            <div className="flex items-center">
              <Target className="w-4 h-4 mr-2" />
              <span>焦点模式：显示节点 "{focusNode}" 及其邻居</span>
            </div>
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
          {/* 图谱统计信息 */}
          <Card className="mb-4">
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Info className="w-5 h-5 mr-2" />
                {focusMode ? '焦点模式统计' : '图谱统计'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {!focusMode && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">总节点数:</span>
                      <span className="font-medium">{graphInfo.total_nodes || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">总边数:</span>
                      <span className="font-medium">{graphInfo.total_edges || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">当前页:</span>
                      <span className="font-medium">{currentPage} / {pagination.total_pages || 1}</span>
                    </div>
                  </>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">当前显示:</span>
                  <span className="font-medium">{graphData.nodes.length} 节点</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">当前边数:</span>
                  <span className="font-medium">{graphData.links.length}</span>
                </div>
                {focusMode && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">焦点节点:</span>
                    <span className="font-medium">{focusNode}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

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
                    <label className="text-sm font-medium text-gray-600">连接数</label>
                    <p className="text-sm text-gray-800">{selectedNode.connections}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">状态</label>
                    <p className="text-sm text-gray-800">
                      {selectedNode.id === focusNode ? '焦点节点' : 
                       focusMode ? '邻居节点' :
                       expandedNodes.has(selectedNode.id) ? '已展开' : '未展开'}
                    </p>
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
                  <p>• <strong>焦点模式</strong>：点击节点进入焦点模式，只显示该节点及其邻居</p>
                  <p>• <strong>退出焦点</strong>：在焦点模式下点击红色按钮或双击焦点节点退出</p>
                  <p>• <strong>切换焦点</strong>：在焦点模式下点击其他节点切换焦点</p>
                  <p>• <strong>分页浏览</strong>：使用分页按钮浏览不同的节点集合</p>
                  <p>• <strong>调整密度</strong>：调整每页节点数控制显示密度</p>
                  <p>• <strong>缩放视图</strong>：使用缩放按钮调整视图</p>
                  <p>• <strong>颜色含义</strong>：红色=焦点节点，灰色=非相关节点</p>
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

