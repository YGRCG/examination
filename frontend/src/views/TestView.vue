<template>
  <div class="test-view">
    <h1>测试页面</h1>
    <p>这是一个用于测试的页面</p>
    <router-link to="/chat">前往智能交互页面</router-link>
  </div>
</template>

<script setup>
// 测试页面组件
</script>

<style scoped>
.test-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #1890ff;
  margin-bottom: 20px;
}

a {
  color: #1890ff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>