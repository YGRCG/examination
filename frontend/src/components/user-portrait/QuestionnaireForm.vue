<template>
  <div class="questionnaire-container">
    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>
      <div class="progress-info">
        <span>{{ currentStepLabel }}</span>
        <span>{{ completedSteps.length }}/{{ totalSteps }}</span>
      </div>
    </div>

    <!-- 问卷内容 -->
    <div class="questionnaire-content">
      <!-- 基础信息步骤 -->
      <div v-if="currentStep === 'basic_info' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">基本信息</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label for="age">年龄</label>
            <input 
              id="age" 
              v-model.number="formData.age" 
              type="number" 
              required 
              min="0" 
              max="150"
              placeholder="请输入年龄"
            >
          </div>
          <div class="form-group">
            <label for="gender">性别</label>
            <select id="gender" v-model="formData.gender" required>
              <option value="">请选择</option>
              <option value="male">男</option>
              <option value="female">女</option>
            </select>
          </div>
          <div class="form-group">
            <label for="height">身高 (cm)</label>
            <input 
              id="height" 
              v-model.number="formData.height" 
              type="number" 
              required 
              min="50" 
              max="250"
              placeholder="请输入身高"
            >
          </div>
          <div class="form-group">
            <label for="weight">体重 (kg)</label>
            <input 
              id="weight" 
              v-model.number="formData.weight" 
              type="number" 
              required 
              min="10" 
              max="300"
              placeholder="请输入体重"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn-primary">下一步</button>
          </div>
        </form>
      </div>

      <!-- 健康史步骤 -->
      <div v-else-if="currentStep === 'health_history' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">健康史</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label>慢性疾病史</label>
            <div class="checkbox-group">
              <label v-for="disease in commonDiseases" :key="disease">
                <input 
                  type="checkbox" 
                  :value="disease" 
                  v-model="formData.chronic_diseases"
                >
                {{ disease }}
              </label>
            </div>
            <input 
              v-model="newDisease" 
              type="text" 
              @keyup.enter="addDisease"
              placeholder="其他疾病"
            >
            <button type="button" @click="addDisease" class="btn-small">添加</button>
          </div>
          <div class="form-group">
            <label>家族病史</label>
            <textarea 
              v-model="formData.family_medical_history" 
              rows="3"
              placeholder="请填写家族成员的重大疾病史"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="skipStep" class="btn-secondary">跳过</button>
            <button type="submit" class="btn-primary">下一步</button>
          </div>
        </form>
      </div>

      <!-- 生活习惯步骤 -->
      <div v-else-if="currentStep === 'lifestyle' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">生活习惯</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label>吸烟情况</label>
            <div class="radio-group">
              <label>
                <input type="radio" value="true" v-model="formData.smoking"> 是
              </label>
              <label>
                <input type="radio" value="false" v-model="formData.smoking"> 否
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>饮酒情况</label>
            <div class="radio-group">
              <label>
                <input type="radio" value="true" v-model="formData.alcohol"> 是
              </label>
              <label>
                <input type="radio" value="false" v-model="formData.alcohol"> 否
              </label>
            </div>
          </div>
          <div class="form-group">
            <label for="exercise">运动频率</label>
            <select id="exercise" v-model="formData.exercise_frequency">
              <option value="很少">很少</option>
              <option value="偶尔">偶尔</option>
              <option value="经常">经常</option>
              <option value="每天">每天</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="skipStep" class="btn-secondary">跳过</button>
            <button type="submit" class="btn-primary">下一步</button>
          </div>
        </form>
      </div>

      <!-- 不适症状步骤 -->
      <div v-else-if="currentStep === 'symptoms' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">不适症状</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label>是否有不适症状？</label>
            <div class="radio-group">
              <label>
                <input type="radio" value="true" v-model="formData.has_symptoms"> 是
              </label>
              <label>
                <input type="radio" value="false" v-model="formData.has_symptoms"> 否
              </label>
            </div>
          </div>
          <div v-if="formData.has_symptoms" class="form-group">
            <label for="symptomDesc">请描述您的症状（如：最近经常头晕）</label>
            <textarea 
              id="symptomDesc" 
              v-model="formData.description" 
              rows="3" 
              required
              placeholder="请详细描述您的症状、频率等信息"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="skipStep" class="btn-secondary">跳过</button>
            <button type="submit" class="btn-primary">下一步</button>
          </div>
        </form>
      </div>

      <!-- 动态追问 -->
      <div v-else-if="currentState === 'symptom_dynamic'" class="step-content">
        <h3 class="step-title">症状详情</h3>
        <div class="dynamic-question">
          <p class="question-text">{{ currentQuestion }}</p>
          <form @submit.prevent="submitDynamicAnswer">
            <div class="form-group">
              <input 
                v-model="dynamicAnswer" 
                type="text" 
                required 
                placeholder="请输入您的回答"
                @keyup.enter="submitDynamicAnswer"
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="btn-primary">提交</button>
            </div>
          </form>
        </div>
      </div>

      <!-- 历史体检报告步骤 -->
      <div v-else-if="currentStep === 'medical_reports' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">历史体检报告</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label>是否有历史体检报告？</label>
            <div class="radio-group">
              <label>
                <input type="radio" value="true" v-model="formData.has_reports"> 是
              </label>
              <label>
                <input type="radio" value="false" v-model="formData.has_reports"> 否
              </label>
            </div>
          </div>
          <div v-if="formData.has_reports" class="form-group">
            <label>最近一次体检时间</label>
            <input 
              v-model="formData.last_report_date" 
              type="date"
              placeholder="选择日期"
            >
          </div>
          <div class="form-actions">
            <button type="button" @click="skipStep" class="btn-secondary">跳过</button>
            <button type="submit" class="btn-primary">下一步</button>
          </div>
        </form>
      </div>

      <!-- 重点关注步骤 -->
      <div v-else-if="currentStep === 'concerns' && currentState === 'normal'" class="step-content">
        <h3 class="step-title">重点关注</h3>
        <form @submit.prevent="submitStep">
          <div class="form-group">
            <label>您最关注的健康问题是？</label>
            <div class="checkbox-group">
              <label v-for="concern in commonConcerns" :key="concern">
                <input 
                  type="checkbox" 
                  :value="concern" 
                  v-model="formData.health_concerns"
                >
                {{ concern }}
              </label>
            </div>
            <textarea 
              v-model="formData.other_concerns" 
              rows="2"
              placeholder="其他关注点"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="skipStep" class="btn-secondary">跳过</button>
            <button type="submit" class="btn-primary">完成</button>
          </div>
        </form>
      </div>

      <!-- 完成页面 -->
      <div v-else-if="isComplete" class="step-content complete-page">
        <div class="complete-icon">✓</div>
        <h3>问卷完成！</h3>
        <p>感谢您完成用户画像问卷，系统已根据您的信息生成个性化健康建议。</p>
        <div class="form-actions">
          <button @click="resetQuestionnaire" class="btn-secondary">重新填写</button>
          <router-link to="/dashboard" class="btn-primary">查看结果</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProgress, submitStep, submitDynamicAnswer, skipStep, resetQuestionnaire as resetAPI } from '@/api/user-portrait'

export default {
  name: 'QuestionnaireForm',
  setup() {
    const router = useRouter()
    
    // 状态管理
    const currentStep = ref('basic_info')
    const currentState = ref('normal')
    const completedSteps = ref([])
    const formData = ref({})
    const dynamicAnswer = ref('')
    const currentQuestion = ref('')
    const isComplete = ref(false)
    
    // 常量数据
    const commonDiseases = [
      '高血压', '糖尿病', '心脏病', '肝病', '肾病', 
      '高脂血症', '关节炎', '哮喘', '过敏', '其他'
    ]
    
    const commonConcerns = [
      '心脏健康', '血压', '血糖', '肝功能', '肾功能',
      '血脂', '骨密度', '肿瘤筛查', '视力', '听力'
    ]
    
    const mainSteps = [
      { key: 'basic_info', label: '基本信息' },
      { key: 'health_history', label: '健康史' },
      { key: 'lifestyle', label: '生活习惯' },
      { key: 'symptoms', label: '不适症状' },
      { key: 'medical_reports', label: '历史体检报告' },
      { key: 'concerns', label: '重点关注' }
    ]
    
    // 计算属性
    const currentStepLabel = computed(() => {
      const step = mainSteps.find(s => s.key === currentStep.value)
      return step ? step.label : ''
    })
    
    const totalSteps = computed(() => mainSteps.length)
    
    const progressPercentage = computed(() => {
      return (completedSteps.value.length / totalSteps.value) * 100
    })
    
    // 方法
    const initFormData = () => {
      // 根据当前步骤初始化表单数据
      switch(currentStep.value) {
        case 'basic_info':
          formData.value = {
            age: null,
            gender: '',
            height: null,
            weight: null
          }
          break
        case 'health_history':
          formData.value = {
            chronic_diseases: [],
            family_medical_history: ''
          }
          break
        case 'lifestyle':
          formData.value = {
            smoking: 'false',
            alcohol: 'false',
            exercise_frequency: '偶尔'
          }
          break
        case 'symptoms':
          formData.value = {
            has_symptoms: 'false',
            description: ''
          }
          break
        case 'medical_reports':
          formData.value = {
            has_reports: 'false',
            last_report_date: ''
          }
          break
        case 'concerns':
          formData.value = {
            health_concerns: [],
            other_concerns: ''
          }
          break
      }
    }
    
    const loadProgress = async () => {
      try {
        const response = await getProgress()
        currentStep.value = response.current_step
        completedSteps.value = response.completed_steps
        currentState.value = response.current_state || 'normal'
        
        if (currentState.value === 'symptom_dynamic') {
          // 动态状态下，问题将在提交时获取
        } else {
          initFormData()
        }
      } catch (error) {
        console.error('加载进度失败:', error)
      }
    }
    
    const handleSubmitStep = async () => {
      try {
        const response = await submitStep(currentStep.value, formData.value)
        
        if (response.next_action === 'dynamic_question') {
          // 进入动态追问状态
          currentState.value = 'symptom_dynamic'
          currentQuestion.value = response.question
          dynamicAnswer.value = ''
        } else if (response.next_action === 'next_step') {
          // 进入下一步
          currentStep.value = response.next_step
          completedSteps.value = response.completed_steps
          currentState.value = 'normal'
          initFormData()
        } else if (response.next_action === 'complete') {
          // 完成问卷
          isComplete.value = true
        }
      } catch (error) {
        console.error('提交步骤失败:', error)
        alert('提交失败，请重试')
      }
    }
    
    const handleDynamicAnswer = async () => {
      try {
        const response = await submitDynamicAnswer(dynamicAnswer.value)
        
        if (response.next_action === 'dynamic_question') {
          // 继续动态追问
          currentQuestion.value = response.question
          dynamicAnswer.value = ''
        } else if (response.next_action === 'next_step') {
          // 返回主流程
          currentStep.value = response.next_step
          completedSteps.value = response.completed_steps
          currentState.value = 'normal'
          initFormData()
        }
      } catch (error) {
        console.error('提交动态回答失败:', error)
        alert('提交失败，请重试')
      }
    }
    
    const handleSkipStep = async () => {
      try {
        const response = await skipStep()
        
        if (response.next_action === 'next_step') {
          currentStep.value = response.next_step
          completedSteps.value = response.completed_steps
          currentState.value = 'normal'
          initFormData()
        } else if (response.next_action === 'complete') {
          isComplete.value = true
        }
      } catch (error) {
        console.error('跳过步骤失败:', error)
        alert('操作失败，请重试')
      }
    }
    
    const handleResetQuestionnaire = async () => {
      try {
        const response = await resetAPI()
        currentStep.value = response.next_step
        completedSteps.value = []
        currentState.value = 'normal'
        isComplete.value = false
        initFormData()
      } catch (error) {
        console.error('重置问卷失败:', error)
        alert('重置失败，请重试')
      }
    }
    
    const addDisease = () => {
      if (formData.value.chronic_diseases && dynamicAnswer.value && !formData.value.chronic_diseases.includes(dynamicAnswer.value)) {
        formData.value.chronic_diseases.push(dynamicAnswer.value)
        dynamicAnswer.value = ''
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadProgress()
    })
    
    return {
      currentStep,
      currentState,
      completedSteps,
      formData,
      dynamicAnswer,
      currentQuestion,
      isComplete,
      commonDiseases,
      commonConcerns,
      currentStepLabel,
      totalSteps,
      progressPercentage,
      submitStep: handleSubmitStep,
      submitDynamicAnswer: handleDynamicAnswer,
      skipStep: handleSkipStep,
      resetQuestionnaire: handleResetQuestionnaire,
      addDisease
    }
  }
}
</script>

<style scoped>
.questionnaire-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.progress-section {
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4caf50;
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.questionnaire-content {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.step-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

input[type="text"],
input[type="number"],
input[type="date"],
select,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.checkbox-group,
.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
}

.checkbox-group label,
.radio-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: normal;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #f1f1f1;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-small {
  padding: 5px 10px;
  font-size: 14px;
  margin-left: 10px;
}

.dynamic-question {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.question-text {
  font-size: 18px;
  margin-bottom: 20px;
  color: #333;
}

.complete-page {
  text-align: center;
  padding: 40px 0;
}

.complete-icon {
  font-size: 60px;
  color: #4caf50;
  margin-bottom: 20px;
}

.complete-page h3 {
  font-size: 28px;
  margin-bottom: 15px;
  color: #333;
}

.complete-page p {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}
</style>