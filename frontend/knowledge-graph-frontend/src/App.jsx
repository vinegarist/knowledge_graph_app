import React, { useState } from 'react';
import KnowledgeGraph from './components/KnowledgeGraph';
import SymptomDiagnosisPage from './components/SymptomDiagnosisPage';
import { Button } from './components/ui/button';
import { 
  Network, 
  Stethoscope, 
  Home,
  Settings
} from 'lucide-react';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('knowledge-graph'); // 'knowledge-graph' or 'symptom-diagnosis'

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
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1">
        {currentPage === 'knowledge-graph' && <KnowledgeGraph />}
        {currentPage === 'symptom-diagnosis' && <SymptomDiagnosisPage />}
      </div>
    </div>
  );
}

export default App
