import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8001/api/v1', // 更新为正确的后端API地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('userId')
          window.location.href = '/login'
          break
        case 403:
          console.error('没有权限访问')
          break
        case 500:
          console.error('服务器错误')
          break
        default:
          console.error('请求错误')
      }
    }
    return Promise.reject(error)
  }
)

// 健康信息API
export const healthInfoAPI = {
  // 更新用户健康信息
  updateUserHealthInfo: async (userId, healthData) => {
    try {
      const response = await api.post('/health-info/update', healthData);
      return response.data;
    } catch (error) {
      console.error('更新健康信息失败:', error);
      throw error;
    }
  },
  
  // 获取用户健康信息
  getUserHealthInfo: async (userId) => {
    try {
      const response = await api.get(`/health-info/user/${userId}`);
      return response.data;
    } catch (error) {
      console.error('获取健康信息失败:', error);
      throw error;
    }
  },
  
  // 提交健康信息
  submitHealthInfo: async (healthData) => {
    try {
      const response = await api.post('/health-info/submit', healthData);
      return response.data;
    } catch (error) {
      console.error('提交健康信息失败:', error);
      throw error;
    }
  },
  
  // 上传体检报告
  uploadMedicalReport: async (formData) => {
    try {
      const response = await api.post('/health-info/upload-report', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('上传体检报告失败:', error);
      throw error;
    }
  },
  
  // 生成用户画像
  generateUserPortrait: async () => {
    try {
      const response = await api.get('/health-info/generate-portrait');
      return response.data;
    } catch (error) {
      console.error('生成用户画像失败:', error);
      throw error;
    }
  }
}

// 体检推荐相关API
export const recommendationAPI = {
  // 获取个性化推荐
  getPersonalizedRecommendations: (userId) => {
    return api.get(`/recommendation/personalized/${userId}`)
  },
  
  // 保存用户对推荐的反馈
  saveRecommendationFeedback: (userId, feedbackData) => {
    return api.post('/recommendation/feedback', {
      user_id: userId,
      ...feedbackData
    })
  }
}

// 体检报告相关API
export const reportAPI = {
  // 获取用户体检报告列表
  getUserReports: (userId) => {
    return api.get(`/user/${userId}/reports`)
  },
  
  // 获取体检报告详情
  getReportDetail: (reportId) => {
    return api.get(`/report/${reportId}`)
  },
  
  // 上传体检报告
  uploadReport: (userId, reportData) => {
    return api.post('/report/upload', {
      user_id: userId,
      ...reportData
    })
  }
}

// 用户相关API
export const userAPI = {
  // 获取用户基本信息
  getUserProfile: (userId) => {
    return api.get(`/user/${userId}/profile`)
  },
  
  // 更新用户基本信息
  updateUserProfile: (userId, profileData) => {
    return api.post(`/user/${userId}/profile/update`, profileData)
  }
}

export default api