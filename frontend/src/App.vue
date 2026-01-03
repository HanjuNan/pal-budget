<script setup lang="ts">
import TabNavigation from '@/components/layout/TabNavigation.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <div class="app-container min-h-screen bg-gray-50 pb-20 md:pb-0">
    <!-- 顶部标题栏 -->
    <AppHeader />

    <!-- 主内容区域 -->
    <main class="main-content px-4 pt-2">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <keep-alive :include="['Home', 'Statistics', 'Profile']">
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </main>

    <!-- 底部导航 -->
    <TabNavigation />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
