<template>
  <div>
    <div
      v-show="showSmallCallPopup"
      class="ml-2 flex cursor-pointer select-none items-center justify-between gap-1 rounded-full bg-surface-gray-7 px-2 py-[7px] text-base text-ink-gray-2"
      @click="toggleCallPopup"
    >
      <div
        class="flex justify-center items-center size-5 rounded-full bg-surface-gray-6 shrink-0 mr-1"
      >
        <Avatar
          v-if="contact?.image"
          :image="contact.image"
          :label="contact.full_name"
          class="!size-5"
        />
        <AvatarIcon v-else class="size-3" />
      </div>
      <span>{{ contact?.full_name ?? contact?.mobile_no }}</span>
      <span>·</span>
      <div v-if="callStatus == 'In progress'">
        {{ counterUp?.updatedTime }}
      </div>
      <div
        v-else-if="callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed'"
        class="blink"
        :class="{
          'text-red-700':
            callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed',
        }"
      >
        <span>{{ __(callStatus) }}</span>
        <span v-if="callStatus == 'Call ended'">
          <span> · </span>
          <span>{{ callDuration }}</span>
        </span>
      </div>
      <div v-else>{{ __(callStatus) }}</div>

      <!-- Quick Actions for small window -->
      <div class="ml-2 flex items-center gap-1">
        <Button
          v-if="onCall"
          variant="solid"
          theme="red"
          class="!h-6 !w-6 rounded-full rotate-[135deg] text-ink-white"
          :icon="PhoneIcon"
          @click.stop="hangUpCall"
        />
        <Button
          v-else-if="calling || callStatus == 'Initiating...'"
          variant="solid"
          theme="red"
          class="!h-6 !w-6 rounded-full rotate-[135deg] text-ink-white"
          :icon="PhoneIcon"
          @click.stop="cancelCall"
        />
        <template v-else-if="callStatus == 'Incoming call'">
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
        </template>
      </div>
    </div>

    <div
      v-show="showCallPopup"
      class="fixed z-20 w-[310px] min-h-44 flex gap-2 flex-col rounded-lg bg-surface-gray-7 p-4 pt-2.5 text-ink-gray-2 shadow-2xl"
      :style="style"
      @click.stop
    >
      <div
        ref="callPopupHeader"
        class="header flex items-center justify-between gap-1 text-base cursor-move select-none"
      >
        <div class="flex gap-2 items-center truncate">
          <div
            v-if="showNote || showTask"
            class="flex items-center gap-3 truncate"
          >
            <Avatar
              v-if="contact?.image"
              :image="contact.image"
              :label="contact.full_name"
              class="!size-7 shrink-0"
            />
            <div
              v-else
              class="flex justify-center items-center size-7 rounded-full bg-surface-gray-6 shrink-0"
            >
              <AvatarIcon class="size-3" />
            </div>
            <div
              class="flex flex-col gap-1 text-base leading-4 overflow-hidden"
            >
              <div class="font-medium truncate">
                {{ contact?.full_name ?? contact?.mobile_no }}
              </div>
              <div class="text-ink-gray-6">
                <div v-if="callStatus == 'In progress'">
                  <span>{{ contact?.mobile_no }}</span>
                  <span> · </span>
                  <span>{{ counterUp?.updatedTime }}</span>
                </div>
                <div
                  v-else-if="
                    callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed'
                  "
                  class="blink"
                  :class="{
                    'text-red-700':
                      callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed',
                  }"
                >
                  <span>{{ __(callStatus) }}</span>
                  <span v-if="callStatus == 'Call ended'">
                    <span> · </span>
                    <span>{{ callDuration }}</span>
                  </span>
                </div>
                <div v-else>{{ __(callStatus) }}</div>
              </div>
            </div>
          </div>
          <div v-else>
            <div v-if="callStatus == 'In progress'">
              {{ counterUp?.updatedTime }}
            </div>
            <div
              v-else-if="
                callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed'
              "
              class="blink"
              :class="{
                'text-red-700':
                  callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed',
              }"
            >
              <span>{{ __(callStatus) }}</span>
              <span v-if="callStatus == 'Call ended'">
                <span> · </span>
                <span>{{ callDuration }}</span>
              </span>
            </div>
            <div v-else>{{ __(callStatus) }}</div>
          </div>
        </div>

        <div class="flex">
          <Button
            class="bg-surface-gray-7 text-ink-white hover:bg-surface-gray-6 shrink-0 cursor-pointer"
            :tooltip="__('Minimize')"
            :icon="MinimizeIcon"
            size="md"
            @click="toggleCallPopup"
          />
          <Button
            v-if="callStatus == 'Call ended' || callStatus == 'No answer' || callStatus == 'Canceled' || callStatus == 'Rejected' || callStatus == 'Failed'"
            class="bg-surface-gray-7 text-ink-white hover:bg-surface-gray-6 shrink-0"
            icon="x"
            size="md"
            @click="closeCallPopup"
          />
        </div>
      </div>
      <div class="body flex-1">
        <div v-if="showNote">
          <TextEditor
            ref="content"
            variant="ghost"
            editor-class="prose-sm h-[290px] text-ink-white overflow-auto mt-1"
            :bubbleMenu="true"
            :content="note.content"
            :placeholder="__('Take a note...')"
            @change="(val) => (note.content = val)"
          />
        </div>
        <TaskPanel v-else-if="showTask" ref="taskRef" :task="task" />
        <div v-else class="flex flex-col items-center justify-center gap-3 py-4">
          <Avatar
            v-if="contact?.image"
            :image="contact.image"
            :label="contact.full_name"
            class="relative flex !h-24 !w-24 items-center justify-center [&>div]:text-[30px]"
            :class="onCall || calling ? '' : 'pulse'"
          />
          <div
            v-else
            class="flex justify-center items-center !size-24 rounded-full bg-surface-gray-6"
            :class="onCall || calling ? '' : 'pulse'"
          >
            <AvatarIcon class="size-12" />
          </div>
          <div v-if="contact?.full_name" class="flex flex-col gap-1 items-center">
            <div class="text-xl font-medium leading-5">
              {{ contact.full_name }}
            </div>
            <div class="text-base text-ink-gray-6 leading-4">
              {{ contact.mobile_no }}
            </div>
          </div>
          <div v-else class="text-xl font-medium leading-5">
            {{ contact.mobile_no || phoneNumber }}
          </div>
        </div>
      </div>
      <div class="footer flex justify-between gap-2 items-center">
        <div class="flex gap-2">
          <Button
            class="bg-surface-gray-6 text-ink-white hover:bg-surface-gray-5"
            :tooltip="__('Add a Note')"
            size="md"
            :icon="NoteIcon"
            @click="showNoteWindow"
          />
          <Button
            class="bg-surface-gray-6 text-ink-white hover:bg-surface-gray-5"
            size="md"
            :tooltip="__('Add a Task')"
            :icon="TaskIcon"
            @click="showTaskWindow"
          />
          <Button
            v-if="contact?.deal || contact?.lead"
            class="bg-surface-gray-6 text-ink-white hover:bg-surface-gray-5"
            size="md"
            :iconRight="ArrowUpRightIcon"
            :label="contact.deal ? __('Deal') : __('Lead')"
            @click="openDealOrLead"
          />
        </div>

        <div class="flex gap-2 items-center">
          <template v-if="!(onCall || calling || callStatus == 'Incoming call' || callStatus == 'Initiating...')">
            <Button
              v-if="(note.name || task.name) && dirty"
              class="bg-surface-white !text-ink-gray-9 hover:!bg-surface-gray-3"
              variant="solid"
              :label="__('Update')"
              size="md"
              @click="update"
            />
            <Button
              v-else-if="
                ((note?.content && note.content != '<p></p>') || task.title) &&
                !note.name &&
                !task.name
              "
              class="bg-surface-white !text-ink-gray-9 hover:!bg-surface-gray-3"
              variant="solid"
              :label="__('Save')"
              size="md"
              @click="save"
            />
          </template>

          <!-- Softphone Controls -->
          <template v-if="onCall || calling || callStatus == 'Incoming call' || callStatus == 'Initiating...'">
            <Button
              v-if="onCall"
              :icon="muted ? 'mic-off' : 'mic'"
              class="rounded-full bg-surface-gray-6 text-ink-white hover:bg-surface-gray-5"
              @click="toggleMute"
            />
            <Button
              v-if="onCall"
              class="rounded-full bg-surface-red-5 hover:bg-surface-red-6 rotate-[135deg] text-ink-white"
              :tooltip="__('Hang Up')"
              :icon="PhoneIcon"
              @click="hangUpCall"
            />
            <Button
              v-else-if="calling || callStatus == 'Initiating...'"
              size="sm"
              variant="solid"
              theme="red"
              :label="__('Cancel')"
              class="rounded-lg text-ink-white"
              :disabled="callStatus == 'Initiating...'"
              @click="cancelCall"
            >
              <template #prefix>
                <PhoneIcon class="rotate-[135deg]" />
              </template>
            </Button>
            <template v-else-if="callStatus == 'Incoming call'">
              <Button
                size="sm"
                variant="solid"
                theme="green"
                :label="__('Accept')"
                class="rounded-lg text-ink-white"
                :iconLeft="PhoneIcon"
                @click="acceptIncomingCall"
              />
              <Button
                size="sm"
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
            </template>
          </template>
        </div>
      </div>
    </div>
    <CountUpTimer ref="counterUp" />
  </div>

  <!-- Hidden audio element to bind FreeSWITCH audio stream -->
  <audio ref="remoteAudio" autoplay></audio>
</template>

<script setup>
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import AvatarIcon from '@/components/Icons/AvatarIcon.vue'
import MinimizeIcon from '@/components/Icons/MinimizeIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskPanel from '@/components/Telephony/TaskPanel.vue'
import CountUpTimer from '@/components/CountUpTimer.vue'
import { globalStore } from '@/stores/global'
import { sessionStore } from '@/stores/session'
import { useDraggable, useWindowSize } from '@vueuse/core'
import { TextEditor, Avatar, Button, createResource, toast, call } from 'frappe-ui'
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { UA, WebSocketInterface } from 'jssip'
import { useTelemetry, useOnboarding } from 'frappe-ui/frappe'

const { capture } = useTelemetry()
const { updateOnboardingStep } = useOnboarding('frappecrm')

const { $socket } = globalStore()
const router = useRouter()

let ua = null
let _call = null
const remoteAudio = ref(null)

const callPopupHeader = ref(null)
const showCallPopup = ref(false)
let showSmallCallPopup = ref(false)
let onCall = ref(false)
let calling = ref(false)
let muted = ref(false)
const callStatus = ref('')
const callDuration = ref('00:00')
const phoneNumber = ref('')
const callData = ref(null)
const counterUp = ref(null)

const contact = ref({
  full_name: '',
  image: '',
  mobile_no: '',
})

function toggleCallPopup() {
  showCallPopup.value = !showCallPopup.value
  showSmallCallPopup.value = !showSmallCallPopup.value
}

const { width, height } = useWindowSize()

let { style } = useDraggable(callPopupHeader, {
  initialValue: { x: width.value - 350, y: height.value - 250 },
  preventDefault: true,
})

const getContact = createResource({
  url: 'crm.integrations.api.get_contact_by_phone_number',
  makeParams() {
    return {
      phone_number: phoneNumber.value,
    }
  },
  onSuccess(data) {
    contact.value = data
  },
})

watch(
  phoneNumber,
  (value) => {
    if (!value) return
    getContact.fetch()
  },
  { immediate: true },
)

const dirty = ref(false)

const note = ref({
  name: '',
  content: '',
})

const showNote = ref(false)

function showNoteWindow() {
  showNote.value = !showNote.value
  if (!showTask.value) {
    updateWindowHeight(showNote.value)
  }
  if (showNote.value) {
    showTask.value = false
  }
}

function createUpdateNote() {
  if (!callData.value || !(callData.value.CallSid || callData.value.uuid)) {
    toast.error(__('Call details not synced yet. Please try again in a few seconds.'))
    return
  }
  createResource({
    url: 'crm.integrations.api.add_note_to_call_log',
    params: {
      call_sid: callData.value.CallSid || callData.value.uuid,
      note: note.value,
    },
    auto: true,
    onSuccess(_note) {
      note.value['name'] = _note.name
      nextTick(() => {
        dirty.value = false
      })
      updateOnboardingStep('create_first_note')
      capture('note_created')
    },
  })
}

const task = ref({
  name: '',
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Backlog',
  priority: 'Low',
})

const showTask = ref(false)

function showTaskWindow() {
  showTask.value = !showTask.value
  if (!showNote.value) {
    updateWindowHeight(showTask.value)
  }
  if (showTask.value) {
    showNote.value = false
  }
}

function createUpdateTask() {
  if (!callData.value || !(callData.value.CallSid || callData.value.uuid)) {
    toast.error(__('Call details not synced yet. Please try again in a few seconds.'))
    return
  }
  createResource({
    url: 'crm.integrations.api.add_task_to_call_log',
    params: {
      call_sid: callData.value.CallSid || callData.value.uuid,
      task: task.value,
    },
    auto: true,
    onSuccess(_task) {
      task.value['name'] = _task.name
      nextTick(() => {
        dirty.value = false
      })
    },
  })
}

watch([note, task], () => (dirty.value = true), { deep: true })

function updateWindowHeight(condition) {
  let callPopup = callPopupHeader.value.parentElement
  let top = parseInt(callPopup.style.top)
  let updatedTop

  updatedTop = condition ? top - 224 : top + 224

  if (updatedTop < 0) {
    updatedTop = 10
  }

  callPopup.style.top = updatedTop + 'px'
}

function openDealOrLead() {
  if (contact.value?.deal) {
    router.push({
      name: 'Deal',
      params: { dealId: contact.value.deal },
    })
  } else if (contact.value?.lead) {
    router.push({
      name: 'Lead',
      params: { leadId: contact.value.lead },
    })
  }
}

function closeCallPopup() {
  showCallPopup.value = false
  showSmallCallPopup.value = false
  note.value = {
    name: '',
    content: '',
  }
  task.value = {
    name: '',
    title: '',
    description: '',
    assigned_to: '',
    due_date: '',
    status: 'Backlog',
    priority: 'Low',
  }
}

function save() {
  if (note.value.content) createUpdateNote()
  if (task.value.title) createUpdateTask()
}

function update() {
  if (note.value.content) createUpdateNote()
  if (task.value.title) createUpdateTask()
}

// Socket listening for Call Data from Backend FreeSWITCH Webhooks
function setupSocketListeners() {
  $socket.on('freeswitch_call', (data) => {
    const { user } = sessionStore()
    const agentEmail = user || user?.value
    if (data.agent_email === agentEmail || data.user === agentEmail) {
      callData.value = data
      
      // Fallback duration tracking
      if (data.status === 'Completed' || data.status === 'Failed') {
        if (!callDuration.value || callDuration.value === '00:00') {
          callDuration.value = counterUp.value?.getTime(data.duration || 0) || '00:00'
        }
      }
    }
  })
}

async function startupClient() {
  setupSocketListeners()
  try {
    const config = await call('crm.integrations.freeswitch.api.get_freeswitch_agent_config')
    if (config.ok) {
      initializeDevice(config)
    }
  } catch (err) {
    console.error('FreeSWITCH init error:', err)
  }
}

onBeforeUnmount(() => {
  $socket.off('freeswitch_call')
})

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
    console.error('SIP UA Initialization failed:', err)
  }
}

function addDeviceListeners() {
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
  phoneNumber.value = session.remote_identity.uri.user

  callStatus.value = 'Incoming call'
  showCallPopup.value = true
  showSmallCallPopup.value = false
  _call = session

  session.on('peerconnection', (data) => {
    bindAudioStream(data.peerconnection)
  })

  session.on('accepted', () => {
    callStatus.value = 'In progress'
    onCall.value = true
    counterUp.value.start()
  })

  session.on('ended', handleDisconnectedCall)
  session.on('failed', handleFailedCall)
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
  callStatus.value = 'Rejected'
  handleDisconnectedCall()
}

function hangUpCall() {
  if (!_call) return
  _call.terminate()
  callStatus.value = 'Call ended'
  handleDisconnectedCall()
}

function cancelCall() {
  if (!_call) return
  _call.terminate()
  callStatus.value = 'Canceled'
  handleDisconnectedCall()
}

function handleFailedCall() {
  callStatus.value = 'Failed'
  handleDisconnectedCall()
}

function handleDisconnectedCall() {
  if (callStatus.value === 'In progress' || callStatus.value === '') {
    callStatus.value = 'Call ended'
  }
  if (counterUp.value) {
    callDuration.value = counterUp.value.getTime() || '00:00'
    counterUp.value.stop()
  }
  
  _call = null
  muted.value = false
  onCall.value = false
  calling.value = false
}

async function makeOutgoingCall(number) {
  phoneNumber.value = number

  if (ua) {
    try {
      showCallPopup.value = true
      showSmallCallPopup.value = false
      callStatus.value = 'Initiating...'
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
        callStatus.value = 'Ringing...'
      })

      _call.on('accepted', () => {
        callStatus.value = 'In progress'
        calling.value = false
        onCall.value = true
        if (counterUp.value) {
          counterUp.value.start()
        }
      })

      _call.on('ended', handleDisconnectedCall)
      _call.on('failed', handleFailedCall)

    } catch (error) {
      console.error(`Could not connect call: ${error.message}`)
      handleFailedCall()
    }
  } else {
    toast.error(__('FreeSWITCH User Agent not initialized.'))
  }
}

defineExpose({ makeOutgoingCall, setup: startupClient })
</script>

<style scoped>
@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.blink {
  animation: blink 1s ease-in-out 6;
}

:deep(.ProseMirror) {
  caret-color: var(--ink-white);
}

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
