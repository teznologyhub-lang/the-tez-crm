<template>
  <Dialog v-model="show" :options="{ title: __('Send SMS'), size: 'lg' }">
    <template #body-content>
      <div class="space-y-4 py-2">
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Recipient Mobile Number') }}</label>
          <Input
            v-model="mobile"
            placeholder="e.g. 254712345678 or 0712345678"
            class="w-full"
          />
        </div>

        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-xs font-medium text-ink-gray-7">{{ __('SMS Message') }}</label>
            <span class="text-[11px]" :class="charCount > 160 ? 'text-amber-600 font-semibold' : 'text-ink-gray-5'">
              {{ charCount }} / 160 {{ segmentCount > 1 ? `(${segmentCount} SMS segments)` : '' }}
            </span>
          </div>
          <Textarea
            v-model="message"
            placeholder="Type your SMS message here..."
            rows="4"
            class="w-full"
          />
        </div>

        <div class="pt-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium text-ink-gray-7">{{ __('Schedule for Later') }}</span>
            <Switch v-model="isScheduled" />
          </div>

          <div v-if="isScheduled" class="mt-2">
            <Input
              v-model="timeToSend"
              type="datetime-local"
              class="w-full text-xs"
            />
            <p class="text-[11px] text-ink-gray-5 mt-1">
              {{ __('Select a future date and time for sending this SMS.') }}
            </p>
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" :label="__('Cancel')" @click="show = false" />
      <Button
        variant="solid"
        :loading="sending"
        :label="isScheduled ? __('Schedule SMS') : __('Send SMS')"
        @click="submitSms"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { call, toast, Dialog, Input, Textarea, Button, Switch } from 'frappe-ui'

const props = defineProps({
  doctype: { type: String, default: 'CRM Lead' },
  doc: { type: Object, default: () => ({}) },
})

const show = defineModel('show', { type: Boolean, default: false })
const emit = defineEmits(['sent'])

const mobile = ref('')
const message = ref('')
const isScheduled = ref(false)
const timeToSend = ref('')
const sending = ref(false)

watch(
  () => show.value,
  (val) => {
    if (val && props.doc) {
      mobile.value = props.doc.mobile_no || props.doc.phone || props.doc.mobile || ''
      message.value = ''
      isScheduled.value = false
      timeToSend.value = ''
    }
  }
)

const charCount = computed(() => message.value.length)
const segmentCount = computed(() => Math.ceil(message.value.length / 160) || 1)

async function submitSms() {
  if (!mobile.value) {
    toast.error(__('Recipient phone number is required.'))
    return
  }
  if (!message.value) {
    toast.error(__('SMS message content cannot be empty.'))
    return
  }

  sending.value = true
  try {
    const formattedTime = isScheduled.value && timeToSend.value ? timeToSend.value.replace('T', ' ') : null

    const res = await call('crm.api.sms.send_sms', {
      mobile: mobile.value,
      message: message.value,
      time_to_send: formattedTime,
      ref_doctype: props.doctype,
      ref_docname: props.doc?.name,
    })

    if (res && res.success) {
      toast.success(isScheduled.value ? __('SMS Scheduled successfully!') : __('SMS Sent successfully!'))
      show.value = false
      emit('sent')
    } else {
      toast.error(res?.error || __('Failed to send SMS'))
    }
  } catch (err) {
    toast.error(err.message || __('Error occurred while sending SMS.'))
  } finally {
    sending.value = false
  }
}
</script>
