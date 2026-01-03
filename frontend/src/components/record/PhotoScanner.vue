<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { scanReceipt } from '@/api/ai'
import { useTransactionStore } from '@/stores/transaction'

const router = useRouter()
const transactionStore = useTransactionStore()

const imagePreview = ref('')
const imageFile = ref<File | null>(null)
const isProcessing = ref(false)
const processingText = ref('正在识别...')
const scanResult = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const dateInputRef = ref<HTMLInputElement | null>(null)
const successMessage = ref('')
const errorMessage = ref('')

// 打开日期选择器 (兼容 Firefox)
const openDatePicker = () => {
  if (dateInputRef.value) {
    if (typeof dateInputRef.value.showPicker === 'function') {
      dateInputRef.value.showPicker()
    } else {
      dateInputRef.value.focus()
      dateInputRef.value.click()
    }
  }
}

// 获取今天的日期 (YYYY-MM-DD 格式)
const getTodayDate = () => {
  return new Date().toISOString().split('T')[0]
}

// 验证并修正日期格式
const validateAndFixDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) {
    return getTodayDate()
  }

  // 检查是否是有效的 YYYY-MM-DD 格式
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    return dateStr
  }

  // 检查是否是 YYYY/MM/DD 格式，转换为 YYYY-MM-DD
  if (/^\d{4}\/\d{2}\/\d{2}$/.test(dateStr)) {
    return dateStr.replace(/\//g, '-')
  }

  // 尝试解析其他日期格式
  try {
    const date = new Date(dateStr)
    if (!isNaN(date.getTime())) {
      return date.toISOString().split('T')[0]
    }
  } catch (e) {
    // 解析失败
  }

  // 如果都不匹配，使用今天的日期
  console.log(`日期格式无效 "${dateStr}"，使用今天日期`)
  return getTodayDate()
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    imageFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
      processImage(file)
    }
    reader.readAsDataURL(file)
  }
}

const processImage = async (file: File) => {
  isProcessing.value = true
  processingText.value = '正在压缩图片...'
  errorMessage.value = ''

  try {
    processingText.value = '正在识别...'

    const result = await scanReceipt(file)

    if (result.success && result.data) {
      // 立即验证和修正日期
      const validDate = validateAndFixDate(result.data.date)

      scanResult.value = {
        amount: result.data.amount || 0,
        merchant: result.data.merchant || '',
        date: validDate,
        category: result.data.category || '购物'
      }

      if (result.data.amount > 0) {
        console.log('AI识别成功:', result.data, '-> 使用日期:', validDate)
      } else {
        errorMessage.value = '未识别到金额，请手动输入'
      }
    } else {
      // 回退到手动输入
      scanResult.value = {
        amount: 0,
        merchant: '',
        date: getTodayDate(),
        category: '购物'
      }
      errorMessage.value = result.message || '请手动输入金额'
    }
  } catch (e: any) {
    console.error('扫描失败:', e)
    scanResult.value = {
      amount: 0,
      merchant: '',
      date: getTodayDate(),
      category: '购物'
    }

    // 更友好的错误提示
    if (e.code === 'ECONNABORTED' || e.message?.includes('timeout')) {
      errorMessage.value = '识别超时，请重试或手动输入'
    } else if (e.message?.includes('Network Error')) {
      errorMessage.value = '网络错误，请检查网络连接'
    } else {
      errorMessage.value = '识别失败，请手动输入'
    }
  } finally {
    isProcessing.value = false
  }
}

const clearImage = () => {
  imagePreview.value = ''
  imageFile.value = null
  scanResult.value = null
  errorMessage.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const confirmAdd = async () => {
  if (!scanResult.value || scanResult.value.amount <= 0) {
    errorMessage.value = '请输入有效金额'
    return
  }

  isProcessing.value = true
  processingText.value = '正在保存...'

  try {
    // 确保日期格式正确
    const dateStr = validateAndFixDate(scanResult.value.date)

    await transactionStore.addTransaction({
      type: 'expense',
      amount: scanResult.value.amount,
      category: scanResult.value.category,
      description: scanResult.value.merchant || '扫描录入',
      date: dateStr,
      source: 'photo'
    })

    successMessage.value = '添加成功！'

    // 等待一会儿让用户看到成功消息，然后导航回首页
    setTimeout(() => {
      successMessage.value = ''
      router.replace('/')
    }, 800)
  } catch (e) {
    console.error('添加失败:', e)
    errorMessage.value = '添加失败，请重试'
    isProcessing.value = false
  }
}

const categories = [
  { icon: '🍜', name: '餐饮' },
  { icon: '🛒', name: '购物' },
  { icon: '🚗', name: '交通' },
  { icon: '🎮', name: '娱乐' },
  { icon: '📦', name: '其他' }
]

const selectCategory = (name: string) => {
  if (scanResult.value) {
    scanResult.value.category = name
  }
}
</script>

<template>
  <div class="photo-scanner">
    <!-- 成功提示 -->
    <div
      v-if="successMessage"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-income text-white rounded-full shadow-lg flex items-center gap-2"
    >
      <span>✓</span>
      {{ successMessage }}
    </div>

    <div class="bg-white rounded-2xl p-6 shadow-card">
      <!-- 上传区域 -->
      <div
        v-if="!imagePreview"
        @click="triggerFileInput"
        class="upload-area border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition-all"
      >
        <div class="flex flex-col items-center">
          <div class="w-16 h-16 bg-cute-lavender rounded-full flex items-center justify-center mb-3">
            <span class="text-3xl">📷</span>
          </div>
          <p class="text-gray-600 font-medium">点击拍照或上传图片</p>
          <p class="text-sm text-gray-400 mt-1">支持小票、发票、账单截图</p>
        </div>
      </div>

      <!-- 图片预览和结果 -->
      <div v-else class="preview-area">
        <div class="relative">
          <img
            :src="imagePreview"
            alt="Preview"
            class="w-full rounded-xl object-cover max-h-48"
          />
          <button
            @click="clearImage"
            class="absolute top-2 right-2 w-8 h-8 bg-black/50 rounded-full flex items-center justify-center text-white hover:bg-black/70"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 处理中 -->
        <div v-if="isProcessing" class="mt-4 flex items-center justify-center gap-2 text-primary-500">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <span>{{ processingText }}</span>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="mt-3 p-3 bg-orange-50 text-orange-600 rounded-lg text-sm">
          {{ errorMessage }}
        </div>

        <!-- 识别/编辑结果 -->
        <div v-if="scanResult && !isProcessing" class="mt-4 space-y-4">
          <!-- 金额输入 -->
          <div>
            <label class="text-sm text-gray-500 mb-1 block">金额</label>
            <div class="flex items-center gap-2">
              <span class="text-xl text-gray-400">¥</span>
              <input
                v-model.number="scanResult.amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                class="flex-1 text-2xl font-bold text-expense outline-none bg-gray-50 rounded-lg px-3 py-2"
              />
            </div>
          </div>

          <!-- 商家/备注 -->
          <div>
            <label class="text-sm text-gray-500 mb-1 block">商家/备注</label>
            <input
              v-model="scanResult.merchant"
              type="text"
              placeholder="输入商家名称..."
              class="w-full px-3 py-2 bg-gray-50 rounded-lg outline-none"
            />
          </div>

          <!-- 分类选择 -->
          <div>
            <label class="text-sm text-gray-500 mb-2 block">分类</label>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="cat in categories"
                :key="cat.name"
                @click="selectCategory(cat.name)"
                class="px-3 py-1.5 rounded-full text-sm flex items-center gap-1 transition-all"
                :class="scanResult.category === cat.name
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
              >
                <span>{{ cat.icon }}</span>
                {{ cat.name }}
              </button>
            </div>
          </div>

          <!-- 日期 -->
          <div class="relative">
            <label class="text-sm text-gray-500 mb-1 block">日期</label>
            <div class="relative" @click="openDatePicker">
              <input
                ref="dateInputRef"
                v-model="scanResult.date"
                type="date"
                class="w-full px-3 py-3 bg-gray-50 rounded-lg border border-gray-200 focus:border-primary-400 focus:outline-none cursor-pointer text-base"
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 cursor-pointer">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- 确认按钮 -->
          <button
            @click="confirmAdd"
            :disabled="isProcessing"
            class="w-full py-3 bg-primary-500 text-white rounded-xl font-bold btn-cute disabled:opacity-50"
          >
            确认添加
          </button>
        </div>
      </div>

      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        capture="environment"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>
  </div>
</template>

<style scoped>
/* 确保日期选择器在所有浏览器上可点击 */
input[type="date"] {
  position: relative;
  min-height: 44px; /* 确保足够的点击区域 */
}

/* 在 WebKit 浏览器上显示日历图标 */
input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 0;
  top: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

/* Firefox 修复 */
input[type="date"]::-moz-calendar-picker-indicator {
  cursor: pointer;
}
</style>
