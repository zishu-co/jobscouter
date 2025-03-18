<template>
  <div class="app">
    <header class="header">
      <h1>工作搜索</h1>
    </header>
    <job-search />
  </div>
</template>

<script setup>
import JobSearch from './components/JobSearch.vue'
</script>

<style>
body {
  margin: 0;
  padding: 0;
}

.app {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: #fff;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}
</style>
