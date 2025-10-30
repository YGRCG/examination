<template>
  <div class="home-container">
    <!-- 头部区域 -->
    <header class="header">
      <h1 class="system-title">医院体检项目智能推荐系统</h1>
    </header>

    <!-- 主体内容区域 -->
    <main class="main-content">
      <div class="welcome-section">
        <!-- Logo removed as the file doesn't exist -->
        <h2 class="welcome-title">欢迎使用智能体检推荐系统</h2>
        <p class="welcome-description">
          我们的系统将根据您的个人健康信息，为您推荐最适合的体检项目和套餐，
          帮助您全面了解自己的健康状况。
        </p>
        
        <!-- 主要行动号召按钮 -->
        <button class="primary-button" @click="startRecommendation">
          开始智能体检推荐
        </button>
        
        <!-- 功能亮点 -->
        <div class="features-section">
          <div class="feature-item">
            <div class="feature-icon">📱</div>
            <div class="feature-text">智能交互体验</div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">👤</div>
            <div class="feature-text">个性化推荐</div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div class="feature-text">报告智能解读</div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部区域 -->
    <footer class="footer">
      <div class="footer-actions">
        <router-link to="/login" class="login-link">
          登录/注册
        </router-link>
        <router-link to="/reports" class="history-link">
          查看历史记录
        </router-link>
        <button class="faq-button" @click="showFaq">
          常见问题
        </button>
      </div>
      <p class="copyright">© 2023 医院体检项目智能推荐系统 版权所有</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

// 导航到智能交互页面
const startRecommendation = () => {
  // 检查是否已登录
  if (localStorage.getItem('token')) {
    router.push('/chat')
  } else {
    router.push({
      name: 'login',
      query: { redirect: '/chat' }
    })
  }
}

// 显示常见问题
const showFaq = () => {
  alert('常见问题功能正在开发中...')
}
</script>

<style scoped>
/* 首页样式 */
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f8ff;
}

.header {
  background-color: var(--primary-color);
  color: white;
  padding: 20px 0;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.system-title {
  font-size: 20px;
  font-weight: bold;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.welcome-section {
  max-width: 600px;
  text-align: center;
}

.welcome-title {
  font-size: 24px;
  color: var(--text-color);
  margin-bottom: 20px;
  font-weight: bold;
}

.welcome-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 30px;
}

.primary-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 16px 40px;
  font-size: 18px;
  font-weight: bold;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.primary-button:hover {
  background-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
}

.features-section {
  display: flex;
  justify-content: space-around;
  margin-top: 50px;
  padding: 0 20px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80px;
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.feature-text {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
}

.footer {
  background-color: white;
  padding: 20px;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.footer-actions {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 15px;
}

.login-link, .history-link, .faq-button {
  color: var(--primary-color);
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.login-link:hover, .history-link:hover, .faq-button:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.copyright {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>