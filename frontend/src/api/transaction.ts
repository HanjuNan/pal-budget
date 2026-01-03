import api from './index'

export interface Transaction {
  id?: number
  type: 'income' | 'expense'
  amount: number
  category: string
  description?: string
  date: string
  source?: 'manual' | 'voice' | 'photo' | 'ai'
  created_at?: string
}

export interface TransactionQuery {
  skip?: number
  limit?: number
  type?: 'income' | 'expense'
  start_date?: string
  end_date?: string
}

// 获取交易列表
export const getTransactions = (params?: TransactionQuery) => {
  return api.get<any, Transaction[]>('/transactions/', { params })
}

// 获取单个交易
export const getTransaction = (id: number) => {
  return api.get<any, Transaction>(`/transactions/${id}`)
}

// 创建交易
export const createTransaction = (data: Omit<Transaction, 'id' | 'created_at'>) => {
  return api.post<any, Transaction>('/transactions/', data)
}

// 更新交易
export const updateTransaction = (id: number, data: Partial<Transaction>) => {
  return api.put<any, Transaction>(`/transactions/${id}`, data)
}

// 删除交易
export const deleteTransaction = (id: number) => {
  return api.delete(`/transactions/${id}`)
}

// 导出交易记录为CSV
export const exportTransactionsCSV = async (params?: { start_date?: string; end_date?: string }) => {
  const response = await api.get('/transactions/export/csv', {
    params,
    responseType: 'blob'
  })

  // 创建下载链接
  const blob = new Blob([response as any], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `账单_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
