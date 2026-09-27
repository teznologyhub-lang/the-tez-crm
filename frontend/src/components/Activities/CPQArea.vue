<template>
  <div class="px-3 pb-3 sm:px-10 sm:pb-5">
    <!-- Quotations Section -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2">
          <FileTextIcon class="h-4 w-4 text-ink-gray-6" />
          {{ __('Quotations') }}
        </h3>
        <Button
          size="sm"
          variant="outline"
          :label="__('New Quotation')"
          icon-left="plus"
          @click="createDoc('CRM Quotation')"
        />
      </div>
      <div v-if="quotations.loading" class="py-4 flex justify-center">
        <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
      </div>
      <div
        v-else-if="quotations.data?.length"
        class="rounded-lg border border-outline-gray-modals overflow-hidden"
      >
        <div
          v-for="(q, i) in quotations.data"
          :key="q.name"
          class="flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-surface-gray-1 transition-colors"
          :class="i < quotations.data.length - 1 ? 'border-b border-outline-gray-modals' : ''"
          @click="openDoc('CRM Quotation', q.name)"
        >
          <div class="flex flex-1 flex-col gap-0.5 min-w-0">
            <div class="font-medium text-ink-gray-9 text-sm truncate">
              {{ q.name }}
            </div>
            <div class="text-xs text-ink-gray-6 flex items-center gap-2">
              <span>{{ formatDate(q.date) }}</span>
              <DotIcon class="h-2 w-2 text-ink-gray-4" :radius="2" />
              <span>{{ n_fmt(q.grand_total) }}</span>
            </div>
          </div>
          <Badge :label="q.status" :theme="statusTheme(q.status)" />
          <Button
            variant="ghost"
            :tooltip="__('Download PDF')"
            icon="download"
            @click.stop="downloadPdf('CRM Quotation', q.name)"
          />
        </div>
      </div>
      <div
        v-else
        class="rounded-lg border border-dashed border-outline-gray-2 py-5 text-center text-sm text-ink-gray-5"
      >
        {{ __('No quotations yet') }}
      </div>
    </div>

    <!-- Sales Orders Section -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2">
          <ShoppingCartIcon class="h-4 w-4 text-ink-gray-6" />
          {{ __('Sales Orders') }}
        </h3>
        <Button
          size="sm"
          variant="outline"
          :label="__('New Sales Order')"
          icon-left="plus"
          @click="createDoc('CRM Sales Order')"
        />
      </div>
      <div v-if="salesOrders.loading" class="py-4 flex justify-center">
        <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
      </div>
      <div
        v-else-if="salesOrders.data?.length"
        class="rounded-lg border border-outline-gray-modals overflow-hidden"
      >
        <div
          v-for="(o, i) in salesOrders.data"
          :key="o.name"
          class="flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-surface-gray-1 transition-colors"
          :class="i < salesOrders.data.length - 1 ? 'border-b border-outline-gray-modals' : ''"
          @click="openDoc('CRM Sales Order', o.name)"
        >
          <div class="flex flex-1 flex-col gap-0.5 min-w-0">
            <div class="font-medium text-ink-gray-9 text-sm truncate">
              {{ o.name }}
            </div>
            <div class="text-xs text-ink-gray-6 flex items-center gap-2">
              <span>{{ formatDate(o.date) }}</span>
              <DotIcon class="h-2 w-2 text-ink-gray-4" :radius="2" />
              <span>{{ n_fmt(o.grand_total) }}</span>
            </div>
          </div>
          <Badge :label="o.status" :theme="statusTheme(o.status)" />
          <Button
            variant="ghost"
            :tooltip="__('Download PDF')"
            icon="download"
            @click.stop="downloadPdf('CRM Sales Order', o.name)"
          />
        </div>
      </div>
      <div
        v-else
        class="rounded-lg border border-dashed border-outline-gray-2 py-5 text-center text-sm text-ink-gray-5"
      >
        {{ __('No sales orders yet') }}
      </div>
    </div>

    <!-- Invoices Section -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2">
          <ReceiptIcon class="h-4 w-4 text-ink-gray-6" />
          {{ __('Invoices') }}
        </h3>
        <Button
          size="sm"
          variant="outline"
          :label="__('New Invoice')"
          icon-left="plus"
          @click="createDoc('CRM Invoice')"
        />
      </div>
      <div v-if="invoices.loading" class="py-4 flex justify-center">
        <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
      </div>
      <div
        v-else-if="invoices.data?.length"
        class="rounded-lg border border-outline-gray-modals overflow-hidden"
      >
        <div
          v-for="(inv, i) in invoices.data"
          :key="inv.name"
          class="flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-surface-gray-1 transition-colors"
          :class="i < invoices.data.length - 1 ? 'border-b border-outline-gray-modals' : ''"
          @click="openDoc('CRM Invoice', inv.name)"
        >
          <div class="flex flex-1 flex-col gap-0.5 min-w-0">
            <div class="font-medium text-ink-gray-9 text-sm truncate">
              {{ inv.name }}
            </div>
            <div class="text-xs text-ink-gray-6 flex items-center gap-2">
              <span>{{ formatDate(inv.date) }}</span>
              <DotIcon class="h-2 w-2 text-ink-gray-4" :radius="2" />
              <span>{{ n_fmt(inv.grand_total) }}</span>
              <DotIcon v-if="inv.due_date" class="h-2 w-2 text-ink-gray-4" :radius="2" />
              <span v-if="inv.due_date">{{ __('Due') }}: {{ formatDate(inv.due_date) }}</span>
            </div>
          </div>
          <Badge :label="inv.status" :theme="statusTheme(inv.status)" />
          <Button
            variant="ghost"
            :tooltip="__('Download PDF')"
            icon="download"
            @click.stop="downloadPdf('CRM Invoice', inv.name)"
          />
        </div>
      </div>
      <div
        v-else
        class="rounded-lg border border-dashed border-outline-gray-2 py-5 text-center text-sm text-ink-gray-5"
      >
        {{ __('No invoices yet') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import DotIcon from '@/components/Icons/DotIcon.vue'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import FileTextIcon from '~icons/lucide/file-text'
import ShoppingCartIcon from '~icons/lucide/shopping-cart'
import ReceiptIcon from '~icons/lucide/receipt'
import { formatDate } from '@/utils'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { createResource, Badge, Button } from 'frappe-ui'
import { watch } from 'vue'

const props = defineProps({
  doctype: { type: String, required: true },
  docname: { type: String, required: true },
})

const { showModal } = useDoctypeModal()

function downloadPdf(doctype, docname) {
  const url = `/api/method/crm.api.cpq.download_pdf?doctype=${encodeURIComponent(doctype)}&docname=${encodeURIComponent(docname)}`
  window.open(url, '_blank')
}

function n_fmt(val) {
  if (val == null) return '—'
  return new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(val)
}

function statusTheme(status) {
  const map = {
    Draft: 'gray',
    Sent: 'blue',
    Accepted: 'green',
    Rejected: 'red',
    Confirmed: 'blue',
    Completed: 'green',
    Cancelled: 'red',
    Unpaid: 'orange',
    Paid: 'green',
    Overdue: 'red',
  }
  return map[status] || 'gray'
}

function openDoc(doctype, name) {
  showModal({
    name,
    doctype,
    title: doctype,
    callbacks: {
      afterUpdate: () => {
        quotations.reload()
        salesOrders.reload()
        invoices.reload()
      },
    },
  })
}

function createDoc(doctype) {
  const defaults = { deal: props.docname }
  showModal({
    doctype,
    title: doctype,
    defaults,
    callbacks: {
      afterInsert: () => {
        quotations.reload()
        salesOrders.reload()
        invoices.reload()
      },
    },
  })
}

const quotations = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Quotation',
    filters: [['deal', '=', props.docname]],
    fields: ['name', 'date', 'grand_total', 'status'],
    order_by: 'creation desc',
    limit: 50,
  },
  auto: true,
})

const salesOrders = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Sales Order',
    filters: [['deal', '=', props.docname]],
    fields: ['name', 'date', 'grand_total', 'status'],
    order_by: 'creation desc',
    limit: 50,
  },
  auto: true,
})

const invoices = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Invoice',
    filters: [['deal', '=', props.docname]],
    fields: ['name', 'date', 'due_date', 'grand_total', 'status'],
    order_by: 'creation desc',
    limit: 50,
  },
  auto: true,
})

// Reload when docname changes
watch(
  () => props.docname,
  () => {
    quotations.reload()
    salesOrders.reload()
    invoices.reload()
  },
)
</script>
