<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore } from '@/stores/transaction'

const router = useRouter()
const transactionStore = useTransactionStore()

const dateInputRef = ref<HTMLInputElement | null>(null)

const formData = reactive({
  type: 'expense' as 'income' | 'expense',
  amount: '',
  category: '',
  description: '',
  date: new Date().toISOString().split('T')[0]
})

const expenseCategories = [
  { icon: '🍜', name: '餐饮' },
  { icon: '🚗', name: '交通' },
  { icon: '🛒', name: '购物' },
  { icon: '🏠', name: '住房' },
  { icon: '🎮', name: '娱乐' },
  { icon: '💊', name: '医疗' },
  { icon: '📚', name: '教育' },
  { icon: '📱', name: '通讯' },
  { icon: '👔', name: '服饰' },
  { icon: '✈️', name: '旅行' },
  { icon: '🎁', name: '礼物' },
  { icon: '📦', name: '其他' }
]

const incomeCategories = [
  { icon: '💰', name: '工资' },
  { icon: '🎁', name: '奖金' },
  { icon: '📈', name: '投资' },
  { icon: '💸', name: '兼职' },
  { icon: '🏦', name: '利息' },
  { icon: '📦', name: '其他' }
]

const categories = ref(expenseCategories)

const switchType = (type: 'income' | 'expense') => {
  formData.type = type
  formData.category = ''
  categories.value = type === 'expense' ? expenseCategories : incomeCategories
}

const selectCategory = (name: string) => {
  formData.category = name
}

// 打开日期选择器 (兼容 Firefox)
const openDatePicker = () => {
  if (dateInputRef.value) {
    // 使用 showPicker API (现代浏览器支持)
    if (typeof dateInputRef.value.showPicker === 'function') {
      dateInputRef.value.showPicker()
    } else {
      // 回退方案：聚焦输入框
      dateInputRef.value.focus()
      dateInputRef.value.click()
    }
  }
}

const isSubmitting = ref(false)
const successMessage = ref('')

const handleSubmit = async () => {
  if (!formData.amount || !formData.category) {
    alert('请填写金额和选择分类')
    return
  }

  isSubmitting.value = true

  try {
    await transactionStore.addTransaction({
      type: formData.type,
      amount: parseFloat(formData.amount),
      category: formData.category,
      description: formData.description,
      date: formData.date,
      source: 'manual'
    })

    successMessage.value = '添加成功！'

    // 重置表单
    formData.amount = ''
    formData.category = ''
    formData.description = ''

    // 2秒后清除消息并返回首页
    setTimeout(() => {
      successMessage.value = ''
      router.replace('/')
    }, 1500)

  } catch (e) {
    alert('添加失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="manual-form">
    <!-- 成功提示 -->
    <div
      v-if="successMessage"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-income text-white rounded-full shadow-lg flex items-center gap-2"
    >
      <span>✓</span>
      {{ successMessage }}
    </div>

    <div class="bg-white rounded-2xl p-5 shadow-card space-y-5">
      <!-- 收入/支出切换 -->
      <div class="type-switch flex bg-gray-100 rounded-xl p-1">
        <button
          @click="switchType('expense')"
          class="flex-1 py-2 rounded-lg font-medium transition-all"
          :class="formData.type === 'expense' ? 'bg-expense text-white shadow' : 'text-gray-500'"
        >
          支出
        </button>
        <button
          @click="switchType('income')"
          class="flex-1 py-2 rounded-lg font-medium transition-all"
          :class="formData.type === 'income' ? 'bg-income text-white shadow' : 'text-gray-500'"
        >
          收入
        </button>
      </div>

      <!-- 金额输入 -->
      <div class="amount-input">
        <label class="text-sm text-gray-500 mb-2 block">金额</label>
        <div class="flex items-center gap-2">
          <span class="text-2xl text-gray-400">¥</span>
          <input
            v-model="formData.amount"
            type="number"
            placeholder="0.00"
            class="flex-1 text-3xl font-bold outline-none bg-transparent"
            :class="formData.type === 'expense' ? 'text-expense' : 'text-income'"
          />
        </div>
      </div>

      <!-- 分类选择 -->
      <div class="category-select">
        <label class="text-sm text-gray-500 mb-2 block">分类</label>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="cat in categories"
            :key="cat.name"
            @click="selectCategory(cat.name)"
            class="category-item flex flex-col items-center p-2 rounded-xl transition-all"
            :class="formData.category === cat.name ? 'bg-primary-100 border-2 border-primary-400' : 'bg-gray-50 border-2 border-transparent'"
          >
            <span class="text-xl">{{ cat.icon }}</span>
            <span class="text-xs text-gray-600 mt-1">{{ cat.name }}</span>
          </button>
        </div>
      </div>

      <!-- 日期选择 -->
      <div class="date-input">
        <label class="text-sm text-gray-500 mb-2 block">日期</label>
        <div class="relative" @click="openDatePicker">
          <input
            ref="dateInputRef"
            v-model="formData.date"
            type="date"
            class="w-full p-3 bg-gray-50 rounded-xl border border-gray-200 outline-none cursor-pointer focus:border-primary-400"
          />
          <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 cursor-pointer">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- 备注 -->
      <div class="description-input">
        <label class="text-sm text-gray-500 mb-2 block">备注（可选）</label>
        <input
          v-model="formData.description"
          type="text"
          placeholder="添加备注..."
          class="w-full p-3 bg-gray-50 rounded-xl border-none outline-none"
        />
      </div>

      <!-- 提交按钮 -->
      <button
        @click="handleSubmit"
        :disabled="isSubmitting"
        class="w-full py-3 bg-primary-500 text-white rounded-xl font-bold btn-cute disabled:opacity-50"
      >
        {{ isSubmitting ? '添加中...' : '确认添加' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 确保日期选择器在所有浏览器上可点击 */
input[type="date"] {
  position: relative;
  min-height: 48px;
}

/* 在 WebKit 浏览器上扩大日历图标点击区域 */
input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 0;
  top: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
</style>
