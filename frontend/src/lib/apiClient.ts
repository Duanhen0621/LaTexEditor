const BACKEND_BASE = ((import.meta as any).env?.VITE_BACKEND_BASE as string) || '/api'
const AI_BASE = ((import.meta as any).env?.VITE_AI_BASE as string) || '/ai'

async function postForm(path: string, form: FormData) {
  const res = await fetch(`${AI_BASE}${path}`, { method: 'POST', body: form })
  return res.json()
}

async function backendFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  }
  // 非 FormData 请求默认带 JSON Content-Type
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BACKEND_BASE}${path}`, { ...options, headers })
  return res.json()
}

// ---- Auth ----
export async function register(data: { username: string; password: string; email?: string }) {
  return backendFetch('/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function login(data: { username: string; password: string }) {
  return backendFetch('/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getMe() {
  return backendFetch('/v1/auth/me')
}

// ---- Records ----
export async function getRecords(params: { page?: number; page_size?: number; keyword?: string } = {}) {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.keyword) q.set('keyword', params.keyword)
  const query = q.toString()
  return backendFetch(`/v1/records${query ? '?' + query : ''}`)
}

export async function getRecord(id: number) {
  return backendFetch(`/v1/records/${id}`)
}

export async function createRecord(data: { content: string; input_type?: string; raw_text?: string; record_id?: number }) {
  return backendFetch('/v1/records', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateRecord(id: number, data: { content?: string; raw_text?: string }) {
  return backendFetch(`/v1/records/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteRecord(id: number) {
  return backendFetch(`/v1/records/${id}`, { method: 'DELETE' })
}

// ---- AI Service (unchanged) ----
export async function postOcr(form: FormData) {
  return postForm('/v1/ai/ocr', form)
}

export async function postSpeech(form: FormData) {
  return postForm('/v1/ai/speech', form)
}

export async function postChat(form: FormData) {
  return postForm('/v1/ai/chat', form)
}
