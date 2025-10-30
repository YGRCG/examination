<template>
  <div class="information-collection">
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
      <div class="form-container">
        <div class="form-header">
          <h2>健康信息收集</h2>
          <p class="form-description">
            请填写以下信息，帮助我们为您提供更准确的体检项目推荐和健康建议
          </p>
        </div>

        <!-- 进度指示器 -->
        <div class="progress-indicator">
          <div 
            class="progress-step" 
            :class="{ active: currentStep === 1, completed: currentStep > 1 }"
          >
            <span class="step-number">{{ currentStep > 1 ? '✓' : '1' }}</span>
            <span class="step-text">基本信息</span>
          </div>
          <div class="progress-line" :class="{ completed: currentStep > 1 }"></div>
          <div 
            class="progress-step" 
            :class="{ active: currentStep === 2, completed: currentStep > 2 }"
          >
            <span class="step-number">{{ currentStep > 2 ? '✓' : '2' }}</span>
            <span class="step-text">健康状况</span>
          </div>
          <div class="progress-line" :class="{ completed: currentStep > 2 }"></div>
          <div 
            class="progress-step" 
            :class="{ active: currentStep === 3, completed: currentStep > 3 }"
          >
            <span class="step-number">{{ currentStep > 3 ? '✓' : '3' }}</span>
            <span class="step-text">既往病史</span>
          </div>
          <div class="progress-line" :class="{ completed: currentStep > 3 }"></div>
          <div 
            class="progress-step" 
            :class="{ active: currentStep === 4, completed: currentStep > 4 }"
          >
            <span class="step-number">{{ currentStep > 4 ? '✓' : '4' }}</span>
            <span class="step-text">生活方式</span>
          </div>
          <div class="progress-line" :class="{ completed: currentStep > 4 }"></div>
          <div 
            class="progress-step" 
            :class="{ active: currentStep === 5 }"
          >
            <span class="step-number">5</span>
            <span class="step-text">确认提交</span>
          </div>
        </div>

        <!-- 表单步骤容器 -->
        <div class="form-steps">
          <!-- 第一步：基本信息 -->
          <div v-if="currentStep === 1" class="form-step">
            <h3>个人基本信息</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="gender">性别 <span class="required">*</span></label>
                <select id="gender" v-model="formData.gender" required>
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                  <option value="other">其他</option>
                </select>
              </div>

              <div class="form-group">
                <label for="birthdate">出生日期 <span class="required">*</span></label>
                <input 
                  id="birthdate" 
                  v-model="formData.birthdate" 
                  type="date" 
                  required
                />
              </div>

              <div class="form-group">
                <label for="height">身高 (cm) <span class="required">*</span></label>
                <input 
                  id="height" 
                  v-model.number="formData.height" 
                  type="number" 
                  min="50" 
                  max="220" 
                  required
                />
              </div>

              <div class="form-group">
                <label for="weight">体重 (kg) <span class="required">*</span></label>
                <input 
                  id="weight" 
                  v-model.number="formData.weight" 
                  type="number" 
                  min="10" 
                  max="300" 
                  required
                />
              </div>

              <div class="form-group">
                <label for="blood_type">血型</label>
                <select id="blood_type" v-model="formData.blood_type">
                  <option value="">请选择</option>
                  <option value="A">A型</option>
                  <option value="B">B型</option>
                  <option value="O">O型</option>
                  <option value="AB">AB型</option>
                  <option value="unknown">未知</option>
                </select>
              </div>

              <div class="form-group">
                <label for="marital_status">婚姻状况</label>
                <select id="marital_status" v-model="formData.marital_status">
                  <option value="">请选择</option>
                  <option value="single">未婚</option>
                  <option value="married">已婚</option>
                  <option value="divorced">离婚</option>
                  <option value="widowed">丧偶</option>
                </select>
              </div>

              <div class="form-group">
                <label for="education">最高学历</label>
                <select id="education" v-model="formData.education">
                  <option value="">请选择</option>
                  <option value="primary">小学及以下</option>
                  <option value="secondary">初中</option>
                  <option value="high">高中/中专</option>
                  <option value="college">大专</option>
                  <option value="bachelor">本科</option>
                  <option value="master">硕士及以上</option>
                </select>
              </div>

              <div class="form-group">
                <label for="occupation">职业</label>
                <input 
                  id="occupation" 
                  v-model="formData.occupation" 
                  type="text" 
                  placeholder="请输入您的职业"
                />
              </div>
            </div>
          </div>

          <!-- 第二步：健康状况 -->
          <div v-if="currentStep === 2" class="form-step">
            <h3>健康状况问卷</h3>
            <div class="form-section">
              <h4>常见症状（过去3个月内）</h4>
              <div class="checkbox-group">
                <label class="checkbox-item" v-for="symptom in commonSymptoms" :key="symptom.id">
                  <input 
                    type="checkbox" 
                    :value="symptom.id" 
                    v-model="formData.symptoms"
                  />
                  <span>{{ symptom.name }}</span>
                </label>
              </div>
              <div class="form-group">
                <label for="other_symptoms">其他症状</label>
                <textarea 
                  id="other_symptoms" 
                  v-model="formData.other_symptoms"
                  placeholder="如有其他症状，请在此描述"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="form-section">
              <h4>健康指标</h4>
              <div class="form-grid">
                <div class="form-group">
                  <label for="blood_pressure_systolic">收缩压 (mmHg)</label>
                  <input 
                    id="blood_pressure_systolic" 
                    v-model.number="formData.blood_pressure_systolic" 
                    type="number" 
                    min="80" 
                    max="220"
                  />
                </div>
                <div class="form-group">
                  <label for="blood_pressure_diastolic">舒张压 (mmHg)</label>
                  <input 
                    id="blood_pressure_diastolic" 
                    v-model.number="formData.blood_pressure_diastolic" 
                    type="number" 
                    min="50" 
                    max="120"
                  />
                </div>
                <div class="form-group">
                  <label for="heart_rate">心率 (次/分)</label>
                  <input 
                    id="heart_rate" 
                    v-model.number="formData.heart_rate" 
                    type="number" 
                    min="40" 
                    max="180"
                  />
                </div>
                <div class="form-group">
                  <label for="blood_sugar">空腹血糖 (mmol/L)</label>
                  <input 
                    id="blood_sugar" 
                    v-model.number="formData.blood_sugar" 
                    type="number" 
                    min="2" 
                    max="30" 
                    step="0.1"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 第三步：既往病史 -->
          <div v-if="currentStep === 3" class="form-step">
            <h3>既往病史记录</h3>
            <div class="form-section">
              <h4>慢性疾病史</h4>
              <div class="checkbox-group">
                <label class="checkbox-item" v-for="disease in commonDiseases" :key="disease.id">
                  <input 
                    type="checkbox" 
                    :value="disease.id" 
                    v-model="formData.chronic_diseases"
                  />
                  <span>{{ disease.name }}</span>
                </label>
              </div>
              <div class="form-group">
                <label for="other_diseases">其他慢性疾病</label>
                <textarea 
                  id="other_diseases" 
                  v-model="formData.other_diseases"
                  placeholder="如有其他慢性疾病，请在此描述"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="form-section">
              <h4>手术史</h4>
              <div class="form-group">
                <label for="surgery_history">是否有手术史？</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input 
                      type="radio" 
                      value="yes" 
                      v-model="formData.has_surgery"
                    />
                    <span>是</span>
                  </label>
                  <label class="radio-item">
                    <input 
                      type="radio" 
                      value="no" 
                      v-model="formData.has_surgery"
                    />
                    <span>否</span>
                  </label>
                </div>
              </div>
              <div v-if="formData.has_surgery === 'yes'" class="form-group">
                <label for="surgery_details">手术详情</label>
                <textarea 
                  id="surgery_details" 
                  v-model="formData.surgery_details"
                  placeholder="请描述手术类型、时间和医院"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="form-section">
              <h4>药物过敏史</h4>
              <div class="form-group">
                <label for="allergy_history">是否有药物过敏史？</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input 
                      type="radio" 
                      value="yes" 
                      v-model="formData.has_allergy"
                    />
                    <span>是</span>
                  </label>
                  <label class="radio-item">
                    <input 
                      type="radio" 
                      value="no" 
                      v-model="formData.has_allergy"
                    />
                    <span>否</span>
                  </label>
                </div>
              </div>
              <div v-if="formData.has_allergy === 'yes'" class="form-group">
                <label for="allergy_details">过敏药物详情</label>
                <textarea 
                  id="allergy_details" 
                  v-model="formData.allergy_details"
                  placeholder="请描述过敏药物名称和反应情况"
                  rows="3"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- 第四步：生活方式 -->
          <div v-if="currentStep === 4" class="form-step">
            <h3>生活方式调查</h3>
            <div class="form-section">
              <h4>饮食习惯</h4>
              <div class="form-group">
                <label for="diet_type">饮食类型</label>
                <select id="diet_type" v-model="formData.diet_type">
                  <option value="">请选择</option>
                  <option value="balanced">均衡饮食</option>
                  <option value="vegetarian">素食</option>
                  <option value="meat">偏肉食</option>
                  <option value="high_fat">高脂饮食</option>
                  <option value="high_salt">高盐饮食</option>
                  <option value="high_sugar">高糖饮食</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div class="form-group">
                <label for="water_intake">每日饮水量 (ml)</label>
                <input 
                  id="water_intake" 
                  v-model.number="formData.water_intake" 
                  type="number" 
                  min="0" 
                  max="5000"
                />
              </div>
            </div>

            <div class="form-section">
              <h4>运动习惯</h4>
              <div class="form-group">
                <label for="exercise_frequency">每周运动频率</label>
                <select id="exercise_frequency" v-model="formData.exercise_frequency">
                  <option value="">请选择</option>
                  <option value="never">几乎不运动</option>
                  <option value="1-2">1-2次</option>
                  <option value="3-4">3-4次</option>
                  <option value="5-7">5-7次</option>
                </select>
              </div>
              <div class="form-group">
                <label for="exercise_duration">每次运动时长 (分钟)</label>
                <input 
                  id="exercise_duration" 
                  v-model.number="formData.exercise_duration" 
                  type="number" 
                  min="0" 
                  max="300"
                />
              </div>
            </div>

            <div class="form-section">
              <h4>不良习惯</h4>
              <div class="form-group">
                <label for="smoking">吸烟情况</label>
                <select id="smoking" v-model="formData.smoking">
                  <option value="">请选择</option>
                  <option value="never">从不吸烟</option>
                  <option value="former">曾经吸烟</option>
                  <option value="current_light">现在吸烟（轻度）</option>
                  <option value="current_heavy">现在吸烟（重度）</option>
                </select>
              </div>
              <div class="form-group">
                <label for="alcohol">饮酒情况</label>
                <select id="alcohol" v-model="formData.alcohol">
                  <option value="">请选择</option>
                  <option value="never">从不饮酒</option>
                  <option value="occasional">偶尔饮酒</option>
                  <option value="regular_light">经常饮酒（轻度）</option>
                  <option value="regular_heavy">经常饮酒（重度）</option>
                </select>
              </div>
              <div class="form-group">
                <label for="sleep_duration">每日睡眠时间 (小时)</label>
                <input 
                  id="sleep_duration" 
                  v-model.number="formData.sleep_duration" 
                  type="number" 
                  min="0" 
                  max="24" 
                  step="0.5"
                />
              </div>
            </div>
          </div>

          <!-- 第五步：确认提交 -->
          <div v-if="currentStep === 5" class="form-step">
            <h3>信息确认</h3>
            <div class="confirmation-summary">
              <div class="summary-section">
                <h4>个人基本信息</h4>
                <div class="summary-item">
                  <span class="summary-label">性别:</span>
                  <span class="summary-value">{{ getGenderText() }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">出生日期:</span>
                  <span class="summary-value">{{ formatDate(formData.birthdate) }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">身高/体重:</span>
                  <span class="summary-value">{{ formData.height }}cm / {{ formData.weight }}kg</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">BMI指数:</span>
                  <span class="summary-value">{{ calculateBMI() }}</span>
                </div>
              </div>

              <div class="summary-section">
                <h4>健康状况概览</h4>
                <div class="summary-item" v-if="formData.symptoms.length > 0">
                  <span class="summary-label">近期症状:</span>
                  <span class="summary-value">{{ getSelectedSymptoms() }}</span>
                </div>
                <div class="summary-item" v-if="formData.blood_pressure_systolic && formData.blood_pressure_diastolic">
                  <span class="summary-label">血压:</span>
                  <span class="summary-value">{{ formData.blood_pressure_systolic }}/{{ formData.blood_pressure_diastolic }} mmHg</span>
                </div>
              </div>

              <div class="summary-section">
                <h4>疾病史</h4>
                <div class="summary-item" v-if="formData.chronic_diseases.length > 0">
                  <span class="summary-label">慢性疾病:</span>
                  <span class="summary-value">{{ getSelectedDiseases() }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">手术史:</span>
                  <span class="summary-value">{{ formData.has_surgery === 'yes' ? '有' : '无' }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">药物过敏史:</span>
                  <span class="summary-value">{{ formData.has_allergy === 'yes' ? '有' : '无' }}</span>
                </div>
              </div>

              <div class="summary-section">
                <h4>生活方式</h4>
                <div class="summary-item">
                  <span class="summary-label">饮食类型:</span>
                  <span class="summary-value">{{ getDietTypeText() }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">运动频率:</span>
                  <span class="summary-value">{{ getExerciseFrequencyText() }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">吸烟/饮酒:</span>
                  <span class="summary-value">{{ getSmokingText() }}/{{ getAlcoholText() }}</span>
                </div>
              </div>
            </div>

            <div class="agreement">
              <label>
                <input type="checkbox" v-model="formData.agreeTerms" required />
                <span>
                  我确认以上信息真实准确，并同意系统使用这些信息为我提供个性化的体检推荐和健康建议
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- 表单导航按钮 -->
        <div class="form-navigation">
          <button 
            class="nav-btn back" 
            @click="prevStep" 
            v-if="currentStep > 1"
            :disabled="isSubmitting"
          >
            上一步
          </button>
          <button 
            class="nav-btn next" 
            @click="nextStep" 
            v-if="currentStep < 5"
            :disabled="isSubmitting || !isCurrentStepValid()"
          >
            下一步
          </button>
          <button 
            class="nav-btn submit" 
            @click="submitForm" 
            v-if="currentStep === 5"
            :disabled="isSubmitting || !formData.agreeTerms"
          >
            {{ isSubmitting ? '提交中...' : '提交' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 成功提示弹窗 -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>提交成功</h3>
        </div>
        <div class="modal-body">
          <div class="success-icon">✓</div>
          <p>您的健康信息已成功提交！</p>
          <p>系统将根据您提供的信息为您生成个性化的体检项目推荐。</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn" @click="goToRecommendation">查看推荐结果</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { router } from '../router'
import { healthInfoAPI } from '../api/interpretation'

// 状态管理
const currentStep = ref(1)
const isSubmitting = ref(false)
const showSuccessModal = ref(false)

// 常见症状选项
const commonSymptoms = ref([
  { id: 1, name: '头痛' },
  { id: 2, name: '头晕' },
  { id: 3, name: '胸闷' },
  { id: 4, name: '心悸' },
  { id: 5, name: '呼吸困难' },
  { id: 6, name: '胃痛' },
  { id: 7, name: '恶心/呕吐' },
  { id: 8, name: '腹泻' },
  { id: 9, name: '便秘' },
  { id: 10, name: '关节疼痛' },
  { id: 11, name: '视力模糊' },
  { id: 12, name: '耳鸣' },
  { id: 13, name: '失眠' },
  { id: 14, name: '疲劳乏力' },
  { id: 15, name: '体重骤变' }
])

// 常见慢性疾病选项
const commonDiseases = ref([
  { id: 1, name: '高血压' },
  { id: 2, name: '糖尿病' },
  { id: 3, name: '冠心病' },
  { id: 4, name: '脑卒中' },
  { id: 5, name: '慢性肝炎' },
  { id: 6, name: '慢性肾病' },
  { id: 7, name: '胃炎/胃溃疡' },
  { id: 8, name: '哮喘' },
  { id: 9, name: '类风湿关节炎' },
  { id: 10, name: '甲状腺疾病' },
  { id: 11, name: '肿瘤病史' },
  { id: 12, name: '精神心理疾病' }
])

// 表单数据
const formData = ref({
  // 基本信息
  gender: '',
  birthdate: '',
  height: '',
  weight: '',
  blood_type: '',
  marital_status: '',
  education: '',
  occupation: '',
  
  // 健康状况
  symptoms: [],
  other_symptoms: '',
  blood_pressure_systolic: '',
  blood_pressure_diastolic: '',
  heart_rate: '',
  blood_sugar: '',
  
  // 既往病史
  chronic_diseases: [],
  other_diseases: '',
  has_surgery: '',
  surgery_details: '',
  has_allergy: '',
  allergy_details: '',
  
  // 生活方式
  diet_type: '',
  water_intake: '',
  exercise_frequency: '',
  exercise_duration: '',
  smoking: '',
  alcohol: '',
  sleep_duration: '',
  
  // 确认提交
  agreeTerms: false
})

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    scrollToTop()
  }
}

// 下一步
const nextStep = () => {
  if (currentStep.value < 5 && isCurrentStepValid()) {
    currentStep.value++
    scrollToTop()
  }
}

// 提交表单
const submitForm = async () => {
  if (isSubmitting.value || !formData.value.agreeTerms) return
  
  isSubmitting.value = true
  
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      alert('请先登录')
      router.push('/login')
      return
    }
    
    // 构建提交数据
    // API调用已经在healthInfoAPI.updateUserHealthInfo中处理了user_id的添加
    
    // 调用后端接口保存健康信息
    const response = await healthInfoAPI.updateUserHealthInfo(userId, formData.value)
    
    if (response.status === 'success') {
      // 显示成功弹窗
      showSuccessModal.value = true
    } else {
      alert(response.message || '提交失败，请重试')
    }
  } catch (error) {
    console.error('提交健康信息错误:', error)
    alert('网络错误，请检查您的网络连接')
  } finally {
    isSubmitting.value = false
  }
}

// 检查当前步骤是否有效
const isCurrentStepValid = () => {
  switch (currentStep.value) {
    case 1:
      return formData.value.gender && 
             formData.value.birthdate && 
             formData.value.height && 
             formData.value.weight
    case 2:
      // 健康状况步骤没有必填项，但如果填了血压，需要两个值都填
      if (formData.value.blood_pressure_systolic && !formData.value.blood_pressure_diastolic) {
        return false
      }
      if (!formData.value.blood_pressure_systolic && formData.value.blood_pressure_diastolic) {
        return false
      }
      return true
    case 3:
      // 既往病史步骤没有必填项
      return true
    case 4:
      // 生活方式步骤没有必填项
      return true
    default:
      return true
  }
}

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 返回
const goBack = () => {
  router.back()
}

// 前往推荐结果页
const goToRecommendation = () => {
  showSuccessModal.value = false
  router.push('/recommendation-result')
}

// 关闭成功弹窗
const closeSuccessModal = () => {
  showSuccessModal.value = false
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 计算BMI
const calculateBMI = () => {
  if (!formData.value.weight || !formData.value.height) return ''
  const weight = parseFloat(formData.value.weight)
  const height = parseFloat(formData.value.height) / 100 // 转换为米
  if (weight <= 0 || height <= 0) return ''
  const bmi = weight / (height * height)
  return bmi.toFixed(1)
}

// 获取性别文本
const getGenderText = () => {
  const genders = {
    'male': '男',
    'female': '女',
    'other': '其他'
  }
  return genders[formData.value.gender] || ''
}

// 获取选中的症状文本
const getSelectedSymptoms = () => {
  if (!formData.value.symptoms || formData.value.symptoms.length === 0) return ''
  const selected = commonSymptoms.value.filter(symptom => 
    formData.value.symptoms.includes(symptom.id.toString())
  )
  return selected.map(symptom => symptom.name).join('、')
}

// 获取选中的疾病文本
const getSelectedDiseases = () => {
  if (!formData.value.chronic_diseases || formData.value.chronic_diseases.length === 0) return ''
  const selected = commonDiseases.value.filter(disease => 
    formData.value.chronic_diseases.includes(disease.id.toString())
  )
  return selected.map(disease => disease.name).join('、')
}

// 获取饮食类型文本
const getDietTypeText = () => {
  const diets = {
    'balanced': '均衡饮食',
    'vegetarian': '素食',
    'meat': '偏肉食',
    'high_fat': '高脂饮食',
    'high_salt': '高盐饮食',
    'high_sugar': '高糖饮食',
    'other': '其他'
  }
  return diets[formData.value.diet_type] || ''
}

// 获取运动频率文本
const getExerciseFrequencyText = () => {
  const frequencies = {
    'never': '几乎不运动',
    '1-2': '1-2次/周',
    '3-4': '3-4次/周',
    '5-7': '5-7次/周'
  }
  return frequencies[formData.value.exercise_frequency] || ''
}

// 获取吸烟情况文本
const getSmokingText = () => {
  const smoking = {
    'never': '不吸烟',
    'former': '已戒烟',
    'current_light': '轻度吸烟',
    'current_heavy': '重度吸烟'
  }
  return smoking[formData.value.smoking] || ''
}

// 获取饮酒情况文本
const getAlcoholText = () => {
  const alcohol = {
    'never': '不饮酒',
    'occasional': '偶尔饮酒',
    'regular_light': '轻度饮酒',
    'regular_heavy': '重度饮酒'
  }
  return alcohol[formData.value.alcohol] || ''
}

// 加载用户已有健康信息
const loadUserHealthInfo = async () => {
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      router.push('/login')
      return
    }
    
    const response = await healthInfoAPI.getUserHealthInfo(userId)
    
    if (response.status === 'success' && response.data) {
      // 填充表单数据
      formData.value = {
        ...formData.value,
        ...response.data
      }
    }
  } catch (error) {
    console.error('加载用户健康信息错误:', error)
    // 不阻止页面加载，让用户重新填写
  }
}

// 组件挂载时加载用户已有健康信息
onMounted(() => {
  loadUserHealthInfo()
})
</script>

<style scoped>
/* 信息收集页面样式 */
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
  --required-color: #f5222d;
}

.information-collection {
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
  justify-content: center;
  padding: 20px;
}

.form-container {
  width: 100%;
  max-width: 1000px;
  background-color: var(--card-background);
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  margin: 0 0 12px;
  color: var(--text-color);
  font-size: 24px;
}

.form-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 进度指示器 */
.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  padding: 0 20px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.step-text {
  color: var(--text-secondary);
  font-size: 12px;
  text-align: center;
}

.progress-line {
  flex: 1;
  height: 2px;
  background-color: var(--border-color);
  margin: 0 10px;
  transition: all 0.3s ease;
}

.progress-step.active .step-number {
  background-color: var(--primary-color);
  color: white;
}

.progress-step.active .step-text {
  color: var(--primary-color);
  font-weight: 500;
}

.progress-step.completed .step-number {
  background-color: var(--success-color);
  color: white;
}

.progress-step.completed .step-text {
  color: var(--success-color);
}

.progress-line.completed {
  background-color: var(--success-color);
}

/* 表单步骤 */
.form-step {
  animation: fadeIn 0.5s ease-in-out;
}

.form-step h3 {
  margin: 0 0 24px;
  color: var(--text-color);
  font-size: 20px;
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 8px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h4 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-color);
  font-weight: 500;
  font-size: 14px;
}

.required {
  color: var(--required-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-color);
}

.checkbox-item input {
  width: auto;
  margin-right: 8px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-color);
}

.radio-item input {
  width: auto;
  margin-right: 8px;
}

/* 表单导航按钮 */
.form-navigation {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.nav-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn.back {
  background-color: var(--border-color);
  color: var(--text-color);
  margin-right: auto;
}

.nav-btn.back:hover:not(:disabled) {
  background-color: #bfbfbf;
}

.nav-btn.next {
  background-color: var(--primary-color);
  color: white;
}

.nav-btn.next:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.nav-btn.submit {
  background-color: var(--success-color);
  color: white;
}

.nav-btn.submit:hover:not(:disabled) {
  background-color: #389e0d;
}

/* 确认提交步骤 */
.confirmation-summary {
  margin-bottom: 30px;
}

.summary-section {
  margin-bottom: 24px;
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 6px;
}

.summary-section h4 {
  margin: 0 0 16px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 500;
}

.summary-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-label {
  min-width: 100px;
  color: var(--text-secondary);
  font-weight: 500;
}

.summary-value {
  color: var(--text-color);
  flex: 1;
}

.agreement {
  margin-top: 24px;
  padding: 16px;
  background-color: #e6f7ff;
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-color);
}

.agreement input {
  width: auto;
  margin-right: 8px;
}

/* 成功提示弹窗 */
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
  text-align: center;
  animation: modalFadeIn 0.3s ease-in-out;
}

.modal-header h3 {
  margin: 0 0 20px;
  color: var(--text-color);
  font-size: 20px;
}

.modal-body {
  margin-bottom: 24px;
}

.success-icon {
  font-size: 48px;
  color: var(--success-color);
  margin-bottom: 16px;
}

.modal-body p {
  margin: 0 0 8px;
  color: var(--text-color);
  font-size: 14px;
}

.modal-btn {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn:hover {
  background-color: var(--primary-dark);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .form-container {
    padding: 20px;
  }
  
  .progress-indicator {
    flex-direction: column;
    padding: 0;
  }
  
  .progress-step {
    flex-direction: row;
    width: 100%;
    justify-content: flex-start;
    margin-bottom: 16px;
  }
  
  .step-number {
    margin-right: 12px;
    margin-bottom: 0;
  }
  
  .progress-line {
    display: none;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .form-navigation {
    flex-direction: column;
  }
  
  .nav-btn {
    width: 100%;
  }
  
  .nav-btn.back {
    margin-right: 0;
  }
}
</style>