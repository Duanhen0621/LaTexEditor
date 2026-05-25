<template>
  <div class="interaction-panel">
    <!-- Header -->
    <div class="panel-header">
      <h3>💬 聊天与操作</h3>
    </div>

    <!-- 聊天历史 -->
    <div class="history-area">
      <div v-for="(h, idx) in history" :key="idx" class="history-item">
        <div class="history-content">
          <p>{{ h.summary }}</p>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="imageUrl" class="preview-section preview-section-image">
      <img :src="imageUrl" class="preview-image" />
      <div class="preview-actions">
        <button class="btn-small btn-success" @click="sendImage" :disabled="sending">🔍 识别</button>
        <button class="btn-small btn-cancel" @click="cancelImage" :disabled="sending">✕ 取消</button>
      </div>
    </div>

    <!-- 音频预览 -->
    <div v-if="audioUrl" class="preview-section preview-section-audio">
      <audio :src="audioUrl" controls controlsList="nodownload noplaybackrate" class="preview-audio" />
      <div class="preview-actions">
        <button class="btn-small btn-success" @click="uploadAudio" :disabled="sending">📤 上传</button>
        <button class="btn-small btn-cancel" @click="cancelAudio" :disabled="sending">✕ 取消</button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <!-- 顶部操作按钮 -->
      <div class="action-buttons-top">
        <button class="btn-action btn-voice" @click="toggleRecord" :disabled="sending" title="录制语音">
          <span class="btn-text">语音输入</span>
          <span v-if="recording" class="recording-badge">{{ remaining }}s</span>
        </button>
        <label class="btn-action btn-image" title="上传图片">
          <span class="btn-text">图片识别</span>
          <input type="file" accept="image/*" @change="onImage" />
        </label>
      </div>

      <!-- 消息输入栏 -->
      <div class="input-bar">
        <textarea v-model="text" placeholder="输入需求..." class="message-input"></textarea>
        <button class="btn-send" @click="sendChat" :disabled="sending || !text.trim()">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAppStore } from '../store/useAppStore'
import { useRecorder } from '../composables/useRecorder'
import { postOcr, postSpeech, postChat } from '../lib/apiClient'

const store = useAppStore()

const file = ref<File | null>(null)
const imageUrl = ref<string | null>(null)
const sending = ref(false)
const audioBlob = ref<Blob | null>(null)

const text = ref(store.currentInputText)

const history = computed(() => store.requestHistory)

const { start, stop, recording, remaining } = useRecorder({ maxSeconds: 60 })
const audioUrl = ref<string | null>(null)

async function onImage(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    file.value = input.files[0]
    imageUrl.value = URL.createObjectURL(file.value)
  }
}

async function sendImage() {
  if (!file.value) return alert('请选择图片')
  sending.value = true
  try {
    const form = new FormData()
    form.append('file', file.value)
    store.addHistory('图片识别中...')
    const resp = await postOcr(form)
    if (resp.code !== 0) {
      store.addHistory(`识别失败: ${resp.message}`)
      return
    }
    
    let ocrResult = '识别结果'
    const type = resp.res?.type
    
    if (type === 'formula') {
      ocrResult = resp.res?.info || '识别结果'
    } else if (type === 'doc') {
      ocrResult = resp.res?.info?.markdown || '识别结果'
    }
    
    store.addHistory(`识别结果: ${ocrResult}`)
    cancelImage()
  } finally { sending.value = false }
}

function cancelImage() {
  imageUrl.value = null
  file.value = null
}

async function toggleRecord() {
  if (!recording.value) {
    await start()
  } else {
    const b = await stop()
    if (!b) return
    audioBlob.value = b
    audioUrl.value = URL.createObjectURL(b)
  }
}

async function uploadAudio() {
  if (!audioBlob.value) return
  sending.value = true
  try {
    const form = new FormData()
    form.append('file', audioBlob.value, 'recording.wav')
    form.append('language', 'cn')
    store.addHistory('语音转写中...')
    const resp = await postSpeech(form)
    if (resp.code !== 0) {
      store.addHistory(`转写失败: ${resp.message}`)
      return
    }
    const speechText = resp.res?.text || ''
      text.value = text.value + (text.value ? '\n' + speechText : speechText)
    store.setCurrentInputText(text.value)
    store.addHistory(`转写结果: ${speechText}`)
    cancelAudio()
  } finally { sending.value = false }
}

function cancelAudio() {
  audioUrl.value = null
  audioBlob.value = null
}

async function sendChat() {
  if (!text.value || !text.value.trim()) return alert('请输入消息')
  sending.value = true
  try {
    const form = new FormData()
    form.append('message', text.value)
    form.append('system_prompt', "你是一个latex公式编写专家，根据用户提出的需求，返回用户想要的latex代码，不要任何多余的解释和文本。")
    store.addHistory('模型调用中...')
    const resp = await postChat(form)
    if (resp.code !== 0) {
      store.addHistory(`调用失败: ${resp.message}`)
      return
    }
    const reply = resp.res?.reply || '无回复'
    store.addHistory(`AI回复: ${reply}`)
    text.value = ''
    store.setCurrentInputText('')
  } finally { sending.value = false }
}

watch(() => store.currentInputText, (v) => { text.value = v })

</script>

<style scoped>
.interaction-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--surface);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.panel-header h3 {
  color: #15803d;
  font-weight: 700;
  margin: 0;
  font-size: 16px;
}

/* History / Chat Area */
.history-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
  display: flex;
  flex-direction: column-reverse;
  gap: 8px;
  align-items: stretch;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.history-area::-webkit-scrollbar {
  display: none;
}

.history-item {
  display: block;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  flex-shrink: 0;
  background: var(--bg-dark);
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--text-primary);
}

.history-item:hover {
  background: #e8f5e9;
  transform: translateX(2px);
}

.history-content {
  min-width: 0;
}

.history-content p {
  margin: 0;
  font-size: 13px;
  color: var(--text-primary);
  word-break: break-word;
  white-space: normal;
  line-height: 1.6;
}

/* Preview Sections */
.preview-section {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-dark);
  border-radius: 8px;
  margin: 0 12px;
}

.preview-section-audio {
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

.preview-section-image .preview-actions {
  margin-left: auto;
}

.preview-image {
  max-height: 60px;
  max-width: 80px;
  border-radius: 6px;
}

.preview-audio {
  width: 100%;
  min-width: 0;
  height: 36px;
}

/* Hide volume slider and download button */
.preview-audio::-webkit-media-controls-mute-button {
  display: none;
}

.preview-audio::-webkit-media-controls-volume-slider {
  display: none;
}

.preview-audio::-webkit-media-controls-download-button {
  display: none;
}

.preview-audio::-webkit-media-controls-timeline {
  flex: 1;
}

.preview-audio::-moz-media-controls-mute-button {
  display: none;
}

.preview-audio::-moz-media-controls-volume-slider {
  display: none;
}

.preview-audio::-moz-media-controls-download-button {
  display: none;
}

/* Preview Actions Container */
.preview-actions {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: flex-end;
}

/* Small Button Base */
.btn-small {
  flex-shrink: 0;
  padding: 6px 10px;
  font-size: 12px;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
}

/* Success Button */
.btn-small.btn-success {
  background: var(--success);
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.2);
}

.btn-small.btn-success:hover:not([disabled]) {
  background: #059669;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* Cancel Button */
.btn-small.btn-cancel {
  background: #ef4444;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.2);
}

.btn-small.btn-cancel:hover:not([disabled]) {
  background: #dc2626;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
}

.btn-small[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
/* Input Section */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border-light);
  background: var(--surface);
  flex-shrink: 0;
}

/* Input Bar */
.input-bar {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 150px;
  max-height: 300px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-primary);
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: all 0.2s ease;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.message-input::-webkit-scrollbar {
  display: none;
}

.message-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.message-input::placeholder {
  color: var(--text-secondary);
}

/* Action Buttons Top Container */
.action-buttons-top {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Action Button Style Base */
.btn-action {
  flex: 1;
  min-width: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-decoration: none;
}

/* Voice Button */
.btn-voice {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
}

.btn-voice:hover:not([disabled]) {
  background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.btn-voice:active:not([disabled]) {
  transform: translateY(-1px);
}

/* Image Button */
.btn-image {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
}

.btn-image:hover:not([disabled]) {
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
}

.btn-image:active:not([disabled]) {
  transform: translateY(-1px);
}

/* Button Disabled State */
.btn-action[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Button Text */
.btn-action .btn-text {
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.3px;
}

/* File Input */
.btn-action input {
  display: none;
}

.recording-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-radius: 50%;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  animation: pulse 1s infinite;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.btn-send {
  flex-shrink: 0;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

.btn-send:hover:not([disabled]) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-send:active:not([disabled]) {
  transform: translateY(0);
}

.btn-send[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
