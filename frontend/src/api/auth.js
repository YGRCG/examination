import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000 // 10秒超时
})

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  config => {
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

// 响应拦截器 - 处理通用错误
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} 登录结果
 */
export const login = async (username, password) => {
  try {
    // 登录接口需要表单数据格式
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await fetch('/api/v1/auth/token', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw {
        response: {
          status: response.status,
          data: errorData
        }
      }
    }
    
    return await response.json()
  } catch (error) {
    throw error
  }
}

/**
 * 用户注册
 * @param {Object} userData - 用户数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @param {string} userData.email - 邮箱
 * @returns {Promise} 注册结果
 */
export const register = async (userData) => {
  try {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息
 */
export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/auth/me')
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * 用户登出
 */
export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  window.location.href = '/login'
}

/**
 * 刷新token
 * @returns {Promise} 新的token
 */
export const refreshToken = async () => {
  try {
    const response = await apiClient.post('/auth/refresh')
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    return access_token
  } catch (error) {
    // 刷新失败，执行登出
    logout()
    throw error
  }
}

/**
 * 重置密码请求
 * @param {string} email - 用户邮箱
 * @returns {Promise} 请求结果
 */
export const requestPasswordReset = async (email) => {
  try {
    const response = await apiClient.post('/auth/password-reset-request', { email })
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * 重置密码
 * @param {string} token - 重置令牌
 * @param {string} newPassword - 新密码
 * @returns {Promise} 重置结果
 */
export const resetPassword = async (token, newPassword) => {
  try {
    const response = await apiClient.post('/auth/password-reset', {
      token,
      new_password: newPassword
    })
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * 修改密码
 * @param {string} oldPassword - 旧密码
 * @param {string} newPassword - 新密码
 * @returns {Promise} 修改结果
 */
export const changePassword = async (oldPassword, newPassword) => {
  try {
    const response = await apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
    return response.data
  } catch (error) {
    throw error
  }
}

export default {
  login,
  register,
  getCurrentUser,
  logout,
  refreshToken,
  requestPasswordReset,
  resetPassword,
  changePassword
}