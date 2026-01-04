import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getTransactions,
  createTransaction,
  deleteTransaction,
  type Transaction,
  type TransactionQuery
} from '@/api/transaction'
import { getMonthlyStats, getCategoryStats, getTrendStats, type MonthlyStats, type CategoryStats, type TrendData } from '@/api/statistics'

export const useTransactionStore = defineStore('transaction', () => {
  // 状态
  const transactions = ref<Transaction[]>([])
  const monthlyStats = ref<MonthlyStats>({
    balance: 0,
    income: 0,
    expense: 0,
    transaction_count: 0
  })
  const categoryStats = ref<CategoryStats[]>([])
  const trendData = ref<TrendData>({
    dates: [],
    expense: [],
    income: []
  })
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const recentTransactions = computed(() => {
    return transactions.value.slice(0, 10)
  })

  const hasTransactions = computed(() => {
    return transactions.value.length > 0
  })

  // 获取交易列表
  const fetchTransactions = async (params?: TransactionQuery) => {
    loading.value = true
    error.value = null
    try {
      const data = await getTransactions(params)
      // 使用新数组替换，确保 Vue 响应式更新
      transactions.value = [...data]
    } catch (e: any) {
      error.value = e.message || '获取数据失败'
      console.error('获取交易列表失败:', e)
    } finally {
      loading.value = false
    }
  }

  // 获取月度统计
  const fetchMonthlyStats = async (year?: number, month?: number) => {
    try {
      monthlyStats.value = await getMonthlyStats(year, month)
    } catch (e) {
      console.error('获取月度统计失败:', e)
    }
  }

  // 获取分类统计
  const fetchCategoryStats = async (type: 'income' | 'expense' = 'expense', year?: number, month?: number) => {
    try {
      categoryStats.value = await getCategoryStats(type, year, month)
    } catch (e) {
      console.error('获取分类统计失败:', e)
    }
  }

  // 获取趋势数据
  const fetchTrendData = async (days: number = 7) => {
    try {
      trendData.value = await getTrendStats(days)
    } catch (e) {
      console.error('获取趋势数据失败:', e)
    }
  }

  // 添加交易
  const addTransaction = async (data: Omit<Transaction, 'id' | 'created_at'>) => {
    loading.value = true
    try {
      const newTransaction = await createTransaction(data)
      // 刷新所有数据（确保列表和统计都是最新的）
      await Promise.all([
        fetchTransactions({ limit: 50 }),
        fetchMonthlyStats(),
        fetchCategoryStats(),
        fetchTrendData()
      ])
      return newTransaction
    } catch (e: any) {
      error.value = e.message || '添加失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  // 删除交易
  const removeTransaction = async (id: number) => {
    try {
      await deleteTransaction(id)
      transactions.value = transactions.value.filter(t => t.id !== id)
      await fetchMonthlyStats()
    } catch (e) {
      console.error('删除失败:', e)
      throw e
    }
  }

  // 初始化数据
  const initData = async () => {
    // 串行执行以确保数据一致性
    try {
      await fetchTransactions({ limit: 50 })
      await fetchMonthlyStats()
      await fetchCategoryStats()
      await fetchTrendData()
    } catch (e) {
      console.error('初始化数据失败:', e)
    }
  }

  // 强制刷新所有数据
  const refreshAllData = async () => {
    loading.value = true
    try {
      await fetchTransactions({ limit: 50 })
      await fetchMonthlyStats()
      await fetchCategoryStats()
      await fetchTrendData()
    } catch (e) {
      console.error('刷新数据失败:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    transactions,
    monthlyStats,
    categoryStats,
    trendData,
    loading,
    error,
    // 计算属性
    recentTransactions,
    hasTransactions,
    // 方法
    fetchTransactions,
    fetchMonthlyStats,
    fetchCategoryStats,
    fetchTrendData,
    addTransaction,
    removeTransaction,
    initData,
    refreshAllData
  }
})
