import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserInfo {
  user_id: number
  username: string
  email: string | null
  created_at?: string
}

export const useAppStore = defineStore('app', () => {
  // ---- Auth state ----
  const token = ref(localStorage.getItem('auth_token') || '')
  const user = ref<UserInfo | null>(null)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('auth_token', t)
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
  }

  // ---- Editor state ----
  const editorContent = ref('')
  const currentRecordId = ref<number | null>(null)
  const currentInputText = ref('')
  const requestHistory = ref<Array<{ summary: string }>>([])

  function setEditorContent(v: string) { editorContent.value = v }
  function setCurrentRecordId(v: number | null) { currentRecordId.value = v }
  function setCurrentInputText(v: string) { currentInputText.value = v }
  function addHistory(summary: string) { requestHistory.value.unshift({ summary }) }

  return {
    // Auth
    token,
    user,
    setToken,
    clearAuth,
    // Editor
    editorContent,
    currentRecordId,
    currentInputText,
    requestHistory,
    setEditorContent,
    setCurrentRecordId,
    setCurrentInputText,
    addHistory,
  }
})
