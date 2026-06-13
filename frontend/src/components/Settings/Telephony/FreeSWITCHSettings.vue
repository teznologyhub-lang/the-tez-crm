<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex gap-1 items-center">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="__('FreeSWITCH Settings')"
          size="md"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-xl hover:opacity-70 !pr-0 !max-w-96 !justify-start"
          @click="emit('updateStep', 'telephony-settings')"
        />
        <Badge
          v-if="freeswitch.doc?.enabled && isDirty"
          :label="__('Not Saved')"
          variant="subtle"
          theme="orange"
        />
      </div>
    </template>
    <template #header-actions>
      <div v-if="freeswitch.doc?.enabled && !freeswitch.get.loading" class="flex gap-2">
        <Button
          v-if="isDirty"
          :label="__('Discard Changes')"
          variant="subtle"
          @click="freeswitch.reload()"
        />
        <Button :label="__('Disable')" variant="subtle" @click="disable" />
        <Button
          variant="solid"
          :label="__('Update')"
          :loading="freeswitch.save.loading"
          :disabled="!isDirty"
          @click="update"
        />
      </div>
    </template>
    <template #content>
      <div v-if="freeswitch.doc" class="h-full">
        <div v-if="freeswitch.doc.enabled" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="freeswitch.doc.server_address"
              :label="__('SIP Server Address')"
              type="text"
              placeholder="sip.example.com"
              required
              autocomplete="off"
            />
            <FormControl
              v-model="freeswitch.doc.wss_url"
              :label="__('WSS URL')"
              type="text"
              placeholder="wss://sip.example.com:7443"
              required
              autocomplete="off"
            />
            <FormControl
              v-model="freeswitch.doc.esl_host"
              :label="__('ESL Host')"
              type="text"
              placeholder="127.0.0.1"
              autocomplete="off"
            />
            <FormControl
              v-model="freeswitch.doc.esl_port"
              :label="__('ESL Port')"
              type="number"
              placeholder="8021"
              autocomplete="off"
            />
            <Password
              v-model="freeswitch.doc.esl_password"
              :label="__('ESL Password')"
              placeholder="************"
            />
          </div>
          <div class="h-px border-t border-outline-gray-modals" />
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <div class="text-p-base font-medium text-ink-gray-7 truncate">
                {{ __('Record Calls') }}
              </div>
              <div class="text-p-sm text-ink-gray-5 truncate">
                {{
                  __('Enable call recording for FreeSWITCH calls')
                }}
              </div>
            </div>
            <div>
              <Switch v-model="freeswitch.doc.record_calls" size="sm" />
            </div>
          </div>
        </div>
        <!--  Disabled state -->
        <div v-else class="relative flex h-full w-full justify-center">
          <div
            class="absolute left-1/2 flex w-64 -translate-x-1/2 flex-col items-center gap-3"
            :style="{ top: '35%' }"
          >
            <div class="flex flex-col items-center gap-1.5 text-center">
              <PhoneIcon class="size-7.5 text-ink-gray-7" />
              <span class="text-lg font-medium text-ink-gray-8">
                {{ __('FreeSWITCH Integration Disabled') }}
              </span>
              <span class="text-center text-p-base text-ink-gray-6">
                {{
                  __(
                    'Enable FreeSWITCH integration to make and receive calls directly from your CRM',
                  )
                }}
              </span>
              <Button :label="__('Enable')" variant="solid" @click="enable" />
            </div>
          </div>
        </div>
      </div>
      <div
        v-else-if="freeswitch.get.loading"
        class="flex items-center justify-center mt-[35%]"
      >
        <LoadingIndicator class="size-6" />
      </div>
    </template>
  </SettingsLayoutBase>
</template>
<script setup>
import { setEnabled } from '@/composables/telephony'
import { useDocument } from '@/data/document'
import { Switch, FormControl, Password } from 'frappe-ui'
import { computed } from 'vue'

const emit = defineEmits(['updateStep'])

const { document: freeswitch } = useDocument(
  'CRM FreeSWITCH Settings',
  'CRM FreeSWITCH Settings',
)

function enable() {
  freeswitch.doc.enabled = true
}

function disable() {
  freeswitch.doc.enabled = false
  update()
}

function update() {
  freeswitch.save.submit(null, {
    onSuccess: () => freeswitch.reload(),
  })

  setEnabled('freeswitch', freeswitch.doc.enabled)
}

const isDirty = computed(() => {
  return (
    freeswitch.doc &&
    freeswitch.originalDoc &&
    JSON.stringify(freeswitch.doc) !== JSON.stringify(freeswitch.originalDoc)
  )
})
</script>
