<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'Home', path: '/', label: '首页', icon: 'home' },
  { name: 'AddRecord', path: '/add', label: '记账', icon: 'add' },
  { name: 'Statistics', path: '/statistics', label: '统计', icon: 'chart' },
  { name: 'Profile', path: '/profile', label: '我的', icon: 'user' }
]

const currentTab = computed(() => route.name)

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <nav class="tab-navigation fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 safe-area-bottom md:hidden">
    <div class="flex items-center justify-around h-16">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="navigateTo(tab.path)"
        class="tab-item flex flex-col items-center justify-center flex-1 h-full btn-cute"
        :class="{ 'active': currentTab === tab.name }"
      >
        <!-- 首页图标 -->
        <template v-if="tab.icon === 'home'">
          <svg class="w-6 h-6" :class="currentTab === tab.name ? 'text-primary-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </template>

        <!-- 记账图标 - 特殊样式 -->
        <template v-else-if="tab.icon === 'add'">
          <div
            class="w-12 h-12 -mt-4 rounded-full flex items-center justify-center shadow-lg transition-all"
            :class="currentTab === tab.name ? 'bg-primary-500' : 'bg-primary-400'"
          >
            <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
            </svg>
          </div>
        </template>

        <!-- 统计图标 -->
        <template v-else-if="tab.icon === 'chart'">
          <svg class="w-6 h-6" :class="currentTab === tab.name ? 'text-primary-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </template>

        <!-- 我的图标 -->
        <template v-else-if="tab.icon === 'user'">
          <svg class="w-6 h-6" :class="currentTab === tab.name ? 'text-primary-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </template>

        <span
          class="text-xs mt-1"
          :class="[
            currentTab === tab.name ? 'text-primary-500 font-semibold' : 'text-gray-400',
            tab.icon === 'add' ? 'mt-0' : ''
          ]"
        >
          {{ tab.label }}
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.tab-item {
  position: relative;
}

.tab-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: linear-gradient(90deg, #5eead4, #14b8a6);
  border-radius: 0 0 4px 4px;
}

.tab-item:nth-child(2).active::before {
  display: none;
}
</style>
