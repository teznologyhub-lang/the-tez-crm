<template>
  <div class="flex flex-col h-full bg-surface-modal p-6 overflow-y-auto">
    <!-- Header -->
    <div class="flex items-center justify-between pb-5 border-b border-border-subtle">
      <div>
        <h2 class="text-xl font-bold text-ink-gray-9">Web-to-Lead Forms</h2>
        <p class="text-sm text-ink-gray-5 mt-1">
          Create embeddable forms to capture leads directly from your external website into TezCRM.
        </p>
      </div>
      <Button variant="solid" label="New Web Form" @click="openCreateModal">
        <template #prefix>
          <LucidePlus class="size-4" />
        </template>
      </Button>
    </div>

    <!-- Forms List -->
    <div v-if="formsResource.loading" class="flex justify-center items-center py-12">
      <Spinner class="size-6 text-ink-gray-5" />
    </div>

    <div v-else-if="!formsResource.data || formsResource.data.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
      <div class="size-12 rounded-full bg-surface-gray-2 flex items-center justify-center mb-3">
        <LucideGlobe class="size-6 text-ink-gray-5" />
      </div>
      <h3 class="text-base font-semibold text-ink-gray-8">No Web Forms Created</h3>
      <p class="text-sm text-ink-gray-5 max-w-sm mt-1 mb-4">
        Build embeddable HTML forms to capture visitors on your website as fresh CRM Leads.
      </p>
      <Button variant="solid" label="Create First Web Form" @click="openCreateModal" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
      <div
        v-for="form in formsResource.data"
        :key="form.name"
        class="border border-border-subtle rounded-xl p-5 bg-surface-cards hover:shadow-sm transition-all"
      >
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-ink-gray-9">{{ form.title }}</h3>
              <Badge :variant="form.is_active ? 'green' : 'gray'">
                {{ form.is_active ? 'Active' : 'Disabled' }}
              </Badge>
            </div>
            <p class="text-xs text-ink-gray-5 mt-1">
              Source: <span class="font-medium text-ink-gray-7">{{ form.lead_source || 'Web Form' }}</span>
            </p>
          </div>
          <Dropdown
            :options="[
              { label: 'Embed Snippet', icon: LucideCode, onClick: () => showEmbedModal(form.name) },
              { label: 'Edit Form', icon: LucidePenLine, onClick: () => editForm(form) },
              { label: 'Delete', icon: LucideTrash2, variant: 'danger', onClick: () => confirmDelete(form.name) },
            ]"
          >
            <Button variant="ghost" class="!px-1.5">
              <LucideMoreVertical class="size-4 text-ink-gray-5" />
            </Button>
          </Dropdown>
        </div>

        <div class="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-border-subtle text-xs">
          <div>
            <span class="text-ink-gray-5">Submissions</span>
            <div class="text-base font-bold text-ink-gray-9 mt-0.5">{{ form.submissions_count || 0 }}</div>
          </div>
          <div>
            <span class="text-ink-gray-5">Fields</span>
            <div class="text-base font-bold text-ink-gray-9 mt-0.5">{{ form.fields ? form.fields.length : 0 }}</div>
          </div>
        </div>

        <div class="flex items-center gap-2 mt-4">
          <Button variant="outline" size="sm" class="w-full" @click="showEmbedModal(form.name)">
            <template #prefix>
              <LucideCode class="size-3.5" />
            </template>
            Get Code Snippet
          </Button>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <Dialog
      v-model="showFormModal"
      :options="{ size: '2xl', title: formModalTitle }"
    >
      <template #body-content>
        <div class="space-y-4 py-2">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-ink-gray-5 mb-1">Form Title *</label>
              <Input v-model="formData.title" placeholder="Contact Us Form" />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-5 mb-1">Lead Source</label>
              <Input v-model="formData.lead_source" placeholder="Web Form" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-ink-gray-5 mb-1">Success Message</label>
              <Input v-model="formData.success_message" placeholder="Thank you! We will get back to you shortly." />
            </div>
            <div>
              <label class="block text-xs font-medium text-ink-gray-5 mb-1">Redirect URL (Optional)</label>
              <Input v-model="formData.redirect_url" placeholder="https://example.com/thank-you" />
            </div>
          </div>

          <div class="flex items-center gap-2 pt-1">
            <Checkbox v-model="formData.is_active" label="Form is Active" />
          </div>

          <!-- Form Fields Configurator -->
          <div class="border-t border-border-subtle pt-4 mt-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-bold text-ink-gray-8">Form Fields</h4>
              <Button variant="ghost" size="sm" label="+ Add Field" @click="addField" />
            </div>

            <div class="space-y-2 max-h-60 overflow-y-auto pr-1">
              <div
                v-for="(field, index) in formData.fields"
                :key="index"
                class="flex items-center gap-2 p-2 rounded-lg border border-border-subtle bg-surface-gray-2 text-xs"
              >
                <div class="w-32">
                  <Input v-model="field.label" placeholder="Label" @input="autoFieldname(field)" />
                </div>
                <div class="w-28">
                  <Input v-model="field.fieldname" placeholder="fieldname" />
                </div>
                <div class="w-28">
                  <select v-model="field.fieldtype" class="w-full p-1.5 border border-border-subtle rounded text-xs bg-surface-modal">
                    <option value="Data">Text Input</option>
                    <option value="Small Text">Textarea</option>
                    <option value="Phone">Phone</option>
                    <option value="Select">Dropdown</option>
                  </select>
                </div>
                <div class="w-28">
                  <Input v-model="field.placeholder" placeholder="Placeholder" />
                </div>
                <div class="flex items-center gap-1 pl-1">
                  <Checkbox v-model="field.reqd" title="Required field" />
                  <span class="text-[10px] text-ink-gray-5">Req</span>
                </div>
                <Button variant="ghost" class="!p-1 text-ink-gray-4 hover:text-ink-red-4 ml-auto" @click="removeField(index)">
                  <LucideTrash2 class="size-3.5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="ghost" label="Cancel" @click="showFormModal = false" />
        <Button variant="solid" label="Save Web Form" :loading="saveResource.loading" @click="saveForm" />
      </template>
    </Dialog>

    <!-- Embed Code Modal -->
    <Dialog
      v-model="showCodeModal"
      :options="{ size: '3xl', title: 'Embed Web Form Code' }"
    >
      <template #body-content>
        <div class="space-y-4 py-2">
          <p class="text-xs text-ink-gray-5">
            Copy and paste this HTML snippet into any webpage on your external website. Submissions will flow directly into TezCRM.
          </p>

          <div v-if="embedData" class="relative">
            <textarea
              readonly
              class="w-full h-64 p-3 font-mono text-xs border border-border-subtle rounded-lg bg-surface-gray-3 text-ink-gray-9 select-all"
              :value="embedData.raw_html"
            />
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="ghost" label="Close" @click="showCodeModal = false" />
        <Button variant="solid" :label="copied ? 'Copied!' : 'Copy Code'" @click="copySnippet">
          <template #prefix>
            <LucideCheck v-if="copied" class="size-4 text-ink-green-4" />
            <LucideCopy v-else class="size-4" />
          </template>
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { createResource, Dialog, Button, Input, Checkbox, Badge, Dropdown, Spinner } from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import LucideGlobe from '~icons/lucide/globe'
import LucideCode from '~icons/lucide/code'
import LucidePenLine from '~icons/lucide/pen-line'
import LucideTrash2 from '~icons/lucide/trash-2'
import LucideMoreVertical from '~icons/lucide/more-vertical'
import LucideCopy from '~icons/lucide/copy'
import LucideCheck from '~icons/lucide/check'

const showFormModal = ref(false)
const showCodeModal = ref(false)
const copied = ref(false)
const selectedFormId = ref('')

const formsResource = createResource({
  url: 'crm.api.web_to_lead.get_web_forms',
  auto: true,
})

const embedResource = createResource({
  url: 'crm.api.web_to_lead.get_embed_code',
})

const embedData = computed(() => embedResource.data)

const formData = reactive({
  name: '',
  title: '',
  lead_source: 'Web Form',
  default_lead_owner: '',
  success_message: 'Thank you! We will get back to you shortly.',
  redirect_url: '',
  is_active: true,
  fields: [] as any[],
})

const formModalTitle = computed(() => formData.name ? 'Edit Web Form' : 'New Web Form')

function defaultFields() {
  return [
    { fieldname: 'first_name', label: 'First Name', fieldtype: 'Data', reqd: true, placeholder: 'John' },
    { fieldname: 'last_name', label: 'Last Name', fieldtype: 'Data', reqd: false, placeholder: 'Doe' },
    { fieldname: 'email', label: 'Email Address', fieldtype: 'Data', reqd: true, placeholder: 'john@example.com' },
    { fieldname: 'phone', label: 'Phone Number', fieldtype: 'Phone', reqd: false, placeholder: '+1 234 567 890' },
    { fieldname: 'organization', label: 'Company Name', fieldtype: 'Data', reqd: false, placeholder: 'Acme Corp' },
    { fieldname: 'message', label: 'Message', fieldtype: 'Small Text', reqd: false, placeholder: 'How can we help you?' },
  ]
}

function openCreateModal() {
  formData.name = ''
  formData.title = 'Website Contact Form'
  formData.lead_source = 'Web Form'
  formData.success_message = 'Thank you! We will get back to you shortly.'
  formData.redirect_url = ''
  formData.is_active = true
  formData.fields = defaultFields()
  showFormModal.value = true
}

function editForm(form: any) {
  formData.name = form.name
  formData.title = form.title
  formData.lead_source = form.lead_source || 'Web Form'
  formData.success_message = form.success_message || ''
  formData.redirect_url = form.redirect_url || ''
  formData.is_active = !!form.is_active
  formData.fields = form.fields ? JSON.parse(JSON.stringify(form.fields)) : defaultFields()
  showFormModal.value = true
}

function addField() {
  formData.fields.push({
    fieldname: `field_${formData.fields.length + 1}`,
    label: 'New Field',
    fieldtype: 'Data',
    reqd: false,
    placeholder: '',
  })
}

function removeField(index: number) {
  formData.fields.splice(index, 1)
}

function autoFieldname(field: any) {
  if (field.label) {
    field.fieldname = field.label.toLowerCase().replace(/[^a-z0-9]/g, '_')
  }
}

const saveResource = createResource({
  url: 'crm.api.web_to_lead.save_web_form',
  onSuccess() {
    showFormModal.value = false
    formsResource.reload()
  },
})

function saveForm() {
  saveResource.submit({
    form_data: JSON.stringify(formData),
  })
}

function confirmDelete(name: string) {
  if (confirm('Are you sure you want to delete this Web Form?')) {
    createResource({
      url: 'crm.api.web_to_lead.delete_web_form',
      auto: true,
      params: { name },
      onSuccess() {
        formsResource.reload()
      },
    })
  }
}

function showEmbedModal(name: string) {
  selectedFormId.value = name
  copied.value = false
  embedResource.submit({ form_id: name })
  showCodeModal.value = true
}

function copySnippet() {
  if (embedData.value?.raw_html) {
    navigator.clipboard.writeText(embedData.value.raw_html)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}
</script>
