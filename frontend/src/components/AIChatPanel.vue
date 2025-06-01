<template>
  <div class="ai-chat-panel" :class="{ 'panel-visible': visible }">
    <div class="panel-header">
      <h3>自塾AI职位顾问</h3>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="createNewConversation">
          新对话
          <el-icon><Plus /></el-icon>
        </el-button>
        <el-button type="text" @click="$emit('close')" class="close-btn">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div class="panel-content">
      <!-- 对话历史侧边栏 -->
      <div class="conversations-sidebar">
        <div 
          v-for="(conv, index) in conversations" 
          :key="conv.id"
          class="conversation-item"
          :class="{ active: currentConversationId === conv.id }"
          @click="switchConversation(conv.id)"
        >
          <span class="conversation-title">对话 {{ index + 1 }}</span>
          <el-button 
            v-if="conversations.length > 1" 
            type="text" 
            size="small"
            @click.stop="deleteConversation(conv.id)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      
      <!-- 当前对话内容 -->
      <div class="current-conversation">
        <div class="messages-container" ref="messagesContainer">
          <div v-for="(message, index) in currentMessages" :key="index" 
               class="message" :class="message.role">
            <div class="message-content">
              <div v-if="message.role === 'assistant'" class="avatar">AI</div>
              <div v-else class="avatar">我</div>
              <div class="text" v-html="formatMessage(message.content)"></div>
            </div>
          </div>
          <div v-if="loading" class="message assistant">
            <div class="message-content">
              <div class="avatar">AI</div>
              <div class="text typing">思考中...</div>
            </div>
          </div>
        </div>
        
        <div class="input-container">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="2"
            placeholder="请输入您的问题，例如：这个职位需要什么技能？"
            @keyup.enter.ctrl="sendMessage"
          />
          <el-button type="primary" @click="sendMessage" :disabled="loading || !userInput.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { Close, Plus, Delete } from '@element-plus/icons-vue'
import { chatWithAI, clearConversation, getConversationHistory } from '../api/ai.js'
import { ElMessage } from 'element-plus'
import { v4 as uuidv4 } from 'uuid'  // 需要安装: npm install uuid

const props = defineProps({
  visible: Boolean,
  jobData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close'])

// 对话状态管理
const conversations = ref([])
const currentConversationId = ref('')
const userInput = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

// 当前对话的消息
const currentMessages = ref([])

// 初始化
onMounted(() => {
  createNewConversation()
})

// 创建新对话
function createNewConversation() {
  const newId = uuidv4()
  conversations.value.push({
    id: newId,
    created: new Date()
  })
  
  switchConversation(newId)
}

// 切换对话
function switchConversation(id) {
  currentConversationId.value = id
  
  // 从后端获取对话历史，或初始化新对话
  const history = getConversationHistory(id)
  
  // 如果是新对话，添加欢迎消息
  if (history.length <= 1) { // 只有系统消息或空
    currentMessages.value = [{
      role: 'assistant',
      content: '你好！我是自塾AI职位顾问，可以回答你关于求职和职位的问题。请问有什么可以帮助你的？'
    }]
  } else {
    // 过滤掉系统消息，只显示用户和助手消息
    currentMessages.value = history
      .filter(msg => msg.role !== 'system')
      .map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content
      }));
  }
  
  nextTick(() => {
    scrollToBottom()
  })
}

// 删除对话
function deleteConversation(id) {
  const index = conversations.value.findIndex(c => c.id === id)
  if (index > -1) {
    conversations.value.splice(index, 1)
    
    // 如果删除的是当前对话，切换到第一个对话
    if (id === currentConversationId.value) {
      if (conversations.value.length > 0) {
        switchConversation(conversations.value[0].id)
      } else {
        createNewConversation()
      }
    }
  }
}

// 当有新消息时，滚动到底部
watch(currentMessages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function formatMessage(text) {
  // 将 \n 转换为 <br>
  return text.replace(/\n/g, '<br>')
}

async function sendMessage() {
  if (!userInput.value.trim() || loading.value) return
  
  // 添加用户消息
  const userMessage = userInput.value.trim()
  currentMessages.value.push({
    role: 'user',
    content: userMessage
  })
  
  userInput.value = ''
  loading.value = true
  
  try {
    // 准备发送给AI的上下文
    const jobContext = {
      jobs: props.jobData.map(job => ({
        title: job.title || '未知职位',
        company: job.company || '未知公司',
        salary: job.salary || '未知薪资',
        tags: job.tags || [],
        location: job.location || '未知地点'
      })),
      totalCount: props.jobData.length
    }
    
    let assistantMessageIndex = -1
    
    // 调用流式API，提供onChunk回调
    const response = await chatWithAI(
      userMessage, 
      jobContext, 
      currentConversationId.value,
      (chunk) => {
        // 收到第一个数据块时
        if (assistantMessageIndex === -1) {
          // 添加AI消息到列表中
          currentMessages.value.push({
            role: 'assistant',
            content: chunk
          })
          assistantMessageIndex = currentMessages.value.length - 1
          // 隐藏"思考中..."提示
          loading.value = false
        } else {
          // 直接更新数组中的对象，确保Vue能够检测到变化
          currentMessages.value[assistantMessageIndex] = {
            ...currentMessages.value[assistantMessageIndex],
            content: currentMessages.value[assistantMessageIndex].content + chunk
          }
        }
      }
    )
    
    if (!response.success) {
      // 如果最终响应失败，显示错误信息
      ElMessage.error(response.error || '请求失败')
    }
  } catch (error) {
    console.error('Chat error:', error)
    // 发生错误时，添加错误消息
    currentMessages.value.push({
      role: 'assistant',
      content: '发生错误，请稍后再试。'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ai-chat-panel {
  position: fixed;
  right: -600px;
  top: 0;
  width: 580px;
  height: 100vh;
  background-color: #fff;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: right 0.3s ease;
  z-index: 1000;
}

.panel-visible {
  right: 0;
}

.panel-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
}

.panel-content {
  display: flex;
  height: calc(100% - 60px);
}

.conversations-sidebar {
  width: 150px;
  border-right: 1px solid #eee;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.conversation-item {
  padding: 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.conversation-item:hover {
  background-color: #f0f0f0;
}

.conversation-item.active {
  background-color: #ecf5ff;
}

.conversation-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f7f9fb;
}

.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.message-content {
  display: flex;
  max-width: 85%;
}

.message.user .message-content {
  margin-left: auto;
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 8px;
}

.message.assistant .avatar {
  background-color: #409EFF;
  color: white;
}

.message.user .avatar {
  background-color: #67C23A;
  color: white;
  margin-right: 0;
  margin-left: 8px;
}

.text {
  padding: 10px 14px;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

.message.user .text {
  background-color: #ecf5ff;
}

.typing::after {
  content: '';
  display: inline-block;
  width: 10px;
  animation: typing 1s infinite;
}

@keyframes typing {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
  100% { content: ''; }
}

.input-container {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.input-container .el-button {
  margin-top: 10px;
  align-self: flex-end;
}
</style>