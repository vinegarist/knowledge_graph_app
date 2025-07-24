import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Bot, 
  User, 
  Send, 
  Trash2, 
  ChevronLeft, 
  ChevronRight, 
  Target, 
  Search,
  AlertTriangle,
  Loader2,
  RefreshCw,
  Eye
} from 'lucide-react';

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

const AIAssistant = ({ onEntityFocus, onEntitySearch }) => {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentSources, setCurrentSources] = useState([]);
  const [sourcePage, setSourcePage] = useState(1);
  const [totalSourcePages, setTotalSourcePages] = useState(1);
  const [aiStatus, setAiStatus] = useState('unknown');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  
  const chatContainerRef = useRef(null);

  // 缓存管理函数
  const clearCache = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/cache/clear`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        console.log('缓存已清除');
        checkAIStatus(); // 重新检查状态
      }
    } catch (error) {
      console.error('清除缓存失败:', error);
    }
  };

  const reloadCache = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/cache/reload`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        console.log('缓存已重新加载:', data.data);
        checkAIStatus(); // 重新检查状态
      }
    } catch (error) {
      console.error('重新加载缓存失败:', error);
    }
  };

  // 初始化时检查AI状态
  useEffect(() => {
    checkAIStatus();
  }, []);

  // 自动滚动到聊天底部
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const checkAIStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/status`);
      const data = await response.json();
      setAiStatus(data.success ? 'ready' : 'error');
    } catch (error) {
      console.error('检查AI状态失败:', error);
      setAiStatus('error');
    }
  };

  const handleSubmit = async () => {
    if (!question.trim() || loading) return;
    
    const userQuestion = question.trim();
    setQuestion('');
    setLoading(true);
    setError(null);

    // 添加用户消息到聊天历史
    const userMessage = {
      type: 'user',
      content: userQuestion,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setChatHistory(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      });

      const data = await response.json();
      
      if (data.success) {
        const aiMessage = {
          type: 'ai',
          content: data.data.answer,
          relatedEntities: data.data.related_entities || [],
          suggestedFocus: data.data.suggested_focus,
          timestamp: new Date().toLocaleTimeString()
        };
        
        setChatHistory(prev => [...prev, aiMessage]);
        
        // 更新来源信息
        if (data.data.sources) {
          console.log('来源数据:', data.data.sources); // 调试信息
          console.log('来源数组:', data.data.sources.sources); // 调试信息
          setCurrentSources(data.data.sources.sources || []);
          setSourcePage(data.data.sources.current_page || 1);
          setTotalSourcePages(data.data.sources.total_pages || 1);
        } else {
          console.log('没有来源数据'); // 调试信息
          setCurrentSources([]);
          setSourcePage(1);
          setTotalSourcePages(1);
        }
      } else {
        setError(data.error || '处理请求时出错');
      }
    } catch (error) {
      console.error('AI聊天失败:', error);
      setError('网络错误，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await fetch(`${API_BASE_URL}/ai/history`, {
        method: 'DELETE',
      });
      setChatHistory([]);
      setCurrentSources([]);
      setSourcePage(1);
      setTotalSourcePages(1);
    } catch (error) {
      console.error('清空历史失败:', error);
    }
  };

  const handleSourcePagination = async (action) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/sources/page`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });

      const data = await response.json();
      if (data.success) {
        console.log('分页数据:', data.data); // 调试信息
        setCurrentSources(data.data.sources || []);
        setSourcePage(data.data.current_page || 1);
        setTotalSourcePages(data.data.total_pages || 1);
      }
    } catch (error) {
      console.error('分页失败:', error);
    }
  };

  const searchEntities = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/ai/search?q=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      
      if (data.success) {
        setSearchResults(data.data.results || []);
      }
    } catch (error) {
      console.error('搜索实体失败:', error);
    }
  };

  const handleEntityClick = (entity) => {
    if (onEntityFocus && entity.id) {
      onEntityFocus(entity.id);
    }
  };

  const handleEntitySearch = (entity) => {
    if (onEntitySearch && entity.label) {
      onEntitySearch(entity.label);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* AI状态指示器 */}
      <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-6 w-6 text-blue-600" />
            <div className="flex flex-col">
              <span className="font-semibold text-gray-800">医疗知识图谱AI助手</span>
              <span className="text-xs text-gray-600">严格基于知识图谱数据回答</span>
            </div>
            <Badge variant={aiStatus === 'ready' ? 'default' : 'destructive'}>
              {aiStatus === 'ready' ? '就绪' : '离线'}
            </Badge>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSearch(!showSearch)}
              title="搜索实体"
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={checkAIStatus}
              title="检查AI状态"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={reloadCache}
              title="重新加载缓存"
            >
              <Loader2 className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearCache}
              title="清除缓存"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* 知识图谱约束提示 */}
        <div className="mt-2 text-xs text-gray-600 bg-blue-50 p-2 rounded">
          💡 本AI仅基于医疗知识图谱数据回答，不使用训练数据或常识。
          <br />
          ⚡ 已启用智能缓存，大幅提升搜索和加载速度。如果知识图谱中没有相关信息，会明确告知。
        </div>
      </div>

      {/* 实体搜索面板 */}
      {showSearch && (
        <div className="p-4 border-b bg-gray-50 flex-shrink-0">
          <div className="space-y-2">
            <Input
              placeholder="搜索医疗实体..."
              onChange={(e) => searchEntities(e.target.value)}
            />
            {searchResults.length > 0 && (
              <div className="max-h-32 overflow-y-auto space-y-1">
                {searchResults.map((entity, index) => (
                  <div 
                    key={index}
                    className="flex items-center justify-between p-2 bg-white border rounded hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="font-medium">{entity.label}</div>
                      <div className="text-xs text-gray-500 flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {entity.match_type === 'exact' ? '精确' : '模糊'}
                        </Badge>
                        <span>连接数: {entity.connections || 0}</span>
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleEntityClick(entity)}
                        title="聚焦节点"
                      >
                        <Target className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleEntitySearch(entity)}
                        title="搜索节点"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 聊天历史 */}
      <div className="flex-1 overflow-hidden flex min-h-0">
        {/* 左侧聊天区域 */}
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div 
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0"
          >
            {chatHistory.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <Bot className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p>您好！我是医疗知识图谱AI助手</p>
                <p className="text-sm mt-2">请提问关于疾病、症状、治疗等医疗问题</p>
              </div>
            )}
            
            {chatHistory.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`${message.type === 'user' ? 'max-w-[70%]' : 'max-w-[75%]'} ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex items-start space-x-2 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
                    }`}>
                      {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </div>
                    <div className={`rounded-lg p-3 ${
                      message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <div className="whitespace-pre-wrap break-words max-w-full overflow-hidden">{message.content}</div>
                      <div className="text-xs opacity-70 mt-1">{message.timestamp}</div>
                      
                      {/* AI回答的相关实体 */}
                      {message.type === 'ai' && message.relatedEntities && message.relatedEntities.length > 0 && (
                        <div className="mt-2 space-y-1">
                          <div className="text-xs font-medium opacity-80">
                            相关实体（来自知识图谱）：
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {message.relatedEntities.slice(0, 3).map((entity, i) => (
                              <Badge 
                                key={i} 
                                variant="secondary" 
                                className="cursor-pointer text-xs"
                                onClick={() => handleEntityClick(entity)}
                                title={`匹配类型：${entity.match_type}, 连接数：${entity.connections}`}
                              >
                                {entity.label}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* 显示知识图谱覆盖情况 */}
                      {message.type === 'ai' && (
                        <div className="mt-1 text-xs opacity-60">
                          {message.relatedEntities && message.relatedEntities.length > 0 
                            ? `🔗 基于 ${message.relatedEntities.length} 个知识图谱实体` 
                            : '⚠️ 知识图谱中未找到相关实体'}
                        </div>
                      )}
                      
                      {/* 建议聚焦按钮 */}
                      {message.type === 'ai' && message.suggestedFocus && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="mt-2 h-6 text-xs"
                          onClick={() => handleEntityClick({ id: message.suggestedFocus })}
                        >
                          <Target className="h-3 w-3 mr-1" />
                          聚焦相关节点
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3 flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>AI正在思考中...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 输入区域 */}
          <div className="p-4 border-t bg-gray-50 flex-shrink-0">
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="flex space-x-2">
              <Textarea
                placeholder="请输入您的医疗问题..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                disabled={loading || aiStatus !== 'ready'}
                className="min-h-[80px] resize-none"
              />
              <div className="flex flex-col space-y-2">
                <Button
                  onClick={handleSubmit}
                  disabled={!question.trim() || loading || aiStatus !== 'ready'}
                  size="sm"
                >
                  <Send className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  onClick={clearHistory}
                  disabled={loading}
                  size="sm"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧来源区域 */}
        <div className="w-80 border-l bg-gray-50 flex flex-col flex-shrink-0 overflow-hidden">
          <div className="p-4 border-b flex-shrink-0">
            <h3 className="font-semibold text-gray-800">参考来源</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 min-h-0">
            {currentSources.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>提问后将显示相关实体</p>
                <p className="text-xs mt-2">调试信息: 当前来源数量 = {currentSources.length}</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-xs text-gray-500 mb-2">
                  找到 {currentSources.length} 个相关实体
                </div>
                {currentSources.map((source, index) => (
                  <Card key={index} className="border border-gray-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{source.label}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            连接数: {source.connections || 0}
                          </div>
                        </div>
                        <div className="flex flex-col space-y-1 ml-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs h-6 px-2"
                            onClick={() => handleEntityClick(source)}
                            title="聚焦节点"
                          >
                            <Target className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs h-6 px-2"
                            onClick={() => handleEntitySearch(source)}
                            title="搜索节点"
                          >
                            <Eye className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="text-xs text-gray-600">
                        <Badge variant="outline" className="text-xs">
                          {source.match_type === 'exact' ? '精确匹配' : '模糊匹配'}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* 来源分页 */}
          {totalSourcePages > 1 && (
            <div className="p-4 border-t flex-shrink-0">
              <div className="flex items-center justify-between">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleSourcePagination('prev')}
                  disabled={sourcePage <= 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-gray-600">
                  {sourcePage} / {totalSourcePages}
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleSourcePagination('next')}
                  disabled={sourcePage >= totalSourcePages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAssistant; 