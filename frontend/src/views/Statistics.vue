<script setup lang="ts">
import { onMounted, onActivated } from 'vue'
import { useTransactionStore } from '@/stores/transaction'
import SummaryCard from '@/components/common/SummaryCard.vue'
import ExpenseChart from '@/components/stats/ExpenseChart.vue'
import TrendChart from '@/components/stats/TrendChart.vue'

defineOptions({
  name: 'Statistics'
})

const transactionStore = useTransactionStore()

const fetchData = () => {
  transactionStore.fetchMonthlyStats()
  transactionStore.fetchCategoryStats()
  transactionStore.fetchTrendData()
}

onMounted(fetchData)
onActivated(fetchData)
</script>

<template>
  <div class="statistics-page space-y-4">
    <!-- 本月账单卡片 -->
    <SummaryCard :stats="transactionStore.monthlyStats" />

    <!-- 支出分类饼图 -->
    <div class="bg-white rounded-2xl p-4 shadow-card">
      <ExpenseChart :data="transactionStore.categoryStats" />
    </div>

    <!-- 近7天趋势 -->
    <div class="bg-white rounded-2xl p-4 shadow-card">
      <TrendChart :data="transactionStore.trendData" />
    </div>
  </div>
</template>
