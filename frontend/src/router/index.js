import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: {
      title: '首页 - 医院体检项目智能推荐系统'
    }
  },
  {
    path: '/test',
    name: 'test',
    component: () => import('../views/TestView.vue'),
    meta: {
      title: '测试页面'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      title: '登录/注册 - 医院体检项目智能推荐系统',
      requiresAuth: false
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/PersonalCenterView.vue'),
    meta: {
      title: '个人中心 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../views/SmartInteractionView.vue'),
    meta: {
      title: '智能交互 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/smart-interaction',
    name: 'smartInteraction',
    component: () => import('../views/SmartInteractionView.vue'),
    meta: {
      title: '智能交互 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },

  {
    path: '/recommendations',
    name: 'recommendations',
    component: () => import('../views/RecommendationResultView.vue'),
    meta: {
      title: '推荐结果 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/appointments',
    name: 'appointments',
    component: () => import('../views/AppointmentManagementView.vue'),
    meta: {
      title: '预约管理 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/reports',
    name: 'reports',
    component: () => import('../views/ReportManagementView.vue'),
    meta: {
      title: '报告管理 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/report/:id/interpretation',
    name: 'reportInterpretation',
    component: () => import('../views/ReportInterpretationView.vue'),
    meta: {
      title: '报告解读 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SystemSettingsView.vue'),
    meta: {
      title: '系统设置 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/questionnaire',
    name: 'questionnaire',
    component: () => import('../views/QuestionnaireView.vue'),
    meta: {
      title: '用户画像问卷 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/portrait-result',
    name: 'portraitResult',
    component: () => import('../views/PortraitResultView.vue'),
    meta: {
      title: '用户画像结果 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/user-profile',
    name: 'userProfile',
    component: () => import('../views/UserProfileView.vue'),
    meta: {
      title: '用户画像 - 医院体检项目智能推荐系统',
      requiresAuth: true
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
export { router }