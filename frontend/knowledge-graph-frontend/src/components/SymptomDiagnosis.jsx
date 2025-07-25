import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
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
  Activity
} from 'lucide-react';

const SymptomDiagnosis = () => {
  const [symptoms, setSymptoms] = useState([]);
  const [newSymptom, setNewSymptom] = useState('');
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [interactiveData, setInteractiveData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [showAvailableSymptoms, setShowAvailableSymptoms] = useState(false);

  const API_BASE_URL = 'http://localhost:8080/api/symptom-diagnosis';

  // 加载可用症状列表
  useEffect(() => {
    loadAvailableSymptoms();
  }, []);

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

  const addSymptom = () => {
    if (newSymptom.trim() && !symptoms.includes(newSymptom.trim())) {
      setSymptoms([...symptoms, newSymptom.trim()]);
      setNewSymptom('');
    }
  };

  const removeSymptom = (symptom) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const diagnoseSymptoms = async () => {
    if (symptoms.length === 0) return;

    setLoading(true);
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
        setDiagnosisResult(data.data);
        setInteractiveMode(false);
      } else {
        console.error('诊断失败:', data.message);
      }
    } catch (error) {
      console.error('诊断请求失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const startInteractiveDiagnosis = async () => {
    if (symptoms.length === 0) return;

    setLoading(true);
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
      } else {
        console.error('交互式诊断失败:', data.message);
      }
    } catch (error) {
      console.error('交互式诊断请求失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestions = async () => {
    if (!interactiveData || Object.keys(answers).length === 0) return;

    setLoading(true);
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

      const data = await response.json();
      if (data.success) {
        setInteractiveData(data.data);
        setAnswers({});
      } else {
        console.error('回答问题失败:', data.message);
      }
    } catch (error) {
      console.error('回答问题请求失败:', error);
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

  const getMatchColor = (ratio) => {
    if (ratio >= 0.7) return 'bg-green-100 text-green-800';
    if (ratio >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5" />
            症状诊断系统
          </CardTitle>
          <CardDescription>
            输入您的症状，系统将帮您分析可能的疾病
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 症状输入 */}
          <div className="space-y-2">
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
          <div className="flex gap-2">
            <Button 
              onClick={diagnoseSymptoms} 
              disabled={symptoms.length === 0 || loading}
              className="flex-1"
            >
              {loading ? '诊断中...' : '开始诊断'}
            </Button>
            <Button 
              variant="outline" 
              onClick={startInteractiveDiagnosis}
              disabled={symptoms.length === 0 || loading}
              className="flex-1"
            >
              交互式诊断
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 诊断结果 */}
      {diagnosisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              诊断结果
            </CardTitle>
            <CardDescription>
              基于您提供的症状，可能的疾病分析
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {diagnosisResult.possible_diseases.length > 0 ? (
              <div className="space-y-4">
                {diagnosisResult.possible_diseases.map((disease, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-lg">{disease.disease}</h3>
                      <Badge className={getMatchColor(disease.match_ratio)}>
                        匹配度: {(disease.match_ratio * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-blue-600" />
                        <span className="text-sm text-gray-600">匹配症状：</span>
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
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">未找到匹配的疾病</p>
              </div>
            )}

            {/* 进一步询问 */}
            {diagnosisResult.further_questions && diagnosisResult.further_questions.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold mb-3">建议进一步确认：</h3>
                <div className="space-y-2">
                  {diagnosisResult.further_questions.map((question, index) => (
                    <div key={index} className="text-sm text-gray-600">
                      <span className="font-medium">{question.disease}：</span>
                      {question.question} {question.symptoms.join('、')}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 交互式诊断 */}
      {interactiveMode && interactiveData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-blue-600" />
              交互式诊断
            </CardTitle>
            <CardDescription>
              请回答以下问题以进一步确认诊断
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 当前症状 */}
            <div>
              <h3 className="font-semibold mb-2">当前症状：</h3>
              <div className="flex flex-wrap gap-1">
                {interactiveData.current_symptoms.map((symptom, index) => (
                  <Badge key={index} variant="secondary">
                    {symptom}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 问题列表 */}
            {interactiveData.interactive_questions && interactiveData.interactive_questions.length > 0 ? (
              <div className="space-y-4">
                <h3 className="font-semibold">请确认以下症状：</h3>
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
                  {loading ? '处理中...' : '提交答案'}
                </Button>
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <p className="text-gray-600">诊断完成！</p>
              </div>
            )}

            {/* 可能的疾病 */}
            {interactiveData.possible_diseases && interactiveData.possible_diseases.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold mb-3">可能的疾病：</h3>
                <div className="space-y-2">
                  {interactiveData.possible_diseases.map((disease, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <span className="font-medium">{disease.disease}</span>
                      <Badge className={getMatchColor(disease.match_ratio)}>
                        {(disease.match_ratio * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SymptomDiagnosis;