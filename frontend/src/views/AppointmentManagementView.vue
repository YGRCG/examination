<template>
  <div class="appointment-management">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-left">
        <span class="system-logo">🏥 医院体检项目智能推荐系统</span>
      </div>
      <div class="nav-right">
        <button class="back-btn" @click="goBack">返回</button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载预约信息中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchAppointments">重新加载</button>
      </div>

      <!-- 预约管理内容 -->
      <div v-else class="appointment-container">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1>预约管理</h1>
          <button class="new-appointment-btn" @click="goToNewAppointment">
            <span class="plus-icon">+</span>
            <span>新建预约</span>
          </button>
        </div>

        <!-- 预约状态标签页 -->
        <div class="appointment-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'upcoming' }"
            @click="switchTab('upcoming')"
          >
            待进行预约
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'completed' }"
            @click="switchTab('completed')"
          >
            已完成预约
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'cancelled' }"
            @click="switchTab('cancelled')"
          >
            已取消预约
          </button>
        </div>

        <!-- 预约列表 -->
        <div class="appointment-list">
          <div v-if="filteredAppointments.length === 0" class="empty-state">
            <div class="empty-icon">📅</div>
            <p>{{ getEmptyStateText() }}</p>
          </div>
          
          <div 
            v-for="appointment in filteredAppointments" 
            :key="appointment.id" 
            class="appointment-card"
          >
            <div class="card-header">
              <div class="appointment-title">
                <h3>{{ appointment.name || '体检预约' }}</h3>
                <span class="appointment-status" :class="getStatusClass(appointment.status)">
                  {{ getStatusText(appointment.status) }}
                </span>
              </div>
              <div class="appointment-date">
                {{ formatAppointmentDate(appointment.appointment_date) }}
              </div>
            </div>
            
            <div class="card-body">
              <div class="appointment-info">
                <div class="info-item">
                  <span class="info-label">体检中心:</span>
                  <span class="info-value">{{ appointment.hospital_name || '未指定' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">预约时间:</span>
                  <span class="info-value">{{ appointment.appointment_time || '未指定' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">预约项目数:</span>
                  <span class="info-value">{{ appointment.total_items || 0 }} 项</span>
                </div>
                <div class="info-item">
                  <span class="info-label">预约金额:</span>
                  <span class="info-value price">¥{{ appointment.total_price || 0 }}</span>
                </div>
              </div>
              
              <div class="appointment-items-preview">
                <div class="preview-label">包含项目:</div>
                <div class="items-list">
                  <span v-for="(item, index) in appointment.items_preview" :key="index" class="item-tag">
                    {{ item }}
                  </span>
                  <span v-if="appointment.items_preview.length > 3" class="item-more">
                    +{{ appointment.items_preview.length - 3 }} 项
                  </span>
                </div>
              </div>
            </div>
            
            <div class="card-footer">
              <button 
                class="action-btn details-btn" 
                @click="showAppointmentDetails(appointment.id)"
              >
                查看详情
              </button>
              
              <div v-if="appointment.status === 'upcoming'" class="right-actions">
                <button 
                  class="action-btn modify-btn" 
                  @click="modifyAppointment(appointment.id)"
                >
                  修改预约
                </button>
                <button 
                  class="action-btn cancel-btn" 
                  @click="confirmCancelAppointment(appointment.id)"
                >
                  取消预约
                </button>
              </div>
              
              <div v-else-if="appointment.status === 'completed'" class="right-actions">
                <button 
                  class="action-btn report-btn" 
                  @click="viewReport(appointment.id)"
                >
                  查看报告
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 预约日历视图 -->
        <div class="calendar-section">
          <h2 class="section-title">预约日历</h2>
          <div class="calendar-container">
            <!-- 简化版日历显示 -->
            <div class="calendar-header">
              <button class="calendar-nav-btn" @click="prevMonth">
                ◀
              </button>
              <h3 class="calendar-title">{{ currentMonthText }}</h3>
              <button class="calendar-nav-btn" @click="nextMonth">
                ▶
              </button>
            </div>
            
            <div class="calendar-weekdays">
              <div class="weekday">日</div>
              <div class="weekday">一</div>
              <div class="weekday">二</div>
              <div class="weekday">三</div>
              <div class="weekday">四</div>
              <div class="weekday">五</div>
              <div class="weekday">六</div>
            </div>
            
            <div class="calendar-days">
              <div 
                v-for="day in calendarDays" 
                :key="day.date"
                class="calendar-day"
                :class="{
                  'other-month': day.isOtherMonth,
                  'current-day': day.isCurrentDay,
                  'has-appointment': day.hasAppointment,
                  'upcoming-appointment': day.upcomingAppointment,
                  'completed-appointment': day.completedAppointment
                }"
                @click="selectDay(day.date)"
              >
                <span class="day-number">{{ day.day }}</span>
                <span v-if="day.hasAppointment" class="appointment-indicator"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预约详情弹窗 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>预约详情</h3>
          <button class="close-btn" @click="closeDetailsModal">×</button>
        </div>
        <div v-if="selectedAppointment" class="modal-body">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">预约名称:</span>
                <span class="detail-value">{{ selectedAppointment.name || '体检预约' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预约状态:</span>
                <span class="detail-value" :class="getStatusClass(selectedAppointment.status)">
                  {{ getStatusText(selectedAppointment.status) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">体检中心:</span>
                <span class="detail-value">{{ selectedAppointment.hospital_name || '未指定' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预约日期:</span>
                <span class="detail-value">{{ formatAppointmentDate(selectedAppointment.appointment_date) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预约时间:</span>
                <span class="detail-value">{{ selectedAppointment.appointment_time || '未指定' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预约金额:</span>
                <span class="detail-value price">¥{{ selectedAppointment.total_price || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间:</span>
                <span class="detail-value">{{ formatDateTime(selectedAppointment.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">更新时间:</span>
                <span class="detail-value">{{ formatDateTime(selectedAppointment.updated_at) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>体检项目</h4>
            <div class="items-table">
              <table>
                <thead>
                  <tr>
                    <th>项目名称</th>
                    <th>类别</th>
                    <th>价格</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in selectedAppointment.items" :key="item.id">
                    <td>{{ item.name }}</td>
                    <td>{{ item.category }}</td>
                    <td>¥{{ item.price }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="2" class="total-label">总计</td>
                    <td class="total-price">¥{{ selectedAppointment.total_price || 0 }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <div class="detail-section">
            <h4>注意事项</h4>
            <div class="notes-content">
              <p>1. 请提前15分钟到达体检中心，携带有效身份证件。</p>
              <p>2. 体检前一天请保持清淡饮食，晚上10点后禁食。</p>
              <p>3. 体检当天早晨请空腹，可少量饮水。</p>
              <p>4. 穿着宽松舒适的衣物，女士避免穿连衣裙。</p>
              <p>5. 如有特殊情况，请提前联系客服。</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="closeDetailsModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 取消预约确认弹窗 -->
    <div v-if="showCancelModal" class="modal-overlay" @click="closeCancelModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>取消预约确认</h3>
        </div>
        <div class="modal-body">
          <p>您确定要取消此预约吗？取消后可能会产生一定的手续费。</p>
          <div class="cancel-reason">
            <label for="cancel_reason">取消原因:</label>
            <textarea 
              id="cancel_reason" 
              v-model="cancelReason" 
              placeholder="请输入取消原因（选填）"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeCancelModal">取消</button>
          <button class="modal-btn confirm danger" @click="cancelAppointment">确认取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { router } from '../router'
import axios from 'axios'

// 状态管理
const isLoading = ref(true)
const error = ref('')
const appointments = ref([])
const activeTab = ref('upcoming')
const selectedAppointmentId = ref(null)
const selectedAppointment = ref(null)
const showDetailsModal = ref(false)
const showCancelModal = ref(false)
const cancelReason = ref('')

// 日历状态
const currentDate = ref(new Date())
const calendarDays = ref([])

// 获取预约信息
const fetchAppointments = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    const response = await axios.get(`/appointment/${userId}/list`)
    
    if (response.status === 'success' && response.data) {
      appointments.value = response.data
      generateCalendarDays()
    } else {
      error.value = '获取预约信息失败'
    }
  } catch (err) {
    console.error('获取预约信息错误:', err)
    error.value = '网络错误，请检查您的网络连接'
  } finally {
    isLoading.value = false
  }
}

// 根据当前标签过滤预约
const filteredAppointments = computed(() => {
  return appointments.value.filter(appointment => 
    appointment.status === activeTab.value
  )
})

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
}

// 查看预约详情
const showAppointmentDetails = async (appointmentId) => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    const response = await axios.get(`/appointment/${appointmentId}/details`)
    
    if (response.status === 'success' && response.data) {
      selectedAppointment.value = response.data
      showDetailsModal.value = true
    } else {
      alert('获取预约详情失败')
    }
  } catch (err) {
    console.error('获取预约详情错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 关闭详情弹窗
const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedAppointment.value = null
}

// 确认取消预约
const confirmCancelAppointment = (appointmentId) => {
  selectedAppointmentId.value = appointmentId
  cancelReason.value = ''
  showCancelModal.value = true
}

// 关闭取消弹窗
const closeCancelModal = () => {
  showCancelModal.value = false
  selectedAppointmentId.value = null
  cancelReason.value = ''
}

// 取消预约
const cancelAppointment = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId || !selectedAppointmentId.value) {
      return
    }
    
    const response = await axios.post(`/appointment/${selectedAppointmentId.value}/cancel`, {
      reason: cancelReason.value
    })
    
    if (response.status === 'success') {
      // 重新获取预约列表
      await fetchAppointments()
      showCancelModal.value = false
      alert('预约已成功取消')
    } else {
      alert(response.message || '取消预约失败，请重试')
    }
  } catch (err) {
    console.error('取消预约错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 修改预约
const modifyAppointment = (appointmentId) => {
  // 保存预约ID到localStorage
  localStorage.setItem('modifyAppointmentId', appointmentId)
  router.push('/appointment-create')
}

// 查看报告
const viewReport = (appointmentId) => {
  // 保存预约ID到localStorage
  localStorage.setItem('appointmentId', appointmentId)
  router.push('/report-management')
}

// 前往新建预约
const goToNewAppointment = () => {
  router.push('/appointment-create')
}

// 返回
const goBack = () => {
  router.back()
}

// 格式化预约日期
const formatAppointmentDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status) => {
  const statuses = {
    'upcoming': '待进行',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statuses[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classes = {
    'upcoming': 'status-upcoming',
    'completed': 'status-completed',
    'cancelled': 'status-cancelled'
  }
  return classes[status] || ''
}

// 获取空状态文本
const getEmptyStateText = () => {
  const texts = {
    'upcoming': '暂无待进行的预约',
    'completed': '暂无已完成的预约',
    'cancelled': '暂无已取消的预约'
  }
  return texts[activeTab.value] || '暂无预约记录'
}

// 生成日历天数
const generateCalendarDays = () => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  // 获取当月第一天和最后一天
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  // 获取当月第一天是星期几
  const firstDayIndex = firstDay.getDay()
  
  // 获取当月总天数
  const daysInMonth = lastDay.getDate()
  
  // 计算需要显示的上个月的天数
  const prevDays = firstDayIndex
  
  // 计算需要显示的下个月的天数
  const nextDays = 42 - (prevDays + daysInMonth) // 6行7列
  
  // 获取上个月的最后一天
  const prevLastDay = new Date(year, month, 0)
  const prevLastDate = prevLastDay.getDate()
  
  const days = []
  
  // 添加上个月的天数
  for (let i = prevDays; i > 0; i--) {
    const date = new Date(year, month - 1, prevLastDate - i + 1)
    days.push({
      day: prevLastDate - i + 1,
      date: date,
      isOtherMonth: true,
      isCurrentDay: false,
      hasAppointment: false,
      upcomingAppointment: false,
      completedAppointment: false
    })
  }
  
  // 添加当月的天数
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i)
    const dateStr = date.toISOString().split('T')[0]
    const hasAppointment = appointments.value.some(appointment => {
      const apptDate = new Date(appointment.appointment_date).toISOString().split('T')[0]
      return apptDate === dateStr
    })
    const upcomingAppointment = appointments.value.some(appointment => {
      const apptDate = new Date(appointment.appointment_date).toISOString().split('T')[0]
      return apptDate === dateStr && appointment.status === 'upcoming'
    })
    const completedAppointment = appointments.value.some(appointment => {
      const apptDate = new Date(appointment.appointment_date).toISOString().split('T')[0]
      return apptDate === dateStr && appointment.status === 'completed'
    })
    
    days.push({
      day: i,
      date: date,
      isOtherMonth: false,
      isCurrentDay: isSameDay(date, new Date()),
      hasAppointment: hasAppointment,
      upcomingAppointment: upcomingAppointment,
      completedAppointment: completedAppointment
    })
  }
  
  // 添加下个月的天数
  for (let i = 1; i <= nextDays; i++) {
    const date = new Date(year, month + 1, i)
    days.push({
      day: i,
      date: date,
      isOtherMonth: true,
      isCurrentDay: false,
      hasAppointment: false,
      upcomingAppointment: false,
      completedAppointment: false
    })
  }
  
  calendarDays.value = days
}

// 检查两个日期是否为同一天
const isSameDay = (date1, date2) => {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate()
}

// 获取当前月份文本
const currentMonthText = computed(() => {
  return currentDate.value.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long'
  })
})

// 上个月
const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  generateCalendarDays()
}

// 下个月
const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  generateCalendarDays()
}

// 选择日期
const selectDay = (date) => {
  if (date.isOtherMonth) return
  
  const dateStr = date.toISOString().split('T')[0]
  const dayAppointments = appointments.value.filter(appointment => {
    const apptDate = new Date(appointment.appointment_date).toISOString().split('T')[0]
    return apptDate === dateStr
  })
  
  if (dayAppointments.length > 0) {
    // 如果有多个预约，显示第一个的详情
    showAppointmentDetails(dayAppointments[0].id)
  }
}

// 组件挂载时获取预约信息
onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
/* 预约管理页面样式 */
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

.appointment-management {
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

/* 预约容器 */
.appointment-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: var(--text-color);
  font-size: 28px;
}

.new-appointment-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.new-appointment-btn:hover {
  background-color: var(--primary-dark);
}

.plus-icon {
  font-size: 18px;
  font-weight: bold;
}

/* 预约状态标签页 */
.appointment-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background-color: var(--card-background);
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  background-color: var(--background-color);
  color: var(--text-secondary);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.tab-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.tab-btn:hover:not(.active) {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

/* 预约列表 */
.appointment-list {
  margin-bottom: 40px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: var(--card-background);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 预约卡片 */
.appointment-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  transition: all 0.3s ease;
}

.appointment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.appointment-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.appointment-title h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 18px;
  font-weight: 500;
}

.appointment-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-upcoming {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

.status-completed {
  background-color: #f6ffed;
  color: var(--success-color);
}

.status-cancelled {
  background-color: #fff1f0;
  color: var(--error-color);
}

.appointment-date {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-body {
  margin-bottom: 20px;
}

.appointment-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  color: var(--text-secondary);
  font-size: 14px;
  min-width: 80px;
}

.info-value {
  color: var(--text-color);
  font-size: 14px;
}

.info-value.price {
  color: var(--primary-color);
  font-weight: 500;
}

.appointment-items-preview {
  background-color: var(--background-color);
  padding: 16px;
  border-radius: 6px;
}

.preview-label {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 12px;
}

.items-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.item-tag {
  padding: 4px 8px;
  background-color: #e6f7ff;
  color: var(--primary-color);
  font-size: 12px;
  border-radius: 3px;
}

.item-more {
  color: var(--text-secondary);
  font-size: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.details-btn {
  background-color: var(--background-color);
  color: var(--text-color);
}

.details-btn:hover {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

.right-actions {
  display: flex;
  gap: 12px;
}

.modify-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.modify-btn:hover {
  background-color: #bfbfbf;
}

.cancel-btn {
  background-color: var(--error-color);
  color: white;
}

.cancel-btn:hover {
  background-color: #cf1322;
}

.report-btn {
  background-color: var(--success-color);
  color: white;
}

.report-btn:hover {
  background-color: #389e0d;
}

/* 日历部分 */
.calendar-section {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.section-title {
  margin: 0 0 24px;
  color: var(--text-color);
  font-size: 20px;
  font-weight: 500;
}

.calendar-container {
  width: 100%;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-nav-btn {
  background-color: var(--background-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.calendar-nav-btn:hover {
  background-color: var(--border-color);
}

.calendar-title {
  margin: 0;
  color: var(--text-color);
  font-size: 18px;
  font-weight: 500;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  padding: 8px;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-color);
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.calendar-day:hover:not(.other-month) {
  background-color: #e6f7ff;
  transform: scale(1.05);
}

.calendar-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.calendar-day.current-day {
  background-color: var(--primary-color);
  color: white;
  font-weight: bold;
}

.calendar-day.has-appointment {
  background-color: #f6ffed;
}

.calendar-day.upcoming-appointment {
  background-color: #e6f7ff;
}

.calendar-day.completed-appointment {
  background-color: #f6ffed;
}

.day-number {
  font-size: 14px;
  color: var(--text-color);
}

.calendar-day.current-day .day-number {
  color: white;
}

.appointment-indicator {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background-color: var(--primary-color);
  border-radius: 50%;
}

/* 预约详情弹窗 */
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
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalFadeIn 0.3s ease-in-out;
}

.modal-content.large {
  max-width: 800px;
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
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
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
  color: var(--text-color);
}

.modal-body {
  margin-bottom: 24px;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section h4 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 14px;
  min-width: 100px;
}

.detail-value {
  color: var(--text-color);
  font-size: 14px;
}

.detail-value.price {
  color: var(--primary-color);
  font-weight: 500;
}

.items-table {
  overflow-x: auto;
}

.items-table table {
  width: 100%;
  border-collapse: collapse;
}

.items-table th,
.items-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.items-table th {
  background-color: var(--background-color);
  color: var(--text-color);
  font-weight: 500;
  font-size: 14px;
}

.items-table td {
  color: var(--text-color);
  font-size: 14px;
}

.items-table tfoot {
  background-color: var(--background-color);
}

.total-label {
  text-align: right;
  font-weight: bold;
  color: var(--text-color);
}

.total-price {
  color: var(--primary-color);
  font-weight: bold;
}

.notes-content p {
  margin: 0 0 12px;
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
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
  background-color: var(--border-color);
  color: var(--text-color);
}

.modal-btn.cancel:hover {
  background-color: #bfbfbf;
}

.modal-btn.confirm {
  background-color: var(--primary-color);
  color: white;
}

.modal-btn.confirm:hover {
  background-color: var(--primary-dark);
}

.modal-btn.confirm.danger {
  background-color: var(--error-color);
}

.modal-btn.confirm.danger:hover {
  background-color: #cf1322;
}

/* 取消原因 */
.cancel-reason {
  margin-top: 16px;
}

.cancel-reason label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
}

.cancel-reason textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.cancel-reason textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .appointment-tabs {
    flex-direction: column;
  }
  
  .appointment-info {
    grid-template-columns: 1fr;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .right-actions {
    flex-direction: column;
  }
  
  .modal-content.large {
    max-height: 90vh;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .calendar-days {
    gap: 4px;
  }
  
  .calendar-day {
    font-size: 12px;
  }
}
</style>