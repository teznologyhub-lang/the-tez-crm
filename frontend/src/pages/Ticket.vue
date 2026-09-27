<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template v-if="!errorTitle" #right-header>
      <CustomActions
        v-if="document._actions?.length"
        :actions="document._actions"
      />
      <AssignTo
        v-model="assignees.data"
        doctype="CRM Ticket"
        :docname="ticketId"
      />
      <!-- Status dropdown -->
      <Dropdown :options="statusOptions" placement="right">
        <template #default="{ open }">
          <Button
            v-if="doc.status"
            :label="doc.status"
            :iconRight="open ? 'chevron-up' : 'chevron-down'"
          >
            <template #prefix>
              <span
                class="inline-block w-2 h-2 rounded-full mr-1"
                :class="statusColor(doc.status)"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
      <!-- Delete -->
      <Button
        v-if="canDelete"
        variant="subtle"
        theme="red"
        icon="trash-2"
        :tooltip="__('Delete Ticket')"
        @click="deleteTicket"
      />
    </template>
  </LayoutHeader>

  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <!-- Left: Activity Tabs -->
    <Tabs
      v-model="tabIndex"
      :tabs="tabs"
      class="flex flex-1 overflow-hidden flex-col [&_[role='tab']]:px-0 [&_[role='tab']]:shrink-0 [&_[role='tablist']]:px-5 [&_[role='tablist']::-webkit-scrollbar]:h-0 [&_[role='tablist']]:min-h-[45px] [&_[role='tablist']]:gap-7.5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-panel>
        <Activities
          ref="activities"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          doctype="CRM Ticket"
          :docname="ticketId"
          :tabs="tabs"
          @afterSave="() => reload = true"
        />
      </template>
    </Tabs>

    <!-- Right: Side Panel -->
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <!-- Header: Ticket ID -->
      <div
        class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-base font-mono font-medium text-ink-gray-7 hover:bg-surface-gray-2 transition-colors"
        @click="copyToClipboard(ticketId)"
      >
        {{ ticketId }}
        <span class="ml-2 text-xs text-ink-gray-4">(click to copy)</span>
      </div>

      <!-- Subject banner -->
      <div class="border-b p-5">
        <div class="text-xl font-semibold text-ink-gray-9 leading-snug">
          {{ doc.subject || __('Untitled Ticket') }}
        </div>
        <div class="mt-2 flex flex-wrap gap-2 items-center">
          <!-- Priority badge -->
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
            :class="priorityClass(doc.priority)"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="priorityDotClass(doc.priority)" />
            {{ doc.priority || 'Medium' }}
          </span>
          <!-- Type badge -->
          <span
            v-if="doc.ticket_type"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-surface-gray-2 text-ink-gray-7"
          >
            {{ doc.ticket_type }}
          </span>
        </div>
      </div>

      <!-- Fields side panel -->
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Ticket"
          :docname="ticketId"
          @reload="sections.reload"
          @afterFieldChange="() => reload = true"
        />
      </div>
    </Resizer>
  </div>

  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />

  <DeleteLinkedDocModal
    v-if="showDeleteModal"
    v-model="showDeleteModal"
    doctype="CRM Ticket"
    :docname="ticketId"
    name="Tickets"
  />
</template>

<script setup>
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignTo from '@/components/AssignTo.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import CustomActions from '@/components/CustomActions.vue'
import { copyToClipboard } from '@/utils'
import { getView } from '@/utils/view'
import { getMeta } from '@/stores/meta'
import { useDocument } from '@/data/document'
import {
  createResource,
  Dropdown,
  Tabs,
  Breadcrumbs,
  usePageMeta,
  toast,
} from 'frappe-ui'
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import { getSettings } from '@/stores/settings'

const { brand } = getSettings()
const { doctypeMeta } = getMeta('CRM Ticket')

const route = useRoute()
const router = useRouter()

const props = defineProps({
  ticketId: { type: String, required: true },
})

const reload = ref(false)
const activities = ref(null)
const errorTitle = ref('')
const errorMessage = ref('')
const showDeleteModal = ref(false)

const {
  document,
  assignees,
  permissions,
  error,
} = useDocument('CRM Ticket', props.ticketId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)
const doc = computed(() => document.doc || {})

onMounted(async () => {
  // intentional: no triggerOnRender for now since no form script yet
})

watch(error, (err) => {
  if (err) {
    errorTitle.value = __(
      err.exc_type === 'DoesNotExistError' ? 'Document not found' : 'Error occurred',
    )
    errorMessage.value = __(err.messages?.[0] || 'An error occurred')
  } else {
    errorTitle.value = ''
    errorMessage.value = ''
  }
})

// Breadcrumbs
const breadcrumbs = computed(() => {
  let items = [{ label: __('Tickets'), route: { name: 'Tickets' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Ticket')
    if (view) {
      items.push({
        label: __(view.label),
        route: {
          name: 'Tickets',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: doc.value?.subject || props.ticketId,
    route: { name: 'Ticket', params: { ticketId: props.ticketId } },
  })
  return items
})

usePageMeta(() => ({
  title: doc.value?.subject || props.ticketId,
  icon: brand.favicon,
}))

// Status helpers
const STATUS_COLORS = {
  Open: 'bg-blue-500',
  Pending: 'bg-yellow-500',
  Resolved: 'bg-green-500',
  Closed: 'bg-surface-gray-5',
}

function statusColor(status) {
  return STATUS_COLORS[status] || 'bg-surface-gray-5'
}

const STATUS_OPTIONS = ['Open', 'Pending', 'Resolved', 'Closed']

const statusOptions = computed(() =>
  STATUS_OPTIONS.map((s) => ({
    label: s,
    onClick: () => updateField('status', s),
  })),
)

// Priority badge helpers
function priorityClass(priority) {
  const p = priority?.toLowerCase()
  if (p === 'urgent') return 'bg-red-100 text-red-700'
  if (p === 'high') return 'bg-orange-100 text-orange-700'
  if (p === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-surface-gray-2 text-ink-gray-6'
}

function priorityDotClass(priority) {
  const p = priority?.toLowerCase()
  if (p === 'urgent') return 'bg-red-500'
  if (p === 'high') return 'bg-orange-500'
  if (p === 'medium') return 'bg-yellow-500'
  return 'bg-ink-gray-4'
}

// Tabs
const tabs = computed(() => [
  { name: 'Activity', label: __('Activity'), icon: ActivityIcon },
  { name: 'Comments', label: __('Comments'), icon: CommentIcon },
  { name: 'Data', label: __('Data'), icon: DetailsIcon },
  { name: 'Tasks', label: __('Tasks'), icon: TaskIcon },
  { name: 'Notes', label: __('Notes'), icon: NoteIcon },
  { name: 'Attachments', label: __('Attachments'), icon: AttachmentIcon },
])

const { tabIndex } = useActiveTabManager(tabs, 'lastTicketTab')

// Side panel sections
const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Ticket'],
  params: { doctype: 'CRM Ticket' },
  auto: true,
})

function updateField(name, value) {
  const oldValue = doc.value[name]
  doc.value[name] = value
  document.save.submit(null, {
    onSuccess: () => (reload.value = true),
    onError: (err) => {
      doc.value[name] = oldValue
      toast.error(err.messages?.[0] || __('Error updating field'))
    },
  })
}

function deleteTicket() {
  showDeleteModal.value = true
}
</script>
