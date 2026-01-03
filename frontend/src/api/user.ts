import api from './index'

export interface User {
  id: number
  username: string
  nickname: string
  avatar_url?: string
  created_at: string
}

export interface UserStats {
  days: number
  total_records: number
  total_income: number
  total_expense: number
}

// 获取当前用户
export const getCurrentUser = () => {
  return api.get<any, User>('/user/me')
}

// 获取用户统计
export const getUserStats = () => {
  return api.get<any, UserStats>('/user/stats')
}
