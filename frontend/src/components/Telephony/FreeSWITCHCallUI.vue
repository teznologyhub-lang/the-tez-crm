<template>
  <div v-show="showCallPopup" v-bind="$attrs">
    <div
      ref="callPopup"
      class="fixed z-20 flex w-60 cursor-move select-none flex-col rounded-lg bg-surface-gray-7 p-4 text-ink-gray-2 shadow-2xl"
      :style="style"
    >
      <div class="flex flex-row-reverse items-center gap-1">
        <MinimizeIcon
          class="h-4 w-4 cursor-pointer"
          @click="toggleCallWindow"
        />
      </div>
      <div class="flex flex-col items-center justify-center gap-3">
        <Avatar
          v-if="contact?.image"
          :image="contact.image"
          :label="contact.full_name"
          class="relative flex !h-24 !w-24 items-center justify-center [&>div]:text-[30px]"
          :class="onCall || calling ? '' : 'pulse'"
        />
        <div class="flex flex-col items-center justify-center gap-1">
          <div class="text-xl font-medium">
            {{ contact?.full_name ?? __('Unknown') }}
          </div>
          <div class="text-sm text-ink-gray-5">{{ contact?.mobile_no }}</div>
        </div>
        <CountUpTimer ref="counterUp">
          <div v-if="onCall" class="my-1 text-base">
            {{ counterUp?.updatedTime }}
          </div>
        </CountUpTimer>
        <div v-if="!onCall" class="my-1 text-base">
          {{
            callStatus == 'initiating'
              ? __('Initiating call...')
              : callStatus == 'ringing'
                ? __('Ringing...')
                : calling
                  ? __('Calling...')
                  : __('Incoming call...')
          }}
        </div>
        <div v-if="onCall" class="flex gap-2">
          <Button
            :icon="muted ? 'mic-off' : 'mic'"
            class="rounded-full"
            @click="toggleMute"
          />
          <Button
            class="cursor-pointer rounded-full"
            :tooltip="__('Add a Note')"
            :icon="NoteIcon"
            @click="openNoteModal"
          />
          <Button
            class="rounded-full bg-surface-red-5 hover:bg-surface-red-6 rotate-[135deg] text-ink-white"
            :tooltip="__('Hang Up')"
            :icon="PhoneIcon"
            @click="hangUpCall"
          />
        </div>
        <div v-else-if="calling || callStatus == 'initiating'">
          <Button
            size="md"
            variant="solid"
            theme="red"
            :label="__('Cancel')"
            class="rounded-lg text-ink-white"
            :disabled="callStatus == 'initiating'"
            @click="cancelCall"
          >
            <template #prefix>
              <PhoneIcon class="rotate-[135deg]" />
            </template>
          </Button>
        </div>
        <div v-else class="flex gap-2">
          <Button
            size="md"
            variant="solid"
            theme="green"
            :label="__('Accept')"
            class="rounded-lg text-ink-white"
            :iconLeft="PhoneIcon"
            @click="acceptIncomingCall"
          />
          <Button
            size="md"
            variant="solid"
            theme="red"
            :label="__('Reject')"
            class="rounded-lg text-ink-white"
            @click="rejectIncomingCall"
          >
            <template #prefix>
              <PhoneIcon class="rotate-[135deg]" />
            </template>
          </Button>
        </div>
      </div>
    </div>
  </div>
  <div
    v-show="showSmallCallWindow"
    class="ml-2 flex cursor-pointer select-none items-center justify-between gap-3 rounded-lg bg-surface-gray-7 px-2 py-[7px] text-base text-ink-gray-2"
    v-bind="$attrs"
    @click="toggleCallWindow"
  >
    <div class="flex items-center gap-2">
      <Avatar
        v-if="contact?.image"
        :image="contact.image"
        :label="contact.full_name"
        class="relative flex !h-5 !w-5 items-center justify-center"
      />
      <div class="max-w-[120px] truncate">
        {{ contact?.full_name ?? __('Unknown') }}
      </div>
    </div>
    <div v-if="onCall" class="flex items-center gap-2">
      <div class="my-1 min-w-[40px] text-center">
        {{ counterUp?.updatedTime }}
      </div>
      <Button
        variant="solid"
        theme="red"
        class="!h-6 !w-6 rounded-full rotate-[135deg] text-ink-white"
        :icon="PhoneIcon"
        @click.stop="hangUpCall"
      />
    </div>
    <div v-else-if="calling" class="flex items-center gap-3">
      <div class="my-1">
        {{ callStatus == 'ringing' ? __('Ringing...') : __('Calling...') }}
      </div>
      <Button
        variant="solid"
        theme="red"
        class="!h-6 !w-6 rounded-full rotate-[135deg] text-ink-white"
        :icon="PhoneIcon"
        @click.stop="cancelCall"
      />
    </div>
    <div v-else class="flex items-center gap-2">
      <Button
        variant="solid"
        theme="green"
        class="pulse relative !h-6 !w-6 rounded-full animate-pulse text-ink-white"
        :tooltip="__('Accept Call')"
        :icon="PhoneIcon"
        @click.stop="acceptIncomingCall"
      />
      <Button
        variant="solid"
        theme="red"
        class="!h-6 !w-6 rounded-full rotate-[135deg] text-ink-white"
        :tooltip="__('Reject Call')"
        :icon="PhoneIcon"
        @click.stop="rejectIncomingCall"
      />
    </div>
  </div>

  <!-- Hidden audio element to bind FreeSWITCH audio stream -->
  <audio ref="remoteAudio" autoplay></audio>
</template>

<script setup>
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import MinimizeIcon from '@/components/Icons/MinimizeIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import CountUpTimer from '@/components/CountUpTimer.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { useDraggable, useWindowSize } from '@vueuse/core'
import { useTelemetry, useOnboarding } from 'frappe-ui/frappe'
import { Avatar, call, createResource } from 'frappe-ui'
import { ref, watch } from 'vue'
import { UA, WebSocketInterface } from 'jssip'

const { capture } = useTelemetry()
const { updateOnboardingStep } = useOnboarding('frappecrm')

let ua = null
let _call = null
let log = ref('Connecting...')

const remoteAudio = ref(null)
const showCallPopup = ref(false)
const showSmallCallWindow = ref(false)
const onCall = ref(false)
const calling = ref(false)
const muted = ref(false)
const callPopup = ref(null)
const counterUp = ref(null)
const callStatus = ref('')

const phoneNumber = ref('')

const contact = ref({
  full_name: '',
  image: '',
  mobile_no: '',
})

watch(phoneNumber, (value) => {
  if (!value) return
  getContact.fetch()
})

const getContact = createResource({
  url: 'crm.integrations.api.get_contact_by_phone_number',
  makeParams() {
    return {
      phone_number: phoneNumber.value,
    }
  },
  cache: ['contact', phoneNumber.value],
  onSuccess(data) {
    contact.value = data
  },
})

const { showModal } = useDoctypeModal()
const note = ref({
  name: '',
  title: '',
  content: '',
})

function openNoteModal() {
  showModal({
    name: note.value.name || null,
    doctype: 'CRM Call Log',
    title: 'Call Log',
    callbacks: {
      afterInsert: (n) => updateNote(n, true),
      afterUpdate: updateNote,
    },
  })
}

async function updateNote(_note, isInsert = false) {
  note.value = _note
  if (isInsert && _note.name && _call) {
    await call('crm.integrations.api.add_note_to_call_log', {
      call_sid: _call.id,
      note: _note,
    })
    updateOnboardingStep('create_first_note')
    capture('note_created')
  } else {
    capture('note_updated')
  }
}

const { width, height } = useWindowSize()

let { style } = useDraggable(callPopup, {
  initialValue: { x: width.value - 280, y: height.value - 310 },
  preventDefault: true,
})

async function startupClient() {
  log.value = 'Requesting FreeSWITCH Agent Configuration...'

  try {
    const config = await call('crm.integrations.freeswitch.api.get_freeswitch_agent_config')
    if (config.ok) {
      log.value = 'Got config. Initializing SIP User Agent...'
      initializeDevice(config)
    } else {
      log.value = 'Failed to load config: ' + config.detail
    }
  } catch (err) {
    log.value = 'An error occurred. ' + err.message
  }
}

function initializeDevice(config) {
  try {
    const socket = new WebSocketInterface(config.wss_url)
    const sipConfiguration = {
      sockets: [socket],
      uri: `sip:${config.extension}@${config.server_address}`,
      password: config.password,
    }

    ua = new UA(sipConfiguration)
    addDeviceListeners()
    ua.start()
  } catch (err) {
    log.value = 'SIP UA Initialization failed: ' + err.message
  }
}

function addDeviceListeners() {
  ua.on('registered', () => {
    log.value = 'Ready to make and receive FreeSWITCH calls!'
  })

  ua.on('unregistered', () => {
    log.value = 'SIP Registration Lost'
  })

  ua.on('registrationFailed', (e) => {
    log.value = 'SIP Registration Failed: ' + e.cause
  })

  ua.on('newRTCSession', (data) => {
    const session = data.session
    if (session.direction === 'incoming') {
      handleIncomingCall(session)
    }
  })
}

function toggleMute() {
  if (!_call) return
  if (_call.isMuted().audio) {
    _call.unmute({ audio: true })
    muted.value = false
  } else {
    _call.mute({ audio: true })
    muted.value = true
  }
}

function handleIncomingCall(session) {
  log.value = `Incoming call from ${session.remote_identity.uri.user}`
  phoneNumber.value = session.remote_identity.uri.user

  showCallPopup.value = true
  _call = session

  session.on('peerconnection', (data) => {
    bindAudioStream(data.peerconnection)
  })

  session.on('accepted', () => {
    log.value = 'Accepted incoming call.'
    onCall.value = true
    counterUp.value.start()
  })

  session.on('ended', handleDisconnectedCall)
  session.on('failed', handleDisconnectedCall)
}

function bindAudioStream(peerconnection) {
  peerconnection.addEventListener('track', (e) => {
    if (remoteAudio.value && e.streams[0]) {
      remoteAudio.value.srcObject = e.streams[0]
    }
  })
}

function acceptIncomingCall() {
  if (!_call) return
  _call.answer({
    mediaConstraints: { audio: true, video: false }
  })
}

function rejectIncomingCall() {
  if (!_call) return
  _call.terminate()
  handleDisconnectedCall()
}

function hangUpCall() {
  if (!_call) return
  _call.terminate()
  handleDisconnectedCall()
}

function cancelCall() {
  if (!_call) return
  _call.terminate()
  handleDisconnectedCall()
}

function handleDisconnectedCall() {
  log.value = 'Call ended'
  showCallPopup.value = false
  showSmallCallWindow.value = false
  _call = null
  muted.value = false
  onCall.value = false
  calling.value = false
  callStatus.value = ''
  if (counterUp.value) {
    counterUp.value.stop()
  }
  note.value = {
    name: '',
    title: '',
    content: '',
  }
}

async function makeOutgoingCall(number) {
  phoneNumber.value = number

  if (ua) {
    log.value = `Attempting to call ${number} ...`

    try {
      showCallPopup.value = true
      callStatus.value = 'initiating'
      calling.value = true
      capture('make_outgoing_call')

      const options = {
        mediaConstraints: { audio: true, video: false },
        rtcOfferConstraints: { offerToReceiveAudio: 1, offerToReceiveVideo: 0 }
      }

      _call = ua.call(`sip:${number}@${ua.configuration.uri.host}`, options)

      _call.on('peerconnection', (data) => {
        bindAudioStream(data.peerconnection)
      })

      _call.on('progress', () => {
        callStatus.value = 'ringing'
        log.value = 'Ringing...'
      })

      _call.on('accepted', () => {
        log.value = 'Call accepted'
        calling.value = false
        onCall.value = true
        if (counterUp.value) {
          counterUp.value.start()
        }
      })

      _call.on('ended', handleDisconnectedCall)
      _call.on('failed', handleDisconnectedCall)

    } catch (error) {
      log.value = `Could not connect call: ${error.message}`
      handleDisconnectedCall()
    }
  } else {
    log.value = 'SIP UA not initialized.'
  }
}

function toggleCallWindow() {
  showCallPopup.value = !showCallPopup.value
  showSmallCallWindow.value = !showSmallCallWindow.value
}

watch(
  () => log.value,
  (value) => {
    console.log(value)
  },
  { immediate: true },
)

defineExpose({ makeOutgoingCall, setup: startupClient })
</script>

<style scoped>
.pulse::before {
  content: '';
  position: absolute;
  border: 1px solid green;
  width: calc(100% + 20px);
  height: calc(100% + 20px);
  border-radius: 50%;
  animation: pulse 1s linear infinite;
}

.pulse::after {
  content: '';
  position: absolute;
  border: 1px solid green;
  width: calc(100% + 20px);
  height: calc(100% + 20px);
  border-radius: 50%;
  animation: pulse 1s linear infinite;
  animation-delay: 0.3s;
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }

  50% {
    transform: scale(1);
    opacity: 1;
  }

  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}
</style>
