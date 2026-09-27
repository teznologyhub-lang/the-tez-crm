<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" :routeName="routeName" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="listView?.customListActions"
        :actions="listView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createDoc()"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="list"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    :doctype="doctype"
    :options="{
      allowedViews: allowedViews,
    }"
  />

  <KanbanView
    v-if="$route.params.viewType == 'kanban' && kanbanColumns.length"
    v-model="list"
    :options="{
      onClick: (row) => showDoc(row.name),
      onNewClick: (column) => createDoc(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <!-- Ticket title: show subject directly from raw data item -->
    <template #title="{ fields, titleField }">
      <div class="flex items-center gap-2 w-full">
        <div
          v-if="fields[titleField]"
          class="truncate text-sm font-semibold text-ink-gray-9 leading-snug"
        >
          {{ fields[titleField] }}
        </div>
        <div v-else class="text-ink-gray-4 text-sm italic">
          {{ __('No Title') }}
        </div>
      </div>
    </template>

    <!-- Ticket fields: priority badge, type, assigned avatar, date -->
    <template #fields="{ fields, fieldName }">
      <!-- Priority -->
      <div
        v-if="fieldName === 'priority' && fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <span
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
          :class="getPriorityClass(fields[fieldName])"
        >
          <span class="w-1.5 h-1.5 rounded-full inline-block" :class="getPriorityDotClass(fields[fieldName])"></span>
          {{ fields[fieldName] }}
        </span>
      </div>

      <!-- Ticket Type -->
      <div
        v-else-if="fieldName === 'ticket_type' && fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <span class="inline-flex items-center gap-1.5 text-xs text-ink-gray-6">
          <svg class="w-3 h-3 text-ink-gray-4" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M5 8h6M5 5h6M5 11h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          {{ fields[fieldName] }}
        </span>
      </div>

      <!-- Assigned To / Owner -->
      <div
        v-else-if="(fieldName === 'assigned_to' || fieldName === 'owner') && fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <Avatar
          :label="getUser(fields[fieldName])?.full_name || fields[fieldName]"
          :image="getUser(fields[fieldName])?.user_image"
          size="xs"
          class="flex-shrink-0"
        />
        <span class="text-xs text-ink-gray-6 truncate">
          {{ getUser(fields[fieldName])?.full_name || fields[fieldName] }}
        </span>
      </div>

      <!-- Customer Contact -->
      <div
        v-else-if="fieldName === 'customer_contact' && fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <svg class="w-3 h-3 text-ink-gray-4 flex-shrink-0" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM2 14s-1 0-1-1 1-4 7-4 7 3 7 4-1 1-1 1H2z" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        <span class="text-xs text-ink-gray-6 truncate">{{ fields[fieldName] }}</span>
      </div>

      <!-- Modified / Creation dates -->
      <div
        v-else-if="['modified', 'creation'].includes(fieldName) && fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <svg class="w-3 h-3 text-ink-gray-4 flex-shrink-0" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
          <path d="M8 5v3.5l2 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <Tooltip :text="formatDate(fields[fieldName])">
          <span class="text-xs text-ink-gray-5">{{ __(timeAgo(fields[fieldName])) }}</span>
        </Tooltip>
      </div>

      <!-- Generic fallback -->
      <div
        v-else-if="fields[fieldName]"
        class="flex items-center gap-1.5"
      >
        <span class="text-xs text-ink-gray-6 truncate">{{ fields[fieldName] }}</span>
      </div>
    </template>

    <!-- Actions slot: ticket name badge -->
    <template #actions="{ itemName }">
      <div class="flex items-center justify-between w-full">
        <span class="text-xs font-mono text-ink-gray-4 bg-surface-gray-2 px-1.5 py-0.5 rounded">
          {{ itemName }}
        </span>
        <Button icon="arrow-up-right" variant="ghost" size="sm" @click.stop.prevent="showDoc(itemName)" />
      </div>
    </template>
  </KanbanView>

  <GenericListView
    v-else-if="list.data && rows.length"
    ref="listView"
    v-model="list.data.page_length_count"
    v-model:list="list"
    :rows="rows"
    :columns="columns"
    :doctype="doctype"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: list.data.row_count,
      totalCount: list.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @showDoc="showDoc"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />

  <EmptyState
    v-else-if="list.data && !rows.length"
    :name="routeName"
    :icon="Email2Icon"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import GenericListView from '@/components/ListViews/GenericListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { formatDate, timeAgo } from '@/utils'
import { useTelemetry } from 'frappe-ui/frappe'
import { Tooltip, Avatar } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const props = defineProps({
  doctype: { type: String, required: true },
  routeName: { type: String, required: true },
  allowedViews: { type: Array, default: () => ['list', 'kanban'] }
})

const { getUser } = usersStore()
const { capture } = useTelemetry()

const listView = ref(null)
const list = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } = getMeta(props.doctype)

// Priority styling helpers
function getPriorityClass(priority) {
  const p = priority?.toLowerCase()
  if (p === 'urgent') return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  if (p === 'high') return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  if (p === 'medium') return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-surface-gray-2 text-ink-gray-6'
}

function getPriorityDotClass(priority) {
  const p = priority?.toLowerCase()
  if (p === 'urgent') return 'bg-red-500'
  if (p === 'high') return 'bg-orange-500'
  if (p === 'medium') return 'bg-yellow-500'
  return 'bg-ink-gray-4'
}

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object') return value
    return { label: value }
  }
  const found = rows.value?.find((row) => row.name == name)
  return getValue(found ? found[field] : '')
}

// Kanban columns (used for v-if check)
const kanbanColumns = computed(() => {
  if (list.value?.data?.view_type !== 'kanban') return []
  return list.value?.data?.data || []
})

const rows = computed(() => {
  if (!list.value?.data?.data) return []

  if (list.value.data.view_type === 'kanban') {
    return getKanbanRows(list.value.data.data, list.value.data.fields)
  }

  return parseRows(list.value?.data.data, list.value?.data.columns)
})

function getKanbanRows(data, columns) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows, columns)
}

const columns = computed(() => {
  let _columns = list.value?.data?.columns || []
  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) return { ...col, align: 'right' }
      return col
    })
  }
  return _columns
})

function parseRows(rowsList, columnsList = []) {
  let view_type = list.value?.data?.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rowsList.map((doc) => {
    let _rows = {}
    let allRowFields = list.value?.data?.rows || Object.keys(doc)

    allRowFields.forEach((row) => {
      _rows[row] = doc[row]
      let fieldType = columnsList?.find((col) => (col[key] || col.key || col.value) == row)?.[type || 'type']

      if (fieldType && ['Date', 'Datetime'].includes(fieldType) && !['modified', 'creation'].includes(row)) {
        _rows[row] = formatDate(doc[row], '', true, fieldType == 'Datetime')
      }
      if (fieldType == 'Currency') _rows[row] = getFormattedCurrency(row, doc)
      if (fieldType == 'Float') _rows[row] = getFormattedFloat(row, doc)
      if (fieldType == 'Percent') _rows[row] = getFormattedPercent(row, doc)

      if (['modified', 'creation'].includes(row)) {
        _rows[row] = { label: formatDate(doc[row]), timeAgo: __(timeAgo(doc[row])) }
      } else if (['assigned_to', 'owner', 'lead_owner', 'deal_owner'].includes(row)) {
        _rows[row] = {
          label: doc[row] && getUser(doc[row])?.full_name,
          ...(doc[row] && getUser(doc[row])),
        }
      }
    })
    _rows['name'] = doc['name']
    return _rows
  })
}

const { showModal } = useDoctypeModal()

const docCallbacks = {
  afterInsert: () => {
    list.value.reload()
    capture(`${props.doctype}_created`)
  },
  afterUpdate: () => {
    list.value.reload()
    capture(`${props.doctype}_updated`)
  },
}

function showDoc(name) {
  if (props.doctype === 'CRM Ticket') {
    router.push({
      name: 'Ticket',
      params: { ticketId: name },
      query: { view: route.query.view, viewType: route.params.viewType },
    })
    return
  }
  showModal({
    name,
    doctype: props.doctype,
    title: props.doctype,
    callbacks: docCallbacks,
  })
}

function createDoc(column) {
  const defaults = {}
  if (column?.column?.name) {
    let column_field = list.value.params?.column_field || 'status'
    if (column_field) {
      defaults[column_field] = column.column.name
    }
  }

  showModal({
    doctype: props.doctype,
    title: props.doctype,
    defaults: defaults,
    callbacks: docCallbacks,
  })
}
</script>
