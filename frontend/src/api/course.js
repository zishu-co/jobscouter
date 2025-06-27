import axios from 'axios'

export async function fetchAllCourses() {
  try {
    const response = await axios.get('https://zishu.co/api/course/fetch_all_courses')
    if (response.status === 200 && response.data) {
      return response.data
    } else {
      throw new Error('获取课程信息失败')
    }
  } catch (error) {
    throw new Error('获取课程信息失败: ' + (error.message || error))
  }
}
