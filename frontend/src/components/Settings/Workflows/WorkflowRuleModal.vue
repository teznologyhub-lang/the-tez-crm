<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body-title>
      <div class="text-lg font-semibold text-ink-gray-9">
        {{ isEdit ? __('Edit Workflow Rule') : __('New Workflow Rule') }}
      </div>
    </template>
    <template #body-content>
      <div class="space-y-5 py-2">
        <!-- Basic Configuration -->
        <div class="grid grid-cols-2 gap-4">
          <FormControl
            v-model="form.rule_name"
            :label="__('Rule Name')"
            placeholder="e.g. Auto-Qualify Web Leads"
            reqd
          />
          <FormControl
            v-model="form.document_type"
            type="select"
            :label="__('Target Module / Doctype')"
            :options="doctypeOptions"
            reqd
            @change="onDoctypeChange"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <FormControl
            v-model="form.trigger_type"
            type="select"
            :label="__('Trigger Event')"
            :options="triggerOptions"
            reqd
          />
          <FormControl
            v-if="form.trigger_type === 'On Field Change'"
            v-model="form.trigger_field"
            type="select"
            :label="__('Trigger Field')"
            :options="fieldOptions"
          />
          <div v-else class="flex items-center pt-6">
            <Switch
              v-model="form.is_active"
              :label="__('Active Rule')"
            />
          </div>
        </div>

        <FormControl
          v-model="form.description"
          type="textarea"
          :label="__('Description (Optional)')"
          placeholder="Describe what this workflow rule accomplishes..."
          rows="2"
        />

        <!-- Section 1: Conditions / Filters -->
        <div class="border-t pt-4">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h4 class="text-sm font-semibold text-ink-gray-9">{{ __('Conditions (Filters)') }}</h4>
              <p class="text-xs text-ink-gray-5">{{ __('Rule triggers only if ALL conditions match (AND logic). Leave empty for all records.') }}</p>
            </div>
            <Button size="sm" variant="subtle" @click="addCondition">
              <template #icon><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
              {{ __('Add Condition') }}
            </Button>
          </div>

          <div v-if="form.conditions.length === 0" class="text-xs text-ink-gray-4 italic py-2 bg-surface-gray-2 rounded text-center">
            {{ __('No filter conditions. Rule will trigger for every record in this module.') }}
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="(cond, index) in form.conditions"
              :key="index"
              class="flex items-center gap-2 bg-surface-gray-1 p-2 rounded border border-[--surface-gray-3]"
            >
              <div class="w-1/3">
                <FormControl
                  v-model="cond.field"
                  type="select"
                  size="sm"
                  :options="fieldOptions"
                  placeholder="Select Field"
                />
              </div>
              <div class="w-1/3">
                <FormControl
                  v-model="cond.operator"
                  type="select"
                  size="sm"
                  :options="operatorOptions"
                />
              </div>
              <div class="w-1/3">
                <FormControl
                  v-model="cond.value"
                  size="sm"
                  placeholder="Target Value"
                />
              </div>
              <Button
                variant="ghost"
                icon="trash-2"
                class="text-ink-red-3 hover:bg-surface-red-1"
                @click="removeCondition(index)"
              />
            </div>
          </div>
        </div>

        <!-- Section 2: Automated Actions -->
        <div class="border-t pt-4">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h4 class="text-sm font-semibold text-ink-gray-9">{{ __('Automated Actions') }}</h4>
              <p class="text-xs text-ink-gray-5">{{ __('Actions executed sequentially when conditions match.') }}</p>
            </div>
            <Button size="sm" variant="subtle" @click="addAction">
              <template #icon><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
              {{ __('Add Action') }}
            </Button>
          </div>

          <div v-if="form.actions.length === 0" class="text-xs text-ink-red-3 py-2 bg-surface-red-1 rounded text-center">
            {{ __('At least one action is required.') }}
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="(act, index) in form.actions"
              :key="index"
              class="bg-surface-gray-1 p-3 rounded border border-[--surface-gray-3] space-y-2"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 w-full max-w-xs">
                  <span class="text-xs font-semibold text-ink-gray-6">#{{ index + 1 }}</span>
                  <FormControl
                    v-model="act.action_type"
                    type="select"
                    size="sm"
                    :options="actionTypeOptions"
                  />
                </div>
                <Button
                  variant="ghost"
                  icon="trash-2"
                  class="text-ink-red-3 hover:bg-surface-red-1"
                  @click="removeAction(index)"
                />
              </div>

              <!-- Action-specific options -->
              <div v-if="act.action_type === 'send_email'" class="grid grid-cols-2 gap-2 pt-1 border-t border-dashed">
                <FormControl
                  v-model="act.email_template"
                  type="select"
                  size="sm"
                  :label="__('Email Template')"
                  :options="emailTemplateOptions"
                />
                <FormControl
                  v-model="act.recipient_field"
                  type="select"
                  size="sm"
                  :label="__('Recipient')"
                  :options="['Lead/Contact Email', 'Owner Email', 'Custom Email']"
                />
                <FormControl
                  v-if="act.recipient_field === 'Custom Email'"
                  v-model="act.custom_recipient"
                  size="sm"
                  :label="__('Custom Email')"
                  placeholder="sales@company.com"
                />
              </div>

              <div v-else-if="act.action_type === 'update_field'" class="grid grid-cols-2 gap-2 pt-1 border-t border-dashed">
                <FormControl
                  v-model="act.update_field_name"
                  type="select"
                  size="sm"
                  :label="__('Field to Update')"
                  :options="fieldOptions"
                />
                <FormControl
                  v-model="act.update_field_value"
                  size="sm"
                  :label="__('New Value')"
                  placeholder="New field value"
                />
              </div>

              <div v-else-if="act.action_type === 'create_task'" class="grid grid-cols-2 gap-2 pt-1 border-t border-dashed">
                <FormControl
                  v-model="act.task_subject"
                  size="sm"
                  :label="__('Task Subject')"
                  placeholder="e.g. Call Lead within 24 hours"
                />
                <FormControl
                  v-model="act.task_due_in_days"
                  type="number"
                  size="sm"
                  :label="__('Due in (Days)')"
                />
              </div>

              <div v-else-if="act.action_type === 'assign_owner'" class="grid grid-cols-1 gap-2 pt-1 border-t border-dashed">
                <FormControl
                  v-model="act.assign_to_user"
                  type="select"
                  size="sm"
                  :label="__('Assign To Owner')"
                  :options="userOptions"
                />
              </div>

              <div v-else-if="act.action_type === 'webhook'" class="grid grid-cols-1 gap-2 pt-1 border-t border-dashed">
                <FormControl
                  v-model="act.webhook_url"
                  size="sm"
                  :label="__('Webhook Endpoint URL')"
                  placeholder="https://hooks.zapier.com/hooks/catch/12345/..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-end gap-2">
        <Button variant="subtle" :label="__('Cancel')" @click="show = false" />
        <Button
          variant="solid"
          :label="isEdit ? __('Save Changes') : __('Create Rule')"
          :loading="saving"
          @click="saveRule"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, Button, FormControl, Switch, FeatherIcon, createResource } from 'frappe-ui'

const props = defineProps({
  modelValue: Boolean,
  ruleData: Object,
})

const emit = defineEmits(['update:modelValue', 'saved'])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const isEdit = computed(() => !!props.ruleData?.name)
const saving = ref(false)

const doctypeOptions = ['CRM Lead', 'CRM Deal', 'CRM Task', 'Contact']
const triggerOptions = [
  'On Creation',
  'On Update',
  'On Creation or Update',
  'On Field Change',
]
const operatorOptions = [
  { label: 'equals', value: 'equals' },
  { label: 'not equals', value: 'not_equals' },
  { label: 'contains', value: 'contains' },
  { label: 'greater than', value: 'greater_than' },
  { label: 'less than', value: 'less_than' },
  { label: 'is set', value: 'is_set' },
  { label: 'is not set', value: 'is_not_set' },
  { label: 'changed to', value: 'changed_to' },
]

const actionTypeOptions = [
  { label: '📧 Send Email', value: 'send_email' },
  { label: '✏️ Update Field', value: 'update_field' },
  { label: '📋 Create Task', value: 'create_task' },
  { label: '👤 Assign Owner', value: 'assign_owner' },
  { label: '🔗 Trigger Webhook', value: 'webhook' },
]

const form = ref({
  name: '',
  rule_name: '',
  document_type: 'CRM Lead',
  trigger_type: 'On Creation',
  trigger_field: '',
  is_active: true,
  description: '',
  conditions: [],
  actions: [],
})

const fieldsRes = createResource({
  url: 'crm.api.workflow.get_doctype_fields',
  auto: false,
})

const emailTemplatesRes = createResource({
  url: 'frappe.client.get_list',
  params: { doctype: 'Email Template', fields: ['name', 'subject'] },
  auto: true,
})

const usersRes = createResource({
  url: 'frappe.client.get_list',
  params: { doctype: 'User', filters: { enabled: 1 }, fields: ['name', 'full_name'] },
  auto: true,
})

const fieldOptions = computed(() => {
  if (!fieldsRes.data) return []
  return fieldsRes.data.map((f) => ({ label: `${f.label} (${f.fieldname})`, value: f.fieldname }))
})

const emailTemplateOptions = computed(() => {
  if (!emailTemplatesRes.data) return []
  return emailTemplatesRes.data.map((t) => ({ label: t.name, value: t.name }))
})

const userOptions = computed(() => {
  if (!usersRes.data) return []
  return usersRes.data.map((u) => ({ label: u.full_name || u.name, value: u.name }))
})

function onDoctypeChange() {
  fieldsRes.fetch({ doctype: form.value.document_type })
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      if (props.ruleData) {
        form.value = JSON.parse(JSON.stringify(props.ruleData))
      } else {
        form.value = {
          name: '',
          rule_name: '',
          document_type: 'CRM Lead',
          trigger_type: 'On Creation',
          trigger_field: '',
          is_active: true,
          description: '',
          conditions: [],
          actions: [
            {
              action_type: 'send_email',
              recipient_field: 'Lead/Contact Email',
              task_due_in_days: 1,
            },
          ],
        }
      }
      onDoctypeChange()
    }
  }
)

function addCondition() {
  form.value.conditions.push({ field: '', operator: 'equals', value: '' })
}

function removeCondition(index) {
  form.value.conditions.splice(index, 1)
}

function addAction() {
  form.value.actions.push({
    action_type: 'send_email',
    recipient_field: 'Lead/Contact Email',
    task_due_in_days: 1,
  })
}

function removeAction(index) {
  form.value.actions.splice(index, 1)
}

const saveRes = createResource({
  url: 'crm.api.workflow.save_workflow_rule',
})

async function saveRule() {
  if (!form.value.rule_name) return
  if (!form.value.actions.length) return

  saving.value = true
  try {
    await saveRes.submit({ rule_data: form.value })
    show.value = false
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
