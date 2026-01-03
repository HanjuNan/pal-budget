<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { chatWithAI, getAIConfig } from '@/api/ai'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputText = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const aiConfigured = ref(false)
const aiModel = ref('')
const ollamaMode = ref(false)

const quickActions = [
  { label: '本月花费分析', icon: '📊' },
  { label: '省钱建议', icon: '💡' },
  { label: '理财建议', icon: '📈' },
  { label: '如何存钱', icon: '💰' }
]

onMounted(async () => {
  try {
    const config = await getAIConfig()
    aiConfigured.value = config.configured
    aiModel.value = config.model || ''
    ollamaMode.value = !!(config.use_ollama && config.ollama_available)
  } catch (e) {
    console.error('Failed to get AI config:', e)
  }
})

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const getHistory = () => {
  return messages.value.map(m => ({
    role: m.role,
    content: m.content
  }))
}

const sendMessage = async (text?: string) => {
  const content = text || inputText.value.trim()
  if (!content || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content
  })

  inputText.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const response = await chatWithAI(content, getHistory().slice(0, -1))
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: response.reply
    })
  } catch (e) {
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，请稍后再试~ 🐷'
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const handleQuickAction = (label: string) => {
  sendMessage(label)
}

const clearChat = () => {
  messages.value = []
}
</script>

<template>
  <div class="ai-assistant flex flex-col h-[60vh]">
    <!-- 聊天区域 -->
    <div
      ref="chatContainer"
      class="chat-container flex-1 bg-white rounded-2xl p-4 shadow-card overflow-y-auto"
    >
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome text-center py-8">
        <div class="inline-block px-4 py-2 bg-cute-pink rounded-full text-primary-600 font-medium mb-3">
          ✨ AI理财助手
        </div>
        <p class="text-gray-500 mb-2">我是小猪，可以帮你分析消费、提供理财建议~</p>
        <p v-if="!aiConfigured" class="text-xs text-gray-400">
          (预设回复模式 - 安装 Ollama 可启用 AI)
        </p>
        <p v-else-if="ollamaMode" class="text-xs text-primary-500">
          🤖 Ollama 本地 AI ({{ aiModel }})
        </p>
        <p v-else class="text-xs text-primary-500">
          🤖 AI 已启用 ({{ aiModel }})
        </p>

        <!-- 快捷操作 -->
        <div class="quick-actions flex flex-wrap justify-center gap-2 mt-4">
          <button
            v-for="action in quickActions"
            :key="action.label"
            @click="handleQuickAction(action.label)"
            class="px-4 py-2 bg-gray-50 rounded-full text-sm text-gray-600 hover:bg-primary-50 hover:text-primary-600 transition-all"
          >
            {{ action.icon }} {{ action.label }}
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages space-y-4">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <!-- AI头像 -->
          <div v-if="msg.role === 'assistant'" class="flex-shrink-0 mr-2">
            <span class="w-8 h-8 rounded-full bg-cute-pink flex items-center justify-center text-sm">🐷</span>
          </div>

          <div
            class="max-w-[75%] px-4 py-2 rounded-2xl whitespace-pre-wrap"
            :class="msg.role === 'user'
              ? 'bg-primary-500 text-white rounded-br-sm'
              : 'bg-gray-100 text-gray-800 rounded-bl-sm'"
          >
            {{ msg.content }}
          </div>

          <!-- 用户头像 -->
          <div v-if="msg.role === 'user'" class="flex-shrink-0 ml-2">
            <span class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-sm">😊</span>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="isLoading" class="message flex justify-start">
          <div class="flex-shrink-0 mr-2">
            <span class="w-8 h-8 rounded-full bg-cute-pink flex items-center justify-center text-sm">🐷</span>
          </div>
          <div class="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-1">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 清空按钮 -->
    <div v-if="messages.length > 0" class="flex justify-center mt-2">
      <button
        @click="clearChat"
        class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
      >
        清空对话
      </button>
    </div>

    <!-- 输入区域 -->
    <div class="input-area mt-3 flex gap-2">
      <input
        v-model="inputText"
        @keyup.enter="sendMessage()"
        type="text"
        placeholder="问我任何理财问题..."
        class="flex-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none focus:border-primary-400"
      />
      <button
        @click="sendMessage()"
        :disabled="!inputText.trim() || isLoading"
        class="px-4 py-3 bg-primary-500 text-white rounded-xl btn-cute disabled:opacity-50"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </div>
  </div>
</template>
