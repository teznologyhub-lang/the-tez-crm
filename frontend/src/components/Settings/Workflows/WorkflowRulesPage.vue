<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-ink-gray-9">{{ __('Workflow Rules & Automation') }}</h2>
        <p class="text-sm text-ink-gray-5">
          {{ __('Automate sales actions (email notifications, field updates, task creation, webhooks) triggered by record events.') }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="openLogs(null)">
          <template #icon><FeatherIcon name="file-text" class="h-4 w-4" /></template>
          {{ __('View Execution Logs') }}
        </Button>
        <Button variant="solid" @click="openCreateModal">
          <template #icon><FeatherIcon name="plus" class="h-4 w-4" /></template>
          {{ __('New Workflow Rule') }}
        </Button>
      </div>
    </div>

    <!-- Rules List / Table -->
    <div v-if="rulesRes.loading" class="py-12 text-center text-ink-gray-4">
      {{ __('Loading workflow rules...') }}
    </div>

    <div v-else-if="!rules.length" class="py-12 text-center border rounded-lg bg-surface-modal space-y-3">
      <div class="text-ink-gray-4 text-sm font-medium">{{ __('No Workflow Rules Configured') }}</div>
      <p class="text-xs text-ink-gray-5 max-w-md mx-auto">
        {{ __('Create automated rules to auto-assign leads, send welcome emails, update deal stages, or create follow-up tasks.') }}
      </p>
      <Button variant="solid" @click="openCreateModal">
        <template #icon><FeatherIcon name="plus" class="h-4 w-4" /></template>
        {{ __('Create First Rule') }}
      </Button>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="rule in rules"
        :key="rule.name"
        class="bg-surface-modal p-4 rounded-lg border border-[--surface-gray-3] flex items-center justify-between shadow-xs hover:border-[--surface-gray-4] transition-all"
      >
        <div class="space-y-1.5 max-w-xl">
          <div class="flex items-center gap-2">
            <span class="font-semibold text-ink-gray-9 text-base">{{ rule.rule_name }}</span>
            <Badge variant="subtle" theme="blue">{{ rule.document_type }}</Badge>
            <Badge variant="outline">{{ rule.trigger_type }}</Badge>
          </div>
          <p v-if="rule.description" class="text-xs text-ink-gray-6">{{ rule.description }}</p>

          <!-- Summary Pills -->
          <div class="flex items-center gap-2 pt-1 text-xs text-ink-gray-5">
            <span class="bg-surface-gray-2 px-2 py-0.5 rounded">
              🔍 {{ rule.conditions ? rule.conditions.length : 0 }} {{ __('conditions') }}
            </span>
            <span class="bg-surface-gray-2 px-2 py-0.5 rounded">
              ⚡ {{ rule.actions ? rule.actions.length : 0 }} {{ __('actions') }}
            </span>
          </div>
        </div>

        <!-- Controls & Actions -->
        <div class="flex items-center gap-4">
          <Switch
            :model-value="!!rule.is_active"
            @update:model-value="(val) => toggleRule(rule.name, val)"
          />

          <div class="flex items-center gap-1">
            <Button variant="ghost" icon="file-text" title="Logs" @click="openLogs(rule.name)" />
            <Button variant="ghost" icon="edit-3" title="Edit" @click="openEditModal(rule)" />
            <Button variant="ghost" icon="trash-2" class="text-ink-red-3 hover:bg-surface-red-1" title="Delete" @click="deleteRule(rule.name)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <WorkflowRuleModal
      v-model="showRuleModal"
      :rule-data="selectedRule"
      @saved="rulesRes.fetch"
    />

    <WorkflowLogsModal
      v-model="showLogsModal"
      :rule-name="selectedLogsRule"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, Badge, Switch, FeatherIcon, createResource } from 'frappe-ui'
import WorkflowRuleModal from './WorkflowRuleModal.vue'
import WorkflowLogsModal from './WorkflowLogsModal.vue'

const showRuleModal = ref(false)
const selectedRule = ref(null)

const showLogsModal = ref(false)
const selectedLogsRule = ref(null)

const rulesRes = createResource({
  url: 'crm.api.workflow.get_workflow_rules',
  auto: true,
})

const rules = computed(() => rulesRes.data || [])

function openCreateModal() {
  selectedRule.value = null
  showRuleModal.value = true
}

function openEditModal(rule) {
  selectedRule.value = rule
  showRuleModal.value = true
}

function openLogs(ruleName) {
  selectedLogsRule.value = ruleName
  showLogsModal.value = true
}

const toggleRes = createResource({
  url: 'crm.api.workflow.toggle_workflow_rule',
})

async function toggleRule(ruleName, isActive) {
  await toggleRes.submit({ rule_name: ruleName, is_active: isActive ? 1 : 0 })
  rulesRes.fetch()
}

const deleteRes = createResource({
  url: 'crm.api.workflow.delete_workflow_rule',
})

async function deleteRule(ruleName) {
  if (confirm(`Are you sure you want to delete workflow rule '${ruleName}'?`)) {
    await deleteRes.submit({ rule_name: ruleName })
    rulesRes.fetch()
  }
}
</script>
