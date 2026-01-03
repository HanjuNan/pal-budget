<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { parseVoiceText } from '@/api/ai'
import { useTransactionStore } from '@/stores/transaction'

const router = useRouter()
const transactionStore = useTransactionStore()

const isRecording = ref(false)
const recordedText = ref('')
const isProcessing = ref(false)
const parseResult = ref<any>(null)
const successMessage = ref('')

const startRecording = () => {
  isRecording.value = true
  recordedText.value = ''
  parseResult.value = null

  // 检查浏览器支持
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

  if (!SpeechRecognition) {
    alert('您的浏览器不支持语音识别功能，请使用 Chrome 浏览器')
    isRecording.value = false
    return
  }

  const recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = false

  recognition.onresult = (event: any) => {
    recordedText.value = event.results[0][0].transcript
    isRecording.value = false
    processVoiceText(recordedText.value)
  }

  recognition.onerror = (e: any) => {
    isRecording.value = false
    console.error('语音识别错误:', e)
    alert('语音识别出错，请重试')
  }

  recognition.onend = () => {
    isRecording.value = false
  }

  recognition.start()
}

const stopRecording = () => {
  isRecording.value = false
}

const processVoiceText = async (text: string) => {
  isProcessing.value = true
  try {
    const result = await parseVoiceText(text)
    parseResult.value = result
  } catch (e) {
    console.error('解析失败:', e)
    alert('解析失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const confirmAdd = async () => {
  if (!parseResult.value) return

  isProcessing.value = true
  try {
    await transactionStore.addTransaction({
      type: parseResult.value.type,
      amount: parseResult.value.amount,
      category: parseResult.value.category,
      description: parseResult.value.description || recordedText.value,
      date: new Date().toISOString().split('T')[0],
      source: 'voice'
    })

    successMessage.value = '添加成功！'
    setTimeout(() => {
      successMessage.value = ''
      router.push('/')
    }, 1500)
  } catch (e) {
    alert('添加失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const resetForm = () => {
  recordedText.value = ''
  parseResult.value = null
}
</script>

<template>
  <div class="voice-recorder">
    <!-- 成功提示 -->
    <div
      v-if="successMessage"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-income text-white rounded-full shadow-lg flex items-center gap-2"
    >
      <span>✓</span>
      {{ successMessage }}
    </div>

    <div class="bg-white rounded-2xl p-6 shadow-card text-center">
      <!-- 录音按钮 -->
      <div class="flex flex-col items-center">
        <button
          @mousedown="startRecording"
          @mouseup="stopRecording"
          @touchstart.prevent="startRecording"
          @touchend.prevent="stopRecording"
          class="record-btn w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300"
          :class="isRecording ? 'bg-red-500 scale-110 animate-pulse' : 'bg-primary-500 hover:bg-primary-600'"
        >
          <svg v-if="!isRecording" class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          <div v-else class="flex gap-1">
            <span class="w-1 h-6 bg-white rounded-full animate-bounce"></span>
            <span class="w-1 h-6 bg-white rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
            <span class="w-1 h-6 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
          </div>
        </button>

        <p class="mt-4 text-gray-500">
          {{ isRecording ? '正在聆听...' : '按住说话' }}
        </p>
        <p class="text-sm text-gray-400 mt-1">
          例如："今天午餐花了25元"
        </p>
      </div>

      <!-- 识别结果 -->
      <div v-if="recordedText" class="mt-6 p-4 bg-gray-50 rounded-xl text-left">
        <p class="text-sm text-gray-500 mb-1">识别结果：</p>
        <p class="text-gray-800 font-medium">{{ recordedText }}</p>
      </div>

      <!-- 处理中 -->
      <div v-if="isProcessing" class="mt-4 flex items-center justify-center gap-2 text-primary-500">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <span>AI 正在解析...</span>
      </div>

      <!-- 解析结果 -->
      <div v-if="parseResult && !isProcessing" class="mt-4 p-4 bg-primary-50 rounded-xl text-left">
        <p class="text-sm text-primary-600 mb-3 font-medium">AI 解析结果：</p>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-500">类型</span>
            <span class="font-medium" :class="parseResult.type === 'income' ? 'text-income' : 'text-expense'">
              {{ parseResult.type === 'income' ? '收入' : '支出' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">金额</span>
            <span class="font-bold" :class="parseResult.type === 'income' ? 'text-income' : 'text-expense'">
              ¥{{ parseResult.amount.toFixed(2) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">分类</span>
            <span class="font-medium text-gray-800">{{ parseResult.category }}</span>
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <button
            @click="resetForm"
            class="flex-1 py-2 border border-gray-200 text-gray-600 rounded-xl font-medium"
          >
            重新录入
          </button>
          <button
            @click="confirmAdd"
            class="flex-1 py-2 bg-primary-500 text-white rounded-xl font-medium btn-cute"
          >
            确认添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
