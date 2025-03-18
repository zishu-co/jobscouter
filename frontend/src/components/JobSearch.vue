<template>
  <div class="job-search-container">
    <div class="search-form">
      <el-form :model="searchForm" @submit.prevent="handleSearch">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item>
              <el-input
                v-model="searchForm.query"
                placeholder="请输入职位关键词"
                class="search-input"
                @keyup.enter="handleSearch"
                :disabled="loading || subscribing"
              >
                <template #append>
                  <el-popover
                    placement="bottom-start"
                    :width="700"
                    trigger="click"
                    v-model:visible="cityPopoverVisible"
                  >
                    <template #reference>
                      <el-button>{{ getCityLabel || '选择城市' }}</el-button>
                    </template>
                    
                    <div class="city-selector">
                      <!-- 导航栏 -->
                      <div class="nav-section">
                        <div 
                          v-for="section in sections" 
                          :key="section.key"
                          class="nav-item"
                          :class="{ active: currentSection === section.key }"
                          @click="selectSection(section.key)"
                        >
                          {{ section.label }}
                        </div>
                      </div>

                      <!-- 城市列表区域 -->
                      <div class="cities-container">
                        <!-- 热门城市列表 -->
                        <template v-if="currentSection === '热门城市'">
                          <div class="city-list">
                            <span
                              v-for="city in hotCities"
                              :key="city.value"
                              class="city-item"
                              :class="{ active: searchForm.city === city.value }"
                              @click="selectCity(city)"
                            >
                              {{ city.label }}
                            </span>
                          </div>
                        </template>

                        <!-- 字母分组的城市列表 -->
                        <template v-else>
                          <div class="letter-cities">
                            <template v-for="letter in getLettersInSection" :key="letter">
                              <div class="letter-group">
                                <div class="letter-title">{{ letter }}</div>
                                <div class="city-list">
                                  <span
                                    v-for="city in getCitiesByLetter(letter)"
                                    :key="city.value"
                                    class="city-item"
                                    :class="{ active: searchForm.city === city.value }"
                                    @click="selectCity(city)"
                                  >
                                    {{ city.label }}
                                  </span>
                                </div>
                              </div>
                            </template>
                          </div>
                        </template>
                      </div>
                    </div>
                  </el-popover>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleSearch" 
                :loading="loading"
                :disabled="subscribing"
              >
                {{ loading ? '搜索中...' : '搜索' }}
              </el-button>
              <el-button 
                type="success" 
                @click="handleSubscribe" 
                :loading="subscribing"
                :disabled="!jobs.length || loading"
              >
                {{ subscribing ? '订阅中...' : '订阅' }}
              </el-button>
              <el-button 
                type="info" 
                @click="showSubscriptionManager = true"
              >
                我的订阅
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="totalJobs"
        @current-change="handlePageChange"
        layout="prev, pager, next"
        background
      />
    </div>

    <job-list :jobs="jobs" v-if="jobs.length > 0" />
    <el-empty description="暂无数据" v-else />

    <!-- 邮箱管理对话框 -->
    <email-manager
      v-model="showEmailManager"
      :initial-emails="userEmails"
      @save="handleEmailsSave"
      @cancel="handleEmailsCancel"
    />

    <!-- 订阅管理器 -->
    <subscription-manager
      v-model="showSubscriptionManager"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { searchJobs, subscribeJobs, cityGroups, hotCities, cityOptions } from '../api/jobs'
import JobList from './JobList.vue'
import EmailManager from './EmailManager.vue'
import SubscriptionManager from './SubscriptionManager.vue'

const searchForm = reactive({
  query: '',
  city: '100010000' // 默认全国
})

const jobs = ref([])
const loading = ref(false)
const subscribing = ref(false)
const showEmailManager = ref(false)
const userEmails = ref([])

// 分页相关变量
const currentPage = ref(1)
const pageSize = ref(30)  // 每页显示30条
const totalJobs = ref(300)  // 总数设为300，因为BOSS直聘通常最多显示10页

const cityPopoverVisible = ref(false)

// 导航栏配置
const sections = [
  { key: '热门城市', label: '热门城市' },
  { key: 'ABCDE', label: 'ABCDE' },
  { key: 'FGHJ', label: 'FGHJ' },
  { key: 'KLMN', label: 'KLMN' },
  { key: 'PQRST', label: 'PQRST' },
  { key: 'UVWXYZ', label: 'UVWXYZ' }
]

const currentSection = ref('热门城市')

// 获取当前分组包含的字母
const getLettersInSection = computed(() => {
  if (currentSection.value === '热门城市') return []
  return Object.keys(cityGroups[currentSection.value] || {})
})

// 获取指定字母的城市列表
const getCitiesByLetter = (letter) => {
  if (currentSection.value === '热门城市') return hotCities
  return cityGroups[currentSection.value]?.[letter] || []
}

// 选择分组
const selectSection = (section) => {
  currentSection.value = section
}

// 获取当前选中城市的显示文本
const getCityLabel = computed(() => {
  const city = cityOptions.find(item => item.value === searchForm.city)
  return city ? city.label : '选择城市'
})

// 选择城市
const selectCity = (city) => {
  searchForm.city = city.value
  cityPopoverVisible.value = false
}

// 搜索职位
const handleSearch = async () => {
  if (!searchForm.query.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  if (loading.value) return; // 防止重复请求
  
  loading.value = true
  try {
    const res = await searchJobs({
      query: searchForm.query,
      city: searchForm.city,
      page: currentPage.value
    })
    
    if (res.code === 200) {
      jobs.value = res.data
      
      // 根据不同状态显示不同提示
      switch (res.message) {
        case 'timeout':
          ElMessage.error('页面加载超时，请稍后重试')
          break
        case 'empty':
          if (currentPage.value === 1) {
            ElMessage.info('未找到相关职位')
          } else {
            ElMessage.info(`第 ${currentPage.value} 页没有更多职位了`)
            totalJobs.value = (currentPage.value - 1) * pageSize.value
          }
          totalJobs.value = 0
          break
        case 'error':
          ElMessage.error('获取数据失败，请稍后重试')
          break
        case 'success':
          if (jobs.value.length === 0) {
            totalJobs.value = 0
          } else {
            totalJobs.value = 300
          }
          break
      }
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
    jobs.value = []
    totalJobs.value = 0
  } finally {
    loading.value = false
  }
}

// 处理订阅
const handleSubscribe = () => {
  console.log('点击订阅按钮')
  showEmailManager.value = true
}

// 保存邮箱设置并订阅
const handleEmailsSave = async (emails) => {
  console.log('保存邮箱:', emails)
  
  subscribing.value = true
  try {
    const res = await subscribeJobs({
      search_params: {
        query: searchForm.query,
        city: searchForm.city,
        position: searchForm.position
      },
      email_list: emails
    })
    
    userEmails.value = emails
    ElMessage.success({
      message: res.action === 'create' 
        ? '订阅成功！有新职位时将通过邮件通知您'
        : '订阅已更新！邮箱设置已保存',
      duration: 5000
    })
    showEmailManager.value = false
  } catch (error) {
    console.error('订阅失败:', error)
    ElMessage.error({
      message: error.response?.data?.detail || '订阅失败，请稍后重试',
      duration: 5000
    })
  } finally {
    subscribing.value = false
  }
}

// 处理邮箱管理取消
const handleEmailsCancel = () => {
  showEmailManager.value = false
}

// 页码改变处理
const handlePageChange = async (page) => {
  if (totalJobs.value === 0) {
    ElMessage.warning('没有更多数据了')
    return
  }
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' }) // 滚动到顶部
  await handleSearch()
}

// 监听搜索条件变化，重置页码和总数
watch([() => searchForm.query, () => searchForm.city], () => {
  currentPage.value = 1
  totalJobs.value = 0
  jobs.value = []
})

const showSubscriptionManager = ref(false)
</script>

<style scoped>
.job-search-container {
  padding: 20px;
}

.search-form {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.search-input {
  width: 100%;
}

.city-selector {
  padding: 16px;
}

.nav-section {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.nav-item {
  padding: 4px 12px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s;
}

.nav-item:hover {
  color: #1890ff;
}

.nav-item.active {
  color: #1890ff;
  background: #e6f7ff;
  border-radius: 4px;
}

.section-title {
  color: #666;
  font-size: 16px;
  margin-bottom: 16px;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.city-item {
  padding: 6px 16px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s;
}

.city-item:hover {
  color: #1890ff;
}

.city-item.active {
  color: #1890ff;
}

.cities-container {
  max-height: 350px;
  overflow-y: auto;
  padding: 0 16px;
}

/* 调整分页器样式 */
.pagination-container {
  margin: 20px 0;
  padding: 10px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
}

:deep(.el-pagination) {
  padding: 10px 0;
}

:deep(.el-pagination .el-pager li) {
  background-color: transparent;
}

:deep(.el-pagination .el-pager li.active) {
  color: #409eff;
  font-weight: bold;
}

/* 添加加载状态样式 */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-icon {
  font-size: 24px;
  margin-bottom: 8px;
  animation: rotate 1s linear infinite;
}

.loading-text {
  color: #909399;
  font-size: 14px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.letter-cities {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.letter-group {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.letter-group:last-child {
  border-bottom: none;
}

.letter-title {
  font-size: 16px;
  color: #333;
  font-weight: bold;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #1890ff;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.city-item {
  padding: 6px 16px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s;
  background: #f5f5f5;
  border-radius: 4px;
}

.city-item:hover {
  color: #1890ff;
  background: #e6f7ff;
}

.city-item.active {
  color: #fff;
  background: #1890ff;
}
</style> 