<template>
  <div class="login-container">
    <!-- 头部区域 -->
    <div class="login-header">
      <div class="logo-area">
        <div class="logo">🏥</div>
        <h1 class="system-name">医院体检项目智能推荐系统</h1>
      </div>
    </div>

    <!-- 表单区域 -->
    <div class="form-container">
      <!-- 模式切换 -->
      <div class="mode-switch">
        <button 
          class="mode-btn" 
          :class="{ active: isLoginMode }"
          @click="switchToLogin"
        >
          登录
        </button>
        <button 
          class="mode-btn" 
          :class="{ active: !isLoginMode }"
          @click="switchToRegister"
        >
          注册
        </button>
      </div>

      <!-- 登录表单 -->
      <form v-if="isLoginMode" @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="login-username">用户名</label>
          <input
            id="login-username"
            v-model="loginForm.username"
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="login-password">密码</label>
          <input
            id="login-password"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            required
            autocomplete="current-password"
          />
        </div>

        <div class="login-options">
          <label class="remember-me">
            <input type="checkbox" v-model="loginForm.rememberMe" />
            <span>记住密码</span>
          </label>
          <button type="button" class="forgot-password" @click="forgotPassword">
            忘记密码？
          </button>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="register-phone">手机号码</label>
          <input
            id="register-phone"
            v-model="registerForm.phone_number"
            type="tel"
            placeholder="请输入手机号码"
            required
          />
        </div>

        <div class="form-group">
          <label for="register-email">电子邮箱 (可选)</label>
          <input
            id="register-email"
            v-model="registerForm.email"
            type="email"
            placeholder="请输入电子邮箱"
          />
        </div>

        <div class="form-group">
          <label for="register-username">设置用户名</label>
          <input
            id="register-username"
            v-model="registerForm.username"
            type="text"
            placeholder="请设置用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="register-password">设置密码</label>
          <input
            id="register-password"
            v-model="registerForm.password"
            type="password"
            placeholder="请设置6-20位密码"
            required
            minlength="6"
            maxlength="20"
          />
        </div>

        <div class="form-group">
          <label for="register-confirm-password">确认密码</label>
          <input
            id="register-confirm-password"
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
          <span v-if="registerForm.password !== registerForm.confirmPassword" class="error-message">
            两次输入的密码不一致
          </span>
        </div>

        <div class="agreement">
          <label>
            <input type="checkbox" v-model="registerForm.agreeTerms" required />
            <span>
              我已阅读并同意 <a href="#" @click.prevent="showTerms">《用户协议》</a> 和 <a href="#" @click.prevent="showPrivacy">《隐私政策》</a>
            </span>
          </label>
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading || registerForm.password !== registerForm.confirmPassword">
          {{ isLoading ? '注册中...' : '注册' }}
        </button>
      </form>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-toast">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { router } from '../router'
import { login, register } from '../api/auth'

// 状态管理
const isLoginMode = ref(true)
const isLoading = ref(false)
const errorMessage = ref('')

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  rememberMe: false
})

// 注册表单数据
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  phone_number: '',
  email: '',
  agreeTerms: false
})

// 切换到登录模式
const switchToLogin = () => {
  isLoginMode.value = true
  errorMessage.value = ''
}

// 切换到注册模式
const switchToRegister = () => {
  isLoginMode.value = false
  errorMessage.value = ''
}

// 处理登录
const handleLogin = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    console.log('开始登录，用户名:', loginForm.value.username)
    const data = await login(loginForm.value.username, loginForm.value.password)
    console.log('登录成功，返回数据:', data)
    
    // 检查响应数据格式
    if (data && (data.access_token || data.token)) {
      // 保存token
      localStorage.setItem('token', data.access_token || data.token)
      localStorage.setItem('username', loginForm.value.username)
      
      // 获取用户ID
      if (data.user_id) {
        localStorage.setItem('userId', data.user_id)
      } else if (data.id) {
        localStorage.setItem('userId', data.id)
      } else {
        // 如果登录响应中没有用户ID，尝试从用户名获取
        try {
          const userResponse = await fetch('/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${data.access_token || data.token}`
            }
          })
          if (userResponse.ok) {
            const userData = await userResponse.json()
            if (userData.id) {
              localStorage.setItem('userId', userData.id)
            }
          }
        } catch (error) {
          console.error('获取用户ID失败:', error)
        }
      }
      
      console.log('Token已保存，准备跳转到信息收集页面')
      
      // 如果需要记住密码，可以在这里实现
      if (loginForm.value.rememberMe) {
        // 实际项目中应该加密存储
        localStorage.setItem('rememberedUsername', loginForm.value.username)
      } else {
        localStorage.removeItem('rememberedUsername')
      }
      
      // 登录成功后跳转到信息收集页面
      console.log('正在执行跳转...')
      router.replace('/information')
      console.log('跳转完成')
    } else {
      errorMessage.value = '登录失败，请重试'
    }
  } catch (error) {
    // 处理超时错误
    if (error.code === 'ECONNABORTED') {
      errorMessage.value = '请求超时，请检查网络连接后重试'
    } 
    // 处理后端返回的业务错误或验证错误
    else if (error.response) {
      // 检查是否有具体的错误信息
      if (error.response.data && error.response.data.message) {
        errorMessage.value = error.response.data.message
      } 
      // 处理422验证错误
      else if (error.response.status === 422) {
        errorMessage.value = '请求参数格式错误，请检查输入'
      } 
      // 处理其他HTTP错误
      else {
        errorMessage.value = `请求失败: ${error.response.statusText || '未知错误'}`
      }
    } else {
      errorMessage.value = '网络错误，请检查您的网络连接'
    }
    console.error('登录错误:', error)
  } finally {
    isLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (isLoading.value || registerForm.value.password !== registerForm.value.confirmPassword) return
  
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const data = await register({
      username: registerForm.value.username,
      password: registerForm.value.password,
      email: registerForm.value.email
    })
    
    // 检查响应是否包含用户数据（UserResponse对象）
    if (data && data.id && data.username) {
      // 注册成功后自动切换到登录模式
      switchToLogin()
      // 填充用户名
      loginForm.value.username = registerForm.value.username
      // 清空注册表单
      registerForm.value = {
        username: '',
        password: '',
        confirmPassword: '',
        phone_number: '',
        email: '',
        agreeTerms: false
      }
      
      // 显示成功提示
      alert('注册成功，请登录！')
    } else {
      errorMessage.value = '注册失败，请重试'
    }
  } catch (error) {
    // 处理后端返回的业务错误或验证错误
    if (error.response) {
      // 检查是否有具体的错误信息
      if (error.response.data && error.response.data.message) {
        errorMessage.value = error.response.data.message
      }
      // 检查是否有错误类型
      else if (error.response.data && error.response.data.error_type === "UsernameAlreadyExists") {
        errorMessage.value = "用户名已被使用，请选择其他用户名"
      }
      else if (error.response.data && error.response.data.error_type === "EmailAlreadyExists") {
        errorMessage.value = "邮箱已被使用，请使用其他邮箱"
      }
      // 处理422验证错误
      else if (error.response.status === 422) {
        errorMessage.value = '请求参数格式错误，请检查输入'
      }
      // 处理400错误
      else if (error.response.status === 400) {
        errorMessage.value = error.response.data?.message || '请求参数错误，请检查输入'
      }
      // 处理其他HTTP错误
      else {
        errorMessage.value = `请求失败: ${error.response.statusText || '未知错误'}`
      }
    } else {
      errorMessage.value = '网络错误，请检查您的网络连接'
    }
    console.error('注册错误:', error)
  } finally {
    isLoading.value = false
  }
}

// 忘记密码
const forgotPassword = () => {
  alert('密码重置功能正在开发中，请联系管理员！')
}

// 显示用户协议
const showTerms = () => {
  alert('用户协议内容正在完善中...')
}

// 显示隐私政策
const showPrivacy = () => {
  alert('隐私政策内容正在完善中...')
}

// 组件挂载时检查是否有记住的用户名
const initForm = () => {
  const rememberedUsername = localStorage.getItem('rememberedUsername')
  if (rememberedUsername) {
    loginForm.value.username = rememberedUsername
    loginForm.value.rememberMe = true
  }
}

// 初始化表单
initForm()
</script>

<style scoped>
/* 登录/注册页面样式 */
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f8ff;
}

.login-header {
  background-color: var(--primary-color);
  padding: 30px 0;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo {
  font-size: 48px;
  margin-bottom: 10px;
}

.system-name {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
}

.mode-switch {
  display: flex;
  background-color: white;
  border-radius: 25px;
  padding: 4px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mode-btn {
  padding: 10px 30px;
  border: none;
  background: none;
  border-radius: 21px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.login-form, .register-form {
  width: 100%;
  max-width: 400px;
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-color);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.remember-me input {
  margin-right: 6px;
}

.forgot-password {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 14px;
}

.forgot-password:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.agreement {
  margin-bottom: 25px;
  font-size: 12px;
  color: var(--text-secondary);
}

.agreement a {
  color: var(--primary-color);
  text-decoration: none;
}

.agreement a:hover {
  text-decoration: underline;
}

.submit-button {
  width: 100%;
  padding: 14px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.submit-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: var(--error-color);
  font-size: 12px;
  margin-top: 5px;
  display: block;
}

.error-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(245, 34, 45, 0.9);
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  z-index: 1000;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-form, .register-form {
    padding: 20px;
  }
  
  .system-name {
    font-size: 16px;
  }
}
</style>