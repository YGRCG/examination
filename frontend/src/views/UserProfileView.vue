<template>
  <div class="user-profile-container">
    <div class="progress-bar">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in mainSteps" 
          :key="index"
          :class="['progress-step', { active: currentMainStep === index, completed: index < currentMainStep }]"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-title">{{ step.title }}</div>
        </div>
      </div>
    </div>

    <div class="interaction-area">
      <div class="chat-container">
        <div class="chat-messages" ref="chatMessages">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="['message', message.sender === 'user' ? 'user-message' : 'ai-message']"
          >
            <div class="message-content">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <div v-if="isTyping" class="typing-indicator">
          <span>AI正在思考中</span>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div class="input-area">
          <div v-if="currentStepType === 'multiple-choice' && currentOptions" class="options-container">
            <button 
              v-for="(option, index) in currentOptions" 
              :key="index"
              @click="selectOption(option)"
              class="option-button"
            >
              {{ option.text }}
            </button>
          </div>
          
          <div v-else class="text-input-container">
            <textarea
              v-model="userInput"
              placeholder="请输入您的回答..."
              @keydown.enter.prevent="sendMessage"
              :disabled="isProcessing"
              rows="3"
            ></textarea>
            <button 
              @click="sendMessage" 
              :disabled="isProcessing || !userInput.trim()"
              class="send-button"
            >
              发送
            </button>
          </div>
        </div>
      </div>

      <div class="profile-summary">
        <h3>用户画像信息</h3>
        <div class="summary-sections">
          <!-- 基本信息 -->
          <div v-if="profileData.basic_info && Object.keys(profileData.basic_info).length > 0" class="summary-section">
            <h4>基本信息</h4>
            <div class="section-content">
              <div v-for="(value, key) in profileData.basic_info" :key="key" class="profile-item">
                <span class="item-label">{{ getFieldLabel(key) }}:</span>
                <span class="item-value">{{ formatFieldValue(key, value) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 健康史 -->
          <div v-if="profileData.health_history && profileData.health_history.length > 0" class="summary-section">
            <h4>健康史</h4>
            <div class="section-content">
              <div v-for="(item, index) in profileData.health_history" :key="index" class="profile-item">
                <div v-if="typeof item === 'object'">
                  <span v-for="(value, itemKey) in item" :key="itemKey">
                    <span class="item-label">{{ getFieldLabel(itemKey) }}:</span>
                    <span class="item-value">{{ value }}</span>
                  </span>
                </div>
                <div v-else>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 生活习惯 -->
          <div v-if="profileData.lifestyle && Object.keys(profileData.lifestyle).length > 0" class="summary-section">
            <h4>生活习惯</h4>
            <div class="section-content">
              <div v-for="(value, key) in profileData.lifestyle" :key="key" class="profile-item">
                <span class="item-label">{{ getFieldLabel(key) }}:</span>
                <span class="item-value">{{ formatFieldValue(key, value) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 症状 -->
          <div v-if="profileData.symptoms && profileData.symptoms.length > 0" class="summary-section">
            <h4>不适症状</h4>
            <div class="section-content">
              <div v-for="(item, index) in profileData.symptoms" :key="index" class="profile-item">
                <div v-if="typeof item === 'object'">
                  <span v-for="(value, itemKey) in item" :key="itemKey">
                    <span class="item-label">{{ getFieldLabel(itemKey) }}:</span>
                    <span class="item-value">{{ value }}</span>
                  </span>
                </div>
                <div v-else>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 体检报告 -->
          <div v-if="profileData.medical_reports && profileData.medical_reports.length > 0" class="summary-section">
            <h4>历史体检报告</h4>
            <div class="section-content">
              <div v-for="(item, index) in profileData.medical_reports" :key="index" class="profile-item">
                <div v-if="typeof item === 'object'">
                  <span v-for="(value, itemKey) in item" :key="itemKey">
                    <span class="item-label">{{ getFieldLabel(itemKey) }}:</span>
                    <span class="item-value">{{ value }}</span>
                  </span>
                </div>
                <div v-else>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 重点关注 -->
          <div v-if="profileData.focus_areas && profileData.focus_areas.length > 0" class="summary-section">
            <h4>重点关注</h4>
            <div class="section-content">
              <div v-for="(item, index) in profileData.focus_areas" :key="index" class="profile-item">
                <div v-if="typeof item === 'object'">
                  <span v-for="(value, itemKey) in item" :key="itemKey">
                    <span class="item-label">{{ getFieldLabel(itemKey) }}:</span>
                    <span class="item-value">{{ value }}</span>
                  </span>
                </div>
                <div v-else>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 如果没有数据 -->
          <div v-if="!hasProfileData" class="no-data">
            <p>暂无用户画像数据</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { userProfileAPI } from '@/api/userProfile'

export default {
  name: 'UserProfileView',
  setup() {
    // 主流程步骤
    const mainSteps = [
      { id: 'basic_info', title: '基本信息', required: true },
      { id: 'health_history', title: '健康史', required: false },
      { id: 'lifestyle', title: '生活习惯', required: false },
      { id: 'symptoms', title: '不适症状', required: false },
      { id: 'medical_reports', title: '历史体检报告', required: false },
      { id: 'focus_areas', title: '重点关注', required: false }
    ]

    // 当前状态
    const currentMainStep = ref(0)
    const currentSubStep = ref(0)
    const isAiSubProcess = ref(false)
    const currentStepType = ref('text') // 'text', 'multiple-choice'
    const currentOptions = ref([])
    
    // UI状态
    const messages = ref([])
    const userInput = ref('')
    const isTyping = ref(false)
    const isProcessing = ref(false)
    const chatMessages = ref(null)
    
    // 用户画像数据
    const profileData = reactive({
      basic_info: {},
      health_history: [],
      lifestyle: {},
      symptoms: [],
      medical_reports: [],
      focus_areas: []
    })

    // 获取步骤标题
    const getSectionTitle = (key) => {
      const titles = {
        basic_info: '基本信息',
        health_history: '健康史',
        lifestyle: '生活习惯',
        symptoms: '不适症状',
        medical_reports: '历史体检报告',
        focus_areas: '重点关注'
      }
      return titles[key] || key
    }

    // 检查是否有用户画像数据
    const hasProfileData = computed(() => {
      if (!profileData) return false;
      
      // 检查各个部分是否有数据
      const hasBasicInfo = profileData.basic_info && Object.keys(profileData.basic_info).length > 0;
      const hasHealthHistory = profileData.health_history && profileData.health_history.length > 0;
      const hasLifestyle = profileData.lifestyle && Object.keys(profileData.lifestyle).length > 0;
      const hasSymptoms = profileData.symptoms && profileData.symptoms.length > 0;
      const hasMedicalReports = profileData.medical_reports && profileData.medical_reports.length > 0;
      const hasFocusAreas = profileData.focus_areas && profileData.focus_areas.length > 0;
      
      return hasBasicInfo || hasHealthHistory || hasLifestyle || hasSymptoms || hasMedicalReports || hasFocusAreas;
    });

    // 获取字段标签
    const getFieldLabel = (key) => {
      const fieldLabels = {
        // 基本信息
        'name': '姓名',
        'age': '年龄',
        'gender': '性别',
        'height': '身高',
        'weight': '体重',
        'occupation': '职业',
        'marital_status': '婚姻状况',
        'education': '教育程度',
        'residence': '居住地',
        
        // 健康史
        'condition': '疾病',
        'duration': '持续时间',
        'medication': '用药情况',
        'family_history': '家族病史',
        'allergies': '过敏史',
        'past_surgeries': '手术史',
        'chronic_conditions': '慢性疾病',
        
        // 生活习惯
        'exercise': '运动频率',
        'diet': '饮食习惯',
        'smoking': '吸烟情况',
        'drinking': '饮酒情况',
        'sleep': '睡眠情况',
        'stress': '压力水平',
        
        // 症状
        'symptom': '症状',
        'severity': '严重程度',
        'frequency': '频率',
        'triggers': '诱因',
        
        // 体检报告
        'report_type': '报告类型',
        'report_date': '报告日期',
        'result': '结果',
        'abnormal_findings': '异常发现',
        
        // 重点关注
        'area': '关注领域',
        'priority': '优先级',
        'notes': '备注'
      };
      
      return fieldLabels[key] || key;
    };

    // 格式化字段值
    const formatFieldValue = (key, value) => {
      // 处理特殊字段
      if (key === 'gender') {
        return value === 'male' ? '男' : value === 'female' ? '女' : value;
      }
      
      if (key === 'marital_status') {
        const statusMap = {
          'single': '未婚',
          'married': '已婚',
          'divorced': '离异',
          'widowed': '丧偶'
        };
        return statusMap[value] || value;
      }
      
      if (key === 'severity') {
        const severityMap = {
          'mild': '轻度',
          'moderate': '中度',
          'severe': '重度'
        };
        return severityMap[value] || value;
      }
      
      if (key === 'priority') {
        const priorityMap = {
          'low': '低',
          'medium': '中',
          'high': '高'
        };
        return priorityMap[value] || value;
      }
      
      // 处理日期字段
      if (key.includes('date') || key.includes('time')) {
        try {
          return new Date(value).toLocaleDateString();
        } catch (e) {
          return value;
        }
      }
      
      // 处理布尔值
      if (typeof value === 'boolean') {
        return value ? '是' : '否';
      }
      
      // 处理数组
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      
      // 默认返回原值
      return value;
    };

    // 格式化时间
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (chatMessages.value) {
          chatMessages.value.scrollTop = chatMessages.value.scrollHeight
        }
      })
    }

    // 添加消息
    const addMessage = (content, sender = 'user') => {
      messages.value.push({
        content,
        sender,
        timestamp: new Date()
      })
      scrollToBottom()
    }

    // 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isProcessing.value) return
  
  const userMessage = userInput.value.trim()
  userInput.value = ''
  
  // 添加用户消息
  addMessage(userMessage, 'user')
  
  // 设置处理状态
  isProcessing.value = true
  isTyping.value = true
  
  try {
    // 调用后端API处理用户输入
    const response = await userProfileAPI.processInput({
      main_step: mainSteps[currentMainStep.value].id,
      sub_step: currentSubStep.value,
      is_ai_sub_process: isAiSubProcess.value,
      user_input: userMessage,
      current_profile: profileData
    })
    
    // 处理响应
    handleResponse(response)
  } catch (error) {
    console.error('处理用户输入失败:', error)
    
    // 显示友好的错误消息
    let errorMessage = '抱歉，处理您的输入时出现了问题。'
    
    // 根据错误类型提供更具体的消息
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      
      if (status === 400) {
        errorMessage = '请求格式不正确，请检查您的输入。'
      } else if (status === 401) {
        errorMessage = '您的登录状态已过期，请重新登录。'
      } else if (status === 403) {
        errorMessage = '您没有权限执行此操作。'
      } else if (status === 404) {
        errorMessage = '请求的资源不存在。'
      } else if (status >= 500) {
        errorMessage = '服务器内部错误，请稍后再试。'
      }
      
      // 如果服务器返回了具体的错误消息，使用它
      if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '无法连接到服务器，请检查您的网络连接。'
    } else {
      // 请求设置出错
      errorMessage = '请求设置出错，请稍后再试。'
    }
    
    // 添加错误消息
    addMessage(errorMessage, 'ai')
    
    // 如果是网络错误，提供重试选项
    if (error.message && error.message.includes('Network Error')) {
      setTimeout(() => {
        addMessage('您是否想要重新发送您的消息？如果是，请重新输入。', 'ai')
      }, 1000)
    }
  } finally {
    isProcessing.value = false
    isTyping.value = false
  }
}

    // 处理API响应
    const handleResponse = (response) => {
      // 添加AI消息
      if (response.message) {
        addMessage(response.message, 'ai')
      }
      
      // 更新步骤类型和选项
      if (response.step_type) {
        currentStepType.value = response.step_type
      }
      
      if (response.options) {
        currentOptions.value = response.options
      } else {
        currentOptions.value = []
      }
      
      // 更新用户画像数据
      if (response.profile_update) {
        Object.assign(profileData, response.profile_update)
      }
      
      // 更新流程状态
      if (response.next_step) {
        if (response.next_step === 'next_main') {
          // 进入下一个主流程步骤
          currentMainStep.value += 1
          currentSubStep.value = 0
          isAiSubProcess.value = false
        } else if (response.next_step === 'ai_sub_process') {
          // 进入AI动态子流程
          isAiSubProcess.value = true
        } else if (typeof response.next_step === 'number') {
          // 更新子步骤
          currentSubStep.value = response.next_step
        } else if (response.next_step === 'complete') {
          // 完成用户画像收集
          completeProfile()
        }
      }
    }

    // 选择选项
    const selectOption = (option) => {
      userInput.value = option.value
      sendMessage()
    }

    // 完成用户画像收集
const completeProfile = async () => {
  addMessage('感谢您的配合，您的用户画像已收集完成！', 'ai')
  
  try {
    isProcessing.value = true
    
    // 保存用户画像到后端
    const response = await userProfileAPI.saveProfile(profileData)
    
    // 处理API响应格式
    let responseData = response
    if (response && response.data) {
      responseData = response.data
    }
    
    if (responseData && responseData.message) {
      addMessage(responseData.message, 'ai')
    } else {
      addMessage('用户画像已成功保存！', 'ai')
    }
    
    // 显示完成消息
    addMessage('健康画像收集已完成！您现在可以查看您的健康画像，或者开始进行健康评估。', 'ai')
  } catch (error) {
    console.error('保存用户画像失败:', error)
    
    // 显示友好的错误消息
    let errorMessage = '抱歉，保存您的健康画像时遇到了问题。'
    
    // 根据错误类型提供更具体的消息
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      
      if (status === 400) {
        errorMessage = '提供的数据格式不正确，请检查您填写的信息。'
      } else if (status === 401) {
        errorMessage = '您的登录状态已过期，请重新登录。'
      } else if (status === 403) {
        errorMessage = '您没有权限保存健康画像。'
      } else if (status === 404) {
        errorMessage = '健康画像服务不可用，请稍后再试。'
      } else if (status >= 500) {
        errorMessage = '服务器内部错误，请稍后再试。'
      }
      
      // 如果服务器返回了具体的错误消息，使用它
      if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '无法连接到服务器，请检查您的网络连接。'
    } else {
      // 请求设置出错
      errorMessage = '保存请求设置出错，请稍后再试。'
    }
    
    // 添加错误消息并提供重试选项
    addMessage(errorMessage, 'ai')
    addMessage('您可以稍后再试保存，或者继续完善您的健康画像信息。', 'ai')
    
    // 如果是网络错误，提供重试选项
    if (error.message && error.message.includes('Network Error')) {
      setTimeout(() => {
        addMessage('您是否想要重新尝试保存？如果是，请再次点击完成按钮。', 'ai')
      }, 1000)
    }
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

    // 初始化对话
const initializeConversation = async () => {
  isTyping.value = true
  
  try {
    // 先尝试获取已保存的用户画像
    try {
      const savedProfile = await userProfileAPI.getProfile()
      if (savedProfile && savedProfile.data) {
        // 处理API响应格式
        let profileDataToLoad = savedProfile.data
        
        // 如果是ApiResponse格式，提取data字段
        if (profileDataToLoad.data) {
          profileDataToLoad = profileDataToLoad.data
        }
        
        // 只更新profileData中需要的字段，过滤掉user_id等额外字段
        const { user_id, created_at, updated_at, ...profileFields } = profileDataToLoad
        Object.assign(profileData, profileFields)
        addMessage('已加载您保存的用户画像信息。', 'ai')
      }
    } catch (profileError) {
      console.log('没有找到已保存的用户画像，开始新的收集流程')
    }
    
    // 初始化对话流程
    const response = await userProfileAPI.initializeProfile()
    handleResponse(response)
  } catch (error) {
    console.error('初始化对话失败:', error)
    
    // 显示友好的错误消息
    let errorMessage = '抱歉，初始化对话时出现了问题。'
    
    // 根据错误类型提供更具体的消息
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      
      if (status === 400) {
        errorMessage = '请求格式不正确，请刷新页面重试。'
      } else if (status === 401) {
        errorMessage = '您的登录状态已过期，请重新登录。'
      } else if (status === 403) {
        errorMessage = '您没有权限执行此操作。'
      } else if (status === 404) {
        errorMessage = '请求的资源不存在。'
      } else if (status >= 500) {
        errorMessage = '服务器内部错误，请稍后再试。'
      }
      
      // 如果服务器返回了具体的错误消息，使用它
      if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '无法连接到服务器，请检查您的网络连接。'
    } else {
      // 请求设置出错
      errorMessage = '请求设置出错，请稍后再试。'
    }
    
    // 添加错误消息
    addMessage(errorMessage, 'ai')
    
    // 如果是网络错误，提供重试选项
    if (error.message && error.message.includes('Network Error')) {
      setTimeout(() => {
        addMessage('您是否想要重新尝试初始化？如果是，请刷新页面。', 'ai')
      }, 1000)
    }
  } finally {
    isTyping.value = false
  }
}

    onMounted(() => {
      initializeConversation()
    })

    return {
      mainSteps,
      currentMainStep,
      currentSubStep,
      isAiSubProcess,
      currentStepType,
      currentOptions,
      messages,
      userInput,
      isTyping,
      isProcessing,
      chatMessages,
      profileData,
      getSectionTitle,
      formatTime,
      sendMessage,
      selectOption
    }
  }
}
</script>

<style scoped>
.user-profile-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
}

.progress-bar {
  margin-bottom: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  max-width: 800px;
  margin: 0 auto;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}

.progress-step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 20px;
  left: 60%;
  width: 80%;
  height: 2px;
  background-color: #e1e5e9;
  z-index: 1;
}

.progress-step.completed:not(:last-child)::after {
  background-color: #4caf50;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e1e5e9;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
}

.progress-step.active .step-number {
  background-color: #2196f3;
  color: white;
}

.progress-step.completed .step-number {
  background-color: #4caf50;
  color: white;
}

.step-title {
  font-size: 12px;
  text-align: center;
  color: #6c757d;
}

.progress-step.active .step-title {
  color: #2196f3;
  font-weight: bold;
}

.interaction-area {
  display: flex;
  flex: 1;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.chat-container {
  flex: 2;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 500px;
}

.message {
  margin-bottom: 15px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px 15px;
  border-radius: 18px;
  word-wrap: break-word;
}

.user-message .message-content {
  background-color: #2196f3;
  color: white;
  border-bottom-right-radius: 5px;
}

.ai-message .message-content {
  background-color: #f1f1f1;
  color: #333;
  border-bottom-left-radius: 5px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 5px;
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  margin-bottom: 15px;
  margin-right: auto;
  max-width: 80%;
}

.typing-dots {
  display: flex;
  margin-left: 10px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-area {
  padding: 15px;
  border-top: 1px solid #e1e5e9;
}

.options-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option-button {
  padding: 8px 16px;
  border: 1px solid #2196f3;
  background-color: white;
  color: #2196f3;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-button:hover {
  background-color: #2196f3;
  color: white;
}

.text-input-container {
  display: flex;
  gap: 10px;
}

.text-input-container textarea {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 18px;
  padding: 10px 15px;
  resize: none;
  font-family: inherit;
  outline: none;
}

.send-button {
  padding: 10px 20px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 18px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #0d8aee;
}

.send-button:disabled {
  background-color: #b6d5f1;
  cursor: not-allowed;
}

.profile-summary {
  flex: 1;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow-y: auto;
  max-height: 600px;
  border: 1px solid #e0e0e0;
}

.profile-summary h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.summary-sections {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-section {
  background-color: white;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #eee;
}

.summary-section h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  padding-bottom: 6px;
}

.section-content {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 5px;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-item {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 4px 0;
  border-bottom: 1px dashed #f0f0f0;
}

.profile-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.item-label {
  font-weight: 600;
  color: #555;
  min-width: 80px;
  flex-shrink: 0;
}

.item-value {
  color: #333;
  word-break: break-word;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #999;
  font-style: italic;
}

@media (max-width: 768px) {
  .interaction-area {
    flex-direction: column;
  }
  
  .chat-container, .profile-summary {
    flex: 1;
    width: 100%;
  }
  
  .progress-steps {
    flex-wrap: wrap;
  }
  
  .step-title {
    font-size: 10px;
  }
}
</style>