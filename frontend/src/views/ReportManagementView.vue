<template>
  <div class="report-management">
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
        <p>加载报告信息中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchReports">重新加载</button>
      </div>

      <!-- 报告管理内容 -->
      <div v-else class="report-container">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1>报告管理</h1>
          <div class="search-filter">
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="搜索报告名称或体检中心"
              class="search-input"
              @input="debouncedSearch"
            />
            <select v-model="filterType" class="filter-select">
              <option value="all">全部报告</option>
              <option value="normal">正常</option>
              <option value="attention">需要关注</option>
              <option value="abnormal">异常</option>
            </select>
          </div>
        </div>

        <!-- 健康概览卡片 -->
        <div class="health-overview">
          <div class="overview-card">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <h3>健康评分</h3>
              <div class="score-display">
                <span class="score-number">{{ healthScore }}</span>
                <span class="score-label">{{ getHealthScoreLabel(healthScore) }}</span>
              </div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon">📋</div>
            <div class="card-content">
              <h3>报告总数</h3>
              <div class="report-count">{{ totalReports }}</div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon">⚠️</div>
            <div class="card-content">
              <h3>异常指标</h3>
              <div class="abnormal-count">{{ abnormalIndicators }}</div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon">🗓️</div>
            <div class="card-content">
              <h3>上次体检</h3>
              <div class="last-exam">{{ lastExamDate }}</div>
            </div>
          </div>
        </div>

        <!-- 报告列表 -->
        <div class="report-list">
          <div v-if="filteredReports.length === 0" class="empty-state">
            <div class="empty-icon">📄</div>
            <p>暂无体检报告</p>
            <button class="new-report-btn" @click="goToNewReport">
              <span class="plus-icon">+</span>
              <span>新建体检</span>
            </button>
          </div>
          
          <div 
            v-for="report in filteredReports" 
            :key="report.id" 
            class="report-card"
            :class="{ 'has-abnormal': report.has_abnormal }"
          >
            <div class="card-header">
              <div class="report-title">
                <h3>{{ report.name || '体检报告' }}</h3>
                <span class="report-status" :class="getStatusClass(report.overall_status)">
                  {{ getStatusText(report.overall_status) }}
                </span>
              </div>
              <div class="report-date">
                {{ formatReportDate(report.report_date) }}
              </div>
            </div>
            
            <div class="card-body">
              <div class="report-info">
                <div class="info-item">
                  <span class="info-label">体检中心:</span>
                  <span class="info-value">{{ report.hospital_name || '未指定' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">体检项目数:</span>
                  <span class="info-value">{{ report.total_items || 0 }} 项</span>
                </div>
                <div class="info-item">
                  <span class="info-label">异常项目:</span>
                  <span class="info-value abnormal">
                    {{ report.abnormal_items || 0 }} 项
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">生成日期:</span>
                  <span class="info-value">{{ formatDateTime(report.created_at) }}</span>
                </div>
              </div>
              
              <div v-if="report.key_indicators && report.key_indicators.length > 0" class="key-indicators">
                <div class="indicators-label">关键指标:</div>
                <div class="indicators-list">
                  <div 
                    v-for="(indicator, index) in report.key_indicators.slice(0, 3)" 
                    :key="index" 
                    class="indicator-item"
                    :class="{ 'abnormal': indicator.is_abnormal }"
                  >
                    <span class="indicator-name">{{ indicator.name }}:</span>
                    <span class="indicator-value">
                      {{ indicator.value }}
                      <span class="indicator-unit">{{ indicator.unit }}</span>
                    </span>
                    <span v-if="indicator.is_abnormal" class="abnormal-badge">异常</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="right-actions">
                <button 
                  class="action-btn view-btn" 
                  @click="viewReport(report.id)"
                >
                  查看报告
                </button>
                <button 
                  class="action-btn download-btn" 
                  @click="downloadReport(report.id)"
                >
                  下载报告
                </button>
                <button 
                  class="action-btn share-btn" 
                  @click="shareReport(report.id)"
                >
                  分享报告
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 报告趋势图 -->
        <div class="trend-section">
          <h2 class="section-title">健康趋势</h2>
          <div class="chart-container">
            <canvas ref="trendChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告详情弹窗 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content report-modal" @click.stop>
        <div class="modal-header">
          <h3>体检报告详情</h3>
          <button class="close-btn" @click="closeDetailsModal">×</button>
        </div>
        <div v-if="selectedReport" class="modal-body">
          <!-- 报告头部信息 -->
          <div class="report-header-info">
            <h2>{{ selectedReport.name || '体检报告' }}</h2>
            <div class="report-meta">
              <span class="meta-item">
                <i class="meta-icon">🏥</i>
                {{ selectedReport.hospital_name || '未指定' }}
              </span>
              <span class="meta-item">
                <i class="meta-icon">🗓️</i>
                {{ formatReportDate(selectedReport.report_date) }}
              </span>
              <span class="meta-item">
                <i class="meta-icon">📋</i>
                共 {{ selectedReport.total_items || 0 }} 项
              </span>
            </div>
            <div class="overall-status">
              <span class="status-label">总体评估:</span>
              <span 
                class="status-value"
                :class="getStatusClass(selectedReport.overall_status)"
              >
                {{ getStatusText(selectedReport.overall_status) }}
              </span>
            </div>
          </div>

          <!-- 体检者信息 -->
          <div class="report-section">
            <h3>体检者信息</h3>
            <div class="person-info">
              <div class="info-row">
                <div class="info-item">
                  <span class="info-label">姓名:</span>
                  <span class="info-value">{{ selectedReport.person_name || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">性别:</span>
                  <span class="info-value">{{ selectedReport.person_gender || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">年龄:</span>
                  <span class="info-value">{{ selectedReport.person_age || '-' }}</span>
                </div>
              </div>
              <div class="info-row">
                <div class="info-item">
                  <span class="info-label">身高:</span>
                  <span class="info-value">{{ selectedReport.person_height || '-' }} cm</span>
                </div>
                <div class="info-item">
                  <span class="info-label">体重:</span>
                  <span class="info-value">{{ selectedReport.person_weight || '-' }} kg</span>
                </div>
                <div class="info-item">
                  <span class="info-label">BMI:</span>
                  <span class="info-value">{{ selectedReport.person_bmi || '-' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 报告摘要 -->
          <div class="report-section">
            <h3>报告摘要</h3>
            <div class="report-summary">
              <p>{{ selectedReport.summary || '暂无摘要信息' }}</p>
            </div>
          </div>

          <!-- 异常指标 -->
          <div v-if="selectedReport.abnormal_indicators && selectedReport.abnormal_indicators.length > 0" class="report-section">
            <h3>异常指标 ({{ selectedReport.abnormal_indicators.length }})</h3>
            <div class="abnormal-indicators-list">
              <div 
                v-for="(indicator, index) in selectedReport.abnormal_indicators" 
                :key="index" 
                class="abnormal-indicator-item"
              >
                <div class="indicator-header">
                  <span class="indicator-name">{{ indicator.name }}</span>
                  <span class="indicator-status">异常</span>
                </div>
                <div class="indicator-details">
                  <div class="detail-row">
                    <span class="detail-label">检测值:</span>
                    <span class="detail-value">{{ indicator.value }}{{ indicator.unit }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">参考范围:</span>
                    <span class="detail-value">{{ indicator.reference_range }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">建议:</span>
                    <span class="detail-value">{{ indicator.suggestion || '请咨询医生' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 详细指标 -->
          <div class="report-section">
            <h3>详细指标</h3>
            <div class="indicators-tabs">
              <button 
                class="tab-btn" 
                :class="{ active: activeIndicatorsTab === 'all' }"
                @click="switchIndicatorsTab('all')"
              >
                全部指标
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeIndicatorsTab === 'normal' }"
                @click="switchIndicatorsTab('normal')"
              >
                正常指标
              </button>
              <button 
                class="tab-btn" 
                :class="{ active: activeIndicatorsTab === 'abnormal' }"
                @click="switchIndicatorsTab('abnormal')"
              >
                异常指标
              </button>
            </div>
            <div class="indicators-table">
              <table>
                <thead>
                  <tr>
                    <th>指标名称</th>
                    <th>检测值</th>
                    <th>参考范围</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="(indicator, index) in filteredIndicators" 
                    :key="index"
                    :class="{ 'abnormal-row': indicator.is_abnormal }"
                  >
                    <td>{{ indicator.name }}</td>
                    <td>{{ indicator.value }}{{ indicator.unit }}</td>
                    <td>{{ indicator.reference_range }}</td>
                    <td>
                      <span class="indicator-status" :class="indicator.is_abnormal ? 'abnormal' : 'normal'">
                        {{ indicator.is_abnormal ? '异常' : '正常' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 医生建议 -->
          <div class="report-section">
            <h3>医生建议</h3>
            <div class="doctor-advice">
              <p>{{ selectedReport.doctor_advice || '暂无医生建议' }}</p>
            </div>
          </div>

          <!-- 后续检查建议 -->
          <div v-if="selectedReport.follow_up_suggestions && selectedReport.follow_up_suggestions.length > 0" class="report-section">
            <h3>后续检查建议</h3>
            <div class="follow-up-suggestions">
              <ul>
                <li v-for="(suggestion, index) in selectedReport.follow_up_suggestions" :key="index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="closeDetailsModal">关闭</button>
          <button class="modal-btn primary" @click="downloadReport(selectedReport?.id)">下载报告</button>
          <button class="modal-btn secondary" @click="viewReportInterpretation(selectedReport?.id)">报告解读</button>
        </div>
      </div>
    </div>

    <!-- 分享报告弹窗 -->
    <div v-if="showShareModal" class="modal-overlay" @click="closeShareModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>分享报告</h3>
        </div>
        <div class="modal-body">
          <p>请选择分享方式:</p>
          <div class="share-options">
            <button class="share-option" @click="shareViaSMS">
              <div class="share-icon">📱</div>
              <span>短信分享</span>
            </button>
            <button class="share-option" @click="shareViaEmail">
              <div class="share-icon">✉️</div>
              <span>邮件分享</span>
            </button>
            <button class="share-option" @click="copyReportLink">
              <div class="share-icon">🔗</div>
              <span>复制链接</span>
            </button>
          </div>
          <div v-if="shareSuccess" class="share-success">
            <div class="success-icon">✅</div>
            <p>{{ shareSuccessMessage }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="closeShareModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { router } from '../router'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'

// 注册Chart.js组件
Chart.register(...registerables)

// 状态管理
const isLoading = ref(true)
const error = ref('')
const reports = ref([])
const searchKeyword = ref('')
const filterType = ref('all')
const selectedReportId = ref(null)
const selectedReport = ref(null)
const showDetailsModal = ref(false)
const showShareModal = ref(false)
const shareSuccess = ref(false)
const shareSuccessMessage = ref('')
const activeIndicatorsTab = ref('all')

// 健康概览数据
const healthScore = ref(85)
const totalReports = computed(() => reports.value.length)
const abnormalIndicators = ref(0)
const lastExamDate = ref('2023-06-15')

// 图表引用
const trendChart = ref(null)
let chartInstance = null

// 获取报告列表
const fetchReports = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    const response = await axios.get(`/report/${userId}/list`)
    
    if (response.status === 'success' && response.data) {
      reports.value = response.data
      // 计算异常指标总数
      calculateAbnormalIndicators()
      // 生成趋势图
      generateTrendChart()
    } else {
      error.value = '获取报告信息失败'
    }
  } catch (err) {
    console.error('获取报告信息错误:', err)
    error.value = '网络错误，请检查您的网络连接'
  } finally {
    isLoading.value = false
  }
}

// 计算异常指标总数
const calculateAbnormalIndicators = () => {
  let count = 0
  reports.value.forEach(report => {
    count += report.abnormal_items || 0
  })
  abnormalIndicators.value = count
}

// 过滤报告
const filteredReports = computed(() => {
  let filtered = reports.value
  
  // 搜索过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(report => 
      (report.name && report.name.toLowerCase().includes(keyword)) ||
      (report.hospital_name && report.hospital_name.toLowerCase().includes(keyword))
    )
  }
  
  // 类型过滤
  if (filterType.value !== 'all') {
    filtered = filtered.filter(report => 
      report.overall_status === filterType.value
    )
  }
  
  // 按日期排序，最新的在前
  return filtered.sort((a, b) => 
    new Date(b.report_date) - new Date(a.report_date)
  )
})

// 防抖搜索
const debouncedSearch = () => {
  clearTimeout(window.searchTimeout)
  window.searchTimeout = setTimeout(() => {
    // 搜索逻辑已在computed中处理
  }, 300)
}

// 查看报告详情
const viewReport = async (reportId) => {
  try {
    const response = await axios.get(`/report/${reportId}/details`)
    
    if (response.status === 'success' && response.data) {
      selectedReport.value = response.data
      showDetailsModal.value = true
    } else {
      alert('获取报告详情失败')
    }
  } catch (err) {
    console.error('获取报告详情错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 关闭详情弹窗
const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedReport.value = null
  activeIndicatorsTab.value = 'all'
}

// 下载报告
const downloadReport = async (reportId) => {
  try {
    const response = await axios.get(`/report/${reportId}/download`, {
      responseType: 'blob'
    })
    
    if (response.data) {
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `体检报告_${reportId}.pdf`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      alert('报告下载成功')
    } else {
      alert('报告下载失败')
    }
  } catch (err) {
    console.error('下载报告错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 分享报告
const shareReport = (reportId) => {
  selectedReportId.value = reportId
  showShareModal.value = true
  shareSuccess.value = false
}

// 关闭分享弹窗
const closeShareModal = () => {
  showShareModal.value = false
  selectedReportId.value = null
  shareSuccess.value = false
  shareSuccessMessage.value = ''
}

// 短信分享
const shareViaSMS = async () => {
  try {
    const phoneNumber = prompt('请输入接收短信的手机号码:')
    if (!phoneNumber) return
    
    const response = await axios.post(`/report/${selectedReportId.value}/share/sms`, {
      phone_number: phoneNumber
    })
    
    if (response.status === 'success') {
      shareSuccess.value = true
      shareSuccessMessage.value = '报告已发送至短信'
    } else {
      alert(response.message || '短信发送失败')
    }
  } catch (err) {
    console.error('短信分享错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 邮件分享
const shareViaEmail = async () => {
  try {
    const email = prompt('请输入接收邮件的邮箱地址:')
    if (!email) return
    
    const response = await axios.post(`/report/${selectedReportId.value}/share/email`, {
      email: email
    })
    
    if (response.status === 'success') {
      shareSuccess.value = true
      shareSuccessMessage.value = '报告已发送至邮箱'
    } else {
      alert(response.message || '邮件发送失败')
    }
  } catch (err) {
    console.error('邮件分享错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 复制链接
const copyReportLink = async () => {
  try {
    const response = await axios.get(`/report/${selectedReportId.value}/share/link`)
    
    if (response.status === 'success' && response.data?.share_link) {
      // 复制链接到剪贴板
      await navigator.clipboard.writeText(response.data.share_link)
      shareSuccess.value = true
      shareSuccessMessage.value = '分享链接已复制到剪贴板'
    } else {
      alert('获取分享链接失败')
    }
  } catch (err) {
    console.error('复制链接错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 查看报告解读
const viewReportInterpretation = (reportId) => {
  localStorage.setItem('currentReportId', reportId)
  router.push('/report-interpretation')
}

// 切换指标标签页
const switchIndicatorsTab = (tab) => {
  activeIndicatorsTab.value = tab
}

// 过滤指标
const filteredIndicators = computed(() => {
  if (!selectedReport.value?.indicators) return []
  
  switch (activeIndicatorsTab.value) {
    case 'normal':
      return selectedReport.value.indicators.filter(indicator => !indicator.is_abnormal)
    case 'abnormal':
      return selectedReport.value.indicators.filter(indicator => indicator.is_abnormal)
    case 'all':
    default:
      return selectedReport.value.indicators
  }
})

// 生成趋势图
const generateTrendChart = async () => {
  await nextTick()
  
  if (!trendChart.value || reports.value.length === 0) return
  
  // 销毁已存在的图表
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  // 准备图表数据
  const labels = reports.value.slice(-6).map(report => formatShortDate(report.report_date))
  const scores = reports.value.slice(-6).map(report => report.health_score || 85)
  const abnormalCounts = reports.value.slice(-6).map(report => report.abnormal_items || 0)
  
  // 创建图表
  chartInstance = new Chart(trendChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '健康评分',
          data: scores,
          borderColor: '#1890ff',
          backgroundColor: 'rgba(24, 144, 255, 0.1)',
          tension: 0.3,
          yAxisID: 'y'
        },
        {
          label: '异常指标数',
          data: abnormalCounts,
          borderColor: '#f5222d',
          backgroundColor: 'rgba(245, 34, 45, 0.1)',
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: '体检日期'
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: '健康评分'
          },
          min: 0,
          max: 100
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: '异常指标数'
          },
          min: 0,
          max: Math.max(...abnormalCounts) * 1.5 || 10,
          grid: {
            drawOnChartArea: false,
          }
        }
      }
    }
  })
}

// 格式化报告日期
const formatReportDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 格式化短日期
const formatShortDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
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
    'normal': '正常',
    'attention': '需要关注',
    'abnormal': '异常'
  }
  return statuses[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classes = {
    'normal': 'status-normal',
    'attention': 'status-attention',
    'abnormal': 'status-abnormal'
  }
  return classes[status] || ''
}

// 获取健康评分标签
const getHealthScoreLabel = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '一般'
  if (score >= 60) return '需关注'
  return '需改善'
}

// 前往新建体检
const goToNewReport = () => {
  router.push('/appointment-create')
}

// 返回
const goBack = () => {
  router.back()
}

// 组件挂载时获取报告信息
onMounted(() => {
  fetchReports()
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
  clearTimeout(window.searchTimeout)
})
</script>

<style scoped>
/* 报告管理页面样式 */
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

.report-management {
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

/* 报告容器 */
.report-container {
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
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0;
  color: var(--text-color);
  font-size: 28px;
}

.search-filter {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  width: 300px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: var(--primary-color);
}

.filter-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  background-color: white;
}

.filter-select:focus {
  border-color: var(--primary-color);
}

/* 健康概览 */
.health-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}

.overview-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.overview-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-icon {
  font-size: 32px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e6f7ff;
  border-radius: 50%;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: normal;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.score-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--primary-color);
}

.score-label {
  font-size: 14px;
  color: var(--text-color);
}

.report-count,
.abnormal-count,
.last-exam {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-color);
}

.abnormal-count {
  color: var(--error-color);
}

.last-exam {
  font-size: 18px;
}

/* 报告列表 */
.report-list {
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
  margin-bottom: 20px;
}

.new-report-btn {
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

.new-report-btn:hover {
  background-color: var(--primary-dark);
}

.plus-icon {
  font-size: 18px;
  font-weight: bold;
}

/* 报告卡片 */
.report-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.report-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.report-card.has-abnormal {
  border-left-color: var(--error-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.report-title h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 18px;
  font-weight: 500;
}

.report-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-normal {
  background-color: #f6ffed;
  color: var(--success-color);
}

.status-attention {
  background-color: #fffbe6;
  color: var(--warning-color);
}

.status-abnormal {
  background-color: #fff1f0;
  color: var(--error-color);
}

.report-date {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-body {
  margin-bottom: 20px;
}

.report-info {
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
  min-width: 100px;
}

.info-value {
  color: var(--text-color);
  font-size: 14px;
}

.info-value.abnormal {
  color: var(--error-color);
  font-weight: 500;
}

.key-indicators {
  background-color: var(--background-color);
  padding: 16px;
  border-radius: 6px;
}

.indicators-label {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 12px;
}

.indicators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.indicator-item.abnormal {
  border-color: var(--error-color);
  background-color: #fff1f0;
}

.indicator-name {
  color: var(--text-color);
  font-size: 14px;
  min-width: 100px;
}

.indicator-value {
  color: var(--text-secondary);
  font-size: 14px;
}

.indicator-unit {
  font-size: 12px;
  color: var(--text-secondary);
}

.abnormal-badge {
  padding: 2px 6px;
  background-color: var(--error-color);
  color: white;
  font-size: 10px;
  border-radius: 3px;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.right-actions {
  display: flex;
  gap: 12px;
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

.view-btn {
  background-color: var(--primary-color);
  color: white;
}

.view-btn:hover {
  background-color: var(--primary-dark);
}

.download-btn {
  background-color: var(--success-color);
  color: white;
}

.download-btn:hover {
  background-color: #389e0d;
}

.share-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.share-btn:hover {
  background-color: #bfbfbf;
}

/* 趋势图部分 */
.trend-section {
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

.chart-container {
  width: 100%;
  height: 300px;
}

/* 报告详情弹窗 */
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

.modal-content.report-modal {
  max-width: 90%;
  max-height: 90vh;
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

/* 报告头部信息 */
.report-header-info {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid var(--border-color);
}

.report-header-info h2 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 28px;
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-icon {
  font-size: 16px;
}

.overall-status {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.status-label {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.status-value {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
}

/* 报告部分 */
.report-section {
  margin-bottom: 32px;
}

.report-section h3 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 18px;
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

/* 体检者信息 */
.person-info {
  background-color: var(--background-color);
  padding: 20px;
  border-radius: 6px;
}

.info-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

/* 报告摘要 */
.report-summary p {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 异常指标列表 */
.abnormal-indicators-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.abnormal-indicator-item {
  background-color: #fff1f0;
  border: 1px solid var(--error-color);
  border-radius: 6px;
  padding: 16px;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.indicator-name {
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
}

.indicator-status {
  padding: 4px 8px;
  background-color: var(--error-color);
  color: white;
  font-size: 12px;
  border-radius: 3px;
}

.indicator-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 12px;
  min-width: 80px;
}

.detail-value {
  color: var(--text-color);
  font-size: 12px;
  flex: 1;
}

/* 指标标签页 */
.indicators-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background-color: var(--background-color);
  padding: 8px;
  border-radius: 6px;
}

.tab-btn {
  padding: 8px 16px;
  background-color: white;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.tab-btn.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.tab-btn:hover:not(.active) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* 指标表格 */
.indicators-table {
  overflow-x: auto;
}

.indicators-table table {
  width: 100%;
  border-collapse: collapse;
}

.indicators-table th,
.indicators-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.indicators-table th {
  background-color: var(--background-color);
  color: var(--text-color);
  font-weight: 500;
  font-size: 14px;
}

.indicators-table td {
  color: var(--text-color);
  font-size: 14px;
}

.indicators-table tr.abnormal-row {
  background-color: #fff1f0;
}

.indicator-status {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.indicator-status.normal {
  background-color: #f6ffed;
  color: var(--success-color);
}

.indicator-status.abnormal {
  background-color: #fff1f0;
  color: var(--error-color);
}

/* 医生建议 */
.doctor-advice p {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 后续检查建议 */
.follow-up-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.follow-up-suggestions li {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.follow-up-suggestions li:last-child {
  margin-bottom: 0;
}

/* 弹窗底部 */
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

.modal-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.modal-btn:hover {
  background-color: #bfbfbf;
}

.modal-btn.primary {
  background-color: var(--primary-color);
  color: white;
}

.modal-btn.primary:hover {
  background-color: var(--primary-dark);
}

.modal-btn.secondary {
  background-color: var(--success-color);
  color: white;
}

.modal-btn.secondary:hover {
  background-color: #389e0d;
}

/* 分享弹窗 */
.share-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.share-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: var(--text-color);
}

.share-option:hover {
  background-color: #e6f7ff;
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.share-icon {
  font-size: 24px;
}

.share-success {
  text-align: center;
  padding: 16px;
  background-color: #f6ffed;
  border: 1px solid var(--success-color);
  border-radius: 6px;
  margin-top: 20px;
}

.success-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.share-success p {
  margin: 0;
  color: var(--success-color);
  font-size: 14px;
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
  
  .search-filter {
    flex-direction: column;
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .health-overview {
    grid-template-columns: 1fr;
  }
  
  .report-info {
    grid-template-columns: 1fr;
  }
  
  .right-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .report-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .info-row {
    grid-template-columns: 1fr;
  }
  
  .indicators-tabs {
    flex-wrap: wrap;
  }
  
  .share-options {
    grid-template-columns: 1fr;
  }
}
</style>