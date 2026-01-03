<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import VoiceRecorder from '@/components/record/VoiceRecorder.vue'
import PhotoScanner from '@/components/record/PhotoScanner.vue'
import ManualForm from '@/components/record/ManualForm.vue'
import AIAssistant from '@/components/ai/AIAssistant.vue'

type TabType = 'voice' | 'photo' | 'manual' | 'ai'

const route = useRoute()
const activeTab = ref<TabType>('manual')

const tabs = [
  { key: 'voice', label: '语音', icon: '🎤' },
  { key: 'photo', label: '拍照', icon: '📷' },
  { key: 'manual', label: '手动', icon: '✏️' },
  { key: 'ai', label: 'AI', icon: '✨' }
]

// 监听路由参数变化
onMounted(() => {
  const tab = route.query.tab as TabType
  if (tab && tabs.some(t => t.key === tab)) {
    activeTab.value = tab
  }
})

watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.some(t => t.key === newTab)) {
    activeTab.value = newTab as TabType
  }
})
</script>

<template>
  <div class="add-record-page">
    <!-- 切换标签 -->
    <div class="tabs-container bg-white rounded-2xl p-1 flex gap-1 shadow-card">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key as TabType"
        class="tab-btn flex-1 py-2.5 px-3 rounded-xl text-sm font-medium transition-all duration-200"
        :class="activeTab === tab.key ? 'bg-primary-500 text-white shadow-cute' : 'text-gray-500 hover:bg-gray-50'"
      >
        <span class="mr-1">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- 内容区域 -->
    <div class="content-area mt-4">
      <transition name="slide-fade" mode="out-in">
        <VoiceRecorder v-if="activeTab === 'voice'" key="voice" />
        <PhotoScanner v-else-if="activeTab === 'photo'" key="photo" />
        <ManualForm v-else-if="activeTab === 'manual'" key="manual" />
        <AIAssistant v-else-if="activeTab === 'ai'" key="ai" />
      </transition>
    </div>
  </div>
</template>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
