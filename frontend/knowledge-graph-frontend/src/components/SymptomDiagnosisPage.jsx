import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { 
  Search, 
  Plus, 
  X, 
  AlertCircle, 
  CheckCircle, 
  Info,
  ChevronRight,
  ChevronDown,
  Stethoscope,
  Thermometer,
  Activity,
  Brain,
  MessageSquare,
  Send,
  RefreshCw,
  Trash2,
  Settings,
  FileText,
  Users,
  Clock,
  TrendingUp,
  Zap,
  Lightbulb,
  Heart,
  Shield,
  Star
} from 'lucide-react';

const SymptomDiagnosisPage = () => {
  const [symptoms, setSymptoms] = useState([]);
  const [newSymptom, setNewSymptom] = useState('');
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [interactiveData, setInteractiveData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [showAvailableSymptoms, setShowAvailableSymptoms] = useState(false);
  const [diagnosisHistory, setDiagnosisHistory] = useState([]);
  const [selectedDisease, setSelectedDisease] = useState(null);
  const [diseaseDetails, setDiseaseDetails] = useState(null);
  const [showDiseaseDetails, setShowDiseaseDetails] = useState(false);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('diagnosis'); // diagnosis, history, stats

  const API_BASE_URL = 'http://localhost:5000/api/symptom-diagnosis';
  const messagesEndRef = useRef(null);

  // 加载可用症状列表和统计信息
  useEffect(() => {
    loadAvailableSymptoms();
    loadStatistics();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [diagnosisHistory]);

  const loadAvailableSymptoms = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms`);
      const data = await response.json();
      if (data.success) {
        setAvailableSymptoms(data.data.symptoms);
      }
    } catch (error) {
      console.error('加载症状列表失败:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/statistics`);
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
      }
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  const addSymptom = () => {
    if (newSymptom.trim() && !symptoms.includes(newSymptom.trim())) {
      setSymptoms([...symptoms, newSymptom.trim()]);
      setNewSymptom('');
    }
  };

  const removeSymptom = (symptom) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const addMessageToHistory = (type, content, data = null) => {
    const message = {
      id: Date.now(),
      type,
      content,
      data,
      timestamp: new Date().toLocaleTimeString()
    };
    setDiagnosisHistory(prev => [...prev, message]);
  };

  const diagnoseSymptoms = async () => {
    if (symptoms.length === 0) return;

    setLoading(true);
    addMessageToHistory('user', `症状: ${symptoms.join('、')}`);

    try {
      const response = await fetch(`${API_BASE_URL}/diagnose`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms: symptoms,
          min_match_ratio: 0.3
        }),
      });

      const data = await response.json();
      if (data.success) {
        const result = data.data;
        setDiagnosisResult(result);
        setInteractiveMode(false);
        
        if (result.possible_diseases.length > 0) {
          addMessageToHistory('system', `找到 ${result.possible_diseases.length} 个可能的疾病`, result);
        } else {
          addMessageToHistory('system', '未找到匹配的疾病，建议咨询专业医生', result);
        }
      } else {
        addMessageToHistory('error', `诊断失败: ${data.message}`);
      }
    } catch (error) {
      addMessageToHistory('error', `诊断请求失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const startInteractiveDiagnosis = async () => {
    if (symptoms.length === 0) return;

    setLoading(true);
    addMessageToHistory('user', `开始交互式诊断，症状: ${symptoms.join('、')}`);

    try {
      const response = await fetch(`${API_BASE_URL}/interactive/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symptoms: symptoms
        }),
      });

      const data = await response.json();
      if (data.success) {
        setInteractiveData(data.data);
        setInteractiveMode(true);
        setDiagnosisResult(null);
        addMessageToHistory('system', '交互式诊断已开始，请回答以下问题', data.data);
      } else {
        addMessageToHistory('error', `交互式诊断失败: ${data.message}`);
      }
    } catch (error) {
      addMessageToHistory('error', `交互式诊断请求失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestions = async () => {
    if (!interactiveData || Object.keys(answers).length === 0) return;

    setLoading(true);
    addMessageToHistory('user', `回答问题: ${JSON.stringify(answers)}`);

    try {
      const response = await fetch(`${API_BASE_URL}/interactive/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answers: answers,
          current_symptoms: interactiveData.current_symptoms
        }),
      });

      const data = response.json();
      if (data.success) {
        setInteractiveData(data.data);
        setAnswers({});
        addMessageToHistory('system', '答案已提交，诊断结果已更新', data.data);
      } else {
        addMessageToHistory('error', `回答问题失败: ${data.message}`);
      }
    } catch (error) {
      addMessageToHistory('error', `回答问题请求失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, symptom, checked) => {
    setAnswers(prev => {
      const newAnswers = { ...prev };
      if (!newAnswers[questionId]) {
        newAnswers[questionId] = [];
      }
      
      if (checked) {
        if (!newAnswers[questionId].includes(symptom)) {
          newAnswers[questionId] = [...newAnswers[questionId], symptom];
        }
      } else {
        newAnswers[questionId] = newAnswers[questionId].filter(s => s !== symptom);
      }
      
      return newAnswers;
    });
  };

  const getDiseaseDetails = async (disease) => {
    try {
      const response = await fetch(`${API_BASE_URL}/disease/${encodeURIComponent(disease)}`);
      const data = await response.json();
      if (data.success) {
        setDiseaseDetails(data.data);
        setSelectedDisease(disease);
        setShowDiseaseDetails(true);
      }
    } catch (error) {
      console.error('获取疾病详情失败:', error);
    }
  };

  const clearHistory = () => {
    setDiagnosisHistory([]);
    setDiagnosisResult(null);
    setInteractiveMode(false);
    setInteractiveData(null);
    setAnswers({});
    setSelectedDisease(null);
    setDiseaseDetails(null);
    setShowDiseaseDetails(false);
  };

  const getMatchColor = (ratio) => {
    if (ratio >= 0.7) return 'bg-green-100 text-green-800 border-green-200';
    if (ratio >= 0.5) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const renderMessage = (message) => {
    switch (message.type) {
      case 'user':
        return (
          <div className="flex justify-end mb-4">
            <div className="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="text-sm">{message.content}</span>
              </div>
              <div className="text-xs opacity-75 mt-1">{message.timestamp}</div>
            </div>
          </div>
        );
      
      case 'system':
        return (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-2xl">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-blue-600" />
                <span className="font-medium">症状诊断系统</span>
              </div>
              <div className="text-sm">{message.content}</div>
              {message.data && renderDiagnosisResult(message.data)}
              <div className="text-xs text-gray-500 mt-1">{message.timestamp}</div>
            </div>
          </div>
        );
      
      case 'error':
        return (
          <div className="flex justify-start mb-4">
            <div className="bg-red-100 border border-red-200 rounded-lg px-4 py-2 max-w-2xl">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <span className="text-sm text-red-800">{message.content}</span>
              </div>
              <div className="text-xs text-red-600 mt-1">{message.timestamp}</div>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const renderDiagnosisResult = (result) => {
    if (!result.possible_diseases || result.possible_diseases.length === 0) {
      return (
        <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2 text-yellow-800">
            <Info className="h-4 w-4" />
            <span className="text-sm">未找到匹配的疾病，建议咨询专业医生</span>
          </div>
        </div>
      );
    }

    return (
      <div className="mt-3 space-y-3">
        <div className="text-sm font-medium text-gray-700">可能的疾病：</div>
        {result.possible_diseases.slice(0, 5).map((disease, index) => (
          <div key={index} className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Heart className="h-4 w-4 text-red-500" />
                <span className="font-medium">{disease.disease}</span>
              </div>
              <Badge className={getMatchColor(disease.match_ratio)}>
                {(disease.match_ratio * 100).toFixed(1)}%
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Thermometer className="h-3 w-3 text-blue-600" />
                <span className="text-xs text-gray-600">匹配症状：</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {disease.matched_symptoms.map((symptom, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {symptom}
                  </Badge>
                ))}
              </div>
              
              <div className="mt-2">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>症状匹配进度</span>
                  <span>{disease.matched_symptoms.length}/{disease.total_symptoms}</span>
                </div>
                <Progress 
                  value={(disease.matched_symptoms.length / disease.total_symptoms) * 100} 
                  className="h-2"
                />
              </div>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              className="mt-2 w-full"
              onClick={() => getDiseaseDetails(disease.disease)}
            >
              <FileText className="h-3 w-3 mr-1" />
              查看详情
            </Button>
          </div>
        ))}
      </div>
    );
  };

  const renderInteractiveQuestions = () => {
    if (!interactiveData?.interactive_questions) return null;

    return (
      <div className="space-y-4">
        <div className="text-sm font-medium text-gray-700">请确认以下症状：</div>
        {interactiveData.interactive_questions.map((question, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ChevronRight className="h-4 w-4 text-blue-600" />
              <span className="font-medium">{question.question}</span>
            </div>
            <div className="space-y-2">
              {question.symptoms.map((symptom, idx) => (
                <label key={idx} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={answers[question.id]?.includes(symptom) || false}
                    onChange={(e) => handleAnswerChange(question.id, symptom, e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">{symptom}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
        
        <Button 
          onClick={answerQuestions}
          disabled={Object.keys(answers).length === 0 || loading}
          className="w-full"
        >
          {loading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              处理中...
            </>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              提交答案
            </>
          )}
        </Button>
      </div>
    );
  };

  const renderDiseaseDetails = () => {
    if (!diseaseDetails) return null;

    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            {diseaseDetails.disease}
          </CardTitle>
          <CardDescription>
            疾病详细信息
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Thermometer className="h-4 w-4 text-blue-600" />
                <span className="font-medium">相关症状</span>
                <Badge variant="secondary">{diseaseDetails.symptom_count} 个</Badge>
              </div>
              <div className="flex flex-wrap gap-1">
                {diseaseDetails.symptoms.slice(0, 10).map((symptom, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {symptom}
                  </Badge>
                ))}
                {diseaseDetails.symptoms.length > 10 && (
                  <Badge variant="outline" className="text-xs">
                    +{diseaseDetails.symptoms.length - 10} 更多
                  </Badge>
                )}
              </div>
            </div>
            
            {diseaseDetails.entity_info && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Info className="h-4 w-4 text-green-600" />
                  <span className="font-medium">实体信息</span>
                </div>
                <div className="text-sm text-gray-600">
                  ID: {diseaseDetails.entity_info.id}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderStats = () => {
    if (!stats) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Thermometer className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{stats.total_symptoms}</div>
                <div className="text-sm text-gray-600">症状总数</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Heart className="h-8 w-8 text-red-500" />
              <div>
                <div className="text-2xl font-bold">{stats.total_diseases}</div>
                <div className="text-sm text-gray-600">疾病总数</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-8 w-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{stats.avg_symptoms_per_disease.toFixed(1)}</div>
                <div className="text-sm text-gray-600">平均症状/疾病</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Zap className="h-8 w-8 text-yellow-500" />
              <div>
                <div className="text-2xl font-bold">{stats.avg_diseases_per_symptom.toFixed(1)}</div>
                <div className="text-sm text-gray-600">平均疾病/症状</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧边栏 */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Stethoscope className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-bold">症状诊断系统</h1>
          </div>
          <p className="text-sm text-gray-600">智能症状分析与疾病诊断</p>
        </div>

        {/* 标签页 */}
        <div className="flex border-b border-gray-200">
          <button
            className={`flex-1 px-4 py-2 text-sm font-medium ${
              activeTab === 'diagnosis' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('diagnosis')}
          >
            <Brain className="h-4 w-4 mr-1" />
            诊断
          </button>
          <button
            className={`flex-1 px-4 py-2 text-sm font-medium ${
              activeTab === 'history' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('history')}
          >
            <Clock className="h-4 w-4 mr-1" />
            历史
          </button>
          <button
            className={`flex-1 px-4 py-2 text-sm font-medium ${
              activeTab === 'stats' 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('stats')}
          >
            <TrendingUp className="h-4 w-4 mr-1" />
            统计
          </button>
        </div>

        {/* 标签页内容 */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'diagnosis' && (
            <div className="p-4 space-y-4">
              {/* 症状输入 */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">输入症状</span>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="输入症状..."
                    value={newSymptom}
                    onChange={(e) => setNewSymptom(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addSymptom()}
                    className="flex-1"
                  />
                  <Button onClick={addSymptom} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setShowAvailableSymptoms(!showAvailableSymptoms)}
                  >
                    <Search className="h-4 w-4" />
                  </Button>
                </div>

                {/* 可用症状列表 */}
                {showAvailableSymptoms && (
                  <div className="border rounded-lg p-3 max-h-40 overflow-y-auto">
                    <div className="text-sm text-gray-600 mb-2">可用症状：</div>
                    <div className="flex flex-wrap gap-1">
                      {availableSymptoms.slice(0, 50).map((symptom, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="cursor-pointer hover:bg-blue-50"
                          onClick={() => {
                            if (!symptoms.includes(symptom)) {
                              setSymptoms([...symptoms, symptom]);
                            }
                          }}
                        >
                          {symptom}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 已选症状 */}
              {symptoms.length > 0 && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">已选症状：</div>
                  <div className="flex flex-wrap gap-2">
                    {symptoms.map((symptom, index) => (
                      <Badge key={index} className="flex items-center gap-1">
                        <Thermometer className="h-3 w-3" />
                        {symptom}
                        <X 
                          className="h-3 w-3 cursor-pointer" 
                          onClick={() => removeSymptom(symptom)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* 操作按钮 */}
              <div className="space-y-2">
                <Button 
                  onClick={diagnoseSymptoms} 
                  disabled={symptoms.length === 0 || loading}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      诊断中...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      开始诊断
                    </>
                  )}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={startInteractiveDiagnosis}
                  disabled={symptoms.length === 0 || loading}
                  className="w-full"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  交互式诊断
                </Button>
              </div>

              {/* 交互式问题 */}
              {interactiveMode && renderInteractiveQuestions()}

              {/* 疾病详情 */}
              {showDiseaseDetails && renderDiseaseDetails()}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium">诊断历史</h3>
                <Button variant="outline" size="sm" onClick={clearHistory}>
                  <Trash2 className="h-4 w-4 mr-1" />
                  清空
                </Button>
              </div>
              {diagnosisHistory.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>暂无诊断历史</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {diagnosisHistory.map((message) => (
                    <div key={message.id}>
                      {renderMessage(message)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="p-4">
              <h3 className="font-medium mb-4">系统统计</h3>
              {renderStats()}
              
              {stats && (
                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle className="text-lg">缓存信息</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">缓存状态：</span>
                        <Badge variant={stats.cache_enabled ? "default" : "secondary"}>
                          {stats.cache_enabled ? "启用" : "禁用"}
                        </Badge>
                      </div>
                      {stats.cache_file && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">缓存文件：</span>
                          <span className="text-sm text-gray-800">已创建</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部工具栏 */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-600">系统状态：</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  正常运行
                </Badge>
              </div>
              {stats && (
                <div className="flex items-center gap-2">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm text-gray-600">
                    知识库：{stats.total_symptoms} 症状 / {stats.total_diseases} 疾病
                  </span>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={loadStatistics}>
                <RefreshCw className="h-4 w-4 mr-1" />
                刷新
              </Button>
            </div>
          </div>
        </div>

        {/* 聊天区域 */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'diagnosis' ? (
            <div className="h-full flex flex-col">
              {/* 消息列表 */}
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {diagnosisHistory.length === 0 ? (
                    <div className="text-center py-16">
                      <Stethoscope className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        欢迎使用症状诊断系统
                      </h3>
                      <p className="text-gray-600 mb-6">
                        请在左侧输入症状，开始智能诊断分析
                      </p>
                      <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Brain className="h-4 w-4" />
                          <span>智能分析</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <MessageSquare className="h-4 w-4" />
                          <span>交互诊断</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Heart className="h-4 w-4" />
                          <span>疾病匹配</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    diagnosisHistory.map((message) => (
                      <div key={message.id}>
                        {renderMessage(message)}
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>请选择左侧标签页查看相应内容</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SymptomDiagnosisPage; 