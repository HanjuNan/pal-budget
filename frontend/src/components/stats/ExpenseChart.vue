<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import type { CategoryStats } from '@/api/statistics'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps<{
  data: CategoryStats[]
}>()

const hasData = computed(() => props.data.length > 0)

const colors = ['#f97316', '#3b82f6', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b', '#6366f1', '#14b8a6']

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: ¥{c} ({d}%)'
  },
  legend: {
    orient: 'horizontal',
    bottom: 0,
    textStyle: {
      fontSize: 12,
      color: '#666'
    }
  },
  series: [
    {
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: props.data.map((item, index) => ({
        value: item.amount,
        name: item.category,
        itemStyle: { color: colors[index % colors.length] }
      }))
    }
  ]
}))
</script>

<template>
  <div class="expense-chart">
    <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2">
      <span>📊</span> 支出分类
    </h3>

    <!-- 空状态 -->
    <div v-if="!hasData" class="empty-state py-8 flex flex-col items-center">
      <span class="text-4xl mb-2">📉</span>
      <p class="text-gray-400">暂无支出数据</p>
    </div>

    <!-- 图表 -->
    <div v-else class="chart-wrapper h-64">
      <v-chart :option="option" autoresize />
    </div>
  </div>
</template>
