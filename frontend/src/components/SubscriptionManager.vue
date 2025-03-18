<template>
  <el-dialog
    title="我的订阅"
    v-model="dialogVisible"
    width="800px"
    :close-on-click-modal="false"
  >
    <div class="subscription-list">
      <el-empty v-if="!subscriptions.length" description="暂无订阅" />
      <el-card v-else v-for="sub in subscriptions" :key="sub.id" class="subscription-item">
        <div class="subscription-header">
          <h3>{{ sub.search_params.query }}</h3>
          <div class="subscription-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEditEmails(sub)"
              :loading="sub.updating"
            >
              编辑邮箱
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(sub)"
              :loading="sub.deleting"
            >
              删除订阅
            </el-button>
          </div>
        </div>
        <div class="subscription-info">
          <p><strong>城市：</strong>{{ getCityLabel(sub.search_params.city) }}</p>
          <p><strong>通知邮箱：</strong>{{ sub.email_list.join(', ') }}</p>
          <p><strong>创建时间：</strong>{{ sub.created_at }}</p>
        </div>
      </el-card>
    </div>
  </el-dialog>

  <!-- 邮箱编辑对话框 -->
  <email-manager
    v-if="showEmailEditor"
    v-model="showEmailEditor"
    :initial-emails="currentEmails"
    @save="handleEmailsSave"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSubscriptions, deleteSubscription, updateSubscriptionEmails } from '../api/jobs'
import { cityOptions } from '../api/cityData'
import EmailManager from './EmailManager.vue'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const subscriptions = ref([])
const showEmailEditor = ref(false)
const currentSubscription = ref(null)
const currentEmails = ref([])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 获取城市名称
const getCityLabel = (cityCode) => {
  const city = cityOptions.find(item => item.value === cityCode)
  return city ? city.label : cityCode
}

// 加载订阅列表
const loadSubscriptions = async () => {
  try {
    const res = await getSubscriptions()
    if (res.data.code === 200) {
      // 为每个订阅添加loading状态
      subscriptions.value = res.data.data.map(sub => ({
        ...sub,
        updating: false,
        deleting: false
      }))
    }
  } catch (error) {
    console.error('获取订阅列表失败:', error)
    ElMessage.error('获取订阅列表失败')
  }
}

// 删除订阅
const handleDelete = async (subscription) => {
  try {
    await ElMessageBox.confirm('确定要删除这个订阅吗？', '提示', {
      type: 'warning'
    })
    
    subscription.deleting = true
    const res = await deleteSubscription(subscription.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      await loadSubscriptions()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除订阅失败:', error)
      ElMessage.error('删除订阅失败')
    }
  } finally {
    subscription.deleting = false
  }
}

// 编辑邮箱
const handleEditEmails = (subscription) => {
  currentSubscription.value = subscription
  currentEmails.value = [...subscription.email_list]
  showEmailEditor.value = true
}

// 保存邮箱设置
const handleEmailsSave = async (emails) => {
  if (!currentSubscription.value) return
  
  try {
    currentSubscription.value.updating = true
    const res = await updateSubscriptionEmails(currentSubscription.value.id, emails)
    if (res.data.code === 200) {
      ElMessage.success('邮箱更新成功')
      await loadSubscriptions()
      showEmailEditor.value = false
    }
  } catch (error) {
    console.error('更新邮箱失败:', error)
    ElMessage.error('更新邮箱失败')
  } finally {
    currentSubscription.value.updating = false
  }
}

// 监听对话框打开
watch(() => dialogVisible.value, (val) => {
  if (val) {
    loadSubscriptions()
  }
})
</script>

<style scoped>
.subscription-list {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px;
}

.subscription-item {
  margin-bottom: 16px;
}

.subscription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.subscription-header h3 {
  margin: 0;
  color: #303133;
}

.subscription-info {
  color: #606266;
  font-size: 14px;
}

.subscription-info p {
  margin: 8px 0;
}

.subscription-actions {
  display: flex;
  gap: 8px;
}
</style> 