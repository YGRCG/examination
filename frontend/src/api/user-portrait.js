import request from '@/utils/request'

/**
 * 获取问卷进度
 */
export const getProgress = async () => {
  const response = await request.get('/api/v1/user-portrait/progress')
  return response.data
}

/**
 * 提交问卷步骤数据
 * @param {string} step - 步骤名称
 * @param {Object} data - 步骤数据
 */
export const submitStep = async (step, data) => {
  const response = await request.post('/api/v1/user-portrait/step', {
    step,
    data
  })
  return response.data
}

/**
 * 提交动态问题的回答
 * @param {string} answer - 回答内容
 */
export const submitDynamicAnswer = async (answer) => {
  const response = await request.post('/api/v1/user-portrait/dynamic-question', {
    answer
  })
  return response.data
}

/**
 * 跳过当前问卷步骤
 */
export const skipStep = async () => {
  const response = await request.post('/api/v1/user-portrait/skip')
  return response.data
}

/**
 * 重置问卷
 */
export const resetQuestionnaire = async () => {
  const response = await request.post('/api/v1/user-portrait/reset')
  return response.data
}

/**
 * 获取所有问卷步骤
 */
export const getAllSteps = async () => {
  const response = await request.get('/api/v1/user-portrait/steps')
  return response.data
}

/**
 * 获取问卷详细状态
 */
export const getFlowStatus = async () => {
  const response = await request.get('/api/v1/user-portrait/status')
  return response.data
}

/**
 * 获取用户画像信息
 */
export const getUserPortrait = async () => {
  const response = await request.get('/api/v1/user-profile/')
  // 处理后端返回的数据结构
  if (response.data && response.data.status === 'success') {
    return response.data.data
  }
  return response.data || response
}

/**
 * 获取用户症状列表
 */
export const getUserSymptoms = async () => {
  const response = await request.get('/api/v1/user-portrait/symptoms')
  return response.data
}

/**
 * 更新用户画像信息
 * @param {Object} data - 更新的数据
 */
export const updateUserPortrait = async (data) => {
  const response = await request.put('/api/v1/user-profile/', data)
  return response.data
}