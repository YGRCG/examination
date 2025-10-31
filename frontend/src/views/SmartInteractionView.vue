<template>
  <div class="user-profile-chat">
    <!-- 顶部导航栏 -->
    <header class="chat-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">← 返回</button>
      </div>
      <div class="header-center">
        <h2>健康助手</h2>
      </div>
      <div class="header-right">
      </div>
    </header>

    <!-- 聊天消息区域 -->
    <main class="chat-messages" ref="chatMessages">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="message-bubble assistant">
          <div class="message-content">
            <p>您好！我是您的健康助手，为了给您提供更精准的健康建议，我需要了解一些基本信息。</p>
            <p>整个过程大约需要3-5分钟，您提供的所有信息都将被严格保密。</p>
            <p>让我们开始吧！首先，请告诉我您的年龄、性别和婚姻状况？</p>
          </div>
        </div>
      </div>

      <!-- 对话消息 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
        <div class="message-bubble" :class="message.sender">
          <div class="message-content" v-html="message.content"></div>
          <div class="message-time">{{ formatTime(message.time) }}</div>
          
          <!-- 消息按钮 -->
          <div v-if="message.hasButtons" class="message-buttons">
            <button 
              v-for="button in message.buttons" 
              :key="button.action"
              class="action-btn"
              :class="button.action === 'viewProfile' ? 'primary-btn' : 'secondary-btn'"
              @click="handleButtonClick(button.action)"
            >
              {{ button.text }}
            </button>
          </div>
        </div>
      </div>

      <!-- 正在输入提示 -->
      <div v-if="isAssistantTyping" class="typing-indicator">
        <div class="message-bubble assistant">
          <div class="typing-animation">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="chat-input-area">
      <div class="input-container">
        <input
          ref="inputRef"
          v-model="userInput"
          type="text"
          placeholder="请输入您的回答..."
          @keyup.enter="sendMessage"
          :disabled="isAssistantTyping"
        />
        <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim() || isAssistantTyping">
          发送
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

// 路由
const router = useRouter()

// 状态管理
const userInput = ref('')
const messages = ref([])
const isAssistantTyping = ref(false)
const chatMessages = ref(null)
const inputRef = ref(null) // 添加输入框的引用

// 用户画像数据
const userProfile = ref({
  basicInfo: {
    age: '',
    gender: '',
    marital_status: ''
  },      // 基本信息
  healthHistory: {},  // 健康史
  lifestyle: {},      // 生活习惯
  symptoms: [],       // 不适症状
  medicalReports: {}, // 历史体检报告
  concerns: {}        // 重点关注
})

// 主流程状态机
const ProfileSteps = {
  BASIC_INFO: 'basic_info',           // 基本信息（必填）
  HEALTH_HISTORY: 'health_history',   // 健康史（重要可选）
  LIFESTYLE: 'lifestyle',             // 生活习惯（可选）
  SYMPTOMS: 'symptoms',               // 不适症状（可选）
  MEDICAL_REPORTS: 'medical_reports', // 历史体检报告（可选）
  CONCERNS: 'concerns',               // 重点关注（可选）
  COMPLETED: 'completed'              // 完成
}

// 当前状态
const currentStep = ref(ProfileSteps.BASIC_INFO)
const subStepIndex = ref(0)
const isDynamicSubProcess = ref(false) // 是否处于AI动态子流程

// 主流程步骤配置
const mainFlowSteps = [
  {
    id: ProfileSteps.BASIC_INFO,
    name: '基本信息',
    required: true,
    questions: [
      {
        id: 'age',
        question: '请告诉我您的年龄？',
        quickReplies: ['18-30岁', '31-40岁', '41-50岁', '51-60岁', '60岁以上']
      },
      {
        id: 'gender',
        question: '请告诉我您的性别？',
        quickReplies: ['男', '女']
      },
      {
        id: 'marital_status',
        question: '请告诉我您的婚姻状况？',
        quickReplies: ['未婚', '已婚', '离异', '丧偶']
      }
    ]
  },
  {
    id: ProfileSteps.HEALTH_HISTORY,
    name: '健康史',
    required: false,
    questions: [
      {
        id: 'chronic_diseases',
        question: '您是否有慢性疾病史（如高血压、糖尿病等）？',
        quickReplies: ['没有', '高血压', '糖尿病', '心脏病', '其他']
      }
    ]
  },
  {
    id: ProfileSteps.LIFESTYLE,
    name: '生活习惯',
    required: false,
    questions: [
      {
        id: 'exercise',
        question: '您平时的运动频率如何？',
        quickReplies: ['几乎不运动', '每周1-2次', '每周3-4次', '每天运动']
      },
      {
        id: 'smoking',
        question: '您有吸烟的习惯吗？',
        quickReplies: ['不吸烟', '偶尔吸烟', '每天吸烟']
      },
      {
        id: 'drinking',
        question: '您有饮酒的习惯吗？',
        quickReplies: ['不饮酒', '偶尔饮酒', '经常饮酒']
      }
    ]
  },
  {
    id: ProfileSteps.SYMPTOMS,
    name: '不适症状',
    required: false,
    questions: [
      {
        id: 'has_symptoms',
        question: '您最近是否有身体不适的症状？',
        quickReplies: ['没有不适', '有轻微不适', '有明显不适']
      }
    ]
  },
  {
    id: ProfileSteps.MEDICAL_REPORTS,
    name: '历史体检报告',
    required: false,
    questions: [
      {
        id: 'has_reports',
        question: '您是否有近期的体检报告？',
        quickReplies: ['没有', '有，在半年内', '有，在一年内', '有，超过一年']
      }
    ]
  },
  {
    id: ProfileSteps.CONCERNS,
    name: '重点关注',
    required: false,
    questions: [
      {
        id: 'health_concerns',
        question: '您最关注哪些健康问题？',
        quickReplies: ['心血管健康', '消化系统', '骨骼健康', '免疫力提升', '其他']
      }
    ]
  }
]

// 症状知识库 - 用于AI动态子流程
const symptomKnowledgeBase = {
  '头晕': {
    followUpQuestions: [
      '请问是眩晕（感觉天旋地转）还是昏沉（感觉头重脚轻）？',
      '这种情况持续多久了？',
      '在什么情况下容易诱发（比如起床、转头时）？'
    ],
    entities: ['type', 'duration', 'triggers']
  },
  '胃痛': {
    followUpQuestions: [
      '是胀痛、刺痛还是反酸？',
      '通常是在饭前还是饭后出现？',
      '是否伴有恶心、没胃口？'
    ],
    entities: ['pain_type', 'timing', 'accompanying_symptoms']
  },
  '胸闷': {
    followUpQuestions: [
      '是持续性的还是间歇性的？',
      '活动后会加重吗？',
      '是否伴有呼吸困难？'
    ],
    entities: ['pattern', 'exertion_relation', 'breathing_difficulty']
  },
  '疲劳': {
    followUpQuestions: [
      '是身体疲劳还是精神疲劳？',
      '这种情况持续多久了？',
      '休息后能缓解吗？'
    ],
    entities: ['fatigue_type', 'duration', 'relief_by_rest']
  }
}

// 计算属性
const currentStepConfig = computed(() => {
  return mainFlowSteps.find(step => step.id === currentStep.value)
})

const currentStepName = computed(() => {
  return currentStepConfig.value?.name || ''
})

const progressPercentage = computed(() => {
  const stepIndex = mainFlowSteps.findIndex(step => step.id === currentStep.value)
  return ((stepIndex + 1) / mainFlowSteps.length) * 100
})

const canSkipCurrentStep = computed(() => {
  return currentStepConfig.value && !currentStepConfig.value.required
})

const currentQuickReplies = computed(() => {
  if (isDynamicSubProcess.value) {
    // AI动态子流程的快捷回复
    return []
  }
  
  if (currentStepConfig.value && subStepIndex.value < currentStepConfig.value.questions.length) {
    return currentStepConfig.value.questions[subStepIndex.value].quickReplies
  }
  
  return []
})

// 方法
const goBack = () => {
  router.push('/')
}

const skipCurrentStep = () => {
  flowController.skipCurrentState()
}

const selectQuickReply = (reply) => {
  userInput.value = reply
  sendMessage()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

const formatTime = (date) => {
  if (!date) return ''
  const time = new Date(date)
  return time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const addMessage = (sender, content) => {
  messages.value.push({
    sender,
    content,
    time: new Date()
  })
  scrollToBottom()
}

const sendMessage = async () => {
  const messageText = userInput.value.trim()
  if (!messageText || isAssistantTyping.value) return

  // 添加用户消息
  addMessage('user', messageText)
  userInput.value = ''

  // 显示正在输入状态
  isAssistantTyping.value = true

  try {
    // 使用flowController处理用户回答
    await flowController.processUserAnswer(messageText)
  } catch (error) {
    console.error('处理消息错误:', error)
    addMessage('assistant', '抱歉，处理您的回答时出现了问题，请稍后再试。')
  } finally {
    isAssistantTyping.value = false
    // 重新聚焦到输入框
    nextTick(() => {
      if (inputRef.value) {
        inputRef.value.focus()
      }
    })
  }
}







const saveUserProfile = async () => {
  try {
    // 获取当前登录用户的用户名
    const username = localStorage.getItem('username') || ''
    
    // 确保数据格式与后端期望的一致
    const symptomsData = Array.isArray(userProfile.value.symptoms) 
      ? userProfile.value.symptoms 
      : (userProfile.value.symptoms?.data || [])
    
    // 将health_history对象转换为数组格式
    let healthHistoryArray = []
    if (userProfile.value.healthHistory && typeof userProfile.value.healthHistory === 'object') {
      // 将对象的每个属性转换为数组项
      Object.keys(userProfile.value.healthHistory).forEach(key => {
        if (userProfile.value.healthHistory[key]) {
          healthHistoryArray.push({
            type: key,
            value: userProfile.value.healthHistory[key]
          })
        }
      })
    }
    
    // 将concerns对象转换为数组格式
    let focusAreasArray = []
    if (userProfile.value.concerns && typeof userProfile.value.concerns === 'object') {
      // 将对象的每个属性转换为数组项
      Object.keys(userProfile.value.concerns).forEach(key => {
        if (userProfile.value.concerns[key]) {
          focusAreasArray.push({
            type: key,
            value: userProfile.value.concerns[key]
          })
        }
      })
    }
    
    // 不再发送user_id，让后端从JWT令牌中获取用户身份
    const response = await request.post('/api/v1/user-profile/', {
      basic_info: {
        ...userProfile.value.basicInfo,
        name: username  // 添加用户名到基本信息中
      },
      health_history: healthHistoryArray,
      lifestyle: userProfile.value.lifestyle || {},
      symptoms: symptomsData,
      medical_reports: Array.isArray(userProfile.value.medicalReports) 
        ? userProfile.value.medicalReports 
        : [],
      focus_areas: focusAreasArray
    })
    console.log('用户画像保存成功:', response)
  } catch (error) {
    console.error('保存用户画像失败:', error)
    // 添加错误处理，显示给用户
    addMessage('assistant', '抱歉，保存用户画像时出现错误，请稍后再试。')
  }
}

const viewProfileResult = async () => {
  // 在查看画像前先保存用户画像数据
  await saveUserProfile()
  router.push('/portrait-result')
}

const getRecommendations = () => {
  router.push('/recommendations')
}

// 处理按钮点击事件
const handleButtonClick = (action) => {
  if (action === 'viewProfile') {
    viewProfileResult()
  } else if (action === 'getRecommendations') {
    getRecommendations()
  }
}

// AI动态子流程状态管理
const dynamicSubProcessState = ref({
  currentSymptom: null,
  currentQuestionIndex: 0,
  symptomData: null,
  waitingForAnswer: false,
  resolveAnswer: null
})

// 状态机管理和流程控制逻辑
const stateMachine = {
  // 当前状态
  currentState: ProfileSteps.BASIC_INFO,
  
  // 状态转换
  transitionTo(newState) {
    this.currentState = newState
    currentStep.value = newState
  },
  
  // 获取当前状态配置
  getCurrentStateConfig() {
    return mainFlowSteps.find(step => step.id === this.currentState)
  },
  
  // 检查是否可以跳过当前状态
  canSkipCurrentState() {
    const config = this.getCurrentStateConfig()
    return config && !config.required
  },
  
  // 进入下一个状态
  moveToNext() {
    const currentIndex = mainFlowSteps.findIndex(step => step.id === this.currentState)
    if (currentIndex < mainFlowSteps.length - 1) {
      this.transitionTo(mainFlowSteps[currentIndex + 1].id)
      subStepIndex.value = 0 // 重置子步骤索引
      return true
    }
    return false
  },
  
  // 重置到初始状态
  reset() {
    this.transitionTo(ProfileSteps.BASIC_INFO)
    subStepIndex.value = 0
    isDynamicSubProcess.value = false
  }
}

// 流程控制逻辑
const flowController = {
  // 初始化流程
  initialize() {
    stateMachine.reset()
    this.sendWelcomeMessage()
  },
  
  // 发送欢迎消息
  sendWelcomeMessage() {
    addMessage('assistant', `
      <p>您好！我是您的健康助手，为了给您提供更精准的健康建议，我需要了解一些基本信息。</p>
      <p>整个过程大约需要3-5分钟，您提供的所有信息都将被严格保密。</p>
      <p>让我们开始吧！首先，请告诉我您的年龄？</p>
    `)
  },
  
  // 处理用户回答
  async processUserAnswer(answer) {
    if (isDynamicSubProcess.value) {
      // 处理AI动态子流程
      await this.handleDynamicSubProcessAnswer(answer)
    } else {
      // 处理主流程
      await this.handleMainFlowAnswer(answer)
    }
  },
  
  // 处理主流程回答
  async handleMainFlowAnswer(answer) {
    const config = stateMachine.getCurrentStateConfig()
    if (!config) return
    
    const currentQuestion = config.questions[subStepIndex.value]
    
    // 保存用户回答
    this.saveUserAnswer(currentQuestion.id, answer)
    
    // 特殊处理症状收集流程
    if (stateMachine.currentState === ProfileSteps.SYMPTOMS && 
        currentQuestion.id === 'has_symptoms') {
      // 如果用户回答没有症状，直接跳过症状收集
      if (answer === '没有不适' || answer === '没有' || answer === '无') {
        // 移动到下一个状态
        if (!stateMachine.moveToNext()) {
          // 所有状态已完成
          await this.completeProfileCollection()
        } else {
          // 发送下一个状态的第一个问题
          this.sendNextQuestion()
        }
        return
      } else {
        // 用户有症状，进入AI动态子流程
        isDynamicSubProcess.value = true
        await this.startSymptomInquiry()
        return
      }
    }
    
    // 移动到下一个问题或状态
    subStepIndex.value++
    
    if (subStepIndex.value >= config.questions.length) {
      // 当前状态的所有问题已完成
      // 移动到下一个状态
      if (!stateMachine.moveToNext()) {
        // 所有状态已完成
        await this.completeProfileCollection()
      } else {
        // 发送下一个状态的第一个问题
        this.sendNextQuestion()
      }
    } else {
      // 发送当前状态的下一个问题
      this.sendNextQuestion()
    }
  },
  
  // 保存用户回答
  saveUserAnswer(questionId, answer) {
    if (stateMachine.currentState === ProfileSteps.BASIC_INFO) {
      userProfile.value.basicInfo[questionId] = answer
    } else if (stateMachine.currentState === ProfileSteps.HEALTH_HISTORY) {
      userProfile.value.healthHistory[questionId] = answer
    } else if (stateMachine.currentState === ProfileSteps.LIFESTYLE) {
      userProfile.value.lifestyle[questionId] = answer
    } else if (stateMachine.currentState === ProfileSteps.SYMPTOMS) {
      userProfile.value.symptoms[questionId] = answer
    } else if (stateMachine.currentState === ProfileSteps.MEDICAL_REPORTS) {
      userProfile.value.medicalReports[questionId] = answer
    } else if (stateMachine.currentState === ProfileSteps.CONCERNS) {
      userProfile.value.concerns[questionId] = answer
    }
  },
  
  // 发送下一个问题
  sendNextQuestion() {
    const config = stateMachine.getCurrentStateConfig()
    if (config && subStepIndex.value < config.questions.length) {
      const nextQuestion = config.questions[subStepIndex.value]
      addMessage('assistant', nextQuestion.question)
    }
  },
  
  // 跳过当前状态
  skipCurrentState() {
    if (stateMachine.canSkipCurrentState()) {
      if (!stateMachine.moveToNext()) {
        // 所有状态已完成
        this.completeProfileCollection()
      } else {
        // 发送下一个状态的第一个问题
        this.sendNextQuestion()
      }
    }
  },
  
  // 完成用户画像采集
  async completeProfileCollection() {
    stateMachine.transitionTo(ProfileSteps.COMPLETED)
    
    // 保存用户画像到后端
    await this.saveUserProfile()
    
    // 显示完成消息
    addMessage('assistant', `
      <p>感谢您完成健康画像采集！</p>
      <p>根据您提供的信息，我将为您生成个性化的健康建议。</p>
      <p>点击下方按钮查看您的健康画像和建议。</p>
    `)
    
    // 添加查看结果按钮
    setTimeout(() => {
      // 创建一个包含按钮的消息对象
      const buttonMessage = {
        sender: 'assistant',
        content: `
          <p>感谢您完成健康画像采集！</p>
          <p>根据您提供的信息，我将为您生成个性化的健康建议。</p>
          <p>点击下方按钮查看您的健康画像和建议。</p>
        `,
        time: new Date(),
        hasButtons: true,
        buttons: [
          { text: '查看健康画像', action: 'viewProfile' },
          { text: '获取体检建议', action: 'getRecommendations' }
        ]
      }
      messages.value.push(buttonMessage)
      scrollToBottom()
    }, 1000)
  },
  
  // 保存用户画像
  async saveUserProfile() {
    try {
      // 获取当前登录用户的用户名
      const username = localStorage.getItem('username') || ''
      
      // 确保symptoms是数组格式
      let formattedSymptoms = []
      if (userProfile.value.symptoms) {
        if (Array.isArray(userProfile.value.symptoms)) {
          formattedSymptoms = userProfile.value.symptoms
        } else if (userProfile.value.symptoms.data && Array.isArray(userProfile.value.symptoms.data)) {
          formattedSymptoms = userProfile.value.symptoms.data
        } else if (typeof userProfile.value.symptoms === 'object') {
          // 如果是对象，转换为数组
          Object.keys(userProfile.value.symptoms).forEach(key => {
            if (key !== 'data' && userProfile.value.symptoms[key]) {
              formattedSymptoms.push({
                type: key,
                value: userProfile.value.symptoms[key]
              })
            }
          })
        }
      }
      
      // 将health_history对象转换为数组格式，以符合后端模型定义
      let healthHistoryArray = []
      if (userProfile.value.healthHistory && typeof userProfile.value.healthHistory === 'object') {
        // 将对象的每个属性转换为数组项，每个项包含type和value字段
        Object.keys(userProfile.value.healthHistory).forEach(key => {
          if (userProfile.value.healthHistory[key]) {
            healthHistoryArray.push({
              type: key,
              value: userProfile.value.healthHistory[key]
            })
          }
        })
      }
      
      // 确保medical_reports是数组格式
      let medicalReports = []
      if (userProfile.value.medicalReports) {
        if (Array.isArray(userProfile.value.medicalReports)) {
          medicalReports = userProfile.value.medicalReports
        } else if (typeof userProfile.value.medicalReports === 'object') {
          // 如果是对象，转换为数组
          Object.keys(userProfile.value.medicalReports).forEach(key => {
            if (userProfile.value.medicalReports[key]) {
              medicalReports.push({
                type: key,
                value: userProfile.value.medicalReports[key]
              })
            }
          })
        }
      }
      
      // 确保focus_areas是数组格式
      let focusAreas = []
      if (userProfile.value.concerns) {
        if (Array.isArray(userProfile.value.concerns)) {
          focusAreas = userProfile.value.concerns
        } else if (typeof userProfile.value.concerns === 'object') {
          // 如果是对象，转换为数组
          Object.keys(userProfile.value.concerns).forEach(key => {
            if (userProfile.value.concerns[key]) {
              focusAreas.push({
                type: key,
                value: userProfile.value.concerns[key]
              })
            }
          })
        }
      }
      
      // 不再发送user_id，让后端从JWT令牌中获取用户身份
      const response = await request.post('/api/v1/user-profile/', {
        basic_info: {
          ...userProfile.value.basicInfo,
          name: username  // 添加用户名到基本信息中
        },
        health_history: healthHistoryArray,
        lifestyle: userProfile.value.lifestyle || {},
        symptoms: formattedSymptoms,
        medical_reports: medicalReports,
        focus_areas: focusAreas
      })
      
      console.log('用户画像保存成功:', response)
      ElMessage.success('用户画像保存成功')
    } catch (error) {
      console.error('保存用户画像失败:', error)
      // 添加错误处理，显示给用户
      ElMessage.error('保存用户画像失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  },
  
  // 开始症状询问
  async startSymptomInquiry() {
    addMessage('assistant', '请详细描述您的不适症状，例如"头晕"、"胃痛"等。')
  },
  
  // 处理AI动态子流程回答
  async handleDynamicSubProcessAnswer(answer) {
    // 如果正在等待回答，处理回答
    if (dynamicSubProcessState.value.waitingForAnswer) {
      dynamicSubProcessState.value.waitingForAnswer = false
      const resolve = dynamicSubProcessState.value.resolveAnswer
      dynamicSubProcessState.value.resolveAnswer = null
      resolve(answer)
      return
    }
    
    // 使用NLU提取症状实体
    const symptomEntity = await this.extractSymptomEntity(answer)
    
    if (!symptomEntity) {
      addMessage('assistant', '抱歉，我没有理解您的症状描述。请尝试用更简单的方式描述，例如"头晕"、"胃痛"等。')
      return
    }
    
    // 获取症状知识库
    const symptomKnowledge = symptomKnowledgeBase[symptomEntity.symptom]
    
    if (!symptomKnowledge) {
      addMessage('assistant', '感谢您的描述。我们已经记录了这个症状。还有其他不适吗？')
      
      // 等待用户回答是否有其他症状
      dynamicSubProcessState.value.waitingForAnswer = true
      const hasMoreSymptoms = await this.waitForUserAnswer()
      
      if (hasMoreSymptoms.includes('没有') || hasMoreSymptoms.includes('不了') || hasMoreSymptoms.includes('完了')) {
        // 结束AI动态子流程，返回主流程
        isDynamicSubProcess.value = false
        if (!stateMachine.moveToNext()) {
          // 所有状态已完成
          await this.completeProfileCollection()
        } else {
          // 发送下一个状态的第一个问题
          this.sendNextQuestion()
        }
      } else {
        // 继续询问其他症状
        await this.startSymptomInquiry()
      }
      return
    }
    
    // 初始化症状数据
    if (!userProfile.value.symptoms.data) {
      userProfile.value.symptoms.data = []
    }
    
    const symptomData = {
      symptom: symptomEntity.symptom,
      description: answer,
      details: {}
    }
    
    userProfile.value.symptoms.data.push(symptomData)
    
    // 开始动态提问
    await this.askSymptomFollowUpQuestions(symptomEntity.symptom, symptomKnowledge, symptomData)
  },
  
  // 询问症状详细信息
  async askSymptomFollowUpQuestions(symptom, knowledge, symptomData) {
    for (let i = 0; i < knowledge.followUpQuestions.length; i++) {
      const question = knowledge.followUpQuestions[i]
      const entity = knowledge.entities[i]
      
      addMessage('assistant', question)
      
      // 等待用户回答
      dynamicSubProcessState.value.waitingForAnswer = true
      const answer = await this.waitForUserAnswer()
      
      // 保存回答
      symptomData.details[entity] = answer
    }
    
    addMessage('assistant', `感谢您详细描述"${symptom}"的症状。还有其他不适吗？`)
    
    // 检查是否还有其他症状
    dynamicSubProcessState.value.waitingForAnswer = true
    const hasMoreSymptoms = await this.waitForUserAnswer()
    
    if (hasMoreSymptoms.includes('没有') || hasMoreSymptoms.includes('不了') || hasMoreSymptoms.includes('完了')) {
      // 结束AI动态子流程，返回主流程
      isDynamicSubProcess.value = false
      if (!stateMachine.moveToNext()) {
        // 所有状态已完成
        await this.completeProfileCollection()
      } else {
        // 发送下一个状态的第一个问题
        this.sendNextQuestion()
      }
    } else {
      // 继续询问其他症状
      await this.startSymptomInquiry()
    }
  },
  
  // 提取症状实体
  async extractSymptomEntity(text) {
    // 这里应该调用NLU服务，现在使用简单的关键词匹配
    const symptoms = Object.keys(symptomKnowledgeBase)
    
    for (const symptom of symptoms) {
      if (text.includes(symptom)) {
        // 提取频率等实体
        let frequency = ''
        if (text.includes('经常') || text.includes('频繁')) {
          frequency = '经常'
        } else if (text.includes('偶尔')) {
          frequency = '偶尔'
        } else if (text.includes('总是') || text.includes('持续')) {
          frequency = '持续'
        }
        
        return {
          symptom,
          frequency
        }
      }
    }
    
    return null
  },
  
  // 等待用户回答
  waitForUserAnswer() {
    return new Promise((resolve) => {
      dynamicSubProcessState.value.resolveAnswer = resolve
    })
  }
}











// 组件初始化
onMounted(() => {
  // 初始化用户画像流程
  flowController.initialize()
  
  // 添加系统消息
  addMessage('system', '健康画像采集已开始，请按照提示回答问题')
})
</script>

<style scoped>
.user-profile-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 顶部导航栏 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-left {
  flex: 1;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #409eff;
  cursor: pointer;
  padding: 8px 0;
}

.header-center {
  flex: 2;
  text-align: center;
}

.header-center h2 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.progress-bar {
  width: 120px;
  height: 4px;
  background-color: #ebeef5;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #409eff;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #909399;
}

.header-right {
  flex: 1;
  text-align: right;
}

.skip-btn {
  background: none;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #909399;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.skip-btn:hover {
  color: #409eff;
  border-color: #409eff;
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
  line-height: 1.4;
}

.message-bubble.user {
  background-color: #409eff;
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background-color: white;
  color: #303133;
  margin-right: auto;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-content {
  margin-bottom: 4px;
}

.message-content p {
  margin: 0 0 8px;
}

.message-content p:last-child {
  margin-bottom: 0;
}

.message-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.message-bubble.user .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.message-bubble.assistant .message-time {
  color: #c0c4cc;
  text-align: left;
}

/* 消息按钮 */
.message-buttons {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.primary-btn {
  background-color: #409eff;
  color: white;
}

.primary-btn:hover {
  background-color: #66b1ff;
}

.secondary-btn {
  background-color: #f0f0f0;
  color: #303133;
  border: 1px solid #dcdfe6;
}

.secondary-btn:hover {
  background-color: #e6e6e6;
}

/* 正在输入指示器 */
.typing-indicator {
  margin-bottom: 16px;
}

.typing-animation {
  display: flex;
  align-items: center;
  padding: 12px 16px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #c0c4cc;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 输入区域 */
.chat-input-area {
  background-color: white;
  padding: 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.input-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.input-container input {
  flex: 1;
  height: 40px;
  padding: 0 16px;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.input-container input:focus {
  border-color: #409eff;
}

.input-container input:disabled {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

.send-btn {
  height: 40px;
  padding: 0 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.send-btn:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

/* 快捷回复 */
.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-reply-btn {
  padding: 8px 16px;
  background-color: #f0f2f5;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-reply-btn:hover:not(:disabled) {
  background-color: #ecf5ff;
  color: #409eff;
  border-color: #c6e2ff;
}

.quick-reply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.primary-btn, .secondary-btn {
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.primary-btn {
  background-color: #409eff;
  color: white;
}

.primary-btn:hover {
  background-color: #66b1ff;
}

.secondary-btn {
  background-color: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.secondary-btn:hover {
  background-color: #409eff;
  color: white;
}
</style>