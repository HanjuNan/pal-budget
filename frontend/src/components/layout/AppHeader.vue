<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

const currentDate = computed(() => {
  return dayjs().format('YYYY年M月')
})
</script>

<template>
  <header class="app-header sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-100">
    <div class="flex items-center justify-between px-4 py-3">
      <!-- 左侧 Logo 和日期 -->
      <div class="flex items-center gap-2">
        <span class="text-2xl">✨</span>
        <div>
          <h1 class="text-lg font-bold text-gray-800">可爱记账</h1>
          <p class="text-xs text-gray-400">{{ currentDate }}</p>
        </div>
      </div>

      <!-- 右侧头像 -->
      <div class="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-200 to-orange-300 flex items-center justify-center shadow-sm">
        <span class="text-xl">😊</span>
      </div>
    </div>
  </header>
</template>
