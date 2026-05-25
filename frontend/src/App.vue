<template>
  <div class="app-root">
    <header class="app-header">
      <div class="brand">
        <div class="logo">✨</div>
        <div>
          <div class="brand-title">Latex在线编辑系统</div>
        </div>
      </div>
      <div class="toolbar">
        <button v-if="$route.name === 'history'" class="btn-history" @click="goBack">返回编辑</button>
        <button v-else-if="$route.name !== 'auth'" class="btn-history" @click="goHistory">历史记录</button>

        <div v-if="$route.name !== 'auth'" ref="dropdownRef" class="dropdown">
          <button class="btn-export" @click="showExportMenu = !showExportMenu">导 出</button>
          <div v-if="showExportMenu" class="dropdown-menu">
            <button @click="exportFile('md')">导出为 .md</button>
            <button @click="exportFile('pdf')">导出为 PDF</button>
            <button @click="exportFile('txt')">导出为 .txt</button>
          </div>
        </div>

        <button v-if="$route.name !== 'auth'" class="btn-save" @click="saveDraft">保 存</button>

        <template v-if="store.user">
          <span class="user-badge">{{ store.user.username }}</span>
          <button class="btn-logout" @click="logout">退出</button>
        </template>
        <button v-else-if="$route.name !== 'auth'" class="btn-auth" @click="goAuth">登录 / 注册</button>
      </div>
    </header>

    <main :class="{ 'history-main': $route.name === 'history' }">
      <router-view />
    </main>

    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from './store/useAppStore'
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getMe, createRecord } from './lib/apiClient'

const store = useAppStore()
const router = useRouter()
const route = useRoute()
const showExportMenu = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' }>({ show: false, message: '', type: 'success' })

let toastTimer: number | undefined

function showToast(message: string, type: 'success' | 'error' = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { show: true, message, type }
  toastTimer = window.setTimeout(() => { toast.value.show = false }, 2000)
}

function requireAuth(): boolean {
  if (!store.user) {
    router.push('/auth')
    return false
  }
  return true
}

// 路由变化时同步 body 样式
watch(
  () => route.name,
  (name) => {
    document.body.classList.toggle('history-mode', name === 'history')
  },
  { immediate: true }
)

onMounted(async () => {
  if (store.token) {
    const resp = await getMe()
    if (resp.code === 0) {
      store.user = resp.data
    } else {
      store.clearAuth()
    }
  }
})

function onDocumentClick(event: MouseEvent) {
  if (!showExportMenu.value) return
  const target = event.target as Node | null
  if (dropdownRef.value && target && dropdownRef.value.contains(target)) return
  showExportMenu.value = false
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
})

function goBack() {
  router.back()
}

function goHistory() {
  if (!requireAuth()) return
  router.push('/history')
}

function goAuth() {
  router.push('/auth')
}

function logout() {
  store.editorContent = ''
  store.currentRecordId = null
  store.currentInputText = ''
  store.requestHistory = []
  store.clearAuth()
  router.push('/')
}

async function saveDraft() {
  if (!requireAuth()) return
  const content = store.editorContent.trim()
  if (!content) {
    showToast('请先输入内容再保存', 'error')
    return
  }
  const resp = await createRecord({
    content,
    record_id: store.currentRecordId ?? undefined,
  })
  if (resp.code !== 0) {
    showToast('保存失败: ' + (resp.message || '未知错误'), 'error')
    return
  }
  if (!store.currentRecordId && resp.data?.record_id) {
    store.currentRecordId = resp.data.record_id
  }
  showToast('保存成功')
}

function exportFile(format: 'md' | 'pdf' | 'txt') {
  if (!requireAuth()) return
  const content = store.editorContent || ''
  const fileName = `markdown_${new Date().getTime()}`

  if (format === 'md') {
    downloadFile(content, `${fileName}.md`, 'text/markdown')
  } else if (format === 'txt') {
    downloadFile(content, `${fileName}.txt`, 'text/plain')
  } else if (format === 'pdf') {
    exportToPdf(content, fileName)
  }

  showExportMenu.value = false
}

function downloadFile(content: string, fileName: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

async function exportToPdf(content: string, fileName: string) {
  try {
    const html2pdf = (await import('html2pdf.js')).default
    const element = document.createElement('div')
    element.innerHTML = `<style>.pdf-content{font-family: monospace; white-space: pre-wrap; word-wrap: break-word;}</style><pre class="pdf-content">${escapeHtml(content)}</pre>`
    const opt = {
      margin: 10,
      filename: `${fileName}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
    }
    html2pdf().set(opt).from(element).save()
  } catch {
    showToast('PDF导出需要安装html2pdf库', 'error')
  }
}

function escapeHtml(text: string) {
  const map: Record<string, string> = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, m => map[m])
}
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
}

main.history-main {
  display: block;
  flex: none;
  height: calc(100vh - 64px);
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

main.history-main::-webkit-scrollbar {
  display: none;
}

:global(body.history-mode) {
  overflow: auto;
}

header.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: 64px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.btn-history {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: linear-gradient(135deg, var(--bg-dark) 0%, var(--surface) 100%);
  color: var(--text-primary);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-history:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
}

.dropdown { position: relative; }

.btn-save {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.btn-export {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 140px;
  margin-top: 4px;
  overflow: hidden;
}

.dropdown-menu button {
  display: block;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: none;
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  transition: all 0.2s ease;
}

.dropdown-menu button:hover {
  background: var(--bg-dark);
  color: var(--primary);
}

.btn-auth {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-auth:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.user-badge {
  padding: 6px 14px;
  border-radius: 8px;
  background: var(--bg-dark);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
}

.btn-logout {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-logout:hover {
  color: #ef4444;
  border-color: #ef4444;
}

.toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 28px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  z-index: 99999;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: toast-in 0.3s ease;
}

.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }

@keyframes toast-in {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
