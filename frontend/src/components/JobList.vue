<template>
  <div class="job-list">
    <el-card v-for="job in jobs" :key="job.job_link" class="job-card">
      <div class="job-header">
        <div class="job-title-wrap">
          <h3 class="job-title">
            <a :href="job.job_link" target="_blank">{{ job.title }}</a>
          </h3>
          <span class="job-salary">{{ job.salary }}</span>
        </div>
        <div class="job-company">
          <span class="company-name">{{ job.company }}</span>
          <span class="job-location">{{ job.location }}</span>
        </div>
      </div>
      
      <div class="job-tags">
        <el-tag 
          v-for="tag in job.tags" 
          :key="tag"
          size="small"
          class="tag"
        >
          {{ tag }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
defineProps({
  jobs: {
    type: Array,
    required: true
  }
})
</script>

<style scoped>
.job-list {
  margin-top: 20px;
}

.job-card {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.job-header {
  margin-bottom: 12px;
}

.job-title-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.job-title {
  margin: 0;
  font-size: 18px;
}

.job-title a {
  color: #333;
  text-decoration: none;
}

.job-title a:hover {
  color: #409EFF;
}

.job-salary {
  color: #f56c6c;
  font-size: 16px;
  font-weight: 500;
}

.job-company {
  display: flex;
  align-items: center;
  color: #666;
}

.company-name {
  margin-right: 16px;
  font-weight: 500;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  margin-right: 8px;
}
</style> 