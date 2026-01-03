import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCurrentUser, getUserStats, type User, type UserStats } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const stats = ref<UserStats>({
    days: 0,
    total_records: 0,
    total_income: 0,
    total_expense: 0
  })
  const loading = ref(false)

  // 获取当前用户
  const fetchUser = async () => {
    loading.value = true
    try {
      user.value = await getCurrentUser()
    } catch (e) {
      console.error('获取用户信息失败:', e)
    } finally {
      loading.value = false
    }
  }

  // 获取用户统计
  const fetchStats = async () => {
    try {
      stats.value = await getUserStats()
    } catch (e) {
      console.error('获取用户统计失败:', e)
    }
  }

  // 初始化
  const initUser = async () => {
    await Promise.all([fetchUser(), fetchStats()])
  }

  return {
    user,
    stats,
    loading,
    fetchUser,
    fetchStats,
    initUser
  }
})
