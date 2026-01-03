<script setup lang="ts">
import { computed } from 'vue'
import type { Transaction } from '@/api/transaction'

const props = defineProps<{
  transactions: Transaction[]
  loading?: boolean
}>()

const isEmpty = computed(() => props.transactions.length === 0)

const getCategoryIcon = (category: string): string => {
  const icons: Record<string, string> = {
    '餐饮': '🍜',
    '交通': '🚗',
    '购物': '🛒',
    '住房': '🏠',
    '娱乐': '🎮',
    '医疗': '💊',
    '教育': '📚',
    '通讯': '📱',
    '服饰': '👔',
    '旅行': '✈️',
    '礼物': '🎁',
    '工资': '💰',
    '奖金': '🎁',
    '投资': '📈',
    '兼职': '💸',
    '利息': '🏦'
  }
  return icons[category] || '📦'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<template>
  <div class="recent-transactions bg-white rounded-2xl p-4 shadow-card">
    <h3 class="font-bold text-gray-800 mb-3">最近记录</h3>

    <!-- 加载中 -->
    <div v-if="loading" class="py-8 flex justify-center">
      <div class="w-8 h-8 border-3 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="isEmpty" class="empty-state py-8 flex flex-col items-center">
      <span class="text-5xl mb-3">🌸</span>
      <p class="text-gray-400">还没有记录哦~</p>
      <p class="text-sm text-gray-300">快去记一笔吧！</p>
    </div>

    <!-- 交易列表 -->
    <div v-else class="transaction-list space-y-3">
      <div
        v-for="item in transactions"
        :key="item.id"
        class="transaction-item flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">{{ getCategoryIcon(item.category) }}</span>
          <div>
            <p class="font-medium text-gray-800">{{ item.category }}</p>
            <p class="text-xs text-gray-400">{{ item.description || formatDate(item.date) }}</p>
          </div>
        </div>
        <span
          class="font-bold"
          :class="item.type === 'income' ? 'text-income' : 'text-expense'"
        >
          {{ item.type === 'income' ? '+' : '-' }}¥{{ item.amount.toFixed(2) }}
        </span>
      </div>
    </div>
  </div>
</template>
