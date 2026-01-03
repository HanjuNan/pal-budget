import api from './index'

export interface VoiceParseResult {
  type: 'income' | 'expense'
  amount: number
  category: string
  description?: string
}

export interface ScanResult {
  success: boolean
  data: {
    amount: number
    merchant: string
    date: string
    category?: string
    items: string[]
  }
  message?: string
}

export interface ChatResponse {
  reply: string
  ai_powered?: boolean
}

export interface AIConfig {
  configured: boolean
  api_base?: string
  model?: string
  use_ollama?: boolean
  ollama_available?: boolean
}

// 压缩图片
const compressImage = (file: File, maxWidth = 1024, quality = 0.8): Promise<File> => {
  return new Promise((resolve) => {
    // 如果文件小于 500KB，不压缩
    if (file.size < 500 * 1024) {
      resolve(file)
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let width = img.width
        let height = img.height

        // 如果图片宽度大于 maxWidth，按比例缩小
        if (width > maxWidth) {
          height = (height * maxWidth) / width
          width = maxWidth
        }

        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve(file)
          return
        }

        ctx.drawImage(img, 0, 0, width, height)

        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now()
              })
              console.log(`图片压缩: ${(file.size / 1024).toFixed(1)}KB -> ${(compressedFile.size / 1024).toFixed(1)}KB`)
              resolve(compressedFile)
            } else {
              resolve(file)
            }
          },
          'image/jpeg',
          quality
        )
      }
      img.onerror = () => resolve(file)
      img.src = e.target?.result as string
    }
    reader.onerror = () => resolve(file)
    reader.readAsDataURL(file)
  })
}

// 解析语音文本
export const parseVoiceText = (text: string) => {
  return api.post<any, VoiceParseResult>('/ai/parse-voice', { text })
}

// 扫描小票（带压缩和重试）
export const scanReceipt = async (file: File, retries = 2): Promise<ScanResult> => {
  // 压缩图片
  const compressedFile = await compressImage(file)

  const formData = new FormData()
  formData.append('file', compressedFile)

  const attemptScan = async (attempt: number): Promise<ScanResult> => {
    try {
      return await api.post<any, ScanResult>('/ai/scan-receipt', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 // 60 秒超时
      })
    } catch (error: any) {
      console.warn(`OCR 扫描尝试 ${attempt + 1} 失败:`, error.message)

      if (attempt < retries && (error.code === 'ECONNABORTED' || error.message?.includes('timeout'))) {
        console.log(`正在重试... (${attempt + 1}/${retries})`)
        return attemptScan(attempt + 1)
      }
      throw error
    }
  }

  return attemptScan(0)
}

// AI 对话
export const chatWithAI = (query: string, history?: { role: string; content: string }[]) => {
  return api.post<any, ChatResponse>('/ai/chat', { query, history })
}

// 获取 AI 配置状态
export const getAIConfig = () => {
  return api.get<any, AIConfig>('/ai/config')
}
