import api from './index'

export interface MonthlyStats {
  balance: number
  income: number
  expense: number
  transaction_count: number
}

export interface CategoryStats {
  category: string
  amount: number
  percentage: number
  count: number
}

export interface TrendData {
  dates: string[]
  expense: number[]
  income: number[]
}

// 获取月度统计
export const getMonthlyStats = (year?: number, month?: number) => {
  return api.get<any, MonthlyStats>('/statistics/monthly', {
    params: { year, month }
  })
}

// 获取分类统计
export const getCategoryStats = (type: 'income' | 'expense' = 'expense', year?: number, month?: number) => {
  return api.get<any, CategoryStats[]>('/statistics/category', {
    params: { type, year, month }
  })
}

// 获取趋势数据
export const getTrendStats = (days: number = 7) => {
  return api.get<any, TrendData>('/statistics/trend', {
    params: { days }
  })
}
