<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{
  refresh: []
}>()

const props = defineProps<{
  loading?: boolean
}>()

const container = ref<HTMLElement | null>(null)
const startY = ref(0)
const pullDistance = ref(0)
const isPulling = ref(false)
const threshold = 60

const handleTouchStart = (e: TouchEvent) => {
  if (container.value && container.value.scrollTop === 0) {
    startY.value = e.touches[0].clientY
    isPulling.value = true
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isPulling.value || props.loading) return

  const currentY = e.touches[0].clientY
  const diff = currentY - startY.value

  if (diff > 0) {
    pullDistance.value = Math.min(diff * 0.5, 100)
    if (pullDistance.value > 10) {
      e.preventDefault()
    }
  }
}

const handleTouchEnd = () => {
  if (pullDistance.value >= threshold && !props.loading) {
    emit('refresh')
  }
  pullDistance.value = 0
  isPulling.value = false
}

onMounted(() => {
  const el = container.value
  if (el) {
    el.addEventListener('touchstart', handleTouchStart, { passive: true })
    el.addEventListener('touchmove', handleTouchMove, { passive: false })
    el.addEventListener('touchend', handleTouchEnd, { passive: true })
  }
})

onUnmounted(() => {
  const el = container.value
  if (el) {
    el.removeEventListener('touchstart', handleTouchStart)
    el.removeEventListener('touchmove', handleTouchMove)
    el.removeEventListener('touchend', handleTouchEnd)
  }
})
</script>

<template>
  <div ref="container" class="pull-refresh-container h-full overflow-y-auto">
    <!-- 下拉提示 -->
    <div
      class="pull-indicator flex items-center justify-center transition-all duration-200"
      :style="{ height: pullDistance + 'px', marginTop: '-' + pullDistance + 'px' }"
    >
      <div v-if="loading" class="flex items-center gap-2 text-primary-500">
        <span class="loading-spinner"></span>
        <span class="text-sm">刷新中...</span>
      </div>
      <div v-else-if="pullDistance >= threshold" class="text-primary-500 text-sm">
        松开刷新
      </div>
      <div v-else-if="pullDistance > 0" class="text-gray-400 text-sm">
        继续下拉
      </div>
    </div>

    <!-- 内容区域 -->
    <div
      class="pull-content transition-transform duration-200"
      :style="{ transform: `translateY(${pullDistance}px)` }"
    >
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.pull-refresh-container {
  -webkit-overflow-scrolling: touch;
}

.loading-spinner {
  width: 18px;
  height: 18px;
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
