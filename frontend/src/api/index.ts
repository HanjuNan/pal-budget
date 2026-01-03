import axios from 'axios'
import { Capacitor } from '@capacitor/core'

// 根据平台选择 API 地址
const getBaseURL = () => {
  if (Capacitor.isNativePlatform()) {
    // 真机/模拟器：使用云端 API
    return 'https://pal-budget-hanjunan875-6n099n0a.leapcell.dev/api'
  }
  // Web 开发环境：使用代理
  return '/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // TODO: 添加 token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
