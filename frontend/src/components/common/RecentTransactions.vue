<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTransactionStore } from '@/stores/transaction'
import type { Transaction } from '@/api/transaction'

const props = defineProps<{
  transactions: Transaction[]
  loading?: boolean
}>()

const transactionStore = useTransactionStore()
const isEmpty = computed(() => props.transactions.length === 0)

// 删除相关状态
const showDeleteModal = ref(false)
const deleteTarget = ref<Transaction | null>(null)
const deleting = ref(false)

// 打开删除确认弹窗
const confirmDelete = (item: Transaction) => {
  deleteTarget.value = item
  showDeleteModal.value = true
}

// 取消删除
const cancelDelete = () => {
  showDeleteModal.value = false
  deleteTarget.value = null
}

// 执行删除
const executeDelete = async () => {
  if (!deleteTarget.value?.id) return

  deleting.value = true
  try {
    await transactionStore.removeTransaction(deleteTarget.value.id)
    // 刷新统计数据
    await transactionStore.refreshAllData()
    showDeleteModal.value = false
    deleteTarget.value = null
  } catch (e) {
    console.error('删除失败:', e)
  } finally {
    deleting.value = false
  }
}

const getCategoryIcon = (category: string): string => {
  const icons: Record<string, string> = {
    '餐饮': '🍜',
    '交通': '🚗',
    '购物': '🛒',
    '住房': '🏠',
    '娱乐': '🎮',
    '医疗': '💊',
    '教育': '📚',
    '通讯': '📱',
    '服饰': '👔',
    '旅行': '✈️',
    '礼物': '🎁',
    '工资': '💰',
    '奖金': '🎁',
    '投资': '📈',
    '兼职': '💸',
    '利息': '🏦'
  }
  return icons[category] || '📦'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<template>
  <div class="recent-transactions bg-white rounded-2xl p-4 shadow-card">
    <h3 class="font-bold text-gray-800 mb-3">最近记录</h3>

    <!-- 加载中 -->
    <div v-if="loading" class="py-8 flex justify-center">
      <div class="w-8 h-8 border-3 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="isEmpty" class="empty-state py-8 flex flex-col items-center">
      <span class="text-5xl mb-3">🌸</span>
      <p class="text-gray-400">还没有记录哦~</p>
      <p class="text-sm text-gray-300">快去记一笔吧！</p>
    </div>

    <!-- 交易列表 -->
    <div v-else class="transaction-list space-y-3">
      <div
        v-for="item in transactions"
        :key="item.id"
        class="transaction-item flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">{{ getCategoryIcon(item.category) }}</span>
          <div>
            <p class="font-medium text-gray-800">{{ item.category }}</p>
            <p class="text-xs text-gray-400">{{ item.description || formatDate(item.date) }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span
            class="font-bold"
            :class="item.type === 'income' ? 'text-income' : 'text-expense'"
          >
            {{ item.type === 'income' ? '+' : '-' }}¥{{ item.amount.toFixed(2) }}
          </span>
          <!-- 删除按钮 -->
          <button
            @click.stop="confirmDelete(item)"
            class="delete-btn w-7 h-7 flex items-center justify-center rounded-full bg-red-50 text-red-400 hover:bg-red-100 hover:text-red-500 transition-colors"
            title="删除"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
          <div class="modal-content" @click.stop>
            <div class="text-center">
              <div class="text-4xl mb-3">🗑️</div>
              <h3 class="text-lg font-bold text-gray-800 mb-2">确认删除</h3>
              <p class="text-gray-500 mb-1">确定要删除这条记录吗？</p>
              <p v-if="deleteTarget" class="text-sm text-gray-400 mb-4">
                {{ deleteTarget.category }} ·
                <span :class="deleteTarget.type === 'income' ? 'text-income' : 'text-expense'">
                  {{ deleteTarget.type === 'income' ? '+' : '-' }}¥{{ deleteTarget.amount.toFixed(2) }}
                </span>
              </p>
            </div>
            <div class="flex gap-3">
              <button
                @click="cancelDelete"
                class="flex-1 py-2.5 rounded-xl bg-gray-100 text-gray-600 font-medium hover:bg-gray-200 transition-colors"
                :disabled="deleting"
              >
                取消
              </button>
              <button
                @click="executeDelete"
                class="flex-1 py-2.5 rounded-xl bg-red-500 text-white font-medium hover:bg-red-600 transition-colors flex items-center justify-center"
                :disabled="deleting"
              >
                <span v-if="deleting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                {{ deleting ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* 删除按钮 */
.delete-btn {
  opacity: 0.6;
}

.transaction-item:hover .delete-btn {
  opacity: 1;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 1.5rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 320px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}
</style>
