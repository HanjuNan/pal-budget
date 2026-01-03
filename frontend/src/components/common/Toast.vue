<script setup lang="ts">
import { ref } from 'vue'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

const toasts = ref<Toast[]>([])

const addToast = (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) => {
  const id = Date.now()
  toasts.value.push({ id, message, type })

  setTimeout(() => {
    removeToast(id)
  }, duration)
}

const removeToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// 暴露方法给外部使用
defineExpose({ addToast })

const getIcon = (type: string) => {
  switch (type) {
    case 'success': return '✓'
    case 'error': return '✕'
    default: return 'ℹ'
  }
}

const getClass = (type: string) => {
  switch (type) {
    case 'success': return 'bg-income'
    case 'error': return 'bg-expense'
    default: return 'bg-primary-500'
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container fixed top-20 left-1/2 -translate-x-1/2 z-[100] space-y-2">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="getClass(toast.type)"
          class="toast-item px-5 py-3 text-white rounded-full shadow-lg flex items-center gap-2 min-w-[200px] justify-center"
        >
          <span class="text-lg">{{ getIcon(toast.type) }}</span>
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}
</style>
