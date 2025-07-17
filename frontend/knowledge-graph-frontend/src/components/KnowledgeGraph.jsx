import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Search, Download } from 'lucide-react';

const KnowledgeGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const graphRef = useRef();

  // 获取图谱数据
  const fetchGraphData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/graph');
      if (response.ok) {
        const data = await response.json();
        // 转换数据格式以适配ForceGraph2D
        const formattedData = {
          nodes: data.nodes.map(node => ({
            id: node.id,
            name: node.label,
            type: node.type,
            color: getNodeColor(node.label)
          })),
          links: data.edges.map(edge => ({
            source: edge.source,
            target: edge.target,
            label: edge.relation,
            color: '#999'
          }))
        };
        setGraphData(formattedData);
      } else {
        console.error('获取图谱数据失败');
      }
    } catch (error) {
      console.error('网络错误:', error);
    } finally {
      setLoading(false);
    }
  };

  // 根据节点类型获取颜色
  const getNodeColor = (label) => {
    if (label.includes('[疾病]')) return '#ff6b6b';
    if (label.includes('科室')) return '#4ecdc4';
    if (label.includes('比例') || label.includes('%')) return '#45b7d1';
    if (label.includes('人群')) return '#96ceb4';
    if (label.includes('传播') || label.includes('方式')) return '#feca57';
    return '#a8e6cf';
  };

  // 处理文件上传
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        const formattedData = {
          nodes: data.nodes.map(node => ({
            id: node.id,
            name: node.label,
            type: node.type,
            color: getNodeColor(node.label)
          })),
          links: data.edges.map(edge => ({
            source: edge.source,
            target: edge.target,
            label: edge.relation,
            color: '#999'
          }))
        };
        setGraphData(formattedData);
      } else {
        console.error('文件上传失败');
      }
    } catch (error) {
      console.error('上传错误:', error);
    } finally {
      setLoading(false);
    }
  };

  // 搜索实体
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        if (data.entities.length > 0) {
          // 高亮搜索结果
          const highlightedData = {
            ...graphData,
            nodes: graphData.nodes.map(node => ({
              ...node,
              color: data.entities.some(entity => entity.id === node.id) 
                ? '#ff4757' 
                : getNodeColor(node.name)
            }))
          };
          setGraphData(highlightedData);
        }
      }
    } catch (error) {
      console.error('搜索错误:', error);
    }
  };

  // 节点点击事件
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    // 聚焦到节点
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 1000);
      graphRef.current.zoom(2, 1000);
    }
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
                    <label className="text-sm font-medium text-gray-600">ID</label>
                    <p className="text-sm text-gray-800">{selectedNode.id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">图谱统计</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">节点数量</span>
                    <span className="text-sm font-medium">{graphData.nodes.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">关系数量</span>
                    <span className="text-sm font-medium">{graphData.links.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-lg">使用说明</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-600 space-y-2">
                <p>• 点击节点查看详细信息</p>
                <p>• 拖拽节点调整位置</p>
                <p>• 滚轮缩放图谱</p>
                <p>• 上传CSV文件更新数据</p>
                <p>• 搜索实体进行高亮显示</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;

