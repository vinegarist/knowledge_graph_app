import React, { useState, useEffect } from 'react';
import KnowledgeGraph from './components/KnowledgeGraph';
import SymptomDiagnosisPage from './components/SymptomDiagnosisPage';
import AISymptomDiagnosisPage from './components/AISymptomDiagnosisPage';
import LoginPage from './components/LoginPage';
import { Button } from './components/ui/button';
import { 
  Network, 
  Stethoscope, 
  Brain,
  Home,
  Settings,
  LogOut,
  User
} from 'lucide-react';
import { AUTH_API_URL, KNOWLEDGE_GRAPH_API_URL } from './config/api';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('knowledge-graph');
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [knowledgeGraphData, setKnowledgeGraphData] = useState(null);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // 检查本地存储的登录状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        // 验证token是否有效
        verifyToken(token);
      } catch (error) {
        console.error('解析用户数据失败:', error);
        handleLogout();
      }
    }
    setIsLoading(false);
  }, []);

  // 验证token
  const verifyToken = async (token) => {
    try {
      const response = await fetch(`${AUTH_API_URL}/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        handleLogout();
      }
    } catch (error) {
      console.error('Token验证失败:', error);
      handleLogout();
    }
  };

  // 登录成功后的处理
  const handleLogin = async (userData) => {
    setUser(userData);
    // 登录成功后立即开始加载知识图谱数据
    await loadKnowledgeGraphData();
  };

  // 加载知识图谱数据缓存
  const loadKnowledgeGraphData = async () => {
    setIsLoadingData(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8080/api/knowledge-graph/nodes', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setKnowledgeGraphData(data);
        console.log('知识图谱数据已缓存');
      } else {
        console.error('加载知识图谱数据失败');
      }
    } catch (error) {
      console.error('加载知识图谱数据错误:', error);
    } finally {
      setIsLoadingData(false);
    }
  };

  // 登出处理
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setKnowledgeGraphData(null);
    setCurrentPage('knowledge-graph');
  };

  // 如果正在加载，显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载...</p>
        </div>
      </div>
    );
  }

  // 如果未登录，显示登录页面
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      {/* 顶部导航栏 */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-900">医疗知识图谱系统</h1>
            <div className="flex items-center gap-2">
              <Button
                variant={currentPage === 'knowledge-graph' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage('knowledge-graph')}
                className="flex items-center gap-2"
              >
                <Network className="h-4 w-4" />
                知识图谱
              </Button>
              <Button
                variant={currentPage === 'symptom-diagnosis' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage('symptom-diagnosis')}
                className="flex items-center gap-2"
              >
                <Stethoscope className="h-4 w-4" />
                症状诊断
              </Button>
              <Button
                variant={currentPage === 'ai-symptom-diagnosis' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage('ai-symptom-diagnosis')}
                className="flex items-center gap-2"
              >
                <Brain className="h-4 w-4" />
                AI诊断
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isLoadingData && (
              <div className="flex items-center gap-2 text-sm text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>加载数据中...</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <User className="h-4 w-4" />
              <span>{user.username}</span>
            </div>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1">
        {currentPage === 'knowledge-graph' && <KnowledgeGraph knowledgeGraphData={knowledgeGraphData} />}
        {currentPage === 'symptom-diagnosis' && <SymptomDiagnosisPage />}
        {currentPage === 'ai-symptom-diagnosis' && <AISymptomDiagnosisPage />}
      </div>
    </div>
  );
}

export default App
