<script setup lang="ts">
import { ref, onMounted, onActivated } from 'vue'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { exportTransactionsCSV } from '@/api/transaction'
import { showToast } from '@/utils/toast'

defineOptions({
  name: 'Profile'
})

const userStore = useUserStore()
const themeStore = useThemeStore()
const exporting = ref(false)

const menuItems = [
  { icon: '📄', label: '导出账单', desc: '导出为CSV文件', action: 'export' },
  { icon: '❓', label: '帮助', desc: '使用指南', action: 'help' },
  { icon: '⭐', label: '给个好评', desc: '支持我们', action: 'rate' }
]

const handleMenuClick = async (action: string) => {
  if (action === 'export') {
    await handleExport()
  } else if (action === 'help') {
    showToast('帮助文档开发中~', 'info')
  } else if (action === 'rate') {
    showToast('感谢您的支持！', 'success')
  }
}

const handleExport = async () => {
  if (exporting.value) return

  exporting.value = true
  try {
    await exportTransactionsCSV()
    showToast('导出成功！', 'success')
  } catch (error) {
    showToast('导出失败，请重试', 'error')
    console.error('Export error:', error)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  userStore.initUser()
})

onActivated(() => {
  userStore.initUser()
})
</script>

<template>
  <div class="profile-page space-y-4">
    <!-- 用户信息卡片 -->
    <div class="user-card bg-white rounded-2xl p-6 shadow-card">
      <div class="flex flex-col items-center">
        <!-- 头像 -->
        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-200 via-orange-200 to-green-200 flex items-center justify-center shadow-lg">
          <span class="text-4xl">😊</span>
        </div>

        <!-- 昵称和天数 -->
        <h2 class="mt-3 text-xl font-bold text-gray-800">
          {{ userStore.user?.nickname || '记账小达人' }}
        </h2>
        <p class="text-sm text-gray-400">已坚持记账 {{ userStore.stats.days }} 天</p>
      </div>

      <!-- 统计数据 -->
      <div class="stats-row flex justify-around mt-6 pt-4 border-t border-gray-100">
        <div class="stat-item text-center">
          <p class="text-2xl font-bold text-primary-500">{{ userStore.stats.total_records }}</p>
          <p class="text-xs text-gray-400 mt-1">总记录</p>
        </div>
        <div class="stat-item text-center">
          <p class="text-2xl font-bold text-income">
            ¥{{ (userStore.stats.total_income / 1000).toFixed(1) }}k
          </p>
          <p class="text-xs text-gray-400 mt-1">总收入</p>
        </div>
        <div class="stat-item text-center">
          <p class="text-2xl font-bold text-expense">
            ¥{{ (userStore.stats.total_expense / 1000).toFixed(1) }}k
          </p>
          <p class="text-xs text-gray-400 mt-1">总支出</p>
        </div>
      </div>
    </div>

    <!-- 外观设置 -->
    <div class="bg-white rounded-2xl shadow-card overflow-hidden">
      <div class="flex items-center justify-between p-4">
        <div class="flex items-center gap-3">
          <span class="w-10 h-10 rounded-xl bg-cute-lavender flex items-center justify-center text-xl">
            {{ themeStore.isDark ? '🌙' : '☀️' }}
          </span>
          <div class="text-left">
            <p class="font-medium text-gray-800">深色模式</p>
            <p class="text-xs text-gray-400">{{ themeStore.isDark ? '已开启' : '已关闭' }}</p>
          </div>
        </div>
        <!-- 切换开关 -->
        <button
          @click="themeStore.toggleDark()"
          class="relative w-12 h-7 rounded-full transition-colors duration-300"
          :class="themeStore.isDark ? 'bg-primary-500' : 'bg-gray-200'"
        >
          <span
            class="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow transition-transform duration-300"
            :class="themeStore.isDark ? 'translate-x-5' : 'translate-x-0'"
          ></span>
        </button>
      </div>
    </div>

    <!-- 菜单列表 -->
    <div class="menu-list bg-white rounded-2xl shadow-card overflow-hidden">
      <button
        v-for="item in menuItems"
        :key="item.action"
        @click="handleMenuClick(item.action)"
        class="menu-item w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-b-0"
        :disabled="item.action === 'export' && exporting"
      >
        <div class="flex items-center gap-3">
          <span class="w-10 h-10 rounded-xl bg-cute-mint flex items-center justify-center text-xl">
            <template v-if="item.action === 'export' && exporting">
              <span class="loading-spinner"></span>
            </template>
            <template v-else>
              {{ item.icon }}
            </template>
          </span>
          <div class="text-left">
            <p class="font-medium text-gray-800">
              {{ item.action === 'export' && exporting ? '导出中...' : item.label }}
            </p>
            <p class="text-xs text-gray-400">{{ item.desc }}</p>
          </div>
        </div>
        <svg class="w-5 h-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <!-- 版本信息 -->
    <div class="text-center py-4">
      <p class="text-sm text-gray-300">🐷 可爱记账 v1.0.0</p>
    </div>
  </div>
</template>

<style scoped>
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e8e8e8;
  border-top-color: #14b8a6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
