<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const actions = [
  { icon: '🎤', label: '语音记账', color: 'bg-cute-pink', tab: 'voice' },
  { icon: '📷', label: '拍照记账', color: 'bg-cute-lavender', tab: 'photo' },
  { icon: '✨', label: 'AI助手', color: 'bg-cute-yellow', tab: 'ai' },
  { icon: '✏️', label: '手动记账', color: 'bg-cute-mint', tab: 'manual' }
]

const handleAction = (tab: string) => {
  router.push({ path: '/add', query: { tab } })
}
</script>

<template>
  <div class="quick-actions grid grid-cols-4 gap-3">
    <button
      v-for="action in actions"
      :key="action.tab"
      @click="handleAction(action.tab)"
      class="action-item flex flex-col items-center p-4 bg-white rounded-2xl shadow-card btn-cute card-hover"
    >
      <div
        class="icon-wrapper w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-2"
        :class="action.color"
      >
        {{ action.icon }}
      </div>
      <span class="text-xs text-gray-600 font-medium">{{ action.label }}</span>
    </button>
  </div>
</template>
