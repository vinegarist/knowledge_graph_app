import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Search, Brain, MessageSquare, AlertTriangle, CheckCircle, XCircle, Plus, Minus } from 'lucide-react';
import { AI_SYMPTOM_DIAGNOSIS_API_URL } from '../config/api';

const AISymptomDiagnosisPage = () => {
  const [symptoms, setSymptoms] = useState([]);
  const [currentSymptom, setCurrentSymptom] = useState('');
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [interactiveQuestions, setInteractiveQuestions] = useState([]);
  const [currentAnswers, setCurrentAnswers] = useState({});
  const [currentSymptoms, setCurrentSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statistics, setStatistics] = useState(null);



  useEffect(() => {
    loadStatistics();
    loadAvailableSymptoms();
  }, []);

  const loadStatistics = async () => {
    try {
      const response = await fetch(`${AI_SYMPTOM_DIAGNOSIS_API_URL}/statistics`);
      const data = await response.json();
      if (data.success) {
        setStatistics(data.data);
      }
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  const loadAvailableSymptoms = async () => {
    try {
      const response = await fetch(`${AI_SYMPTOM_DIAGNOSIS_API_URL}/symptoms`);
      const data = await response.json();
      if (data.success) {
        setAvailableSymptoms(data.data.symptoms);
      }
    } catch (error) {
      console.error('加载症状列表失败:', error);
    }
  };

  const addSymptom = () => {
    if (currentSymptom.trim() && !symptoms.includes(currentSymptom.trim())) {
      setSymptoms([...symptoms, currentSymptom.trim()]);
      setCurrentSymptom('');
    }
  };

  const removeSymptom = (symptomToRemove) => {
    setSymptoms(symptoms.filter(s => s !== symptomToRemove));
  };

  const handleDiagnose = async () => {
    if (symptoms.length === 0) {
      setError('请至少添加一个症状');
      return;
    }

    setLoading(true);
    setError('');
    setDiagnosisResult(null);

    try {
      const response = await fetch(`${AI_SYMPTOM_DIAGNOSIS_API_URL}/diagnose`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms }),
      });

      const data = await response.json();
      if (data.success) {
        setDiagnosisResult(data.data);
      } else {
        setError(data.message || '诊断失败');
      }
    } catch (error) {
      setError('网络错误，请稍后重试');
      console.error('诊断失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const startInteractiveDiagnosis = async () => {
    if (symptoms.length === 0) {
      setError('请至少添加一个症状');
      return;
    }

    setLoading(true);
    setError('');
    setInteractiveMode(true);
    setCurrentSymptoms([...symptoms]);

    try {
      const response = await fetch(`${AI_SYMPTOM_DIAGNOSIS_API_URL}/interactive/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms }),
      });

      const data = await response.json();
      if (data.success) {
        setInteractiveQuestions(data.data.interactive_questions);
        setDiagnosisResult(data.data);
        setCurrentAnswers({});
      } else {
        setError(data.message || '启动交互式诊断失败');
        setInteractiveMode(false);
      }
    } catch (error) {
      setError('网络错误，请稍后重试');
      setInteractiveMode(false);
      console.error('启动交互式诊断失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestions = async () => {
    if (Object.keys(currentAnswers).length === 0) {
      setError('请回答至少一个问题');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${AI_SYMPTOM_DIAGNOSIS_API_URL}/interactive/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answers: currentAnswers,
          current_symptoms: currentSymptoms,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setDiagnosisResult(data.data);
        setCurrentSymptoms(data.data.current_symptoms);
        setCurrentAnswers({});
        setInteractiveQuestions([]);
        setInteractiveMode(false);
      } else {
        setError(data.message || '回答问题失败');
      }
    } catch (error) {
      setError('网络错误，请稍后重试');
      console.error('回答问题失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addSymptom();
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Brain className="mr-3 text-blue-600" />
          AI智能症状诊断
        </h1>
        <p className="text-gray-600">
          基于AI大语言模型的智能症状诊断系统，提供专业的医疗建议和诊断分析
        </p>
      </div>

      {/* 统计信息 */}
      {statistics && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">系统统计</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{statistics.total_symptoms}</div>
                <div className="text-sm text-gray-600">症状总数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{statistics.total_diseases}</div>
                <div className="text-sm text-gray-600">疾病总数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {statistics.avg_symptoms_per_disease?.toFixed(1) || '0'}
                </div>
                <div className="text-sm text-gray-600">平均症状数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {statistics.avg_diseases_per_symptom?.toFixed(1) || '0'}
                </div>
                <div className="text-sm text-gray-600">平均疾病数</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 症状输入 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Search className="mr-2" />
            症状输入
          </CardTitle>
          <CardDescription>
            请输入您的症状，系统将基于AI进行智能诊断分析
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="输入症状..."
              value={currentSymptom}
              onChange={(e) => setCurrentSymptom(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button onClick={addSymptom} disabled={!currentSymptom.trim()}>
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          {/* 已添加的症状 */}
          {symptoms.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">已添加的症状：</h3>
              <div className="flex flex-wrap gap-2">
                {symptoms.map((symptom, index) => (
                  <Badge key={index} variant="secondary" className="flex items-center gap-1">
                    {symptom}
                    <button
                      onClick={() => removeSymptom(symptom)}
                      className="ml-1 hover:text-red-500"
                    >
                      <XCircle className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* 可用症状建议 */}
          {availableSymptoms.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">常用症状：</h3>
              <div className="flex flex-wrap gap-2">
                {availableSymptoms.slice(0, 20).map((symptom) => (
                  <Badge
                    key={symptom}
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

          {/* 操作按钮 */}
          <div className="flex gap-3 mt-6">
            <Button
              onClick={handleDiagnose}
              disabled={loading || symptoms.length === 0}
              className="flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
              AI智能诊断
            </Button>
            <Button
              onClick={startInteractiveDiagnosis}
              disabled={loading || symptoms.length === 0}
              variant="outline"
              className="flex items-center gap-2"
            >
              <MessageSquare className="w-4 h-4" />
              交互式诊断
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 错误提示 */}
      {error && (
        <Alert className="mb-6" variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 交互式问题 */}
      {interactiveMode && interactiveQuestions.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="mr-2" />
              AI智能提问
            </CardTitle>
            <CardDescription>
              请回答以下问题，帮助AI更准确地诊断您的病情
            </CardDescription>
          </CardHeader>
          <CardContent>
            {interactiveQuestions.map((question) => (
              <div key={question.id} className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {question.question}
                </label>
                <Textarea
                  placeholder="请详细描述..."
                  value={currentAnswers[question.id] || ''}
                  onChange={(e) =>
                    setCurrentAnswers({
                      ...currentAnswers,
                      [question.id]: e.target.value,
                    })
                  }
                  className="w-full"
                  rows={3}
                />
              </div>
            ))}
            <Button
              onClick={answerQuestions}
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              提交答案并诊断
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 诊断结果 */}
      {diagnosisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="mr-2" />
              AI诊断结果
            </CardTitle>
            <CardDescription>
              基于您的症状，AI提供的专业诊断分析
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* AI诊断分析 */}
            {diagnosisResult.ai_diagnosis && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">AI诊断分析</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="whitespace-pre-wrap text-gray-800">
                    {diagnosisResult.ai_diagnosis}
                  </div>
                </div>
              </div>
            )}

            {/* 可能疾病 */}
            {diagnosisResult.possible_diseases && diagnosisResult.possible_diseases.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  可能的疾病 ({diagnosisResult.possible_diseases.length})
                </h3>
                <div className="space-y-3">
                  {diagnosisResult.possible_diseases.slice(0, 10).map((disease, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900">{disease.disease}</h4>
                        <Badge variant="secondary">
                          匹配度: {(disease.match_ratio * 100).toFixed(1)}%
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        <div>匹配症状: {disease.matched_symptoms.join(', ')}</div>
                        <div>总症状数: {disease.total_symptoms}</div>
                        <div>匹配分数: {disease.score}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 当前症状 */}
            {diagnosisResult.current_symptoms && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">当前症状</h3>
                <div className="flex flex-wrap gap-2">
                  {diagnosisResult.current_symptoms.map((symptom, index) => (
                    <Badge key={index} variant="outline">
                      {symptom}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* 医疗免责声明 */}
            <Alert className="mt-6">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>重要提醒：</strong>本系统提供的诊断结果仅供参考，不能替代专业医生的诊断。
                如有疑问或症状严重，请及时就医咨询专业医生。
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AISymptomDiagnosisPage;