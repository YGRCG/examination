import request from '@/utils/request'

const userProfileAPI = {
  // 初始化用户画像收集
  initializeProfile: async () => {
    const response = await request.post('/api/user-profile/initialize')
    return response
  },

  // 处理用户输入
  processInput: async (data) => {
    const response = await request.post('/api/user-profile/process', data)
    return response
  },

  // 保存用户画像
  saveProfile: async (profileData) => {
    const response = await request.post('/api/user-profile', profileData)
    return response
  },

  // 获取用户画像
  getProfile: async () => {
    const response = await request.get('/api/user-profile')
    return response
  },

  // 更新用户画像
  updateProfile: async (userId, profileData) => {
    const response = await request.put(`/api/user-profile/${userId}`, profileData)
    return response
  },

  // 获取症状追问知识库
  getSymptomFollowUpQuestions: async (symptom) => {
    const response = await request.get(`/api/user-profile/symptom-questions/${symptom}`)
    return response
  }
}

export default userProfileAPI