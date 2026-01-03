<script setup lang="ts">
defineProps<{
  type?: 'card' | 'list' | 'chart' | 'text'
  rows?: number
}>()
</script>

<template>
  <!-- 卡片骨架 -->
  <div v-if="type === 'card'" class="skeleton-card bg-white rounded-2xl p-4 shadow-card">
    <div class="flex justify-between items-center mb-4">
      <div class="skeleton-line w-24 h-4"></div>
      <div class="skeleton-line w-16 h-4"></div>
    </div>
    <div class="flex justify-around">
      <div class="text-center">
        <div class="skeleton-line w-16 h-6 mx-auto mb-2"></div>
        <div class="skeleton-line w-12 h-3 mx-auto"></div>
      </div>
      <div class="text-center">
        <div class="skeleton-line w-16 h-6 mx-auto mb-2"></div>
        <div class="skeleton-line w-12 h-3 mx-auto"></div>
      </div>
      <div class="text-center">
        <div class="skeleton-line w-16 h-6 mx-auto mb-2"></div>
        <div class="skeleton-line w-12 h-3 mx-auto"></div>
      </div>
    </div>
  </div>

  <!-- 列表骨架 -->
  <div v-else-if="type === 'list'" class="skeleton-list bg-white rounded-2xl shadow-card overflow-hidden">
    <div v-for="i in (rows || 3)" :key="i" class="flex items-center p-4 border-b border-gray-50 last:border-0">
      <div class="skeleton-circle w-10 h-10 mr-3"></div>
      <div class="flex-1">
        <div class="skeleton-line w-24 h-4 mb-2"></div>
        <div class="skeleton-line w-16 h-3"></div>
      </div>
      <div class="skeleton-line w-16 h-5"></div>
    </div>
  </div>

  <!-- 图表骨架 -->
  <div v-else-if="type === 'chart'" class="skeleton-chart bg-white rounded-2xl p-4 shadow-card">
    <div class="skeleton-line w-20 h-4 mb-4"></div>
    <div class="flex items-end justify-center gap-2 h-40">
      <div class="skeleton-bar w-8 h-20"></div>
      <div class="skeleton-bar w-8 h-32"></div>
      <div class="skeleton-bar w-8 h-24"></div>
      <div class="skeleton-bar w-8 h-36"></div>
      <div class="skeleton-bar w-8 h-16"></div>
      <div class="skeleton-bar w-8 h-28"></div>
      <div class="skeleton-bar w-8 h-12"></div>
    </div>
  </div>

  <!-- 文字骨架 -->
  <div v-else class="skeleton-text">
    <div v-for="i in (rows || 3)" :key="i" class="skeleton-line h-4 mb-2" :class="i === (rows || 3) ? 'w-2/3' : 'w-full'"></div>
  </div>
</template>

<style scoped>
.skeleton-line,
.skeleton-circle,
.skeleton-bar {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-circle {
  border-radius: 50%;
}

.skeleton-bar {
  border-radius: 4px 4px 0 0;
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
