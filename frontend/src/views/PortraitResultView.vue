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
                <h4>{{ symptom.name || symptom.symptom }}</h4>
                <div class="symptom-details">
                  <p v-if="symptom.frequency"><strong>频率：</strong>{{ symptom.frequency }}</p>
                  <p v-if="symptom.details"><strong>详情：</strong>{{ symptom.details }}</p>
                  <p v-if="symptom.severity"><strong>严重程度：</strong>{{ symptom.severity }}</p>
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
                <p>{{ recommendation.description || recommendation }}</p>
              </div>
            </div>
          </div>

          <!-- 推荐检查项目 -->
          <div class="section">
            <h3><i class="el-icon-document"></i> 推荐检查项目</h3>
            <div class="recommended-exams">
              <div v-for="(exam, index) in recommendedExams" :key="index" class="exam-tag">
                {{ exam.name || exam }}
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
        
        // 计算总体健康评分
        const totalRisk = riskIndicators.value.reduce((sum, item) => sum + item.value, 0) / riskIndicators.value.length
        portraitData.value.healthScore = Math.round(100 - totalRisk)
        
        // 根据风险指标生成健康建议
        generateHealthRecommendations(data)
        
        // 根据风险指标生成推荐体检项目
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
      
      // 基于风险指标生成建议
      riskIndicators.value.forEach(indicator => {
        if (indicator.value >= 70) {
          if (indicator.name === 'BMI指数') {
            recommendations.push({
              title: '体重管理',
              description: '您的BMI指数偏高，建议咨询营养师制定合理的饮食计划，并增加有氧运动。',
              priority: 'high'
            })
          } else if (indicator.name === '生活习惯') {
            recommendations.push({
              title: '改善生活习惯',
              description: '您的生活习惯可能对健康造成负面影响，建议戒烟限酒，增加运动，改善睡眠质量。',
              priority: 'high'
            })
          } else if (indicator.name === '健康历史') {
            recommendations.push({
              title: '定期复查',
              description: '基于您的健康历史，建议定期进行相关检查，并遵医嘱进行治疗。',
              priority: 'high'
            })
          } else if (indicator.name === '当前症状') {
            recommendations.push({
              title: '症状管理',
              description: '您的当前症状需要及时关注，建议尽快就医进行详细检查。',
              priority: 'high'
            })
          }
        } else if (indicator.value >= 40) {
          if (indicator.name === 'BMI指数') {
            recommendations.push({
              title: '体重监测',
              description: '您的BMI指数接近正常范围上限，建议注意饮食平衡，保持适量运动。',
              priority: 'medium'
            })
          } else if (indicator.name === '生活习惯') {
            recommendations.push({
              title: '健康生活方式',
              description: '建议保持健康的生活方式，适量运动，保证充足睡眠。',
              priority: 'medium'
            })
          }
        }
      })
      
      // 基于具体数据生成建议
      if (data && data.lifestyle) {
        if (data.lifestyle.smoking_status === '吸烟') {
          recommendations.push({
            title: '戒烟建议',
            description: '吸烟是多种疾病的风险因素，建议您制定戒烟计划，可寻求专业医疗帮助。',
            priority: 'high'
          })
        }
        if (data.lifestyle.drinking_status === '饮酒') {
          recommendations.push({
            title: '限酒建议',
            description: '过量饮酒会对肝脏等器官造成损害，建议控制饮酒量或戒酒。',
            priority: 'medium'
          })
        }
      }
      
      // 更新健康建议
      healthRecommendations.value = recommendations
    }
    
    const generateRecommendedExams = (data) => {
      const exams = []
      
      // 基于年龄推荐基础体检项目
      if (data && data.basic_info && data.basic_info.age) {
        const age = data.basic_info.age
        if (age >= 30) {
          exams.push({
            name: '血常规',
            reason: '基础健康指标检查',
            category: '基础检查'
          })
          exams.push({
            name: '肝功能',
            reason: '肝脏健康指标检查',
            category: '基础检查'
          })
          exams.push({
            name: '肾功能',
            reason: '肾脏健康指标检查',
            category: '基础检查'
          })
        }
        if (age >= 40) {
          exams.push({
            name: '血脂四项',
            reason: '心血管疾病风险评估',
            category: '心血管检查'
          })
          exams.push({
            name: '血糖',
            reason: '糖尿病筛查',
            category: '代谢检查'
          })
        }
        if (age >= 50) {
          exams.push({
            name: '肿瘤标志物',
            reason: '肿瘤早期筛查',
            category: '肿瘤筛查'
          })
        }
      }
      
      // 基于性别推荐特定检查
      if (data && data.basic_info && data.basic_info.gender) {
        if (data.basic_info.gender === '男' && data.basic_info.age >= 40) {
          exams.push({
            name: '前列腺特异抗原(PSA)',
            reason: '前列腺健康检查',
            category: '专科检查'
          })
        } else if (data.basic_info.gender === '女' && data.basic_info.age >= 30) {
          exams.push({
            name: '宫颈涂片',
            reason: '宫颈癌筛查',
            category: '专科检查'
          })
          if (data.basic_info.age >= 40) {
            exams.push({
              name: '乳腺钼靶',
              reason: '乳腺癌筛查',
              category: '专科检查'
            })
          }
        }
      }
      
      // 基于健康历史推荐特定检查
      if (data && data.health_history) {
        if (data.health_history.family_medical_history && 
            data.health_history.family_medical_history.includes('心血管疾病')) {
          exams.push({
            name: '心电图',
            reason: '心血管疾病风险评估',
            category: '心血管检查'
          })
          exams.push({
            name: '心脏超声',
            reason: '心脏结构和功能检查',
            category: '心血管检查'
          })
        }
      }
      
      // 基于生活习惯推荐特定检查
      if (data && data.lifestyle) {
        if (data.lifestyle.smoking_status === '吸烟') {
          exams.push({
            name: '胸部X光/CT',
            reason: '肺部健康检查',
            category: '呼吸系统检查'
          })
        }
        if (data.lifestyle.drinking_status === '饮酒') {
          exams.push({
            name: '腹部超声',
            reason: '肝脏健康检查',
            category: '消化系统检查'
          })
        }
      }
      
      // 基于症状推荐特定检查
      if (data && data.symptoms && data.symptoms.length > 0) {
        data.symptoms.forEach(symptom => {
          if (symptom.symptom.includes('胸') || symptom.symptom.includes('心')) {
            exams.push({
              name: '心电图',
              reason: '心脏相关症状检查',
              category: '心血管检查'
            })
          }
          if (symptom.symptom.includes('腹') || symptom.symptom.includes('胃')) {
            exams.push({
              name: '腹部超声',
              reason: '腹部症状检查',
              category: '消化系统检查'
            })
          }
        })
      }
      
      // 去重并限制数量
      const uniqueExams = []
      const examNames = new Set()
      
      for (const exam of exams) {
        if (!examNames.has(exam.name)) {
          examNames.add(exam.name)
          uniqueExams.push(exam)
        }
      }
      
      // 更新推荐体检项目
      recommendedExams.value = uniqueExams.slice(0, 8)
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