<template>
  <div class="personal-center">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-left">
        <span class="system-logo">🏥 医院体检项目智能推荐系统</span>
      </div>
      <div class="nav-right">
        <span class="welcome-text">欢迎，{{ userInfo.username }}</span>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 侧边导航 -->
      <aside class="sidebar">
        <div class="profile-summary">
          <div class="avatar">
            {{ userInfo.username?.substring(0, 2).toUpperCase() || '用户' }}
          </div>
          <h3>{{ userInfo.username }}</h3>
          <p class="user-id">ID: {{ userInfo.user_id }}</p>
        </div>
        
        <ul class="nav-menu">
          <li 
            class="menu-item"
            :class="{ active: currentTab === 'basic-info' }"
            @click="switchTab('basic-info')"
          >
            <span class="menu-icon">👤</span>
            <span class="menu-text">基本信息</span>
          </li>
          <li 
            class="menu-item"
            :class="{ active: currentTab === 'health-data' }"
            @click="switchTab('health-data')"
          >
            <span class="menu-icon">📊</span>
            <span class="menu-text">健康数据</span>
          </li>
          <li 
            class="menu-item"
            :class="{ active: currentTab === 'appointment-history' }"
            @click="switchTab('appointment-history')"
          >
            <span class="menu-icon">📅</span>
            <span class="menu-text">预约记录</span>
          </li>
          <li 
            class="menu-item"
            :class="{ active: currentTab === 'report-history' }"
            @click="switchTab('report-history')"
          >
            <span class="menu-icon">📋</span>
            <span class="menu-text">报告记录</span>
          </li>
          <li 
            class="menu-item"
            :class="{ active: currentTab === 'system-settings' }"
            @click="switchTab('system-settings')"
          >
            <span class="menu-icon">⚙️</span>
            <span class="menu-text">系统设置</span>
          </li>
        </ul>
      </aside>

      <!-- 内容区 -->
      <main class="content-area">
        <div class="content-header">
          <h2>{{ getTabTitle() }}</h2>
          <div class="header-actions" v-if="currentTab === 'basic-info' && !isEditing">
            <button class="edit-btn" @click="startEditing">编辑信息</button>
          </div>
          <div class="header-actions" v-if="currentTab === 'basic-info' && isEditing">
            <button class="cancel-btn" @click="cancelEditing">取消</button>
            <button class="save-btn" @click="saveChanges">保存更改</button>
          </div>
        </div>

        <!-- 基本信息标签页 -->
        <div v-if="currentTab === 'basic-info'" class="basic-info-content">
          <div class="info-card">
            <h3>个人基本信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>用户名:</label>
                <span v-if="!isEditing">{{ userInfo.username }}</span>
                <input v-else v-model="editForm.username" type="text" class="info-input" />
              </div>
              <div class="info-item">
                <label>性别:</label>
                <span v-if="!isEditing">{{ userInfo.gender || '未设置' }}</span>
                <select v-else v-model="editForm.gender" class="info-select">
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div class="info-item">
                <label>出生日期:</label>
                <span v-if="!isEditing">{{ formatDate(userInfo.birthdate) || '未设置' }}</span>
                <input v-else v-model="editForm.birthdate" type="date" class="info-input" />
              </div>
              <div class="info-item">
                <label>手机号码:</label>
                <span v-if="!isEditing">{{ userInfo.phone_number || '未设置' }}</span>
                <input v-else v-model="editForm.phone_number" type="tel" class="info-input" />
              </div>
              <div class="info-item">
                <label>电子邮箱:</label>
                <span v-if="!isEditing">{{ userInfo.email || '未设置' }}</span>
                <input v-else v-model="editForm.email" type="email" class="info-input" />
              </div>
              <div class="info-item">
                <label>身高 (cm):</label>
                <span v-if="!isEditing">{{ userInfo.height || '未设置' }}</span>
                <input v-else v-model="editForm.height" type="number" class="info-input" />
              </div>
              <div class="info-item">
                <label>体重 (kg):</label>
                <span v-if="!isEditing">{{ userInfo.weight || '未设置' }}</span>
                <input v-else v-model="editForm.weight" type="number" class="info-input" />
              </div>
              <div class="info-item">
                <label>血型:</label>
                <span v-if="!isEditing">{{ userInfo.blood_type || '未设置' }}</span>
                <select v-else v-model="editForm.blood_type" class="info-select">
                  <option value="">请选择</option>
                  <option value="A">A型</option>
                  <option value="B">B型</option>
                  <option value="O">O型</option>
                  <option value="AB">AB型</option>
                </select>
              </div>
            </div>
          </div>

          <div class="info-card" v-if="!isEditing">
            <h3>健康风险因素</h3>
            <div class="risk-factors">
              <div class="risk-item" v-for="risk in userInfo.risk_factors" :key="risk.id">
                <span class="risk-name">{{ risk.name }}</span>
                <span class="risk-level" :class="getRiskClass(risk.level)">{{ getRiskText(risk.level) }}</span>
              </div>
              <div v-if="!userInfo.risk_factors || userInfo.risk_factors.length === 0" class="no-data">
                暂无健康风险因素数据
              </div>
            </div>
          </div>

          <div class="info-card" v-if="!isEditing">
            <h3>既往病史</h3>
            <div class="medical-history">
              <div class="history-item" v-for="history in userInfo.medical_history" :key="history.id">
                <span class="disease-name">{{ history.disease_name }}</span>
                <span class="diagnosis-date">{{ formatDate(history.diagnosis_date) }}</span>
              </div>
              <div v-if="!userInfo.medical_history || userInfo.medical_history.length === 0" class="no-data">
                暂无既往病史数据
              </div>
            </div>
          </div>
        </div>

        <!-- 健康数据标签页 -->
        <div v-else-if="currentTab === 'health-data'" class="health-data-content">
          <div class="charts-container">
            <div class="chart-card">
              <h3>体重趋势 (过去6个月)</h3>
              <div class="chart-placeholder">
                <!-- 这里将集成图表组件 -->
                <div class="chart-simulation">📊 体重趋势图表</div>
              </div>
            </div>
            <div class="chart-card">
              <h3>血压趋势 (过去6个月)</h3>
              <div class="chart-placeholder">
                <!-- 这里将集成图表组件 -->
                <div class="chart-simulation">📊 血压趋势图表</div>
              </div>
            </div>
          </div>

          <div class="health-metrics">
            <div class="metric-card">
              <h3>健康指标概览</h3>
              <div class="metrics-grid">
                <div class="metric-item">
                  <span class="metric-label">BMI指数</span>
                  <span class="metric-value">{{ calculateBMI() }}</span>
                  <span class="metric-status" :class="getBMIClass()">{{ getBMIStatus() }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">平均血压</span>
                  <span class="metric-value">{{ userInfo.avg_blood_pressure || '未设置' }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">心率</span>
                  <span class="metric-value">{{ userInfo.heart_rate || '未设置' }} 次/分</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">血糖</span>
                  <span class="metric-value">{{ userInfo.blood_sugar || '未设置' }} mmol/L</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 预约记录标签页 -->
        <div v-else-if="currentTab === 'appointment-history'" class="appointment-history-content">
          <div class="appointment-filter">
            <select v-model="appointmentFilter" class="filter-select">
              <option value="all">全部预约</option>
              <option value="upcoming">即将到来</option>
              <option value="completed">已完成</option>
              <option value="canceled">已取消</option>
            </select>
          </div>
          
          <div class="appointment-list">
            <div class="appointment-item" v-for="appointment in filteredAppointments" :key="appointment.id">
              <div class="appointment-header">
                <h4>{{ appointment.examination_name }}</h4>
                <span class="appointment-status" :class="getStatusClass(appointment.status)">{{ getStatusText(appointment.status) }}</span>
              </div>
              <div class="appointment-details">
                <div class="detail-item">
                  <span class="detail-label">预约时间:</span>
                  <span class="detail-value">{{ formatDateTime(appointment.appointment_time) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">医院:</span>
                  <span class="detail-value">{{ appointment.hospital_name }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">科室:</span>
                  <span class="detail-value">{{ appointment.department_name }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">价格:</span>
                  <span class="detail-value">¥{{ appointment.price }}</span>
                </div>
              </div>
              <div class="appointment-actions">
                <button v-if="appointment.status === 'upcoming'" class="action-btn cancel-btn" @click="cancelAppointment(appointment.id)">取消预约</button>
                <button v-if="appointment.status === 'completed'" class="action-btn view-btn" @click="viewReport(appointment.report_id)">查看报告</button>
                <button class="action-btn reschedule-btn" @click="rescheduleAppointment(appointment.id)">重新预约</button>
              </div>
            </div>
            <div v-if="filteredAppointments.length === 0" class="no-data">
              暂无预约记录
            </div>
          </div>
        </div>

        <!-- 报告记录标签页 -->
        <div v-else-if="currentTab === 'report-history'" class="report-history-content">
          <div class="report-list">
            <div class="report-item" v-for="report in userInfo.report_history" :key="report.id">
              <div class="report-header">
                <h4>{{ report.examination_name }}</h4>
                <span class="report-date">{{ formatDate(report.report_date) }}</span>
              </div>
              <div class="report-summary">
                <p>{{ report.summary }}</p>
              </div>
              <div class="report-actions">
                <button class="action-btn view-btn" @click="viewFullReport(report.id)">查看完整报告</button>
                <button class="action-btn download-btn" @click="downloadReport(report.id)">下载报告</button>
              </div>
            </div>
            <div v-if="!userInfo.report_history || userInfo.report_history.length === 0" class="no-data">
              暂无报告记录
            </div>
          </div>
        </div>

        <!-- 系统设置标签页 -->
        <div v-else-if="currentTab === 'system-settings'" class="system-settings-content">
          <div class="settings-card">
            <h3>账户安全</h3>
            <div class="setting-item">
              <label>修改密码</label>
              <button class="setting-btn" @click="changePassword">修改密码</button>
            </div>
            <div class="setting-item">
              <label>绑定手机</label>
              <span class="setting-value">{{ userInfo.phone_number || '未绑定' }}</span>
              <button class="setting-btn" @click="bindPhone">绑定/更换</button>
            </div>
            <div class="setting-item">
              <label>绑定邮箱</label>
              <span class="setting-value">{{ userInfo.email || '未绑定' }}</span>
              <button class="setting-btn" @click="bindEmail">绑定/更换</button>
            </div>
          </div>

          <div class="settings-card">
            <h3>通知设置</h3>
            <div class="setting-item">
              <label>预约提醒</label>
              <input type="checkbox" v-model="notificationSettings.appointment_reminder" class="setting-checkbox" />
            </div>
            <div class="setting-item">
              <label>报告提醒</label>
              <input type="checkbox" v-model="notificationSettings.report_reminder" class="setting-checkbox" />
            </div>
            <div class="setting-item">
              <label>健康建议</label>
              <input type="checkbox" v-model="notificationSettings.health_advice" class="setting-checkbox" />
            </div>
          </div>

          <div class="settings-card">
            <h3>隐私设置</h3>
            <div class="setting-item">
              <label>允许数据分析</label>
              <input type="checkbox" v-model="privacySettings.allow_data_analysis" class="setting-checkbox" />
            </div>
            <div class="setting-item">
              <label>数据共享</label>
              <select v-model="privacySettings.data_sharing" class="setting-select">
                <option value="none">不共享</option>
                <option value="anonymous">匿名共享</option>
                <option value="research">仅用于研究</option>
              </select>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { router } from '../router'
import axios from 'axios'

// 状态管理
const currentTab = ref('basic-info')
const isEditing = ref(false)
const userInfo = ref({})
const editForm = ref({})
const appointmentFilter = ref('all')
const notificationSettings = ref({
  appointment_reminder: true,
  report_reminder: true,
  health_advice: true
})
const privacySettings = ref({
  allow_data_analysis: false,
  data_sharing: 'none'
})

// 切换标签页
const switchTab = (tab) => {
  currentTab.value = tab
}

// 获取标签页标题
const getTabTitle = () => {
  const titles = {
    'basic-info': '基本信息',
    'health-data': '健康数据',
    'appointment-history': '预约记录',
    'report-history': '报告记录',
    'system-settings': '系统设置'
  }
  return titles[currentTab.value] || '个人中心'
}

// 开始编辑
const startEditing = () => {
  // 复制用户信息到编辑表单
  editForm.value = {
    ...userInfo.value
  }
  isEditing.value = true
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  editForm.value = {}
}

// 保存更改
const saveChanges = async () => {
  try {
    const response = await axios.put('/user/profile/update', editForm.value)
    
    if (response.status === 'success') {
      // 更新用户信息
      userInfo.value = response.data.user_info
      isEditing.value = false
      alert('信息更新成功！')
    } else {
      alert(response.message || '信息更新失败，请重试')
    }
  } catch (error) {
    console.error('更新用户信息错误:', error)
    alert('网络错误，请检查您的网络连接')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取风险等级样式
const getRiskClass = (level) => {
  const classes = {
    'high': 'high-risk',
    'medium': 'medium-risk',
    'low': 'low-risk'
  }
  return classes[level] || ''
}

// 获取风险等级文本
const getRiskText = (level) => {
  const texts = {
    'high': '高风险',
    'medium': '中风险',
    'low': '低风险'
  }
  return texts[level] || level
}

// 计算BMI
const calculateBMI = () => {
  if (!userInfo.value.weight || !userInfo.value.height) return '未设置'
  const weight = parseFloat(userInfo.value.weight)
  const height = parseFloat(userInfo.value.height) / 100 // 转换为米
  if (weight <= 0 || height <= 0) return '无效数据'
  const bmi = weight / (height * height)
  return bmi.toFixed(1)
}

// 获取BMI等级样式
const getBMIClass = () => {
  const bmi = parseFloat(calculateBMI())
  if (isNaN(bmi)) return ''
  if (bmi < 18.5) return 'underweight'
  if (bmi < 24) return 'normal'
  if (bmi < 28) return 'overweight'
  return 'obese'
}

// 获取BMI状态文本
const getBMIStatus = () => {
  const bmi = parseFloat(calculateBMI())
  if (isNaN(bmi)) return ''
  if (bmi < 18.5) return '偏瘦'
  if (bmi < 24) return '正常'
  if (bmi < 28) return '超重'
  return '肥胖'
}

// 获取预约状态样式
const getStatusClass = (status) => {
  const classes = {
    'upcoming': 'status-upcoming',
    'completed': 'status-completed',
    'canceled': 'status-canceled'
  }
  return classes[status] || ''
}

// 获取预约状态文本
const getStatusText = (status) => {
  const texts = {
    'upcoming': '即将到来',
    'completed': '已完成',
    'canceled': '已取消'
  }
  return texts[status] || status
}

// 过滤预约记录
const filteredAppointments = computed(() => {
  if (!userInfo.value.appointment_history) return []
  if (appointmentFilter.value === 'all') return userInfo.value.appointment_history
  return userInfo.value.appointment_history.filter(item => item.status === appointmentFilter.value)
})

// 取消预约
const cancelAppointment = async (appointmentId) => {
  if (!confirm('确定要取消此预约吗？')) return
  
  try {
    const response = await axios.post(`/appointment/cancel/${appointmentId}`)
    
    if (response.status === 'success') {
      // 更新预约状态
      const appointment = userInfo.value.appointment_history.find(item => item.id === appointmentId)
      if (appointment) {
        appointment.status = 'canceled'
      }
      alert('预约已取消')
    } else {
      alert(response.message || '取消预约失败，请重试')
    }
  } catch (error) {
    console.error('取消预约错误:', error)
    alert('网络错误，请检查您的网络连接')
  }
}

// 重新预约
const rescheduleAppointment = (appointmentId) => {
  // 跳转到预约页面，并带上当前预约的信息
  router.push({ path: '/appointment', query: { appointmentId } })
}

// 查看报告
const viewReport = (reportId) => {
  router.push({ path: '/report/interpretation', query: { reportId } })
}

// 查看完整报告
const viewFullReport = (reportId) => {
  router.push({ path: '/report/interpretation', query: { reportId } })
}

// 下载报告
const downloadReport = (reportId) => {
  // 模拟下载操作
  alert('报告下载功能正在开发中...')
}

// 修改密码
const changePassword = () => {
  // 弹出修改密码对话框
  alert('修改密码功能正在开发中...')
}

// 绑定手机
const bindPhone = () => {
  // 弹出绑定手机对话框
  alert('绑定手机功能正在开发中...')
}

// 绑定邮箱
const bindEmail = () => {
  // 弹出绑定邮箱对话框
  alert('绑定邮箱功能正在开发中...')
}

// 退出登录
const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    // 清除token和用户信息
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    // 跳转到登录页面
    router.push('/login')
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      router.push('/login')
      return
    }
    
    const response = await axios.get(`/user/profile/${userId}`)
    
    if (response.status === 'success') {
      userInfo.value = response.data
      // 初始化通知和隐私设置
      if (userInfo.value.notification_settings) {
        notificationSettings.value = { ...userInfo.value.notification_settings }
      }
      if (userInfo.value.privacy_settings) {
        privacySettings.value = { ...userInfo.value.privacy_settings }
      }
    } else {
      alert(response.message || '获取用户信息失败，请重试')
      router.push('/login')
    }
  } catch (error) {
    console.error('获取用户信息错误:', error)
    alert('网络错误，请检查您的网络连接')
    router.push('/login')
  }
}

// 组件挂载时加载用户信息
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
/* 个人中心页面样式 */
:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  --text-color: #333;
  --text-secondary: #666;
  --border-color: #d9d9d9;
  --background-color: #f5f5f5;
  --card-background: #fff;
}

.personal-center {
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

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  font-size: 14px;
}

.logout-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  margin: 20px;
  gap: 20px;
}

/* 侧边导航 */
.sidebar {
  width: 240px;
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.profile-summary {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.avatar {
  width: 80px;
  height: 80px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 16px;
}

.profile-summary h3 {
  margin: 0 0 8px;
  color: var(--text-color);
}

.user-id {
  color: var(--text-secondary);
  font-size: 12px;
  margin: 0;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color);
}

.menu-item:hover {
  background-color: rgba(24, 144, 255, 0.1);
  color: var(--primary-color);
}

.menu-item.active {
  background-color: var(--primary-color);
  color: white;
}

.menu-icon {
  font-size: 18px;
  margin-right: 12px;
}

.menu-text {
  font-size: 14px;
}

/* 内容区 */
.content-area {
  flex: 1;
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.content-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.edit-btn, .save-btn, .cancel-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.edit-btn {
  background-color: var(--primary-color);
  color: white;
}

.edit-btn:hover {
  background-color: var(--primary-dark);
}

.save-btn {
  background-color: var(--success-color);
  color: white;
}

.save-btn:hover {
  background-color: #389e0d;
}

.cancel-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.cancel-btn:hover {
  background-color: #bfbfbf;
}

/* 基本信息样式 */
.info-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.info-card h3 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.info-item span {
  color: var(--text-color);
  font-size: 14px;
}

.info-input, .info-select {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
}

.risk-factors, .medical-history {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-item, .history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--background-color);
  border-radius: 6px;
}

.risk-name, .disease-name {
  color: var(--text-color);
  font-size: 14px;
}

.risk-level {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.high-risk {
  background-color: #fff2f0;
  color: var(--error-color);
}

.medium-risk {
  background-color: #fff7e6;
  color: var(--warning-color);
}

.low-risk {
  background-color: #f6ffed;
  color: var(--success-color);
}

.diagnosis-date {
  color: var(--text-secondary);
  font-size: 12px;
}

/* 健康数据样式 */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.chart-card h3 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-color);
  border-radius: 4px;
}

.chart-simulation {
  font-size: 18px;
  color: var(--text-secondary);
}

.health-metrics {
  margin-top: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-item {
  text-align: center;
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 8px;
}

.metric-label {
  display: block;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.metric-value {
  display: block;
  color: var(--text-color);
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.metric-status {
  display: block;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.normal {
  background-color: #f6ffed;
  color: var(--success-color);
}

.underweight {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

.overweight {
  background-color: #fff7e6;
  color: var(--warning-color);
}

.obese {
  background-color: #fff2f0;
  color: var(--error-color);
}

/* 预约记录样式 */
.appointment-filter {
  margin-bottom: 20px;
}

.filter-select {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.appointment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.appointment-item {
  background-color: var(--background-color);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.appointment-header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
}

.appointment-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-upcoming {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

.status-completed {
  background-color: #f6ffed;
  color: var(--success-color);
}

.status-canceled {
  background-color: #fff2f0;
  color: var(--error-color);
}

.appointment-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.detail-item {
  display: flex;
  gap: 8px;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 12px;
  min-width: 60px;
}

.detail-value {
  color: var(--text-color);
  font-size: 14px;
}

.appointment-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.view-btn {
  background-color: var(--primary-color);
  color: white;
}

.view-btn:hover {
  background-color: var(--primary-dark);
}

.cancel-btn {
  background-color: var(--error-color);
  color: white;
}

.cancel-btn:hover {
  background-color: #cf1322;
}

.reschedule-btn {
  background-color: var(--warning-color);
  color: white;
}

.reschedule-btn:hover {
  background-color: #d48806;
}

.download-btn {
  background-color: var(--success-color);
  color: white;
}

.download-btn:hover {
  background-color: #389e0d;
}

/* 报告记录样式 */
.report-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-item {
  background-color: var(--background-color);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.report-header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
}

.report-date {
  color: var(--text-secondary);
  font-size: 12px;
}

.report-summary {
  margin-bottom: 16px;
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
}

.report-actions {
  display: flex;
  gap: 12px;
}

/* 系统设置样式 */
.settings-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.settings-card h3 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item label {
  color: var(--text-color);
  font-size: 14px;
}

.setting-value {
  color: var(--text-secondary);
  font-size: 14px;
}

.setting-btn {
  padding: 6px 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.setting-btn:hover {
  background-color: var(--primary-dark);
}

.setting-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.setting-select {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

/* 无数据提示 */
.no-data {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 14px;
  background-color: var(--background-color);
  border-radius: 8px;
  margin: 20px 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .top-nav {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .appointment-details {
    grid-template-columns: 1fr;
  }
  
  .appointment-actions {
    flex-direction: column;
  }
  
  .content-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>