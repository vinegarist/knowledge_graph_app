// API配置文件
// 根据当前访问的域名动态设置API基础URL

const getApiBaseUrl = () => {
  // 获取当前页面的协议和主机名
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  // 如果是本地开发环境
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8080/api';
  }
  
  // 如果是其他IP地址，使用相同的IP地址但端口为8080
  return `${protocol}//${hostname}:8080/api`;
};

export const API_BASE_URL = getApiBaseUrl();

// 各个模块的API URL
export const AUTH_API_URL = API_BASE_URL.replace('/api', '/api/auth');
export const KNOWLEDGE_GRAPH_API_URL = API_BASE_URL;
export const SYMPTOM_DIAGNOSIS_API_URL = API_BASE_URL.replace('/api', '/api/symptom-diagnosis');
export const AI_SYMPTOM_DIAGNOSIS_API_URL = API_BASE_URL.replace('/api', '/api/ai-symptom-diagnosis');
export const AI_ASSISTANT_API_URL = API_BASE_URL;

console.log('API Base URL:', API_BASE_URL); 