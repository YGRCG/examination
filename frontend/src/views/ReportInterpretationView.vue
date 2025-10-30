<template>
  <div class="report-interpretation">
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
        <p>加载报告解读中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchReportInterpretation">重新加载</button>
      </div>

      <!-- 报告解读内容 -->
      <div v-else-if="reportInterpretation" class="interpretation-container">
        <!-- 页面标题和报告信息 -->
        <div class="page-header">
          <div class="header-left">
            <h1>报告解读</h1>
            <div class="report-info-header">
              <span class="report-title">{{ reportInterpretation.report_name }}</span>
              <span class="report-date">{{ formatReportDate(reportInterpretation.report_date) }}</span>
            </div>
          </div>
          <div class="header-right">
            <button class="action-btn" @click="printInterpretation">打印解读</button>
            <button class="action-btn primary" @click="saveToHealthRecord">保存到健康档案</button>
          </div>
        </div>

        <!-- 解读导航 -->
        <div class="interpretation-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'overview' }"
            @click="switchTab('overview')"
          >
            总体解读
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'detailed' }"
            @click="switchTab('detailed')"
          >
            详细解读
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'suggestions' }"
            @click="switchTab('suggestions')"
          >
            健康建议
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'trends' }"
            @click="switchTab('trends')"
          >
            趋势分析
          </button>
        </div>

        <!-- 总体解读内容 -->
        <div v-if="activeTab === 'overview'" class="tab-content">
          <!-- 健康评分卡片 -->
          <div class="health-score-card">
            <div class="score-left">
              <div class="score-icon">📊</div>
              <div class="score-info">
                <h3>健康评分</h3>
                <div class="score-display">
                  <span class="score-number">{{ reportInterpretation.health_score }}</span>
                  <span class="score-label">{{ getHealthScoreLabel(reportInterpretation.health_score) }}</span>
                </div>
              </div>
            </div>
            <div class="score-right">
              <div class="score-meaning">
                <h4>评分说明</h4>
                <p>{{ getScoreMeaning(reportInterpretation.health_score) }}</p>
              </div>
            </div>
          </div>

          <!-- 总体评估 -->
          <div class="section-card">
            <h3>总体评估</h3>
            <div class="assessment-content">
              <p>{{ reportInterpretation.overall_assessment }}</p>
            </div>
          </div>

          <!-- 异常指标概览 -->
          <div v-if="reportInterpretation.abnormal_indicators && reportInterpretation.abnormal_indicators.length > 0" class="section-card">
            <h3>异常指标概览</h3>
            <div class="abnormal-overview">
              <div class="abnormal-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ reportInterpretation.abnormal_indicators.length }}</span>
                  <span class="stat-label">个异常指标</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ criticalIndicatorsCount }}</span>
                  <span class="stat-label">个需立即关注</span>
                </div>
              </div>
              <div class="abnormal-list">
                <div 
                  v-for="(indicator, index) in reportInterpretation.abnormal_indicators.slice(0, 5)" 
                  :key="index" 
                  class="abnormal-item"
                  :class="{ 'critical': indicator.is_critical }"
                >
                  <span class="indicator-name">{{ indicator.name }}</span>
                  <div class="indicator-values">
                    <span class="current-value">{{ indicator.value }}{{ indicator.unit }}</span>
                    <span class="reference-range">(参考值: {{ indicator.reference_range }})</span>
                  </div>
                </div>
                <div v-if="reportInterpretation.abnormal_indicators.length > 5" class="more-indicators">
                  <span>还有 {{ reportInterpretation.abnormal_indicators.length - 5 }} 个异常指标...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 主要发现 -->
          <div class="section-card">
            <h3>主要发现</h3>
            <div class="findings-list">
              <div 
                v-for="(finding, index) in reportInterpretation.key_findings" 
                :key="index" 
                class="finding-item"
              >
                <div class="finding-icon">{{ finding.icon || '🔍' }}</div>
                <div class="finding-content">
                  <h4>{{ finding.title }}</h4>
                  <p>{{ finding.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细解读内容 -->
        <div v-if="activeTab === 'detailed'" class="tab-content">
          <!-- 系统分类解读 -->
          <div class="section-card">
            <h3>系统分类解读</h3>
            <div class="system-categories">
              <div 
                v-for="(system, index) in reportInterpretation.system_categories" 
                :key="index" 
                class="system-category"
                :class="{ 'has-abnormal': system.has_abnormal }"
              >
                <div class="category-header" @click="toggleSystemDetails(index)">
                  <div class="category-title">
                    <span class="category-icon">{{ system.icon }}</span>
                    <h4>{{ system.name }}</h4>
                    <span v-if="system.has_abnormal" class="abnormal-badge">异常</span>
                  </div>
                  <span class="toggle-icon">{{ system.expanded ? '▼' : '▶' }}</span>
                </div>
                <div v-if="system.expanded" class="category-content">
                  <div class="category-interpretation">
                    {{ system.interpretation }}
                  </div>
                  <div v-if="system.indicators && system.indicators.length > 0" class="system-indicators">
                    <div 
                      v-for="(indicator, idx) in system.indicators" 
                      :key="idx" 
                      class="system-indicator-item"
                      :class="{ 'abnormal': indicator.is_abnormal }"
                    >
                      <div class="indicator-info">
                        <span class="indicator-name">{{ indicator.name }}</span>
                        <span v-if="indicator.is_abnormal" class="abnormal-badge small">异常</span>
                      </div>
                      <div class="indicator-values">
                        <span class="current-value">{{ indicator.value }}{{ indicator.unit }}</span>
                        <span class="reference-range">{{ indicator.reference_range }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 指标详细解读 -->
          <div class="section-card">
            <h3>指标详细解读</h3>
            <div class="detailed-indicators">
              <div class="search-filter">
                <input
                  type="text"
                  v-model="indicatorSearchKeyword"
                  placeholder="搜索指标名称"
                  class="search-input"
                  @input="debouncedIndicatorSearch"
                />
                <select v-model="indicatorFilterType" class="filter-select">
                  <option value="all">全部指标</option>
                  <option value="normal">正常指标</option>
                  <option value="abnormal">异常指标</option>
                </select>
              </div>
              <div class="indicators-list">
                <div v-if="filteredIndicators.length === 0" class="empty-state">
                  <p>未找到匹配的指标</p>
                </div>
                <div 
                  v-for="(indicator, index) in filteredIndicators" 
                  :key="index" 
                  class="detailed-indicator-item"
                  :class="{ 'abnormal': indicator.is_abnormal }"
                >
                  <div class="indicator-header">
                    <h4>{{ indicator.name }}</h4>
                    <span v-if="indicator.is_abnormal" class="abnormal-badge">异常</span>
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
                      <span class="detail-label">解读:</span>
                      <span class="detail-value">{{ indicator.interpretation }}</span>
                    </div>
                    <div v-if="indicator.suggestion" class="detail-row">
                      <span class="detail-label">建议:</span>
                      <span class="detail-value suggestion">{{ indicator.suggestion }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 健康建议内容 -->
        <div v-if="activeTab === 'suggestions'" class="tab-content">
          <!-- 饮食建议 -->
          <div class="section-card">
            <h3>饮食建议</h3>
            <div class="diet-suggestions">
              <div v-if="reportInterpretation.diet_suggestions && reportInterpretation.diet_suggestions.length > 0" class="suggestions-list">
                <div 
                  v-for="(suggestion, index) in reportInterpretation.diet_suggestions" 
                  :key="index" 
                  class="suggestion-item"
                >
                  <div class="suggestion-icon">🍎</div>
                  <div class="suggestion-content">
                    <h4>{{ suggestion.title }}</h4>
                    <p>{{ suggestion.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="no-suggestions">
                <p>暂无饮食建议</p>
              </div>
            </div>
          </div>

          <!-- 运动建议 -->
          <div class="section-card">
            <h3>运动建议</h3>
            <div class="exercise-suggestions">
              <div v-if="reportInterpretation.exercise_suggestions && reportInterpretation.exercise_suggestions.length > 0" class="suggestions-list">
                <div 
                  v-for="(suggestion, index) in reportInterpretation.exercise_suggestions" 
                  :key="index" 
                  class="suggestion-item"
                >
                  <div class="suggestion-icon">🏃</div>
                  <div class="suggestion-content">
                    <h4>{{ suggestion.title }}</h4>
                    <p>{{ suggestion.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="no-suggestions">
                <p>暂无运动建议</p>
              </div>
            </div>
          </div>

          <!-- 生活方式建议 -->
          <div class="section-card">
            <h3>生活方式建议</h3>
            <div class="lifestyle-suggestions">
              <div v-if="reportInterpretation.lifestyle_suggestions && reportInterpretation.lifestyle_suggestions.length > 0" class="suggestions-list">
                <div 
                  v-for="(suggestion, index) in reportInterpretation.lifestyle_suggestions" 
                  :key="index" 
                  class="suggestion-item"
                >
                  <div class="suggestion-icon">💤</div>
                  <div class="suggestion-content">
                    <h4>{{ suggestion.title }}</h4>
                    <p>{{ suggestion.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="no-suggestions">
                <p>暂无生活方式建议</p>
              </div>
            </div>
          </div>

          <!-- 随访建议 -->
          <div class="section-card">
            <h3>随访建议</h3>
            <div class="follow-up-suggestions">
              <div class="follow-up-info">
                <div class="info-item">
                  <span class="info-label">下次体检时间:</span>
                  <span class="info-value">{{ reportInterpretation.next_exam_suggestion || '未提供' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">重点关注指标:</span>
                  <span class="info-value">
                    <span v-for="(indicator, index) in reportInterpretation.follow_up_indicators" :key="index" class="indicator-tag">
                      {{ indicator }}
                    </span>
                  </span>
                </div>
              </div>
              <div class="follow-up-content">
                <p>{{ reportInterpretation.follow_up_suggestion || '暂无随访建议' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 趋势分析内容 -->
        <div v-if="activeTab === 'trends'" class="tab-content">
          <!-- 健康趋势图 -->
          <div class="section-card">
            <h3>健康趋势</h3>
            <div class="chart-container">
              <canvas ref="healthTrendChart"></canvas>
            </div>
          </div>

          <!-- 关键指标趋势 -->
          <div class="section-card">
            <h3>关键指标趋势</h3>
            <div class="key-trends">
              <div class="trend-selector">
                <select v-model="selectedTrendIndicator" class="trend-select">
                  <option v-for="indicator in trendIndicators" :key="indicator.id" :value="indicator.id">
                    {{ indicator.name }}
                  </option>
                </select>
              </div>
              <div class="indicator-trend-chart">
                <canvas ref="indicatorTrendChart"></canvas>
              </div>
              <div class="trend-interpretation">
                <h4>趋势解读</h4>
                <p>{{ getSelectedTrendInterpretation() }}</p>
              </div>
            </div>
          </div>

          <!-- 风险评估 -->
          <div class="section-card">
            <h3>健康风险评估</h3>
            <div class="risk-assessment">
              <div class="risk-overview">
                <div class="risk-score">
                  <h4>风险评分</h4>
                  <div class="score-display">
                    <span class="score-number">{{ reportInterpretation.risk_score }}</span>
                    <span class="score-label">{{ getRiskLevelLabel(reportInterpretation.risk_score) }}</span>
                  </div>
                </div>
                <div class="risk-summary">
                  <h4>风险概述</h4>
                  <p>{{ reportInterpretation.risk_summary }}</p>
                </div>
              </div>
              <div v-if="reportInterpretation.risk_factors && reportInterpretation.risk_factors.length > 0" class="risk-factors">
                <h4>主要风险因素</h4>
                <div class="factors-list">
                  <div 
                    v-for="(factor, index) in reportInterpretation.risk_factors" 
                    :key="index" 
                    class="factor-item"
                    :class="{ 'high-risk': factor.level === 'high' }"
                  >
                    <div class="factor-name">
                      <span class="factor-level">{{ getRiskLevelText(factor.level) }}</span>
                      {{ factor.name }}
                    </div>
                    <div class="factor-description">{{ factor.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI助手解读 -->
        <div class="section-card ai-assistant-section">
          <h3>AI助手解读</h3>
          <div class="ai-assistant-content">
            <div class="ai-chat-container">
              <div class="chat-messages">
                <div class="chat-message bot-message">
                  <div class="message-avatar">🤖</div>
                  <div class="message-content">
                    <p>您好！我是您的AI健康助手。我已经分析了您的体检报告，请问您对报告有什么疑问吗？我可以为您提供更详细的解读。</p>
                  </div>
                </div>
                <div v-for="(message, index) in aiMessages" :key="index" :class="['chat-message', message.type]">
                  <div class="message-avatar">{{ message.type === 'user' ? '👤' : '🤖' }}</div>
                  <div class="message-content">
                    <p>{{ message.content }}</p>
                  </div>
                </div>
              </div>
              <div class="chat-input-area">
                <input
                  type="text"
                  v-model="aiInputMessage"
                  placeholder="输入您的问题..."
                  class="ai-input"
                  @keypress.enter="sendAiMessage"
                />
                <button class="send-btn" @click="sendAiMessage">发送</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存成功弹窗 -->
    <div v-if="showSaveSuccessModal" class="modal-overlay" @click="closeSaveSuccessModal">
      <div class="modal-content small" @click.stop>
        <div class="modal-body">
          <div class="success-icon">✅</div>
          <h3>保存成功</h3>
          <p>报告解读已成功保存到您的健康档案</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn primary" @click="closeSaveSuccessModal">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { router } from '../router'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'

// 注册Chart.js组件
Chart.register(...registerables)

// 状态管理
const isLoading = ref(true)
const error = ref('')
const reportInterpretation = ref(null)
const activeTab = ref('overview')
const indicatorSearchKeyword = ref('')
const indicatorFilterType = ref('all')
const selectedTrendIndicator = ref(null)
const trendIndicators = ref([])
const aiMessages = ref([])
const aiInputMessage = ref('')
const showSaveSuccessModal = ref(false)

// 图表引用
const healthTrendChart = ref(null)
const indicatorTrendChart = ref(null)
let healthChartInstance = null
let indicatorChartInstance = null

// 获取报告解读
const fetchReportInterpretation = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const reportId = localStorage.getItem('currentReportId') || '1'
    
    const response = await axios.get(`/report/${reportId}/interpretation`)
    
    if (response.status === 'success' && response.data) {
      reportInterpretation.value = response.data
      
      // 初始化系统分类展开状态
      if (reportInterpretation.value.system_categories) {
        reportInterpretation.value.system_categories.forEach(category => {
          category.expanded = category.has_abnormal
        })
      }
      
      // 初始化趋势指标
      if (reportInterpretation.value.trend_indicators) {
        trendIndicators.value = reportInterpretation.value.trend_indicators
        if (trendIndicators.value.length > 0) {
          selectedTrendIndicator.value = trendIndicators.value[0].id
        }
      }
      
      // 生成图表
      await nextTick()
      generateHealthTrendChart()
      generateIndicatorTrendChart()
    } else {
      error.value = '获取报告解读失败'
    }
  } catch (err) {
    console.error('获取报告解读错误:', err)
    error.value = '网络错误，请检查您的网络连接'
  } finally {
    isLoading.value = false
  }
}

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab
  
  // 延迟生成图表，确保DOM已更新
  if (tab === 'trends') {
    setTimeout(() => {
      generateHealthTrendChart()
      generateIndicatorTrendChart()
    }, 100)
  }
}

// 切换系统详情展开/收起
const toggleSystemDetails = (index) => {
  if (reportInterpretation.value && reportInterpretation.value.system_categories) {
    reportInterpretation.value.system_categories[index].expanded = 
      !reportInterpretation.value.system_categories[index].expanded
  }
}

// 过滤指标
const filteredIndicators = computed(() => {
  if (!reportInterpretation.value?.detailed_indicators) return []
  
  let filtered = [...reportInterpretation.value.detailed_indicators]
  
  // 搜索过滤
  if (indicatorSearchKeyword.value.trim()) {
    const keyword = indicatorSearchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(indicator => 
      indicator.name.toLowerCase().includes(keyword)
    )
  }
  
  // 类型过滤
  if (indicatorFilterType.value !== 'all') {
    filtered = filtered.filter(indicator => 
      (indicatorFilterType.value === 'abnormal' && indicator.is_abnormal) ||
      (indicatorFilterType.value === 'normal' && !indicator.is_abnormal)
    )
  }
  
  return filtered
})

// 防抖指标搜索
const debouncedIndicatorSearch = () => {
  clearTimeout(window.indicatorSearchTimeout)
  window.indicatorSearchTimeout = setTimeout(() => {
    // 搜索逻辑已在computed中处理
  }, 300)
}

// 计算需立即关注的异常指标数量
const criticalIndicatorsCount = computed(() => {
  if (!reportInterpretation.value?.abnormal_indicators) return 0
  return reportInterpretation.value.abnormal_indicators.filter(indicator => indicator.is_critical).length
})

// 发送AI消息
const sendAiMessage = async () => {
  if (!aiInputMessage.value.trim()) return
  
  // 添加用户消息
  aiMessages.value.push({
    type: 'user',
    content: aiInputMessage.value.trim()
  })
  
  const userMessage = aiInputMessage.value.trim()
  aiInputMessage.value = ''
  
  try {
    const reportId = localStorage.getItem('currentReportId') || '1'
    
    const response = await axios.post(`/ai/report-interpretation`, {
      report_id: reportId,
      question: userMessage
    })
    
    if (response.status === 'success' && response.data?.answer) {
      // 添加AI回复
      aiMessages.value.push({
        type: 'bot',
        content: response.data.answer
      })
      
      // 滚动到底部
      setTimeout(() => {
        const chatContainer = document.querySelector('.chat-messages')
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight
        }
      }, 100)
    }
  } catch (err) {
    console.error('发送AI消息错误:', err)
    aiMessages.value.push({
      type: 'bot',
      content: '抱歉，我暂时无法回答您的问题，请稍后再试。'
    })
  }
}

// 保存到健康档案
const saveToHealthRecord = async () => {
  try {
    const reportId = localStorage.getItem('currentReportId') || '1'
    const userId = localStorage.getItem('userId')
    
    if (!userId) {
      alert('请先登录')
      router.push('/login')
      return
    }
    
    const response = await axios.post(`/report/${reportId}/save-to-record`, {
      user_id: userId
    })
    
    if (response.status === 'success') {
      showSaveSuccessModal.value = true
    } else {
      alert('保存失败，请重试')
    }
  } catch (err) {
    console.error('保存到健康档案错误:', err)
    alert('网络错误，请检查您的网络连接')
  }
}

// 关闭保存成功弹窗
const closeSaveSuccessModal = () => {
  showSaveSuccessModal.value = false
}

// 打印解读
const printInterpretation = () => {
  window.print()
}

// 返回
const goBack = () => {
  router.back()
}

// 生成健康趋势图
const generateHealthTrendChart = async () => {
  if (!healthTrendChart.value || !reportInterpretation.value?.trend_data) return
  
  // 销毁已存在的图表
  if (healthChartInstance) {
    healthChartInstance.destroy()
  }
  
  // 准备图表数据
  const trendData = reportInterpretation.value.trend_data
  const labels = trendData.map(item => formatShortDate(item.date))
  const healthScores = trendData.map(item => item.health_score)
  const abnormalCounts = trendData.map(item => item.abnormal_count)
  
  // 创建图表
  healthChartInstance = new Chart(healthTrendChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '健康评分',
          data: healthScores,
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

// 生成指标趋势图
const generateIndicatorTrendChart = async () => {
  if (!indicatorTrendChart.value || !selectedTrendIndicator.value) return
  
  // 销毁已存在的图表
  if (indicatorChartInstance) {
    indicatorChartInstance.destroy()
  }
  
  // 查找选中指标的趋势数据
  const indicator = trendIndicators.value.find(ind => ind.id === selectedTrendIndicator.value)
  if (!indicator || !indicator.trend_data) return
  
  const trendData = indicator.trend_data
  const labels = trendData.map(item => formatShortDate(item.date))
  const values = trendData.map(item => item.value)
  
  // 创建图表
  indicatorChartInstance = new Chart(indicatorTrendChart.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: indicator.name,
          data: values,
          borderColor: '#52c41a',
          backgroundColor: 'rgba(82, 196, 26, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return `${indicator.name}: ${context.parsed.y}${indicator.unit}`
            }
          }
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
          title: {
            display: true,
            text: `${indicator.name} (${indicator.unit})`
          },
          suggestedMin: Math.min(...values) * 0.9 || 0,
          suggestedMax: Math.max(...values) * 1.1 || 100
        }
      }
    }
  })
}

// 获取选中指标的趋势解读
const getSelectedTrendInterpretation = () => {
  const indicator = trendIndicators.value.find(ind => ind.id === selectedTrendIndicator.value)
  return indicator?.trend_interpretation || '暂无趋势解读'
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

// 获取健康评分标签
const getHealthScoreLabel = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '一般'
  if (score >= 60) return '需关注'
  return '需改善'
}

// 获取健康评分说明
const getScoreMeaning = (score) => {
  if (score >= 90) {
    return '您的身体状况非常好，各项指标都在正常范围内，请继续保持健康的生活方式。'
  } else if (score >= 80) {
    return '您的身体状况良好，只有少数指标略偏离正常范围，建议定期复查并保持健康习惯。'
  } else if (score >= 70) {
    return '您的身体状况一般，部分指标需要关注，建议调整饮食和生活方式，定期复查。'
  } else if (score >= 60) {
    return '您的身体状况需要关注，多个指标异常，建议咨询医生并制定改善计划。'
  } else {
    return '您的身体状况需要改善，多个重要指标异常，建议立即就医并全面调整生活方式。'
  }
}

// 获取风险等级标签
const getRiskLevelLabel = (riskScore) => {
  if (riskScore >= 80) return '高风险'
  if (riskScore >= 50) return '中风险'
  return '低风险'
}

// 获取风险等级文本
const getRiskLevelText = (level) => {
  const levels = {
    'high': '高风险',
    'medium': '中风险',
    'low': '低风险'
  }
  return levels[level] || level
}

// 监听选中指标变化，重新生成图表
watch(selectedTrendIndicator, () => {
  generateIndicatorTrendChart()
})

// 组件挂载时获取报告解读
onMounted(() => {
  fetchReportInterpretation()
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (healthChartInstance) {
    healthChartInstance.destroy()
  }
  if (indicatorChartInstance) {
    indicatorChartInstance.destroy()
  }
  clearTimeout(window.indicatorSearchTimeout)
})
</script>

<style scoped>
/* 报告解读页面样式 */
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

.report-interpretation {
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

/* 解读容器 */
.interpretation-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  color: var(--text-color);
  font-size: 28px;
}

.report-info-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
}

.report-title {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.report-date {
  color: var(--text-secondary);
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.action-btn:hover {
  background-color: var(--border-color);
}

.action-btn.primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.primary:hover {
  background-color: var(--primary-dark);
}

/* 解读标签页 */
.interpretation-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background-color: var(--card-background);
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  flex-wrap: wrap;
}

.tab-btn {
  flex: 1;
  min-width: 120px;
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

/* 标签内容 */
.tab-content {
  margin-bottom: 30px;
}

/* 健康评分卡片 */
.health-score-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  gap: 32px;
  align-items: center;
  flex-wrap: wrap;
}

.score-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.score-icon {
  font-size: 48px;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e6f7ff;
  border-radius: 50%;
}

.score-info h3 {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: normal;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.score-number {
  font-size: 36px;
  font-weight: bold;
  color: var(--primary-color);
}

.score-label {
  font-size: 18px;
  color: var(--text-color);
  font-weight: 500;
}

.score-right {
  flex: 1;
  min-width: 300px;
}

.score-right h4 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 16px;
}

.score-right p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 区块卡片 */
.section-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.section-card h3 {
  margin: 0 0 20px;
  color: var(--text-color);
  font-size: 20px;
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

/* 总体评估 */
.assessment-content p {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 异常指标概览 */
.abnormal-overview {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.abnormal-stats {
  flex: 1;
  min-width: 200px;
  background-color: var(--background-color);
  padding: 20px;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: var(--error-color);
  margin-bottom: 4px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.abnormal-list {
  flex: 2;
  min-width: 300px;
}

.abnormal-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff1f0;
  border: 1px solid var(--error-color);
  border-radius: 4px;
  margin-bottom: 8px;
}

.abnormal-item.critical {
  background-color: #ffccc7;
  border-color: #cf1322;
}

.indicator-name {
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
}

.indicator-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.current-value {
  color: var(--error-color);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
}

.reference-range {
  color: var(--text-secondary);
  font-size: 12px;
}

.more-indicators {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  padding: 12px;
  background-color: var(--background-color);
  border-radius: 4px;
}

/* 主要发现 */
.findings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.finding-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: var(--background-color);
  border-radius: 6px;
}

.finding-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e6f7ff;
  border-radius: 50%;
  flex-shrink: 0;
}

.finding-content {
  flex: 1;
}

.finding-content h4 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 16px;
}

.finding-content p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 系统分类解读 */
.system-categories {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.system-category {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.system-category.has-abnormal {
  border-color: var(--error-color);
  border-left: 4px solid var(--error-color);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: var(--background-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-header:hover {
  background-color: #e6f7ff;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  font-size: 20px;
}

.category-title h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
}

.abnormal-badge {
  padding: 4px 8px;
  background-color: var(--error-color);
  color: white;
  font-size: 12px;
  border-radius: 3px;
  font-weight: 500;
}

.abnormal-badge.small {
  padding: 2px 4px;
  font-size: 10px;
}

.toggle-icon {
  color: var(--text-secondary);
  font-size: 12px;
  transition: transform 0.3s ease;
}

.category-content {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.category-interpretation {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.system-indicators {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.system-indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.system-indicator-item.abnormal {
  border-color: var(--error-color);
  background-color: #fff1f0;
}

.indicator-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 指标详细解读 */
.search-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
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

.detailed-indicators {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.indicators-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detailed-indicator-item {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.detailed-indicator-item.abnormal {
  border-color: var(--error-color);
  border-left: 4px solid var(--error-color);
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: var(--background-color);
}

.indicator-header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
}

.indicator-details {
  padding: 16px;
}

.detail-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 14px;
  min-width: 80px;
}

.detail-value {
  color: var(--text-color);
  font-size: 14px;
  flex: 1;
  line-height: 1.6;
}

.detail-value.suggestion {
  color: var(--primary-color);
}

/* 建议列表 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: var(--background-color);
  border-radius: 6px;
}

.suggestion-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f6ffed;
  border-radius: 50%;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-content h4 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 16px;
}

.suggestion-content p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.no-suggestions {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 随访建议 */
.follow-up-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 16px;
}

.follow-up-info .info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.follow-up-info .info-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.follow-up-info .info-value {
  color: var(--text-color);
  font-size: 14px;
}

.indicator-tag {
  display: inline-block;
  padding: 4px 8px;
  background-color: #e6f7ff;
  color: var(--primary-color);
  font-size: 12px;
  border-radius: 3px;
  margin-right: 8px;
  margin-bottom: 8px;
}

.follow-up-content p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 300px;
}

/* 关键指标趋势 */
.trend-selector {
  margin-bottom: 20px;
}

.trend-select {
  width: 100%;
  max-width: 300px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  background-color: white;
}

.trend-select:focus {
  border-color: var(--primary-color);
}

.indicator-trend-chart {
  width: 100%;
  height: 250px;
  margin-bottom: 20px;
}

.trend-interpretation h4 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 16px;
}

.trend-interpretation p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 风险评估 */
.risk-overview {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.risk-score {
  flex: 1;
  min-width: 200px;
  background-color: var(--background-color);
  padding: 20px;
  border-radius: 6px;
}

.risk-score h4 {
  margin: 0 0 12px;
  color: var(--text-color);
  font-size: 16px;
}

.risk-summary {
  flex: 2;
  min-width: 300px;
}

.risk-summary h4 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 16px;
}

.risk-summary p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.risk-factors h4 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
}

.factors-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.factor-item {
  padding: 16px;
  background-color: #fff7e6;
  border: 1px solid var(--warning-color);
  border-radius: 6px;
}

.factor-item.high-risk {
  background-color: #fff1f0;
  border-color: var(--error-color);
}

.factor-name {
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.factor-level {
  display: inline-block;
  padding: 2px 6px;
  background-color: var(--warning-color);
  color: white;
  font-size: 10px;
  border-radius: 3px;
  margin-right: 8px;
}

.factor-item.high-risk .factor-level {
  background-color: var(--error-color);
}

.factor-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

/* AI助手解读 */
.ai-assistant-section {
  margin-bottom: 0;
}

.ai-chat-container {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.chat-messages {
  height: 300px;
  overflow-y: auto;
  padding: 16px;
  background-color: var(--background-color);
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in-out;
}

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

.chat-message:last-child {
  margin-bottom: 0;
}

.message-avatar {
  font-size: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border-radius: 50%;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-content p {
  margin: 0;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  max-width: 80%;
}

.bot-message .message-content p {
  background-color: #e6f7ff;
  color: var(--text-color);
}

.user-message .message-content p {
  background-color: var(--primary-color);
  color: white;
  margin-left: auto;
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  background-color: white;
  border-top: 1px solid var(--border-color);
}

.ai-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  outline: none;
}

.ai-input:focus {
  border-color: var(--primary-color);
}

.send-btn {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.send-btn:hover {
  background-color: var(--primary-dark);
}

/* 保存成功弹窗 */
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
  animation: modalFadeIn 0.3s ease-in-out;
}

.modal-content.small {
  max-width: 400px;
  text-align: center;
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

.modal-body {
  margin-bottom: 24px;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-body h3 {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 20px;
}

.modal-body p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

/* 打印样式 */
@media print {
  .top-nav,
  .header-right,
  .interpretation-tabs,
  .ai-assistant-section {
    display: none !important