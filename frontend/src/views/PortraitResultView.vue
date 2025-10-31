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
            <h2>{{ portraitData.basic_info?.name || '用户' }}</h2>
            <p>{{ portraitData.basic_info?.age || '未知' }}岁 | {{ portraitData.basic_info?.gender || '未知' }}</p>
          </div>
          <div class="health-rating">
            <div class="rating-badge" :class="getRatingClass(portraitData.healthScore)">
              {{ getRatingText(portraitData.healthScore) }}
            </div>
            <p>健康评分：{{ portraitData.healthScore || '未知' }}/100</p>
          </div>
        </div>

        <div class="result-content">
          <!-- 健康风险评估 -->
          <div class="section">
            <h3><i class="el-icon-warning"></i> 健康风险评估</h3>
            <div class="risk-indicators">
              <div v-for="(risk, index) in riskIndicators" :key="index" class="risk-item">
                <div class="risk-label">{{ risk.name }}</div>
                <el-progress 
                  :percentage="risk.value" 
                  :color="getProgressColor(risk.value)"
                  :stroke-width="10"
                />
              </div>
            </div>
            <div v-if="portraitData.health_risk" class="overall-risk">
              <p><strong>总体风险等级：</strong>{{ portraitData.health_risk }}</p>
              <p v-if="portraitData.recommended_frequency"><strong>建议体检频率：</strong>{{ portraitData.recommended_frequency }}</p>
            </div>
          </div>

          <!-- 重点关注领域 -->
          <div v-if="portraitData.focus_areas && portraitData.focus_areas.length > 0" class="section">
            <h3><i class="el-icon-star"></i> 重点关注领域</h3>
            <div class="focus-areas">
              <div v-for="(area, index) in portraitData.focus_areas" :key="index" class="focus-card" :class="area.priority">
                <h4>{{ area.name }}</h4>
                <p class="reason">{{ area.reason }}</p>
                <span class="priority-badge" :class="area.priority">{{ area.priority }}优先级</span>
              </div>
            </div>
          </div>

          <!-- 主要症状分析 -->
          <div v-if="portraitData.symptoms && portraitData.symptoms.length > 0" class="section">
            <h3><i class="el-icon-notebook-2"></i> 主要症状分析</h3>
            <div class="symptoms-list">
              <div v-for="(symptom, index) in portraitData.symptoms" :key="index" class="symptom-card">
                <h4>{{ symptom.name || symptom.symptom }}</h4>
                <div class="symptom-details">
                  <p v-if="symptom.frequency"><strong>频率：</strong>{{ symptom.frequency }}</p>
                  <p v-if="symptom.details"><strong>详情：</strong>{{ symptom.details }}</p>
                  <p v-if="symptom.severity"><strong>严重程度：</strong>{{ symptom.severity }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 体检报告记录 -->
          <div v-if="portraitData.medical_reports && portraitData.medical_reports.length > 0" class="section">
            <h3><i class="el-icon-document"></i> 体检报告记录</h3>
            <div class="medical-reports">
              <div v-for="(report, index) in portraitData.medical_reports" :key="index" class="report-card">
                <h4>{{ report.title || '体检报告' }}</h4>
                <div class="report-details">
                  <p v-if="report.date"><strong>检查日期：</strong>{{ report.date }}</p>
                  <p v-if="report.hospital"><strong>检查机构：</strong>{{ report.hospital }}</p>
                  <p v-if="report.summary"><strong>主要发现：</strong>{{ report.summary }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 生活习惯分析 -->
          <div v-if="portraitData.lifestyle" class="section">
            <h3><i class="el-icon-s-home"></i> 生活习惯分析</h3>
            <div class="lifestyle-grid">
              <div class="habit-item">
                <span class="habit-label">吸烟状态：</span>
                <span class="habit-value">{{ portraitData.lifestyle.smoking_status || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">饮酒状态：</span>
                <span class="habit-value">{{ portraitData.lifestyle.drinking_status || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">运动习惯：</span>
                <span class="habit-value">{{ portraitData.lifestyle.exercise_habits || '未提供' }}</span>
              </div>
              <div class="habit-item">
                <span class="habit-label">睡眠质量：</span>
                <span class="habit-value">{{ portraitData.lifestyle.sleep_quality || '未提供' }}</span>
              </div>
            </div>
          </div>

          <!-- 健康建议 -->
          <div class="section">
            <h3><i class="el-icon-medal"></i> 健康建议</h3>
            <div class="recommendations">
              <div v-for="(recommendation, index) in healthRecommendations" :key="index" class="recommendation-item" :class="recommendation.priority">
                <i class="el-icon-check"></i>
                <div class="recommendation-content">
                  <p class="recommendation-text">{{ recommendation.content || recommendation.description || recommendation }}</p>
                  <span class="priority-tag" :class="recommendation.priority">{{ recommendation.priority }}优先级</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 推荐检查项目 -->
          <div class="section">
            <h3><i class="el-icon-document"></i> 推荐检查项目</h3>
            <div class="recommended-exams">
              <div v-for="(exam, index) in recommendedExams" :key="index" class="exam-card">
                <h4>{{ exam.name }}</h4>
                <p class="exam-description">{{ exam.description }}</p>
                <span class="exam-frequency">{{ exam.frequency }}</span>
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
        
        // 初始化风险指标，确保与数据库结构一致
        riskIndicators.value = [
          { name: 'BMI指数', value: 0 },
          { name: '年龄因素', value: 0 },
          { name: '健康历史', value: 0 },
          { name: '生活习惯', value: 0 },
          { name: '当前症状', value: 0 }
        ]
        
        // 根据实际返回的数据更新风险指标等信息
        if (data && data.basic_info) {
          // 根据基本信息计算BMI和健康风险
          if (data.basic_info.height && data.basic_info.weight) {
            const bmi = data.basic_info.weight / Math.pow(data.basic_info.height / 100, 2)
            let bmiRisk = 0
            if (bmi < 18.5) bmiRisk = 30
            else if (bmi < 24) bmiRisk = 10
            else if (bmi < 28) bmiRisk = 50
            else bmiRisk = 80
            
            // 更新BMI风险指标
            const bmiIndex = riskIndicators.value.findIndex(item => item.name === 'BMI指数')
            if (bmiIndex !== -1) {
              riskIndicators.value[bmiIndex].value = bmiRisk
            }
          }
          
          // 根据年龄计算健康风险
          if (data.basic_info.age) {
            let ageRisk = 0
            if (data.basic_info.age < 30) ageRisk = 10
            else if (data.basic_info.age < 45) ageRisk = 20
            else if (data.basic_info.age < 60) ageRisk = 40
            else ageRisk = 60
            
            // 更新年龄风险指标
            const ageIndex = riskIndicators.value.findIndex(item => item.name === '年龄因素')
            if (ageIndex !== -1) {
              riskIndicators.value[ageIndex].value = ageRisk
            }
          }
        }
        
        // 处理健康历史数据
        if (data && data.health_history) {
          let healthRisk = 0
          if (data.health_history.chronic_diseases) {
            healthRisk += 30
          }
          if (data.health_history.allergies) {
            healthRisk += 10
          }
          
          // 更新健康历史风险指标
          const healthIndex = riskIndicators.value.findIndex(item => item.name === '健康历史')
          if (healthIndex !== -1) {
            riskIndicators.value[healthIndex].value = Math.min(healthRisk, 100)
          }
        }
        
        // 处理生活习惯数据
        if (data && data.lifestyle) {
          let lifestyleRisk = 0
          if (data.lifestyle.smoking_status === '吸烟') {
            lifestyleRisk += 40
          }
          if (data.lifestyle.drinking_status === '饮酒') {
            lifestyleRisk += 20
          }
          if (data.lifestyle.exercise_habits === '很少运动') {
            lifestyleRisk += 30
          }
          if (data.lifestyle.sleep_quality === '差') {
            lifestyleRisk += 20
          }
          
          // 更新生活习惯风险指标
          const lifestyleIndex = riskIndicators.value.findIndex(item => item.name === '生活习惯')
          if (lifestyleIndex !== -1) {
            riskIndicators.value[lifestyleIndex].value = Math.min(lifestyleRisk, 100)
          }
        }
        
        // 处理症状数据
        if (data && data.symptoms && data.symptoms.length > 0) {
          // 根据症状数量和严重程度计算风险
          let symptomRisk = Math.min(data.symptoms.length * 15, 70)
          
          // 更新症状风险指标
          const symptomIndex = riskIndicators.value.findIndex(item => item.name === '当前症状')
          if (symptomIndex !== -1) {
            riskIndicators.value[symptomIndex].value = symptomRisk
          }
        }
        
        // 处理体检报告数据
        if (data && data.medical_reports && data.medical_reports.length > 0) {
          // 如果有体检报告，增加额外风险因素
          riskIndicators.value.forEach(indicator => {
            if (indicator.value > 0) {
              indicator.value = Math.min(indicator.value + 5, 100)
            }
          })
        }
        
        // 计算总体健康评分
        const totalRisk = riskIndicators.value.reduce((sum, item) => sum + item.value, 0) / riskIndicators.value.length
        portraitData.value.healthScore = Math.round(100 - totalRisk)
        
        // 根据数据库结构生成健康建议
        generateHealthRecommendations(data)
        
        // 根据数据库结构生成推荐体检项目
        generateRecommendedExams(data)
        
      } catch (error) {
        console.error('获取画像数据失败:', error)
        ElMessage.error('获取画像数据失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
    
    const generateHealthRecommendations = (data) => {
      const recommendations = []
      
      // 如果后端已经生成了健康建议，直接使用
      if (data && data.health_recommendations && data.health_recommendations.length > 0) {
        healthRecommendations.value = data.health_recommendations
        return
      }
      
      // 基于风险指标生成建议
      riskIndicators.value.forEach(indicator => {
        if (indicator.value > 60) {
          recommendations.push({
            priority: '高',
            content: `${indicator.name}风险较高，建议重点关注`
          })
        } else if (indicator.value > 30) {
          recommendations.push({
            priority: '中',
            content: `${indicator.name}存在一定风险，建议适当关注`
          })
        }
      })
      
      // 基于生活习惯生成建议
      if (data && data.lifestyle) {
        if (data.lifestyle.smoking_status === '吸烟') {
          recommendations.push({
            priority: '高',
            content: '吸烟对健康危害较大，建议戒烟'
          })
        }
        
        if (data.lifestyle.drinking_status === '饮酒') {
          recommendations.push({
            priority: '中',
            content: '饮酒需适量，建议控制饮酒量'
          })
        }
        
        if (data.lifestyle.exercise_habits === '很少运动') {
          recommendations.push({
            priority: '中',
            content: '缺乏运动，建议每周至少进行150分钟中等强度运动'
          })
        }
        
        if (data.lifestyle.sleep_quality === '差') {
          recommendations.push({
            priority: '中',
            content: '睡眠质量差，建议改善睡眠环境和习惯'
          })
        }
      }
      
      // 基于健康历史生成建议
      if (data && data.health_history) {
        if (data.health_history.chronic_diseases) {
          recommendations.push({
            priority: '高',
            content: '有慢性疾病史，建议定期复查和规范治疗'
          })
        }
        
        if (data.health_history.allergies) {
          recommendations.push({
            priority: '中',
            content: '有过敏史，建议避免接触过敏原'
          })
        }
      }
      
      // 基于症状生成建议
      if (data && data.symptoms && data.symptoms.length > 0) {
        recommendations.push({
          priority: '高',
          content: `有${data.symptoms.length}个症状表现，建议及时就医检查`
        })
      }
      
      // 基于体检报告生成建议
      if (data && data.medical_reports && data.medical_reports.length > 0) {
        recommendations.push({
          priority: '高',
          content: '有体检报告记录，建议根据报告结果进行针对性健康管理'
        })
      }
      
      // 基于重点关注领域生成建议
      if (data && data.focus_areas && data.focus_areas.length > 0) {
        data.focus_areas.forEach(area => {
          recommendations.push({
            priority: area.priority === '高' ? '高' : '中',
            content: `${area.name}：${area.reason}`
          })
        })
      }
      
      // 如果没有高优先级建议，添加基础健康建议
      if (recommendations.filter(r => r.priority === '高').length === 0) {
        recommendations.push({
          priority: '中',
          content: '健康状况良好，建议保持健康生活方式和定期体检'
        })
      }
      
      healthRecommendations.value = recommendations
    }
    
    const generateRecommendedExams = (data) => {
      const exams = []
      
      // 如果后端已经生成了推荐检查项目，直接使用
      if (data && data.recommended_exams && data.recommended_exams.length > 0) {
        recommendedExams.value = data.recommended_exams
        return
      }
      
      // 基础体检项目
      exams.push({
        name: '血常规',
        description: '检查血液成分，评估基本健康状况',
        frequency: '每年一次'
      })
      
      exams.push({
        name: '尿常规',
        description: '检查尿液成分，评估肾脏功能',
        frequency: '每年一次'
      })
      
      exams.push({
        name: '肝功能',
        description: '检查肝脏功能指标',
        frequency: '每年一次'
      })
      
      exams.push({
        name: '肾功能',
        description: '检查肾脏功能指标',
        frequency: '每年一次'
      })
      
      exams.push({
        name: '血脂四项',
        description: '检查血脂水平，评估心血管风险',
        frequency: '每年一次'
      })
      
      exams.push({
        name: '血糖',
        description: '检查血糖水平，评估糖尿病风险',
        frequency: '每年一次'
      })
      
      // 基于年龄的额外检查
      if (data && data.basic_info && data.basic_info.age >= 40) {
        exams.push({
          name: '心电图',
          description: '检查心脏电活动，评估心脏健康',
          frequency: '每年一次'
        })
        
        exams.push({
          name: '腹部B超',
          description: '检查腹部器官形态',
          frequency: '每年一次'
        })
      }
      
      if (data && data.basic_info && data.basic_info.age >= 50) {
        exams.push({
          name: '胸部X光',
          description: '检查肺部健康状况',
          frequency: '每年一次'
        })
        
        exams.push({
          name: '骨密度',
          description: '检查骨骼健康状况，评估骨质疏松风险',
          frequency: '每两年一次'
        })
      }
      
      // 基于生活习惯的检查
      if (data && data.lifestyle) {
        if (data.lifestyle.smoking_status === '吸烟') {
          exams.push({
            name: '肺功能检查',
            description: '评估肺部功能状况',
            frequency: '每年一次'
          })
        }
        
        if (data.lifestyle.drinking_status === '饮酒') {
          exams.push({
            name: '肝脏B超',
            description: '检查肝脏形态和结构',
            frequency: '每年一次'
          })
        }
      }
      
      // 基于健康历史的检查
      if (data && data.health_history) {
        if (data.health_history.chronic_diseases) {
          exams.push({
            name: '专科复查',
            description: '根据慢性疾病情况进行专科复查',
            frequency: '每半年一次'
          })
        }
      }
      
      // 基于症状的检查
      if (data && data.symptoms && data.symptoms.length > 0) {
        exams.push({
          name: '针对性检查',
          description: '根据具体症状进行针对性医学检查',
          frequency: '根据医生建议'
        })
      }
      
      // 基于体检报告的检查
      if (data && data.medical_reports && data.medical_reports.length > 0) {
        exams.push({
          name: '复查项目',
          description: '根据既往体检报告结果进行复查',
          frequency: '根据医生建议'
        })
      }
      
      // 基于重点关注领域的检查
      if (data && data.focus_areas && data.focus_areas.length > 0) {
        data.focus_areas.forEach(area => {
          if (area.priority === '高') {
            exams.push({
              name: `${area.name}专项检查`,
              description: `针对${area.name}进行专项医学检查`,
              frequency: '每半年一次'
            })
          }
        })
      }
      
      recommendedExams.value = exams
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