import request from '@/utils/request'

const userProfileAPI = {
  // 初始化用户画像收集
  initializeProfile: async () => {
    const response = await request.post('/api/v1/user-profile/initialize')
    return response
  },

  // 处理用户输入
  processInput: async (data) => {
    const response = await request.post('/api/v1/user-profile/process', data)
    return response
  },

  // 保存用户画像
  saveProfile: async (profileData) => {
    const response = await request.post('/api/v1/user-profile/', profileData)
    return response
  },

  // 获取用户画像
  getProfile: async () => {
    const response = await request.get('/api/v1/user-profile/')
    return response
  },

  // 获取对话历史
  getConversationHistory: async () => {
    const response = await request.get('/api/v1/user-profile/conversation-history')
    return response
  },

  // 清除对话历史
  clearConversationHistory: async () => {
    const response = await request.delete('/api/v1/user-profile/conversation-history')
    return response
  },

  // 获取症状知识库
  getSymptomKnowledge: async (symptom) => {
    const url = symptom 
      ? `/api/v1/user-profile/symptom-knowledge?symptom=${encodeURIComponent(symptom)}`
      : '/api/v1/user-profile/symptom-knowledge'
    const response = await request.get(url)
    return response
  },

  // 创建症状知识库
  createSymptomKnowledge: async (data) => {
    const response = await request.post('/api/v1/user-profile/symptom-knowledge', data)
    return response
  },

  // 更新症状知识库
  updateSymptomKnowledge: async (symptom, data) => {
    const response = await request.put(`/api/v1/user-profile/symptom-knowledge/${encodeURIComponent(symptom)}`, data)
    return response
  },

  // 删除症状知识库
  deleteSymptomKnowledge: async (symptom) => {
    const response = await request.delete(`/api/v1/user-profile/symptom-knowledge/${encodeURIComponent(symptom)}`)
    return response
  }
}

export default userProfileAPI