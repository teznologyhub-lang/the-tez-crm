<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
    <template #body-title>
      <div class="text-lg font-semibold text-ink-gray-9 flex items-center gap-2">
        <span>{{ __('Workflow Execution Logs') }}</span>
        <Badge v-if="ruleName" variant="outline">{{ ruleName }}</Badge>
      </div>
    </template>
    <template #body-content>
      <div class="py-2 space-y-4">
        <div v-if="logsRes.loading" class="py-8 text-center text-ink-gray-4">
          {{ __('Loading execution logs...') }}
        </div>
        <div v-else-if="!logsRes.data || logsRes.data.length === 0" class="py-8 text-center text-ink-gray-4 border rounded">
          {{ __('No execution history recorded yet.') }}
        </div>
        <div v-else class="max-h-96 overflow-y-auto space-y-2">
          <div
            v-for="log in logsRes.data"
            :key="log.name"
            class="p-3 rounded border border-[--surface-gray-3] bg-surface-gray-1 space-y-1"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Badge :variant="log.status === 'Success' ? 'subtle' : 'solid'" :theme="log.status === 'Success' ? 'green' : 'red'">
                  {{ log.status }}
                </Badge>
                <span class="text-xs font-semibold text-ink-gray-9">{{ log.workflow_rule }}</span>
                <span class="text-xs text-ink-gray-4">→ {{ log.reference_doctype }} ({{ log.reference_name }})</span>
              </div>
              <span class="text-xs text-ink-gray-4">{{ log.creation }}</span>
            </div>

            <div class="text-xs text-ink-gray-6 font-mono whitespace-pre-line bg-surface-modal p-2 rounded">
              {{ log.executed_actions || __('No actions summary') }}
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="subtle" :label="__('Close')" @click="show = false" />
    </template>
  </Dialog>
</template>

<script setup>
import { computed, watch } from 'vue'
import { Dialog, Button, Badge, createResource } from 'frappe-ui'

const props = defineProps({
  modelValue: Boolean,
  ruleName: String,
})

const emit = defineEmits(['update:modelValue'])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const logsRes = createResource({
  url: 'crm.api.workflow.get_execution_logs',
  auto: false,
})

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      logsRes.fetch({ workflow_rule: props.ruleName })
    }
  }
)
</script>
