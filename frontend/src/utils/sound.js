let audioCtx = null

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext
    if (AudioContextClass) {
      audioCtx = new AudioContextClass()
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {})
  }
  return audioCtx
}

if (typeof window !== 'undefined') {
  const unlockAudio = () => {
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume().catch(() => {})
    }
    window.removeEventListener('click', unlockAudio)
    window.removeEventListener('keydown', unlockAudio)
    window.removeEventListener('touchstart', unlockAudio)
  }
  window.addEventListener('click', unlockAudio)
  window.addEventListener('keydown', unlockAudio)
  window.addEventListener('touchstart', unlockAudio)
}

/**
 * Plays a pleasant, subtle synthesized sound for CRM notifications and popups using Web Audio API.
 * @param {'notification' | 'popup'} type 
 */
export function playNotificationSound(type = 'notification') {
  try {
    const ctx = getAudioContext()
    if (!ctx) return

    const now = ctx.currentTime

    if (type === 'popup' || type === 'event') {
      // Warm 3-tone chime for pop-ups (C5 -> E5 -> G5)
      const notes = [523.25, 659.25, 783.99]
      notes.forEach((freq, idx) => {
        const startTime = now + idx * 0.07
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()

        osc.type = 'sine'
        osc.frequency.setValueAtTime(freq, startTime)

        gain.gain.setValueAtTime(0.18, startTime)
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.25)

        osc.connect(gain)
        gain.connect(ctx.destination)

        osc.start(startTime)
        osc.stop(startTime + 0.25)
      })
    } else {
      // Standard dual-tone chime (E5 -> B5)
      const osc1 = ctx.createOscillator()
      const gain1 = ctx.createGain()
      osc1.type = 'sine'
      osc1.frequency.setValueAtTime(659.25, now) // E5
      gain1.gain.setValueAtTime(0.15, now)
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.3)
      osc1.connect(gain1)
      gain1.connect(ctx.destination)

      const osc2 = ctx.createOscillator()
      const gain2 = ctx.createGain()
      osc2.type = 'sine'
      osc2.frequency.setValueAtTime(987.77, now + 0.08) // B5
      gain2.gain.setValueAtTime(0.18, now + 0.08)
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.4)
      osc2.connect(gain2)
      gain2.connect(ctx.destination)

      osc1.start(now)
      osc1.stop(now + 0.3)
      osc2.start(now + 0.08)
      osc2.stop(now + 0.4)
    }
  } catch (err) {
    console.warn('Could not play notification sound:', err)
  }
}
