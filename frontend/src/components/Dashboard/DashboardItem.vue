<template>
  <div class="h-full w-full overflow-hidden">
    <!-- Number Chart (Compact, Clean KPI Card) -->
    <div
      v-if="item.type == 'number_chart'"
      class="h-full w-full rounded-xl bg-surface-white border border-surface-gray-3 p-3 shadow-2xs hover:shadow-xs transition-shadow duration-200 flex flex-col justify-between cursor-pointer overflow-hidden"
    >
      <!-- Top Row: Small Title + Tooltip -->
      <div class="flex items-center justify-between gap-1.5 min-w-0">
        <span class="text-[11px] font-semibold text-ink-gray-5 truncate">
          {{ __(item.data?.title || formatTitle(item.name)) }}
        </span>
        <Tooltip v-if="item.data?.tooltip" :text="__(item.data.tooltip)">
          <FeatherIcon name="info" class="size-3 text-ink-gray-4 hover:text-ink-gray-7 shrink-0 cursor-help" />
        </Tooltip>
      </div>

      <!-- Main Value -->
      <div class="my-1 leading-none truncate">
        <span class="text-xl sm:text-2xl font-bold text-ink-gray-9 tracking-tight">
          {{ formatKpiValue(item.data) }}
        </span>
      </div>

      <!-- Footer: Compact Trend delta pill + Comparison note -->
      <div class="flex items-center justify-between text-[11px] pt-1.5 border-t border-surface-gray-2 min-w-0">
        <div
          v-if="item.data && item.data.delta !== undefined && item.data.delta !== null"
          class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded font-semibold text-[10px]"
          :class="getDeltaClass(item.data)"
        >
          <span v-if="item.data.delta > 0">↑</span>
          <span v-else-if="item.data.delta < 0">↓</span>
          <span v-else>•</span>
          <span>{{ Math.abs(Math.round(item.data.delta * 10) / 10) }}{{ item.data.deltaSuffix || '%' }}</span>
        </div>
        <div v-else class="text-[10px] text-ink-gray-4">
          --
        </div>
        <span class="text-[10px] text-ink-gray-4 truncate">
          vs prev. period
        </span>
      </div>
    </div>

    <!-- Spacer -->
    <div
      v-else-if="item.type == 'spacer'"
      class="rounded-xl bg-surface-white h-full overflow-hidden text-ink-gray-4 text-xs font-medium flex items-center justify-center"
      :class="editing ? 'border border-dashed border-outline-gray-3' : ''"
    >
      {{ editing ? __('Spacer') : '' }}
    </div>

    <!-- Axis Chart (Line / Bar) -->
    <div
      v-else-if="item.type == 'axis_chart'"
      class="h-full w-full rounded-xl bg-surface-white border border-surface-gray-3 shadow-2xs hover:shadow-xs transition-shadow duration-200 p-3 flex flex-col overflow-hidden"
    >
      <div v-if="item.data?.title" class="mb-1.5 flex items-center justify-between min-w-0">
        <h3 class="text-xs font-semibold text-ink-gray-8 truncate">
          {{ __(item.data.title) }}
        </h3>
      </div>
      <div class="flex-1 w-full min-h-0 overflow-hidden">
        <AxisChart v-if="item.data" :config="item.data" />
      </div>
    </div>

    <!-- Donut Chart -->
    <div
      v-else-if="item.type == 'donut_chart'"
      class="h-full w-full rounded-xl bg-surface-white border border-surface-gray-3 shadow-2xs hover:shadow-xs transition-shadow duration-200 p-3 flex flex-col overflow-hidden"
    >
      <div v-if="item.data?.title" class="mb-1.5 flex items-center justify-between min-w-0">
        <h3 class="text-xs font-semibold text-ink-gray-8 truncate">
          {{ __(item.data.title) }}
        </h3>
      </div>
      <div class="flex-1 w-full min-h-0 overflow-hidden">
        <DonutChart v-if="item.data" :config="item.data" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { AxisChart, DonutChart, Tooltip } from 'frappe-ui'

defineProps({
  index: { type: Number, required: true },
  item: { type: Object, required: true },
  editing: { type: Boolean, default: false },
})

function formatTitle(name = '') {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatKpiValue(data) {
  if (!data) return '0'
  let val = data.value
  if (val === undefined || val === null) return '0'

  if (typeof val === 'number') {
    val = Number.isInteger(val) ? val.toLocaleString() : val.toFixed(1)
  }

  let prefix = data.prefix || ''
  let suffix = data.suffix || ''
  return `${prefix}${val}${suffix}`
}

function getDeltaClass(data) {
  const delta = parseFloat(data?.delta) || 0

  if (delta > 0) {
    return 'text-green-700 font-bold dark:bg-green-950/50 dark:text-green-400'
  }
  if (delta < 0) {
    return 'text-red-700 font-bold dark:bg-red-950/50 dark:text-red-400'
  }
  return 'bg-surface-gray-2 text-ink-gray-6 border border-surface-gray-3'
}
</script>
