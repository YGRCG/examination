<template>
  <div class="smart-interaction">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-left">
        <span class="system-logo">🏥 医院体检项目智能推荐系统</span>
      </div>
      <div class="nav-right">
        <button class="back-btn" @click="goBack">返回首页</button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧面板 - 健康档案概览 -->
      <aside class="left-panel">
        <div class="panel-header">
          <h3>健康档案概览</h3>
        </div>
        
        <div class="health-summary">
          <div class="summary-item">
            <span class="summary-label">年龄:</span>
            <span class="summary-value">{{ userProfile.age || '未设置' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">性别:</span>
            <span class="summary-value">{{ userProfile.gender || '未设置' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">BMI指数:</span>
            <span class="summary-value">{{ userProfile.bmi || '未设置' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">血压:</span>
            <span class="summary-value">{{ userProfile.bloodPressure || '未设置' }}</span>
          </div>
        </div>

        <div class="recent-reports">
          <h4>最近体检报告</h4>
          <div v-if="recentReports.length > 0" class="report-list">
            <div class="report-item" v-for="report in recentReports" :key="report.id">
              <span class="report-date">{{ formatDate(report.date) }}</span>
              <span class="report-name">{{ report.name }}</span>
              <button class="view-report-btn" @click="viewReport(report.id)">查看</button>
            </div>
          </div>
          <div v-else class="no-data">暂无最近报告</div>
        </div>

        <div class="quick-actions">
          <h4>快速操作</h4>
          <button class="action-btn" @click="goToInformationCollection">完善健康信息</button>
          <button class="action-btn" @click="goToRecommendation">获取体检建议</button>
        </div>
      </aside>

      <!-- 中央面板 - 智能对话 -->
      <main class="chat-panel">
        <div class="chat-header">
          <div class="assistant-info">
            <div class="assistant-avatar">🤖</div>
            <div class="assistant-details">
              <h3>智能健康助手</h3>
              <p class="assistant-status">在线，随时为您提供健康咨询</p>
            </div>
          </div>
        </div>

        <div class="chat-messages" ref="chatMessages">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="message-bubble assistant">
              <div class="message-content">
                <p>您好！我是您的智能健康助手。</p>
                <p>我可以为您提供以下帮助：</p>
                <ul>
                  <li>解答健康相关问题</li>
                  <li>提供个性化体检项目建议</li>
                  <li>解读体检报告</li>
                  <li>提供健康生活方式建议</li>
                </ul>
                <p>请问有什么可以帮助您的吗？</p>
              </div>
            </div>
          </div>

          <!-- 对话消息 -->
          <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
            <div class="message-bubble" :class="message.sender">
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-time">{{ formatTime(message.time) }}</div>
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
        </div>

        <div class="chat-input-area">
          <div class="input-container">
            <input
              v-model="userInput"
              type="text"
              placeholder="请输入您的问题，例如：'我需要做哪些体检项目？'或'我的体检报告有什么问题？'"
              @keyup.enter="sendMessage"
              :disabled="isAssistantTyping"
            />
            <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim() || isAssistantTyping">
              <span class="send-icon">📤</span>
            </button>
          </div>
          
          <div class="quick-questions">
            <button 
              v-for="question in quickQuestions" 
              :key="question.id"
              class="quick-question-btn"
              @click="sendQuickQuestion(question.text)"
              :disabled="isAssistantTyping"
            >
              {{ question.text }}
            </button>
          </div>
        </div>
      </main>

      <!-- 右侧面板 - 知识推荐 -->
      <aside class="right-panel">
        <div class="panel-header">
          <h3>为您推荐</h3>
        </div>

        <div class="recommended-knowledge">
          <h4>健康知识</h4>
          <div class="knowledge-list">
            <div 
              class="knowledge-item" 
              v-for="article in recommendedArticles" 
              :key="article.id"
              @click="viewKnowledge(article.id)"
            >
              <h5>{{ article.title }}</h5>
              <p class="knowledge-preview">{{ article.preview }}</p>
              <div class="knowledge-meta">
                <span class="knowledge-category">{{ article.category }}</span>
                <span class="knowledge-read-time">{{ article.readTime }}分钟阅读</span>
              </div>
            </div>
          </div>
        </div>

        <div class="recommended-examinations">
          <h4>热门体检项目</h4>
          <div class="examination-list">
            <div 
              class="examination-item" 
              v-for="exam in popularExaminations" 
              :key="exam.id"
              @click="viewExamination(exam.id)"
            >
              <h5>{{ exam.name }}</h5>
              <p class="examination-desc">{{ exam.description }}</p>
              <div class="examination-info">
                <span class="examination-price">¥{{ exam.price }}</span>
                <button class="add-to-cart-btn">+</button>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { router } from '../router'
import axios from 'axios'

// 状态管理
const userInput = ref('')
const messages = ref([])
const isAssistantTyping = ref(false)
const userProfile = ref({})
const recentReports = ref([])
const chatMessagesRef = ref(null)

// 快速问题选项
const quickQuestions = ref([
  { id: 1, text: '我这个年龄段应该做哪些体检项目？' },
  { id: 2, text: '如何解读体检报告中的异常指标？' },
  { id: 3, text: '有高血压病史的人体检需要注意什么？' },
  { id: 4, text: '体检前需要做哪些准备？' }
])

// 推荐的健康知识文章
const recommendedArticles = ref([
  {
    id: 1,
    title: '体检报告解读全指南',
    preview: '了解体检报告中的各项指标含义，掌握自己的健康状况...',
    category: '体检指南',
    readTime: 5
  },
  {
    id: 2,
    title: '不同年龄段的体检重点',
    preview: '根据您的年龄阶段，选择最适合的体检项目...',
    category: '健康管理',
    readTime: 4
  },
  {
    id: 3,
    title: '科学预防常见慢性疾病',
    preview: '通过生活方式干预，有效降低慢性疾病风险...',
    category: '疾病预防',
    readTime: 6
  }
])

// 热门体检项目
const popularExaminations = ref([
  {
    id: 1,
    name: '基础体检套餐',
    description: '包含血常规、尿常规、肝功能等基础检查项目',
    price: 399
  },
  {
    id: 2,
    name: '心脑血管专项检查',
    description: '针对心脏和脑血管的全面检查，适合中老年人',
    price: 899
  },
  {
    id: 3,
    name: '肿瘤标志物筛查',
    description: '早期发现癌症风险，提高治疗成功率',
    price: 699
  }
])

// 发送消息
const sendMessage = async () => {
  const messageText = userInput.value.trim()
  if (!messageText || isAssistantTyping.value) return

  // 添加用户消息到对话列表
  const userMessage = {
    id: messages.value.length + 1,
    sender: 'user',
    content: messageText,
    time: new Date()
  }
  messages.value.push(userMessage)
  userInput.value = ''

  // 滚动到底部
  scrollToBottom()

  try {
    // 显示正在输入状态
    isAssistantTyping.value = true
    scrollToBottom()

    // 调用后端智能交互接口
    const response = await axios.post('/ai/interaction', {
      user_id: localStorage.getItem('userId'),
      query: messageText,
      context: messages.value.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      }))
    })

    // 隐藏正在输入状态
    isAssistantTyping.value = false

    if (response.status === 'success') {
      // 添加助手回复到对话列表
      const assistantMessage = {
        id: messages.value.length + 1,
        sender: 'assistant',
        content: response.data.answer,
        time: new Date()
      }
      messages.value.push(assistantMessage)
    } else {
      // 添加错误消息
      const errorMessage = {
        id: messages.value.length + 1,
        sender: 'assistant',
        content: '抱歉，我暂时无法回答这个问题，请稍后再试或换个问题。',
        time: new Date()
      }
      messages.value.push(errorMessage)
    }
  } catch (error) {
    console.error('智能交互错误:', error)
    isAssistantTyping.value = false
    // 添加错误消息
    const errorMessage = {
      id: messages.value.length + 1,
      sender: 'assistant',
      content: '网络错误，请检查您的网络连接后重试。',
      time: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 发送快速问题
const sendQuickQuestion = (question) => {
  userInput.value = question
  sendMessage()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return ''
  const time = new Date(date)
  return time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 查看报告
const viewReport = (reportId) => {
  router.push({ path: '/report/interpretation', query: { reportId } })
}

// 完善健康信息
const goToInformationCollection = () => {
  router.push('/information-collection')
}

// 获取体检建议
const goToRecommendation = () => {
  router.push('/recommendation-result')
}

// 查看健康知识
const viewKnowledge = (articleId) => {
  // 跳转到健康知识详情页
  alert(`查看健康知识文章：${articleId}`)
}

// 查看体检项目
const viewExamination = (examId) => {
  // 跳转到体检项目详情页
  alert(`查看体检项目：${examId}`)
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 加载用户资料
const loadUserProfile = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      // 如果用户未登录，跳转到登录页面
      router.push('/login')
      return
    }

    // 获取用户基本信息
    const profileResponse = await axios.get(`/user/profile/${userId}`)
    if (profileResponse.status === 'success') {
      userProfile.value = profileResponse.data
    }

    // 获取最近的体检报告
    const reportsResponse = await axios.get(`/user/${userId}/recent-reports`)
    if (reportsResponse.status === 'success') {
      recentReports.value = reportsResponse.data
    }
  } catch (error) {
    console.error('加载用户资料错误:', error)
  }
}

// 组件挂载时加载用户资料
onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
/* 智能交互页面样式 */
:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --assistant-bg: #f0f8ff;
  --user-bg: #e6f7ff;
  --text-color: #333;
  --text-secondary: #666;
  --border-color: #d9d9d9;
  --background-color: #f5f5f5;
  --card-background: #fff;
}

.smart-interaction {
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
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-left {
  font-size: 18px;
  font-weight: bold;
}

.back-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  margin: 20px;
  gap: 20px;
  height: calc(100vh - 100px);
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-header {
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
}

.health-summary {
  background-color: var(--background-color);
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-value {
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
}

.recent-reports {
  margin-bottom: 20px;
}

.recent-reports h4,
.quick-actions h4 {
  margin: 0 0 12px;
  color: var(--text-color);
  font-size: 14px;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-item {
  background-color: var(--background-color);
  border-radius: 4px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-date {
  color: var(--text-secondary);
  font-size: 12px;
}

.report-name {
  color: var(--text-color);
  font-size: 14px;
}

.view-report-btn {
  align-self: flex-end;
  padding: 4px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 4px;
}

.view-report-btn:hover {
  background-color: var(--primary-dark);
}

.quick-actions {
  margin-top: auto;
}

.action-btn {
  width: 100%;
  padding: 10px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background-color: var(--primary-dark);
}

/* 中央面板 - 聊天区域 */
.chat-panel {
  flex: 1;
  background-color: var(--card-background);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 16px;
}

.assistant-avatar {
  font-size: 48px;
}

.assistant-details h3 {
  margin: 0 0 4px;
  color: var(--text-color);
  font-size: 18px;
}

.assistant-status {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  animation: fadeIn 0.5s ease-in-out;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  animation: fadeIn 0.3s ease-in-out;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
}

.message-bubble.user {
  background-color: var(--user-bg);
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background-color: var(--assistant-bg);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.message-content {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.message-time {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
  margin-top: 4px;
}

.message-bubble.assistant .message-time {
  text-align: left;
}

.typing-indicator {
  align-self: flex-start;
}

.typing-animation {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
}

.typing-animation .dot {
  width: 8px;
  height: 8px;
  background-color: var(--text-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-animation .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-animation .dot:nth-child(2) {
  animation-delay: -0.16s;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.input-container input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-container input:focus {
  border-color: var(--primary-color);
}

.input-container input:disabled {
  background-color: var(--background-color);
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.send-icon {
  font-size: 16px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-question-btn {
  padding: 6px 16px;
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.quick-question-btn:hover:not(:disabled) {
  background-color: var(--assistant-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.quick-question-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 右侧面板 - 推荐内容 */
.right-panel {
  width: 320px;
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.recommended-knowledge {
  margin-bottom: 24px;
}

.recommended-knowledge h4,
.recommended-examinations h4 {
  margin: 0 0 12px;
  color: var(--text-color);
  font-size: 14px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  background-color: var(--background-color);
  border-radius: 6px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.knowledge-item:hover {
  background-color: var(--assistant-bg);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.knowledge-item h5 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 14px;
}

.knowledge-preview {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.knowledge-category {
  color: var(--primary-color);
  font-size: 12px;
  font-weight: 500;
}

.knowledge-read-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.examination-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.examination-item {
  background-color: var(--background-color);
  border-radius: 6px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.examination-item:hover {
  background-color: var(--assistant-bg);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.examination-item h5 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 14px;
}

.examination-desc {
  margin: 0 0 12px;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.examination-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.examination-price {
  color: var(--primary-color);
  font-size: 14px;
  font-weight: bold;
}

.add-to-cart-btn {
  width: 24px;
  height: 24px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-to-cart-btn:hover {
  background-color: var(--primary-dark);
}

/* 无数据提示 */
.no-data {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-panel,
  .right-panel {
    width: 100%;
    height: auto;
  }
  
  .chat-panel {
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin: 10px;
    gap: 10px;
  }
  
  .top-nav {
    padding: 12px 16px;
  }
  
  .nav-left {
    font-size: 16px;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .quick-questions {
    justify-content: center;
  }
  
  .assistant-avatar {
    font-size: 36px;
  }
}
</style>