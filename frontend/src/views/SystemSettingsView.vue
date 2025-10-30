<template>
  <div class="system-settings">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <span class="page-title">系统设置</span>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载设置中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchSettings">重新加载</button>
      </div>

      <!-- 设置内容 -->
      <div v-else class="settings-container">
        <!-- 账户与安全 -->
        <div class="settings-section">
          <h2 class="section-title">账户与安全</h2>
          <div class="settings-group">
            <div class="setting-item" @click="navigateToPage('/profile')">
              <div class="setting-info">
                <div class="setting-icon">👤</div>
                <span class="setting-name">个人资料</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="showChangePasswordModal">
              <div class="setting-info">
                <div class="setting-icon">🔒</div>
                <span class="setting-name">修改密码</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="showBindPhoneModal">
              <div class="setting-info">
                <div class="setting-icon">📱</div>
                <span class="setting-name">绑定手机</span>
                <span v-if="userInfo?.phone_number" class="setting-value">{{ formatPhoneNumber(userInfo.phone_number) }}</span>
                <span v-else class="setting-hint">未绑定</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="showBindEmailModal">
              <div class="setting-info">
                <div class="setting-icon">✉️</div>
                <span class="setting-name">绑定邮箱</span>
                <span v-if="userInfo?.email" class="setting-value">{{ formatEmail(userInfo.email) }}</span>
                <span v-else class="setting-hint">未绑定</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div class="settings-section">
          <h2 class="section-title">通知设置</h2>
          <div class="settings-group">
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">🔔</div>
                <span class="setting-name">预约提醒</span>
                <span class="setting-desc">体检预约前通知</span>
              </div>
              <el-switch 
                v-model="notifications.appointment_reminder" 
                @change="updateNotificationSetting('appointment_reminder', $event)"
              ></el-switch>
            </div>
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">📊</div>
                <span class="setting-name">报告通知</span>
                <span class="setting-desc">报告生成与解读完成通知</span>
              </div>
              <el-switch 
                v-model="notifications.report_notification" 
                @change="updateNotificationSetting('report_notification', $event)"
              ></el-switch>
            </div>
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">💡</div>
                <span class="setting-name">健康提醒</span>
                <span class="setting-desc">定期健康建议和提醒</span>
              </div>
              <el-switch 
                v-model="notifications.health_reminder" 
                @change="updateNotificationSetting('health_reminder', $event)"
              ></el-switch>
            </div>
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">🛠️</div>
                <span class="setting-name">系统通知</span>
                <span class="setting-desc">系统更新和维护通知</span>
              </div>
              <el-switch 
                v-model="notifications.system_notification" 
                @change="updateNotificationSetting('system_notification', $event)"
              ></el-switch>
            </div>
          </div>
        </div>

        <!-- 隐私设置 -->
        <div class="settings-section">
          <h2 class="section-title">隐私设置</h2>
          <div class="settings-group">
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">🔐</div>
                <span class="setting-name">数据共享</span>
                <span class="setting-desc">允许匿名健康数据共享</span>
              </div>
              <el-switch 
                v-model="privacy.data_sharing" 
                @change="updatePrivacySetting('data_sharing', $event)"
              ></el-switch>
            </div>
            <div class="setting-item" @click="navigateToPage('/privacy-policy')">
              <div class="setting-info">
                <div class="setting-icon">📄</div>
                <span class="setting-name">隐私政策</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="navigateToPage('/terms-of-service')">
              <div class="setting-info">
                <div class="setting-icon">📑</div>
                <span class="setting-name">用户协议</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="showDeleteAccountModal">
              <div class="setting-info danger">
                <div class="setting-icon">🗑️</div>
                <span class="setting-name">删除账户</span>
                <span class="setting-desc">此操作不可撤销</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
          </div>
        </div>

        <!-- 通用设置 -->
        <div class="settings-section">
          <h2 class="section-title">通用设置</h2>
          <div class="settings-group">
            <div class="setting-item">
              <div class="setting-info">
                <div class="setting-icon">🌐</div>
                <span class="setting-name">语言</span>
                <span class="setting-value">{{ languages[language] }}</span>
              </div>
              <el-select 
                v-model="language" 
                @change="updateLanguage"
                class="setting-select"
                size="small"
                popper-class="language-select-popper"
              >
                <el-option 
                  v-for="(label, key) in languages" 
                  :key="key" 
                  :label="label" 
                  :value="key"
                ></el-option>
              </el-select>
            </div>
            <div class="setting-item" @click="showClearCacheModal">
              <div class="setting-info">
                <div class="setting-icon">🧹</div>
                <span class="setting-name">清除缓存</span>
                <span class="setting-value">{{ cacheSize }}MB</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="checkForUpdates">
              <div class="setting-info">
                <div class="setting-icon">🔄</div>
                <span class="setting-name">检查更新</span>
                <span class="setting-value">当前版本 v{{ appVersion }}</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
            <div class="setting-item" @click="aboutUs">
              <div class="setting-info">
                <div class="setting-icon">ℹ️</div>
                <span class="setting-name">关于我们</span>
              </div>
              <div class="setting-arrow">→</div>
            </div>
          </div>
        </div>

        <!-- 退出登录按钮 -->
        <div class="logout-container">
          <button class="logout-btn" @click="showLogoutModal">退出登录</button>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="closePasswordModal">×</button>
        </div>
        <div class="modal-body">
          <el-form ref="passwordForm" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码"></el-input>
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码"></el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码"></el-input>
            </el-form-item>
          </el-form>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closePasswordModal">取消</button>
          <button class="modal-btn confirm" @click="changePassword" :disabled="isUpdating">
            {{ isUpdating ? '修改中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 绑定手机弹窗 -->
    <div v-if="showPhoneModal" class="modal-overlay" @click="closePhoneModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ userInfo?.phone_number ? '修改手机号' : '绑定手机号' }}</h3>
          <button class="close-btn" @click="closePhoneModal">×</button>
        </div>
        <div class="modal-body">
          <el-form ref="phoneForm" :model="phoneForm" :rules="phoneRules" label-width="100px">
            <el-form-item label="手机号码" prop="phoneNumber">
              <el-input v-model="phoneForm.phoneNumber" placeholder="请输入手机号码"></el-input>
            </el-form-item>
            <el-form-item label="验证码" prop="verificationCode">
              <div class="verification-code-container">
                <el-input v-model="phoneForm.verificationCode" placeholder="请输入验证码"></el-input>
                <button 
                  class="get-code-btn" 
                  @click="sendPhoneVerificationCode"
                  :disabled="isSendingCode || countdown > 0"
                >
                  {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
                </button>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closePhoneModal">取消</button>
          <button class="modal-btn confirm" @click="bindPhone" :disabled="isUpdating">
            {{ isUpdating ? '处理中...' : '确认绑定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 绑定邮箱弹窗 -->
    <div v-if="showEmailModal" class="modal-overlay" @click="closeEmailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ userInfo?.email ? '修改邮箱' : '绑定邮箱' }}</h3>
          <button class="close-btn" @click="closeEmailModal">×</button>
        </div>
        <div class="modal-body">
          <el-form ref="emailForm" :model="emailForm" :rules="emailRules" label-width="100px">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="emailForm.email" placeholder="请输入电子邮箱"></el-input>
            </el-form-item>
            <el-form-item label="验证码" prop="verificationCode">
              <div class="verification-code-container">
                <el-input v-model="emailForm.verificationCode" placeholder="请输入验证码"></el-input>
                <button 
                  class="get-code-btn" 
                  @click="sendEmailVerificationCode"
                  :disabled="isSendingCode || countdown > 0"
                >
                  {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
                </button>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeEmailModal">取消</button>
          <button class="modal-btn confirm" @click="bindEmail" :disabled="isUpdating">
            {{ isUpdating ? '处理中...' : '确认绑定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 清除缓存弹窗 -->
    <div v-if="showClearCacheConfirm" class="modal-overlay" @click="closeClearCacheModal">
      <div class="modal-content small" @click.stop>
        <div class="modal-body">
          <h3>清除缓存</h3>
          <p>确定要清除应用缓存吗？这将删除临时文件，但不会删除您的个人数据。</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeClearCacheModal">取消</button>
          <button class="modal-btn confirm danger" @click="clearCache">确认清除</button>
        </div>
      </div>
    </div>

    <!-- 删除账户弹窗 -->
    <div v-if="showDeleteAccountConfirm" class="modal-overlay" @click="closeDeleteAccountModal">
      <div class="modal-content small" @click.stop>
        <div class="modal-body">
          <h3 class="danger">删除账户</h3>
          <p>警告：删除账户后，所有个人数据将无法恢复。请谨慎操作！</p>
          <el-input 
            v-model="deleteAccountConfirmText" 
            placeholder="请输入'删除'以确认操作"
            class="confirm-text-input"
          ></el-input>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeDeleteAccountModal">取消</button>
          <button 
            class="modal-btn confirm danger" 
            @click="deleteAccount"
            :disabled="deleteAccountConfirmText !== '删除'"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 退出登录弹窗 -->
    <div v-if="showLogoutConfirm" class="modal-overlay" @click="closeLogoutModal">
      <div class="modal-content small" @click.stop>
        <div class="modal-body">
          <h3>退出登录</h3>
          <p>确定要退出当前账户吗？</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeLogoutModal">取消</button>
          <button class="modal-btn confirm" @click="logout">确认退出</button>
        </div>
      </div>
    </div>

    <!-- 操作成功提示 -->
    <div v-if="showSuccessToast" class="toast-overlay success">
      <div class="toast-content">
        <div class="toast-icon">✅</div>
        <span class="toast-message">{{ toastMessage }}</span>
      </div>
    </div>

    <!-- 操作失败提示 -->
    <div v-if="showErrorToast" class="toast-overlay error">
      <div class="toast-content">
        <div class="toast-icon">❌</div>
        <span class="toast-message">{{ toastMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { router } from '../router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 状态管理
const isLoading = ref(true)
const error = ref('')
const userInfo = ref({})
const notifications = ref({
  appointment_reminder: true,
  report_notification: true,
  health_reminder: true,
  system_notification: true
})
const privacy = ref({
  data_sharing: false
})
const cacheSize = ref('0.0')
const appVersion = ref('1.0.0')
const language = ref('zh-CN')
const languages = {
  'zh-CN': '简体中文',
  'en-US': 'English'
}

// 弹窗状态
const showPasswordModal = ref(false)
const showPhoneModal = ref(false)
const showEmailModal = ref(false)
const showClearCacheConfirm = ref(false)
const showDeleteAccountConfirm = ref(false)
const showLogoutConfirm = ref(false)
const showSuccessToast = ref(false)
const showErrorToast = ref(false)
const toastMessage = ref('')
const isUpdating = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)

// 表单数据
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const phoneForm = reactive({
  phoneNumber: '',
  verificationCode: ''
})

const emailForm = reactive({
  email: '',
  verificationCode: ''
})

const deleteAccountConfirmText = ref('')

// 表单验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const phoneRules = {
  phoneNumber: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{4,6}$/, message: '验证码格式不正确', trigger: 'blur' }
  ]
}

const emailRules = {
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的电子邮箱', trigger: 'blur' }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{4,6}$/, message: '验证码格式不正确', trigger: 'blur' }
  ]
}

// 获取设置信息
const fetchSettings = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    // 获取用户信息
    const userResponse = await axios.get('/api/v1/users/profile')
    if (userResponse.status === 'success' && userResponse.data) {
      userInfo.value = userResponse.data
    }
    
    // 获取通知设置
    const notificationResponse = await axios.get('/api/v1/users/settings/notifications')
    if (notificationResponse.status === 'success' && notificationResponse.data) {
      notifications.value = { ...notifications.value, ...notificationResponse.data }
    }
    
    // 获取隐私设置
    const privacyResponse = await axios.get('/api/v1/users/settings/privacy')
    if (privacyResponse.status === 'success' && privacyResponse.data) {
      privacy.value = { ...privacy.value, ...privacyResponse.data }
    }
    
    // 计算缓存大小（模拟）
    calculateCacheSize()
    
  } catch (err) {
    console.error('获取设置信息错误:', err)
    error.value = '网络错误，请检查您的网络连接'
    showToast('error', '获取设置信息失败')
  } finally {
    isLoading.value = false
  }
}

// 更新通知设置
const updateNotificationSetting = async (key, value) => {
  try {
    const response = await axios.put('/api/v1/users/settings/notifications', {
      [key]: value
    })
    
    if (response.status === 'success') {
      showToast('success', '通知设置已更新')
    } else {
      // 恢复原始值
      notifications.value[key] = !value
      showToast('error', '更新通知设置失败')
    }
  } catch (err) {
    console.error('更新通知设置错误:', err)
    // 恢复原始值
    notifications.value[key] = !value
    showToast('error', '网络错误，请检查您的网络连接')
  }
}

// 更新隐私设置
const updatePrivacySetting = async (key, value) => {
  try {
    const response = await axios.put('/api/v1/users/settings/privacy', {
      [key]: value
    })
    
    if (response.status === 'success') {
      showToast('success', '隐私设置已更新')
    } else {
      // 恢复原始值
      privacy.value[key] = !value
      showToast('error', '更新隐私设置失败')
    }
  } catch (err) {
    console.error('更新隐私设置错误:', err)
    // 恢复原始值
    privacy.value[key] = !value
    showToast('error', '网络错误，请检查您的网络连接')
  }
}

// 更新语言设置
const updateLanguage = async () => {
  try {
    const response = await axios.put('/api/v1/users/settings/language', {
      language: language.value
    })
    
    if (response.status === 'success') {
      showToast('success', '语言设置已更新')
    } else {
      showToast('error', '更新语言设置失败')
    }
  } catch (err) {
    console.error('更新语言设置错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  }
}

// 修改密码
const changePassword = async () => {
  try {
    // 表单验证
    const formEl = document.querySelector('.passwordForm')
    if (formEl && formEl.validate) {
      const isValid = await formEl.validate()
      if (!isValid) return
    }
    
    isUpdating.value = true
    
    const response = await axios.put('/api/v1/users/settings/password', passwordForm)
    
    if (response.status === 'success') {
      showToast('success', '密码修改成功')
      closePasswordModal()
      
      // 清空表单
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      showToast('error', response.message || '密码修改失败')
    }
  } catch (err) {
    console.error('修改密码错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isUpdating.value = false
  }
}

// 发送手机验证码
const sendPhoneVerificationCode = async () => {
  if (!phoneForm.phoneNumber) {
    showToast('error', '请输入手机号码')
    return
  }
  
  try {
    isSendingCode.value = true
    
    const response = await axios.post('/api/v1/auth/send-sms-code', {
      phone_number: phoneForm.phoneNumber
    })
    
    if (response.status === 'success') {
      showToast('success', '验证码已发送')
      startCountdown()
    } else {
      showToast('error', response.message || '发送验证码失败')
    }
  } catch (err) {
    console.error('发送手机验证码错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isSendingCode.value = false
  }
}

// 发送邮箱验证码
const sendEmailVerificationCode = async () => {
  if (!emailForm.email) {
    showToast('error', '请输入电子邮箱')
    return
  }
  
  try {
    isSendingCode.value = true
    
    const response = await axios.post('/api/v1/auth/send-email-code', {
      email: emailForm.email
    })
    
    if (response.status === 'success') {
      showToast('success', '验证码已发送')
      startCountdown()
    } else {
      showToast('error', response.message || '发送验证码失败')
    }
  } catch (err) {
    console.error('发送邮箱验证码错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isSendingCode.value = false
  }
}

// 绑定手机号
const bindPhone = async () => {
  try {
    // 表单验证
    const formEl = document.querySelector('.phoneForm')
    if (formEl && formEl.validate) {
      const isValid = await formEl.validate()
      if (!isValid) return
    }
    
    isUpdating.value = true
    
    const response = await axios.put('/api/v1/users/settings/phone', phoneForm)
    
    if (response.status === 'success') {
      showToast('success', userInfo.value?.phone_number ? '手机号修改成功' : '手机号绑定成功')
      userInfo.value.phone_number = phoneForm.phoneNumber
      closePhoneModal()
      
      // 清空表单
      phoneForm.phoneNumber = ''
      phoneForm.verificationCode = ''
    } else {
      showToast('error', response.message || '手机号绑定失败')
    }
  } catch (err) {
    console.error('绑定手机号错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isUpdating.value = false
  }
}

// 绑定邮箱
const bindEmail = async () => {
  try {
    // 表单验证
    const formEl = document.querySelector('.emailForm')
    if (formEl && formEl.validate) {
      const isValid = await formEl.validate()
      if (!isValid) return
    }
    
    isUpdating.value = true
    
    const response = await axios.put('/api/v1/users/settings/email', emailForm)
    
    if (response.status === 'success') {
      showToast('success', userInfo.value?.email ? '邮箱修改成功' : '邮箱绑定成功')
      userInfo.value.email = emailForm.email
      closeEmailModal()
      
      // 清空表单
      emailForm.email = ''
      emailForm.verificationCode = ''
    } else {
      showToast('error', response.message || '邮箱绑定失败')
    }
  } catch (err) {
    console.error('绑定邮箱错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isUpdating.value = false
  }
}

// 清除缓存
const clearCache = async () => {
  try {
    // 在实际应用中，这里应该调用清理缓存的API
    // 模拟清理缓存
    setTimeout(() => {
      cacheSize.value = '0.0'
      showToast('success', '缓存已清除')
      closeClearCacheModal()
    }, 1000)
  } catch (err) {
    console.error('清除缓存错误:', err)
    showToast('error', '清除缓存失败')
  }
}

// 删除账户
const deleteAccount = async () => {
  if (deleteAccountConfirmText.value !== '删除') {
    showToast('error', '请输入"删除"以确认操作')
    return
  }
  
  try {
    isUpdating.value = true
    
    const response = await axios.delete('/api/v1/users/account')
    
    if (response.status === 'success') {
      showToast('success', '账户已删除')
      // 退出登录并跳转到登录页
      logout(true)
    } else {
      showToast('error', response.message || '删除账户失败')
    }
  } catch (err) {
    console.error('删除账户错误:', err)
    showToast('error', '网络错误，请检查您的网络连接')
  } finally {
    isUpdating.value = false
    closeDeleteAccountModal()
    deleteAccountConfirmText.value = ''
  }
}

// 退出登录
const logout = async (isAccountDeleted = false) => {
  try {
    // 在实际应用中，这里应该调用退出登录的API
    
    // 清除本地存储的用户信息和token
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('userInfo')
    
    // 跳转到登录页
    router.replace('/login')
    
    if (!isAccountDeleted) {
      showToast('success', '已成功退出登录')
    }
  } catch (err) {
    console.error('退出登录错误:', err)
    // 即使出错也跳转到登录页
    router.replace('/login')
  } finally {
    closeLogoutModal()
  }
}

// 检查更新
const checkForUpdates = async () => {
  try {
    // 在实际应用中，这里应该调用检查更新的API
    // 模拟检查更新
    showToast('success', '已是最新版本')
  } catch (err) {
    console.error('检查更新错误:', err)
    showToast('error', '检查更新失败')
  }
}

// 关于我们
const aboutUs = () => {
  // 可以跳转到关于我们页面，这里简单显示一个提示
  ElMessage.info(`医院体检项目智能推荐系统\n版本: v${appVersion.value}\n版权所有 © 2023`)
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 计算缓存大小（模拟）
const calculateCacheSize = () => {
  // 模拟计算缓存大小
  cacheSize.value = (Math.random() * 10).toFixed(1)
}

// 导航到其他页面
const navigateToPage = (path) => {
  router.push(path)
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 显示操作提示
const showToast = (type, message) => {
  toastMessage.value = message
  
  if (type === 'success') {
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
  } else if (type === 'error') {
    showErrorToast.value = true
    setTimeout(() => {
      showErrorToast.value = false
    }, 3000)
  }
}

// 弹窗控制函数
const showChangePasswordModal = () => {
  showPasswordModal.value = true
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  
  // 重置表单验证
  const formEl = document.querySelector('.passwordForm')
  if (formEl && formEl.resetFields) {
    formEl.resetFields()
  }
}

const showBindPhoneModal = () => {
  showPhoneModal.value = true
}

const closePhoneModal = () => {
  showPhoneModal.value = false
  phoneForm.phoneNumber = ''
  phoneForm.verificationCode = ''
  
  // 重置表单验证
  const formEl = document.querySelector('.phoneForm')
  if (formEl && formEl.resetFields) {
    formEl.resetFields()
  }
}

const showBindEmailModal = () => {
  showEmailModal.value = true
}

const closeEmailModal = () => {
  showEmailModal.value = false
  emailForm.email = ''
  emailForm.verificationCode = ''
  
  // 重置表单验证
  const formEl = document.querySelector('.emailForm')
  if (formEl && formEl.resetFields) {
    formEl.resetFields()
  }
}

const showClearCacheModal = () => {
  showClearCacheConfirm.value = true
}

const closeClearCacheModal = () => {
  showClearCacheConfirm.value = false
}

const showDeleteAccountModal = () => {
  showDeleteAccountConfirm.value = true
  deleteAccountConfirmText.value = ''
}

const closeDeleteAccountModal = () => {
  showDeleteAccountConfirm.value = false
  deleteAccountConfirmText.value = ''
}

const showLogoutModal = () => {
  showLogoutConfirm.value = true
}

const closeLogoutModal = () => {
  showLogoutConfirm.value = false
}

// 格式化手机号
const formatPhoneNumber = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1****$3')
}

// 格式化邮箱
const formatEmail = (email) => {
  if (!email) return ''
  const [username, domain] = email.split('@')
  const maskedUsername = username.charAt(0) + '***' + username.charAt(username.length - 1)
  return maskedUsername + '@' + domain
}

// 组件挂载时获取设置信息
onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
/* 系统设置页面样式 */
:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  --text-color: #333;
  --text-secondary: #666;
  --text-tertiary: #999;
  --border-color: #d9d9d9;
  --background-color: #f5f5f5;
  --card-background: #fff;
}

.system-settings {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--background-color);
}

/* 顶部导航栏 */
.top-nav {
  background-color: var(--primary-color);
  color: white;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  margin-right: 16px;
  padding: 4px 8px;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-container p {
  color: var(--text-secondary);
  margin-bottom: 20px;
  font-size: 14px;
}

.retry-btn {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.retry-btn:hover {
  background-color: var(--primary-dark);
}

/* 设置容器 */
.settings-container {
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
}

/* 设置区块 */
.settings-section {
  margin-bottom: 24px;
}

.section-title {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: normal;
  margin-bottom: 12px;
  padding: 0 16px;
}

.settings-group {
  background-color: var(--card-background);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

/* 设置项 */
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background-color: var(--background-color);
}

.setting-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.setting-info.danger {
  color: var(--error-color);
}

.setting-icon {
  font-size: 20px;
  margin-right: 16px;
  width: 24px;
  text-align: center;
}

.setting-name {
  color: var(--text-color);
  font-size: 16px;
  margin-right: 8px;
}

.setting-desc {
  color: var(--text-tertiary);
  font-size: 12px;
}

.setting-value {
  color: var(--text-tertiary);
  font-size: 14px;
  margin-left: 8px;
}

.setting-hint {
  color: var(--warning-color);
  font-size: 14px;
  margin-left: 8px;
}

.setting-arrow {
  color: var(--text-tertiary);
  font-size: 14px;
}

.setting-select {
  width: 120px;
}

/* 退出登录按钮 */
.logout-container {
  margin-top: 32px;
  padding: 0 16px;
}

.logout-btn {
  width: 100%;
  padding: 12px;
  background-color: var(--card-background);
  color: var(--error-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background-color: #fff1f0;
  border-color: var(--error-color);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalFadeIn 0.3s ease-in-out;
}

.modal-content.small {
  max-width: 400px;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 18px;
}

.modal-header h3.danger {
  color: var(--error-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background-color: var(--background-color);
  color: var(--text-secondary);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

.modal-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.modal-btn.cancel {
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.modal-btn.cancel:hover {
  background-color: var(--border-color);
}

.modal-btn.confirm {
  background-color: var(--primary-color);
  color: white;
}

.modal-btn.confirm:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.modal-btn.confirm.danger {
  background-color: var(--error-color);
}

.modal-btn.confirm.danger:hover:not(:disabled) {
  background-color: #cf1322;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 验证码输入框容器 */
.verification-code-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.verification-code-container .el-input {
  flex: 1;
}

.get-code-btn {
  padding: 10px 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.get-code-btn:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.get-code-btn:disabled {
  background-color: var(--border-color);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

/* 确认文本输入框 */
.confirm-text-input {
  margin-top: 16px;
}

/* 语言选择器弹出层 */
.language-select-popper {
  min-width: 120px;
}

/* 提示框样式 */
.toast-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2000;
  animation: toastFadeIn 0.3s ease-in-out;
}

@keyframes toastFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.toast-overlay.success .toast-content {
  background-color: rgba(82, 196, 26, 0.9);
  color: white;
}

.toast-overlay.error .toast-content {
  background-color: rgba(245, 34, 45, 0.9);
  color: white;
}

.toast-icon {
  font-size: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 12px;
  }
  
  .settings-container {
    width: 100%;
  }
  
  .modal-content {
    width: 95%;
    margin: 0 10px;
  }
  
  .setting-item {
    padding: 14px 12px;
  }
  
  .setting-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .setting-name {
    margin-right: 0;
  }
  
  .setting-desc {
    margin-left: 40px;
  }
}
</style>