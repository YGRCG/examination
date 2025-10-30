<template>
  <div class="portrait-result-view">
    <div class="container">
      <h1>用户画像分析结果</h1>
      
      <div v-if="loading" class="loading-container">
        <el-loading v-loading="loading" text="正在加载您的画像数据..." />
      </div>
      
      <div v-else-if="portraitData" class="result-container">
        <div class="result-header">
          <div class="user-info">
            <h2>{{ portraitData.name || '用户' }}</h2>
            <p>{{ portraitData.age }}岁 | {{ portraitData.gender === 'male' ? '男' : '女' }}</p>
          </div>
          <div class="health-rating">
            <div class="rating-badge" :class="getRatingClass(portraitData.health_risk)">
              {{ getRatingText(portraitData.health_risk) }}
            </div>
            <p>建议检查频率：{{ portraitData.recommended_frequency }}</p>
          </div>
        </div>

        <div class="result-content">
          <!-- 健康风险评估 -->
          <div class="section">
            <h3><i class="el-icon-warning"></i> 健康风险评估</h3>
            <div class="risk-indicators">
              <div v-for="(risk, index) in riskIndicators" :key="index" class="risk-item">
                <div class="risk-label">{{ risk.label }}</div>
                <el-progress 
                  :percentage="risk.value" 
                  :color="getProgressColor(risk.value)"
                  :stroke-width="10"
                />
              </div>
            </div>
          </div>

          <!-- 主要症状分析 -->
          <div v-if="portraitData.symptoms && portraitData.symptoms.length > 0" class="section">
            <h3><i class="el-icon-notebook-2"></i> 主要症状分析</h3>
            <div class="symptoms-list">
              <div v-for="(symptom, index) in portraitData.symptoms" :key="index" class="symptom-card">
                <h4>{{ symptom.name }}</h4>
                <div class="symptom-details">
                  <p><strong>频率：</strong>{{ symptom.frequency }}</p>
                  <p v-if="symptom.details"><strong>详情：</strong>{{ symptom.details }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 生活习惯分析 -->
          <div v-if="portraitData.lifestyle" class="section">
            <h3><i class="el-icon-s-home"></i> 生活习惯分析</h3>
            <div class="lifestyle-grid">
              <div class="habit-item">
                <span class="habit-label">饮食习惯：</span>
                <span class="habit-value">{{ portraitData.lifestyle.diet || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">运动情况：</span>
                <span class="habit-value">{{ portraitData.lifestyle.exercise || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">睡眠情况：</span>
                <span class="habit-value">{{ portraitData.lifestyle.sleep || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">吸烟饮酒：</span>
                <span class="habit-value">{{ portraitData.lifestyle.smoking_drinking || '未提供' }}</span>
              </div>
            </div>
          </div>

          <!-- 健康建议 -->
          <div class="section">
            <h3><i class="el-icon-medal"></i> 健康建议</h3>
            <div class="recommendations">
              <div v-for="(recommendation, index) in healthRecommendations" :key="index" class="recommendation-item">
                <i class="el-icon-check"></i>
                <p>{{ recommendation }}</p>
              </div>
            </div>
          </div>

          <!-- 推荐检查项目 -->
          <div class="section">
            <h3><i class="el-icon-document"></i> 推荐检查项目</h3>
            <div class="recommended-exams">
              <div v-for="(exam, index) in recommendedExams" :key="index" class="exam-tag">
                {{ exam }}
              </div>
            </div>
          </div>
        </div>

        <div class="result-actions">
          <el-button type="primary" size="large" @click="goToAppointment">
            <i class="el-icon-calendar"></i> 预约体检
          </el-button>
          <el-button size="large" @click="viewRecommendations">
            <i class="el-icon-s-grid"></i> 查看套餐推荐
          </el-button>
          <el-button size="large" @click="retryQuestionnaire">
            <i class="el-icon-refresh"></i> 重新填写问卷
          </el-button>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-empty description="未找到画像数据，请先完成问卷" />
        <el-button type="primary" @click="goToQuestionnaire">开始问卷</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserPortrait } from '@/api/user-portrait'

export default {
  name: 'PortraitResultView',
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const portraitData = ref(null)

    // 模拟风险指标数据
    const riskIndicators = ref([
      { label: '心血管风险', value: 35 },
      { label: '代谢性疾病风险', value: 45 },
      { label: '肿瘤风险', value: 20 },
      { label: '呼吸系统风险', value: 30 }
    ])

    // 模拟健康建议
    const healthRecommendations = ref([
      '保持规律的作息时间，建议每晚睡眠7-8小时',
      '增加有氧运动，每周至少进行150分钟中等强度运动',
      '注意饮食均衡，减少高脂、高糖食物摄入',
      '定期监测血压和血糖变化',
      '保持良好心态，避免长期精神压力'
    ])

    // 模拟推荐检查项目
    const recommendedExams = ref([
      '血常规', '生化全套', '心电图', '胸部CT',
      '腹部B超', '肿瘤标志物筛查', '骨密度检查'
    ])

    const getRatingClass = (riskLevel) => {
      switch (riskLevel) {
        case 'low':
          return 'rating-low'
        case 'medium':
          return 'rating-medium'
        case 'high':
          return 'rating-high'
        default:
          return 'rating-low'
      }
    }

    const getRatingText = (riskLevel) => {
      switch (riskLevel) {
        case 'low':
          return '低风险'
        case 'medium':
          return '中风险'
        case 'high':
          return '高风险'
        default:
          return '低风险'
      }
    }

    const getProgressColor = (value) => {
      if (value < 30) return '#67C23A'
      if (value < 70) return '#E6A23C'
      return '#F56C6C'
    }

    const fetchPortraitData = async () => {
      try {
        const data = await getUserPortrait()
        portraitData.value = data
        // 这里可以根据实际返回的数据更新风险指标等信息
      } catch (error) {
        console.error('获取画像数据失败:', error)
        ElMessage.error('获取画像数据失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }

    const goToAppointment = () => {
      router.push('/appointments')
    }

    const viewRecommendations = () => {
      router.push('/recommendations')
    }

    const retryQuestionnaire = () => {
      router.push('/questionnaire')
    }

    const goToQuestionnaire = () => {
      router.push('/questionnaire')
    }

    onMounted(() => {
      fetchPortraitData()
    })

    return {
      loading,
      portraitData,
      riskIndicators,
      healthRecommendations,
      recommendedExams,
      getRatingClass,
      getRatingText,
      getProgressColor,
      goToAppointment,
      viewRecommendations,
      retryQuestionnaire,
      goToQuestionnaire
    }
  }
}
</script>

<style scoped>
.portrait-result-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 2rem 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 2.2rem;
  font-weight: 600;
}

.loading-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.result-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 500;
}

.user-info p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.health-rating {
  text-align: right;
}

.rating-badge {
  display: inline-block;
  padding: 0.5rem 1.2rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.rating-low {
  background-color: #67c23a;
}

.rating-medium {
  background-color: #e6a23c;
}

.rating-high {
  background-color: #f56c6c;
}

.health-rating p {
  margin: 0;
  opacity: 0.9;
}

.result-content {
  padding: 2rem;
}

.section {
  margin-bottom: 2rem;
}

.section h3 {
  display: flex;
  align-items: center;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
  font-weight: 500;
}

.section h3 i {
  margin-right: 0.5rem;
  color: #667eea;
}

.risk-indicators {
  display: grid;
  gap: 1rem;
}

.risk-item {
  margin-bottom: 1rem;
}

.risk-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
  font-weight: 500;
  color: #606266;
}

.symptoms-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.symptom-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #667eea;
}

.symptom-card h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.symptom-details p {
  margin: 0.3rem 0;
  color: #606266;
  font-size: 0.9rem;
}

.lifestyle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.habit-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}

.habit-label {
  font-weight: 500;
  color: #606266;
}

.habit-value {
  color: #2c3e50;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  padding: 0.8rem;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.recommendation-item i {
  color: #409eff;
  margin-right: 0.8rem;
  margin-top: 0.2rem;
}

.recommendation-item p {
  margin: 0;
  color: #303133;
}

.recommended-exams {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.exam-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 0.9rem;
  border: 1px solid #d9ecff;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
}

.empty-state .el-button {
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .health-rating {
    text-align: center;
  }
  
  .symptoms-list,
  .lifestyle-grid {
    grid-template-columns: 1fr;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>