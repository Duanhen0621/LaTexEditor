import { ref } from 'vue'

export function useRecorder(opts: { maxSeconds?: number } = {}) {
  const maxSeconds = opts.maxSeconds || 60
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const recording = ref(false)
  const remaining = ref(maxSeconds)

  let chunks: Blob[] = []
  let recordedBlob: Blob | null = null
  let timer: number | undefined

  async function start() {
    if (recording.value) return
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    chunks = []
    recordedBlob = null
    mediaRecorder.value.ondataavailable = (e) => { if (e.data && e.data.size) chunks.push(e.data) }
    mediaRecorder.value.onstop = () => {
      recordedBlob = new Blob(chunks, { type: 'audio/wav' })
    }
    mediaRecorder.value.start()
    recording.value = true
    remaining.value = maxSeconds
    timer = window.setInterval(() => {
      remaining.value -= 1
      if (remaining.value <= 0) stop()
    }, 1000)
  }

  async function stop() {
    if (!mediaRecorder.value) return null
    mediaRecorder.value.stop()
    recording.value = false
    if (timer) window.clearInterval(timer)
    // wait a tick for onstop
    await new Promise((r) => setTimeout(r, 200))
    if (!recordedBlob) {
      // try to convert recorded chunks to wav via AudioContext
      try {
        const raw = new Blob(chunks, { type: chunks[0]?.type || 'audio/webm' })
        const wav = await blobToWav(raw)
        recordedBlob = wav
      } catch (err) {
        recordedBlob = new Blob(chunks, { type: chunks[0]?.type || 'audio/webm' })
      }
    }
    return recordedBlob
  }

  return { start, stop, recording, remaining }
}

async function blobToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer()
  const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext
  const audioCtx = new AudioCtx()
  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer)

  const numChannels = audioBuffer.numberOfChannels
  const sampleRate = audioBuffer.sampleRate
  const length = audioBuffer.length
  const result = new Float32Array(length)
  for (let ch = 0; ch < numChannels; ch++) {
    const channelData = audioBuffer.getChannelData(ch)
    for (let i = 0; i < length; i++) { result[i] += channelData[i] / numChannels }
  }

  const wavBuffer = encodeWAV(result, sampleRate)
  const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' })
  audioCtx.close()
  return wavBlob
}

function encodeWAV(samples: Float32Array, sampleRate: number) {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  function writeString(v: DataView, offset: number, str: string) { for (let i=0;i<str.length;i++) v.setUint8(offset+i,str.charCodeAt(i)) }
  let offset=0
  writeString(view, offset, 'RIFF'); offset+=4
  view.setUint32(offset, 36 + samples.length * 2, true); offset+=4
  writeString(view, offset, 'WAVE'); offset+=4
  writeString(view, offset, 'fmt '); offset+=4
  view.setUint32(offset, 16, true); offset+=4
  view.setUint16(offset, 1, true); offset+=2
  view.setUint16(offset, 1, true); offset+=2
  view.setUint32(offset, sampleRate, true); offset+=4
  view.setUint32(offset, sampleRate * 2, true); offset+=4
  view.setUint16(offset, 2, true); offset+=2
  view.setUint16(offset, 16, true); offset+=2
  writeString(view, offset, 'data'); offset+=4
  view.setUint32(offset, samples.length * 2, true); offset+=4
  let pos=44
  for (let i=0;i<samples.length;i++,pos+=2) {
    let s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(pos, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
  return view
}
