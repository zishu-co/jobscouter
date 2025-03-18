<template>
  <el-dialog
    :title="initialEmails.length ? '修改订阅邮箱' : '添加订阅邮箱'"
    v-model="visible"
    width="500px"
  >
    <div class="email-list">
      <div v-if="emails.length === 0" class="empty-tip">
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          请添加接收工作更新的邮箱地址
        </el-alert>
      </div>
      
      <div v-for="(email, index) in emails" :key="index" class="email-item">
        <el-input
          v-model="emails[index]"
          placeholder="请输入邮箱"
          class="email-input"
          :status="getEmailValidationStatus(email)"
          @blur="validateEmail(index)"
        >
          <template #append>
            <el-button @click="removeEmail(index)" type="danger" :icon="Delete">
              删除
            </el-button>
          </template>
        </el-input>
        <div class="email-error" v-if="emailErrors[index]">
          {{ emailErrors[index] }}
        </div>
      </div>
      
      <el-button
        type="primary"
        @click="addEmail"
        class="add-btn"
        :icon="Plus"
      >
        添加邮箱
      </el-button>
    </div>

    <div class="tip-text" v-if="emails.length > 0">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        有新职位时，系统会同时发送通知到以上所有邮箱
      </el-alert>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave">
          {{ initialEmails.length ? '更新并订阅' : '添加并订阅' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, defineEmits, defineProps } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: Boolean,
  initialEmails: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const visible = ref(props.modelValue)
const emails = ref([...props.initialEmails])
const emailErrors = ref({})

// 监听props变化
watch(() => props.modelValue, (val) => {
  visible.value = val
})

// 监听visible变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 监听initialEmails变化
watch(() => props.initialEmails, (val) => {
  emails.value = [...val]
}, { deep: true })

// 验证单个邮箱
const validateEmail = (index) => {
  const email = emails.value[index]
  if (!email) {
    emailErrors.value[index] = '邮箱不能为空'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    emailErrors.value[index] = '请输入有效的邮箱地址'
    return false
  }
  
  emailErrors.value[index] = ''
  return true
}

// 获取邮箱验证状态
const getEmailValidationStatus = (email) => {
  if (!email) return ''
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email) ? 'success' : 'error'
}

// 添加邮箱
const addEmail = () => {
  emails.value.push('')
  emailErrors.value = {}
}

// 删除邮箱
const removeEmail = (index) => {
  emails.value.splice(index, 1)
  delete emailErrors.value[index]
}

// 保存邮箱列表
const handleSave = () => {
  // 验证所有邮箱
  const hasErrors = emails.value.some((_, index) => !validateEmail(index))
  if (hasErrors) {
    ElMessage.warning('请修正邮箱格式错误')
    return
  }
  
  const validEmails = emails.value.filter(email => email.trim())
  if (validEmails.length === 0) {
    ElMessage.warning('请至少添加一个邮箱地址')
    return
  }
  
  emit('save', validEmails)
}

// 取消
const handleCancel = () => {
  emails.value = [...props.initialEmails]
  emailErrors.value = {}
  emit('cancel')
  visible.value = false
}
</script>

<style scoped>
.email-list {
  max-height: 400px;
  overflow-y: auto;
}

.email-item {
  margin-bottom: 10px;
}

.email-input {
  width: 100%;
}

.add-btn {
  width: 100%;
  margin-top: 10px;
}

.empty-tip {
  margin-bottom: 20px;
}

.tip-text {
  margin-top: 20px;
}

.email-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
  padding-left: 4px;
}

.el-input.is-error {
  .el-input__inner {
    border-color: #f56c6c;
  }
}
</style> 