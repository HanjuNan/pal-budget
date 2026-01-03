import { ref } from 'vue'

interface ToastOptions {
  message: string
  type?: 'success' | 'error' | 'info'
  duration?: number
}

interface ToastItem extends ToastOptions {
  id: number
}

const toasts = ref<ToastItem[]>([])

export const useToast = () => {
  const show = (options: ToastOptions | string) => {
    const config: ToastOptions = typeof options === 'string'
      ? { message: options }
      : options

    const id = Date.now()
    const toast: ToastItem = {
      id,
      message: config.message,
      type: config.type || 'info',
      duration: config.duration || 3000
    }

    toasts.value.push(toast)

    setTimeout(() => {
      remove(id)
    }, toast.duration)

    return id
  }

  const remove = (id: number) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (message: string, duration?: number) => {
    return show({ message, type: 'success', duration })
  }

  const error = (message: string, duration?: number) => {
    return show({ message, type: 'error', duration })
  }

  const info = (message: string, duration?: number) => {
    return show({ message, type: 'info', duration })
  }

  return {
    toasts,
    show,
    success,
    error,
    info,
    remove
  }
}

// 便捷函数，可以直接调用
const toastInstance = useToast()

export const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  return toastInstance.show({ message, type })
}
