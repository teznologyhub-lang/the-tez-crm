<template>
  <div class="flex flex-col h-full bg-surface-modal p-6 overflow-y-auto">
    <div class="flex items-center justify-between pb-4 border-b border-border-subtle">
      <div>
        <h2 class="text-lg font-semibold text-ink-gray-9">{{ __('SMS Gateway Settings') }}</h2>
        <p class="text-xs text-ink-gray-5 mt-0.5">
          {{ __('Configure SMS providers to send transactional and promotional messages directly from TezCRM.') }}
        </p>
      </div>
      <Button
        variant="solid"
        :loading="saving"
        :label="__('Save Settings')"
        @click="saveSettings"
      />
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12 text-ink-gray-4">
      <Spinner class="w-6 h-6" />
      <span class="ml-2 text-sm">{{ __('Loading SMS configuration...') }}</span>
    </div>

    <div v-else class="mt-6 space-y-6 max-w-2xl">
      <!-- Global SMS Settings -->
      <div class="bg-surface-gray-2 rounded-lg p-4 border border-border-subtle space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm font-medium text-ink-gray-9">{{ __('Enable Global SMS Integration') }}</span>
            <p class="text-xs text-ink-gray-5">
              {{ __('Master toggle to activate or deactivate SMS features across TezCRM.') }}
            </p>
          </div>
          <Switch v-model="settings.sms_enabled" />
        </div>

        <div v-if="settings.sms_enabled" class="pt-3 border-t border-border-subtle">
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Default SMS Provider') }}</label>
          <Select
            v-model="settings.default_provider"
            :options="[
              { label: 'TextSMS (Kenya API)', value: 'TextSMS' },
              { label: 'HostPinnacle Bulk SMS (Coming Soon)', value: 'HostPinnacle', disabled: true }
            ]"
            class="w-full"
          />
        </div>
      </div>

      <!-- TextSMS Provider Card -->
      <div class="bg-surface-modal border border-border-subtle rounded-lg p-5 space-y-4 shadow-sm">
        <div class="flex items-center justify-between pb-3 border-b border-border-subtle">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg">
              TS
            </div>
            <div>
              <h3 class="text-sm font-semibold text-ink-gray-9">TextSMS API</h3>
              <p class="text-xs text-ink-gray-5">https://sms.textsms.co.ke</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Badge :variant="settings.textsms.enabled ? 'green' : 'gray'">
              {{ settings.textsms.enabled ? __('Active') : __('Disabled') }}
            </Badge>
            <Switch v-model="settings.textsms.enabled" />
          </div>
        </div>

        <div v-if="settings.textsms.enabled" class="space-y-4 pt-1">
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Partner ID') }}</label>
            <Input
              v-model="settings.textsms.partner_id"
              placeholder="e.g. 123"
              class="w-full"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Shortcode / Sender ID') }}</label>
            <Input
              v-model="settings.textsms.shortcode"
              placeholder="e.g. SENDERID or TezCRM"
              class="w-full"
            />
          </div>

          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('API Key') }}</label>
            <div class="relative">
              <Input
                v-model="settings.textsms.api_key"
                :type="showApiKey ? 'text' : 'password'"
                placeholder="Enter your TextSMS API Key"
                class="w-full pr-10"
              />
              <button
                type="button"
                class="absolute right-3 top-2.5 text-xs text-ink-gray-5 hover:text-ink-gray-8"
                @click="showApiKey = !showApiKey"
              >
                {{ showApiKey ? __('Hide') : __('Show') }}
              </button>
            </div>
          </div>

          <div class="pt-2 flex justify-end">
            <Button
              variant="outline"
              size="sm"
              :label="__('Send Test SMS')"
              @click="showTestModal = true"
            />
          </div>
        </div>
      </div>

      <!-- HostPinnacle Provider Card (Upcoming) -->
      <div class="bg-surface-modal border border-border-subtle rounded-lg p-5 opacity-75">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center font-bold text-lg">
              HP
            </div>
            <div>
              <h3 class="text-sm font-semibold text-ink-gray-9">HostPinnacle Bulk SMS</h3>
              <p class="text-xs text-ink-gray-5">{{ __('Modular provider framework ready for HostPinnacle integration.') }}</p>
            </div>
          </div>
          <Badge variant="orange">{{ __('Coming Soon') }}</Badge>
        </div>
      </div>
    </div>

    <!-- Test SMS Dialog -->
    <Dialog v-model="showTestModal" :options="{ title: __('Send Test SMS') }">
      <template #body-content>
        <div class="space-y-4 py-2">
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Recipient Mobile Number') }}</label>
            <Input
              v-model="testMobile"
              placeholder="e.g. 254712345678 or 0712345678"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-ink-gray-7 mb-1">{{ __('Message') }}</label>
            <Textarea
              v-model="testMessage"
              placeholder="Enter test message"
              rows="3"
              class="w-full"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" :label="__('Cancel')" @click="showTestModal = false" />
        <Button variant="solid" :loading="sendingTest" :label="__('Send Now')" @click="sendTestSms" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call, toast, Button, Input, Select, Switch, Badge, Spinner, Dialog, Textarea } from 'frappe-ui'

const loading = ref(true)
const saving = ref(false)
const showApiKey = ref(false)
const showTestModal = ref(false)
const sendingTest = ref(false)

const testMobile = ref('')
const testMessage = ref('TezCRM Test SMS - TextSMS integration working successfully!')

const settings = ref({
  sms_enabled: false,
  default_provider: 'TextSMS',
  textsms: {
    enabled: false,
    partner_id: '',
    shortcode: '',
    api_key: '',
  },
})

async function fetchSettings() {
  loading.value = true
  try {
    const res = await call('crm.api.sms.get_sms_settings')
    if (res) {
      settings.value = res
    }
  } catch (err) {
    toast.error(err.message || __('Failed to fetch SMS settings'))
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await call('crm.api.sms.save_sms_settings', {
      sms_enabled: settings.value.sms_enabled ? 1 : 0,
      default_provider: settings.value.default_provider,
      textsms_enabled: settings.value.textsms.enabled ? 1 : 0,
      partner_id: settings.value.textsms.partner_id,
      shortcode: settings.value.textsms.shortcode,
      api_key: settings.value.textsms.api_key,
    })
    toast.success(__('SMS Settings saved successfully'))
  } catch (err) {
    toast.error(err.message || __('Failed to save SMS settings'))
  } finally {
    saving.value = false
  }
}

async function sendTestSms() {
  if (!testMobile.value) {
    toast.error(__('Please enter a recipient mobile number'))
    return
  }
  sendingTest.value = true
  try {
    const res = await call('crm.api.sms.send_test_sms', {
      mobile: testMobile.value,
      message: testMessage.value,
    })
    if (res && res.success) {
      toast.success(__('Test SMS sent successfully!'))
      showTestModal.value = false
    } else {
      toast.error(res?.error || __('Failed to send test SMS'))
    }
  } catch (err) {
    toast.error(err.message || __('Error sending test SMS'))
  } finally {
    sendingTest.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
