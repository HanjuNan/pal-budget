<script setup lang="ts">
interface Stats {
  balance: number
  income: number
  expense: number
}

defineProps<{
  stats: Stats
}>()
</script>

<template>
  <div class="summary-card gradient-primary rounded-2xl p-5 text-white shadow-cute">
    <!-- 标题行 -->
    <div class="flex items-center gap-2 mb-3">
      <span class="text-2xl">🐷</span>
      <div>
        <h2 class="font-bold">本月账单</h2>
        <p class="text-xs text-white/70">记录每一笔花销~</p>
      </div>
    </div>

    <!-- 本月结余 -->
    <div class="balance-section bg-white/20 rounded-xl p-3 mb-3">
      <p class="text-sm text-white/80">本月结余</p>
      <p class="text-3xl font-bold mt-1">¥{{ stats.balance.toFixed(2) }}</p>
    </div>

    <!-- 收入/支出 -->
    <div class="flex gap-3">
      <div class="flex-1 bg-white/20 rounded-xl p-3 flex items-center gap-2">
        <div class="w-8 h-8 bg-white/30 rounded-full flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-white/70">收入</p>
          <p class="font-bold">¥{{ stats.income.toFixed(2) }}</p>
        </div>
      </div>

      <div class="flex-1 bg-white/20 rounded-xl p-3 flex items-center gap-2">
        <div class="w-8 h-8 bg-white/30 rounded-full flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6" />
          </svg>
        </div>
        <div>
          <p class="text-xs text-white/70">支出</p>
          <p class="font-bold">¥{{ stats.expense.toFixed(2) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
