<template>
  <div class="recommendation-result">
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
        <p>正在生成您的个性化体检方案...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchRecommendationResult">重新加载</button>
      </div>

      <!-- 推荐结果内容 -->
      <div v-else-if="recommendationResult" class="result-container">
        <!-- 结果头部 -->
        <div class="result-header">
          <div class="header-left">
            <h1>个性化体检方案</h1>
            <p class="generated-date">生成日期: {{ formatDate(recommendationResult.generated_at) }}</p>
          </div>
          <div class="header-right">
            <button class="regenerate-btn" @click="regenerateRecommendation">
              <span class="refresh-icon">🔄</span>
              <span>重新生成</span>
            </button>
          </div>
        </div>

        <!-- 推荐概览卡片 -->
        <div class="overview-card">
          <h2 class="card-title">方案概览</h2>
          <div class="overview-grid">
            <div class="overview-item">
              <span class="overview-label">推荐方案等级</span>
              <span class="overview-value" :class="getLevelClass(recommendationResult.recommendation_level)">
                {{ getLevelText(recommendationResult.recommendation_level) }}
              </span>
            </div>
            <div class="overview-item">
              <span class="overview-label">总项目数</span>
              <span class="overview-value">{{ recommendationResult.total_items }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">预计总价</span>
              <span class="overview-value price">¥{{ recommendationResult.estimated_price }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">预计耗时</span>
              <span class="overview-value">{{ recommendationResult.estimated_time }} 小时</span>
            </div>
          </div>
          <div class="health-score-container">
            <div class="score-label">健康风险评估</div>
            <div class="score-display">
              <div class="score-value" :class="getRiskClass(recommendationResult.health_risk_score)">
                {{ recommendationResult.health_risk_score }}
              </div>
              <div class="score-desc">
                {{ getRiskDescription(recommendationResult.health_risk_score) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 推荐理由 -->
        <div class="reasons-section">
          <h2 class="section-title">推荐理由</h2>
          <div class="reasons-content">
            <p class="reason-text">{{ recommendationResult.recommendation_reason }}</p>
          </div>
        </div>

        <!-- 推荐项目详情 -->
        <div class="items-section">
          <div class="section-header">
            <h2 class="section-title">推荐体检项目</h2>
            <div class="section-filters">
              <select v-model="currentCategory" @change="filterItems">
                <option value="all">全部类别</option>
                <option v-for="category in availableCategories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
          </div>

          <div class="items-grid">
            <div 
              v-for="item in filteredItems" 
              :key="item.id" 
              class="item-card"
            >
              <div class="item-header">
                <h3 class="item-name">{{ item.name }}</h3>
                <span class="item-category">{{ item.category }}</span>
              </div>
              <div class="item-body">
                <div class="item-desc">{{ item.description }}</div>
                <div class="item-price">¥{{ item.price }}</div>
                <div class="item-reason">
                  <span class="reason-label">推荐理由:</span>
                  <span class="reason-text">{{ item.recommendation_reason }}</span>
                </div>
              </div>
              <div class="item-footer">
                <div class="item-importance" :class="getImportanceClass(item.importance)">
                  {{ getImportanceText(item.importance) }}
                </div>
                <div class="item-action">
                  <input 
                    type="checkbox" 
                    :id="`item-${item.id}`" 
                    v-model="selectedItems" 
                    :value="item.id"
                    :checked="item.selected"
                  />
                  <label :for="`item-${item.id}`">选择</label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 专家解读 -->
        <div class="expert-interpretation-section">
          <h2 class="section-title">专家解读</h2>
          <div class="interpretation-content">
            <div class="expert-info">
              <div class="expert-avatar">👨‍⚕️</div>
              <div class="expert-details">
                <div class="expert-name">{{ recommendationResult.expert_name }}</div>
                <div class="expert-title">{{ recommendationResult.expert_title }}</div>
              </div>
            </div>
            <div class="interpretation-text">
              {{ recommendationResult.expert_interpretation }}
            </div>
          </div>
        </div>

        <!-- 备选方案比较 -->
        <div class="comparison-section" v-if="alternativePlans && alternativePlans.length > 0">
          <h2 class="section-title">备选方案比较</h2>
          <div class="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>方案名称</th>
                  <th>项目数量</th>
                  <th>价格</th>
                  <th>耗时</th>
                  <th>覆盖风险</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="plan in alternativePlans" 
                  :key="plan.id" 
                  class="plan-row"
                  :class="{ selected: plan.id === recommendationResult.id }"
                >
                  <td>{{ plan.name }}</td>
                  <td>{{ plan.total_items }}</td>
                  <td class="price-cell">¥{{ plan.estimated_price }}</td>
                  <td>{{ plan.estimated_time }} 小时</td>
                  <td>{{ plan.risk_coverage }}%</td>
                  <td>
                    <button 
                      class="select-plan-btn"
                      :disabled="plan.id === recommendationResult.id"
                      @click="selectAlternativePlan(plan.id)"
                    >
                      {{ plan.id === recommendationResult.id ? '当前方案' : '选择' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="bottom-actions">
          <div class="selected-info">
            <span>已选择 {{ selectedItems.length }} 项，总价: ¥{{ calculateTotalPrice() }}</span>
          </div>
          <div class="action-buttons">
            <button class="action-btn print-btn" @click="printRecommendation">
              <span class="print-icon">🖨️</span>
              <span>打印方案</span>
            </button>
            <button class="action-btn share-btn" @click="shareRecommendation">
              <span class="share-icon">📤</span>
              <span>分享方案</span>
            </button>
            <button class="action-btn primary appointment-btn" @click="goToAppointment">
              <span>立即预约</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 重新生成弹窗 -->
    <div v-if="showRegenerateModal" class="modal-overlay" @click="closeRegenerateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>重新生成体检方案</h3>
        </div>
        <div class="modal-body">
          <p>重新生成方案将根据您的最新健康信息重新计算推荐结果，是否继续？</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="closeRegenerateModal">取消</button>
          <button class="modal-btn confirm" @click="confirmRegenerate">确认重新生成</button>
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
const recommendationResult = ref(null)
const alternativePlans = ref([])
const selectedItems = ref([])
const currentCategory = ref('all')
const availableCategories = ref([])
const showRegenerateModal = ref(false)

// 获取推荐结果
const fetchRecommendationResult = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    const response = await axios.get(`/recommendation/${userId}/result`)
    
    if (response.status === 'success' && response.data) {
      recommendationResult.value = response.data
      
      // 提取已选择的项目
      if (response.data.items) {
        selectedItems.value = response.data.items
          .filter(item => item.selected)
          .map(item => item.id)
      }
      
      // 提取可用的类别
      if (response.data.items) {
        const categories = [...new Set(response.data.items.map(item => item.category))]
        availableCategories.value = categories
      }
      
      // 获取备选方案
      await fetchAlternativePlans(userId)
    } else {
      error.value = '获取推荐结果失败'
    }
  } catch (err) {
    console.error('获取推荐结果错误:', err)
    error.value = '网络错误，请检查您的网络连接'
  } finally {
    isLoading.value = false
  }
}

// 获取备选方案
const fetchAlternativePlans = async (userId) => {
  try {
    const response = await axios.get(`/recommendation/${userId}/alternative-plans`)
    
    if (response.status === 'success' && response.data) {
      alternativePlans.value = response.data
    }
  } catch (err) {
    console.error('获取备选方案错误:', err)
    // 不阻止页面加载
  }
}

// 过滤项目
const filteredItems = computed(() => {
  if (!recommendationResult.value || !recommendationResult.value.items) {
    return []
  }
  
  if (currentCategory.value === 'all') {
    return recommendationResult.value.items
  }
  
  return recommendationResult.value.items.filter(item => 
    item.category === currentCategory.value
  )
})

// 计算总价
const calculateTotalPrice = () => {
  if (!recommendationResult.value || !recommendationResult.value.items) {
    return 0
  }
  
  return recommendationResult.value.items
    .filter(item => selectedItems.value.includes(item.id))
    .reduce((total, item) => total + item.price, 0)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 获取等级文本
const getLevelText = (level) => {
  const levels = {
    'basic': '基础版',
    'standard': '标准版',
    'advanced': '高级版',
    'comprehensive': '全面版',
    'customized': '定制版'
  }
  return levels[level] || level
}

// 获取等级样式类
const getLevelClass = (level) => {
  const classes = {
    'basic': 'level-basic',
    'standard': 'level-standard',
    'advanced': 'level-advanced',
    'comprehensive': 'level-comprehensive',
    'customized': 'level-customized'
  }
  return classes[level] || ''
}

// 获取风险等级文本
const getRiskDescription = (score) => {
  if (score < 30) return '低风险'
  if (score < 60) return '中等风险'
  if (score < 80) return '高风险'
  return '极高风险'
}

// 获取风险等级样式类
const getRiskClass = (score) => {
  if (score < 30) return 'risk-low'
  if (score < 60) return 'risk-medium'
  if (score < 80) return 'risk-high'
  return 'risk-very-high'
}

// 获取重要性文本
const getImportanceText = (importance) => {
  const importanceMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'very_high': '极高'
  }
  return importanceMap[importance] || importance
}

// 获取重要性样式类
const getImportanceClass = (importance) => {
  const classes = {
    'low': 'importance-low',
    'medium': 'importance-medium',
    'high': 'importance-high',
    'very_high': 'importance-very-high'
  }
  return classes[importance] || ''
}

// 返回
const goBack = () => {
  router.back()
}

// 前往预约
const goToAppointment = () => {
  if (selectedItems.value.length === 0) {
    alert('请至少选择一个体检项目')
    return
  }
  
  // 保存选择的项目到localStorage
  localStorage.setItem('selectedItems', JSON.stringify(selectedItems.value))
  router.push('/appointment-management')
}

// 打印方案
const printRecommendation = () => {
  window.print()
}

// 分享方案
const shareRecommendation = () => {
  alert('分享功能即将上线，敬请期待！')
}

// 重新生成推荐
const regenerateRecommendation = () => {
  showRegenerateModal.value = true
}

// 确认重新生成
const confirmRegenerate = async () => {
  showRegenerateModal.value = false
  
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    // 显示加载状态
    isLoading.value = true
    
    const response = await axios.post(`/recommendation/${userId}/regenerate`)
    
    if (response.status === 'success') {
      // 重新获取推荐结果
      await fetchRecommendationResult()
    } else {
      alert(response.message || '重新生成失败，请重试')
      isLoading.value = false
    }
  } catch (err) {
    console.error('重新生成推荐错误:', err)
    alert('网络错误，请检查您的网络连接')
    isLoading.value = false
  }
}

// 关闭重新生成弹窗
const closeRegenerateModal = () => {
  showRegenerateModal.value = false
}

// 选择备选方案
const selectAlternativePlan = async (planId) => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      error.value = '请先登录'
      router.push('/login')
      return
    }
    
    // 显示加载状态
    isLoading.value = true
    
    const response = await axios.post(`/recommendation/${userId}/select-plan`, {
      plan_id: planId
    })
    
    if (response.status === 'success') {
      // 重新获取推荐结果
      await fetchRecommendationResult()
    } else {
      alert(response.message || '选择方案失败，请重试')
      isLoading.value = false
    }
  } catch (err) {
    console.error('选择备选方案错误:', err)
    alert('网络错误，请检查您的网络连接')
    isLoading.value = false
  }
}

// 组件挂载时获取推荐结果
onMounted(() => {
  fetchRecommendationResult()
})
</script>

<style scoped>
/* 推荐结果页面样式 */
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
  --low-risk-color: #52c41a;
  --medium-risk-color: #faad14;
  --high-risk-color: #fa8c16;
  --very-high-risk-color: #f5222d;
}

.recommendation-result {
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

/* 结果容器 */
.result-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* 结果头部 */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.result-header h1 {
  margin: 0;
  color: var(--text-color);
  font-size: 28px;
}

.generated-date {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.regenerate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--border-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.regenerate-btn:hover {
  background-color: #bfbfbf;
}

.refresh-icon {
  font-size: 16px;
}

/* 概览卡片 */
.overview-card {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.card-title {
  margin: 0 0 20px;
  color: var(--text-color);
  font-size: 20px;
  font-weight: 500;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.overview-item {
  text-align: center;
  padding: 16px;
  background-color: var(--background-color);
  border-radius: 6px;
}

.overview-label {
  display: block;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.overview-value {
  display: block;
  color: var(--text-color);
  font-size: 24px;
  font-weight: bold;
}

.overview-value.price {
  color: var(--primary-color);
}

.level-basic {
  color: #1890ff;
}

.level-standard {
  color: #52c41a;
}

.level-advanced {
  color: #faad14;
}

.level-comprehensive {
  color: #fa8c16;
}

.level-customized {
  color: #f5222d;
}

.health-score-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 20px;
  background-color: #e6f7ff;
  border-radius: 6px;
}

.score-label {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.risk-low {
  color: var(--low-risk-color);
}

.risk-medium {
  color: var(--medium-risk-color);
}

.risk-high {
  color: var(--high-risk-color);
}

.risk-very-high {
  color: var(--very-high-risk-color);
}

.score-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 推荐理由 */
.reasons-section {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.section-title {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 20px;
  font-weight: 500;
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 8px;
}

.reasons-content {
  padding: 16px 0;
}

.reason-text {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* 推荐项目 */
.items-section {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-filters select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-color);
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.item-card {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 20px;
  transition: all 0.3s ease;
}

.item-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.item-name {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
  flex: 1;
}

.item-category {
  padding: 4px 8px;
  background-color: #e6f7ff;
  color: var(--primary-color);
  font-size: 12px;
  border-radius: 3px;
  margin-left: 12px;
}

.item-body {
  margin-bottom: 16px;
}

.item-desc {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.item-price {
  color: var(--primary-color);
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
}

.item-reason {
  background-color: #f6ffed;
  padding: 12px;
  border-radius: 4px;
}

.reason-label {
  color: var(--success-color);
  font-weight: 500;
  font-size: 14px;
  margin-right: 8px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-importance {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.importance-low {
  background-color: #e6f7ff;
  color: var(--primary-color);
}

.importance-medium {
  background-color: #fffbe6;
  color: var(--warning-color);
}

.importance-high {
  background-color: #fff1f0;
  color: var(--high-risk-color);
}

.importance-very-high {
  background-color: #fff1f0;
  color: var(--very-high-risk-color);
}

.item-action {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-action input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.item-action label {
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
}

/* 专家解读 */
.expert-interpretation-section {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.interpretation-content {
  padding: 16px 0;
}

.expert-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.expert-avatar {
  font-size: 48px;
}

.expert-details {
  display: flex;
  flex-direction: column;
}

.expert-name {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.expert-title {
  color: var(--text-secondary);
  font-size: 14px;
}

.interpretation-text {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
}

/* 备选方案比较 */
.comparison-section {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.comparison-table {
  overflow-x: auto;
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
}

.comparison-table th,
.comparison-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.comparison-table th {
  background-color: var(--background-color);
  color: var(--text-color);
  font-weight: 500;
  font-size: 14px;
}

.comparison-table td {
  color: var(--text-color);
  font-size: 14px;
}

.price-cell {
  color: var(--primary-color);
  font-weight: 500;
}

.plan-row:hover {
  background-color: #f0f9ff;
}

.plan-row.selected {
  background-color: #e6f7ff;
  border-left: 4px solid var(--primary-color);
}

.select-plan-btn {
  padding: 6px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.select-plan-btn:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.select-plan-btn:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
}

/* 底部操作栏 */
.bottom-actions {
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-info {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.print-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.print-btn:hover {
  background-color: #bfbfbf;
}

.share-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.share-btn:hover {
  background-color: #bfbfbf;
}

.appointment-btn {
  background-color: var(--primary-color);
  color: white;
}

.appointment-btn:hover {
  background-color: var(--primary-dark);
}

.print-icon,
.share-icon {
  font-size: 16px;
}

/* 重新生成弹窗 */
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
  max-width: 400px;
  width: 90%;
  animation: modalFadeIn 0.3s ease-in-out;
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

.modal-header h3 {
  margin: 0 0 20px;
  color: var(--text-color);
  font-size: 20px;
}

.modal-body p {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
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

.cancel {
  background-color: var(--border-color);
  color: var(--text-color);
}

.cancel:hover {
  background-color: #bfbfbf;
}

.confirm {
  background-color: var(--primary-color);
  color: white;
}

.confirm:hover {
  background-color: var(--primary-dark);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .health-score-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .items-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .bottom-actions {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    justify-content: center;
  }
  
  .comparison-table {
    margin-left: -24px;
    margin-right: -24px;
    width: calc(100% + 48px);
  }
}
</style>