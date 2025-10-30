<template>
  <div class="questionnaire-view">
    <div class="container">
      <h1>用户画像问卷</h1>
      <p class="subtitle">完成以下问卷，帮助我们为您生成个性化的健康画像</p>
      
      <div class="questionnaire-container">
        <QuestionnaireForm 
          @completed="handleQuestionnaireCompleted"
          @error="handleError"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import QuestionnaireForm from '@/components/user-portrait/QuestionnaireForm.vue'

export default {
  name: 'QuestionnaireView',
  components: {
    QuestionnaireForm
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)

    const handleQuestionnaireCompleted = () => {
      ElMessage.success('问卷完成！正在生成用户画像...')
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        router.push('/portrait-result')
      }, 1500)
    }

    const handleError = (error) => {
      console.error('问卷处理错误:', error)
      ElMessage.error('处理请求时发生错误，请稍后重试')
    }

    return {
      loading,
      handleQuestionnaireCompleted,
      handleError
    }
  }
}
</script>

<style scoped>
.questionnaire-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

h1 {
  text-align: center;
  color: #fff;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 600;
}

.subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
}

.questionnaire-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  padding: 2rem;
}

@media (max-width: 768px) {
  .questionnaire-view {
    padding: 1rem 0;
  }
  
  .questionnaire-container {
    padding: 1.5rem;
    border-radius: 12px;
  }
  
  h1 {
    font-size: 2rem;
  }
}
</style>