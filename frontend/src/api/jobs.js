import axios from 'axios'
import { cityGroups, hotCities, cityOptions } from './cityData'

// 使用相对路径，让 Vite 代理处理跨域
export const searchJobs = async (params) => {
  try {
    const response = await axios.post('/api/jobs/search', params)
    return response.data
  } catch (error) {
    console.error('搜索工作失败:', error)
    throw error
  }
}

// 订阅职位
export const subscribeJobs = async (params) => {
  try {
    const response = await axios.post('/api/jobs/subscribe', params)
    return response.data
  } catch (error) {
    console.error('订阅失败:', error)
    throw error
  }
}

// 获取用户邮箱列表
export const getUserEmails = async () => {
  try {
    const response = await axios.get('/api/user/emails')
    return response.data
  } catch (error) {
    console.error('获取邮箱列表失败:', error)
    throw error
  }
}

// 更新用户邮箱列表
export const updateUserEmails = async (emails) => {
  try {
    const response = await axios.put('/api/user/emails', { emails })
    return response.data
  } catch (error) {
    console.error('更新邮箱列表失败:', error)
    throw error
  }
}

// 获取订阅列表
export function getSubscriptions() {
  return axios.get('/api/jobs/subscriptions')
}

// 删除订阅
export function deleteSubscription(id) {
  return axios.delete(`/api/jobs/subscription/${id}`)
}

// 更新订阅邮箱
export function updateSubscriptionEmails(id, emailList) {
  return axios.put(`/api/jobs/subscription/${id}/emails`, emailList)
}

export { cityGroups, hotCities, cityOptions } 