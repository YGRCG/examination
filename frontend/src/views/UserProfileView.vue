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
          <div v-for="(section, key) in profileData" :key="key" class="summary-section">
            <h4>{{ getSectionTitle(key) }}</h4>
            <div class="section-content">
              <div v-if="Array.isArray(section)">
                <div v-for="(item, index) in section" :key="index" class="profile-item">
                  <span v-for="(value, itemKey) in item" :key="itemKey">
                    {{ itemKey }}: {{ value }}<br>
                  </span>
                </div>
              </div>
              <div v-else>
                {{ section }}
              </div>
            </div>
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
        addMessage('抱歉，处理您的输入时出现了问题，请稍后再试。', 'ai')
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
        // 保存用户画像到后端
        await userProfileAPI.saveProfile(profileData)
        addMessage('用户画像已成功保存！', 'ai')
      } catch (error) {
        console.error('保存用户画像失败:', error)
        addMessage('保存用户画像时出现问题，请稍后再试。', 'ai')
      }
    }

    // 初始化对话
    const initializeConversation = async () => {
      isTyping.value = true
      
      try {
        const response = await userProfileAPI.initializeProfile()
        handleResponse(response)
      } catch (error) {
        console.error('初始化对话失败:', error)
        addMessage('抱歉，初始化对话时出现了问题，请刷新页面重试。', 'ai')
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
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow-y: auto;
  max-height: 600px;
}

.profile-summary h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.summary-sections {
  margin-top: 15px;
}

.summary-section {
  margin-bottom: 20px;
}

.summary-section h4 {
  margin: 0 0 10px 0;
  color: #2196f3;
  font-size: 16px;
}

.section-content {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 5px;
  font-size: 14px;
}

.profile-item {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #eee;
}

.profile-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
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