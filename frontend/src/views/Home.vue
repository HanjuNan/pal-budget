<script setup lang="ts">
import { ref, onMounted, onActivated } from 'vue'
import { useTransactionStore } from '@/stores/transaction'
import SummaryCard from '@/components/common/SummaryCard.vue'
import QuickActions from '@/components/common/QuickActions.vue'
import RecentTransactions from '@/components/common/RecentTransactions.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import PullRefresh from '@/components/common/PullRefresh.vue'

defineOptions({
  name: 'Home'
})

const transactionStore = useTransactionStore()
const refreshing = ref(false)
const initialLoading = ref(true)

const loadData = async () => {
  try {
    await transactionStore.initData()
  } catch (e) {
    console.error('加载数据失败:', e)
  }
}

const handleRefresh = async () => {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

onMounted(async () => {
  await loadData()
  initialLoading.value = false
})

// 当从其他页面返回时刷新数据
onActivated(async () => {
  // 确保每次激活时都刷新数据
  await loadData()
  initialLoading.value = false
})
</script>

<template>
  <PullRefresh @refresh="handleRefresh" :loading="refreshing">
    <div class="home-page space-y-4 pb-4">
      <!-- 骨架屏 -->
      <template v-if="initialLoading">
        <Skeleton type="card" />
        <div class="bg-white rounded-2xl p-4 shadow-card">
          <div class="grid grid-cols-4 gap-4">
            <div v-for="i in 4" :key="i" class="flex flex-col items-center">
              <div class="skeleton-circle w-12 h-12 mb-2"></div>
              <div class="skeleton-line w-10 h-3"></div>
            </div>
          </div>
        </div>
        <Skeleton type="list" :rows="5" />
      </template>

      <!-- 实际内容 -->
      <template v-else>
        <!-- 本月账单卡片 -->
        <SummaryCard :stats="transactionStore.monthlyStats" />

        <!-- 快捷操作入口 -->
        <QuickActions />

        <!-- 最近交易记录 -->
        <RecentTransactions
          :transactions="transactionStore.recentTransactions"
          :loading="transactionStore.loading"
        />
      </template>
    </div>
  </PullRefresh>
</template>

<style scoped>
.skeleton-circle,
.skeleton-line {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-circle {
  border-radius: 50%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
