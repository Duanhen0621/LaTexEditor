<template>
  <div class="auth-page" @mousemove="onMouseMove">
    <!-- Math symbols background -->
    <div class="math-bg" ref="mathBgRef">
      <span class="math-sym">∑</span>
      <span class="math-sym">∫</span>
      <span class="math-sym">π</span>
      <span class="math-sym">√</span>
      <span class="math-sym">∞</span>
      <span class="math-sym">Δ</span>
      <span class="math-sym">θ</span>
      <span class="math-sym">α</span>
      <span class="math-sym">β</span>
      <span class="math-sym">γ</span>
      <span class="math-sym">λ</span>
      <span class="math-sym">φ</span>
      <span class="math-sym">∈</span>
      <span class="math-sym">⊂</span>
      <span class="math-sym">∪</span>
      <span class="math-sym">∩</span>
      <span class="math-sym">∂</span>
      <span class="math-sym">∇</span>
      <span class="math-sym">∏</span>
      <span class="math-sym">⇒</span>
      <span class="math-sym">∀</span>
      <span class="math-sym">∃</span>
      <span class="math-sym">⊥</span>
      <span class="math-sym">≅</span>
    </div>

    <div class="auth-card">
      <div class="card-header">
        <div class="logo-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 7V4h16v3" />
            <path d="M9 20h6" />
            <path d="M12 4v16" />
            <path d="M6 12h4" />
            <path d="M14 12h4" />
          </svg>
        </div>
        <h1 class="card-title">LaTeX 在线编辑</h1>
        <p class="card-sub">登录以保存你的文档和历史记录</p>
      </div>

      <div class="tabs">
        <button :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
        <button :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</button>
        <div class="tab-bar" :class="mode" />
      </div>

      <div class="form-wrapper">
        <transition name="shift" mode="out-in">
          <form v-if="mode === 'login'" key="login" @submit.prevent="submit" class="form-body">
            <div class="field">
              <label>用户名</label>
              <div class="input-box">
                <svg class="i-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-8 8-8s8 4 8 8"/></svg>
                <input v-model="form.username" type="text" placeholder="输入用户名" required />
              </div>
            </div>
            <div class="field">
              <label>密码</label>
              <div class="input-box">
                <svg class="i-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <input v-model="form.password" type="password" placeholder="输入密码" required />
              </div>
            </div>
            <transition name="fade"><p v-if="errorMsg" class="err">{{ errorMsg }}</p></transition>
            <button type="submit" class="btn-go" :disabled="loading">
              <span v-if="!loading">登 录</span>
              <span v-else class="spinner" />
            </button>
          </form>

          <form v-else key="register" @submit.prevent="submit" class="form-body">
            <div class="field">
              <label>用户名</label>
              <div class="input-box">
                <svg class="i-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-8 8-8s8 4 8 8"/></svg>
                <input v-model="form.username" type="text" placeholder="输入用户名" required />
              </div>
            </div>
            <div class="field">
              <label>密码</label>
              <div class="input-box">
                <svg class="i-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                <input v-model="form.password" type="password" placeholder="至少 6 位" required />
              </div>
            </div>
            <div class="field">
              <label>邮箱 <span class="opt">选填</span></label>
              <div class="input-box">
                <svg class="i-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/></svg>
                <input v-model="form.email" type="email" placeholder="用于找回密码" />
              </div>
            </div>
            <transition name="fade"><p v-if="errorMsg" class="err">{{ errorMsg }}</p></transition>
            <button type="submit" class="btn-go" :disabled="loading">
              <span v-if="!loading">注 册</span>
              <span v-else class="spinner" />
            </button>
          </form>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { login as apiLogin, register as apiRegister } from '../lib/apiClient'
import { useAppStore } from '../store/useAppStore'

const store = useAppStore()
const router = useRouter()
const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const errorMsg = ref('')
const form = reactive({ username: '', password: '', email: '' })

// Animation state
const mathBgRef = ref<HTMLElement | null>(null)

const depths = [
  0.6, 0.4, 0.7, 0.35, 0.5, 0.45, 0.55, 0.3,
  0.5, 0.65, 0.4, 0.6, 0.35, 0.5, 0.45, 0.55,
  0.4, 0.6, 0.5, 0.35, 0.55, 0.45, 0.5, 0.4,
]
const phases = [
  0, 1.8, 3.0, 0.8, 2.5, 1.2, 4.0, 0.5,
  2.0, 3.5, 1.0, 2.8, 0.3, 1.5, 3.2, 4.5,
  0.7, 2.2, 3.8, 1.6, 0.2, 1.9, 3.3, 4.2,
]

let rafId = 0
let targetX = 0
let targetY = 0
// Smoothed offset — lerps toward target each frame
let smoothX = 0
let smoothY = 0

function onMouseMove(e: MouseEvent) {
  targetX = e.clientX
  targetY = e.clientY
}

function updateFrame() {
  try {
    const t = performance.now() / 1000

    const parent = mathBgRef.value?.parentElement
    if (parent) {
      const rect = parent.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2

      const rawX = (targetX - cx) * 0.07
      const rawY = (targetY - cy) * 0.07

      smoothX += (rawX - smoothX) * 0.06
      smoothY += (rawY - smoothY) * 0.06
    }

    const symbols = mathBgRef.value?.querySelectorAll('.math-sym')
    if (symbols) {
      for (let i = 0; i < symbols.length; i++) {
        const el = symbols[i] as HTMLElement
        if (!el) continue
        const d = depths[i % depths.length]
        const p = phases[i % phases.length]

        const idleX = Math.sin(t * 0.4 + p) * 35 * (0.5 + d * 0.8)
        const idleY = Math.cos(t * 0.3 + p * 1.3) * 25 * (0.5 + d * 0.6)
        const px = smoothX * d
        const py = smoothY * d

        el.style.transform = `translate(${idleX + px}px, ${idleY + py}px)`
      }
    }
  } catch { /* noop */ }
  rafId = requestAnimationFrame(updateFrame)
}

onMounted(() => {
  const parent = mathBgRef.value?.parentElement
  if (parent) {
    const rect = parent.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    targetX = cx
    targetY = cy
    smoothX = 0
    smoothY = 0
  }
  rafId = requestAnimationFrame(updateFrame)
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
})

function switchMode(m: 'login' | 'register') {
  if (m === mode.value) return
  errorMsg.value = ''
  mode.value = m
}

async function submit() {
  loading.value = true; errorMsg.value = ''
  try {
    const act = mode.value === 'login' ? apiLogin : apiRegister
    const data = mode.value === 'login'
      ? { username: form.username, password: form.password }
      : { username: form.username, password: form.password, email: form.email || undefined }
    const resp = await act(data as any)

    if (mode.value === 'login') {
      if (resp.code !== 0) { errorMsg.value = resp.message || '用户名或密码错误'; return }
      store.setToken(resp.data.token); store.user = resp.data.user; router.push('/')
    } else {
      if (resp.code !== 0) { errorMsg.value = resp.message || '注册失败'; return }
      errorMsg.value = ''; form.password = ''; mode.value = 'login'
    }
  } catch { errorMsg.value = '网络错误，请稍后重试'
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  position: relative;
  overflow: hidden;
}

/* ── Math Symbols Background ── */
.math-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.math-sym {
  position: absolute;
  font-family: 'Times New Roman', 'CMU Serif', serif;
  font-weight: 700;
  color: rgba(59, 130, 246, .13);
  will-change: transform;
  user-select: none;
}
.math-bg :nth-child(1) { font-size: 52px; top: 5%; left: 4%; }
.math-bg :nth-child(2) { font-size: 46px; top: 12%; right: 5%; }
.math-bg :nth-child(3) { font-size: 40px; bottom: 30%; left: 3%; }
.math-bg :nth-child(4) { font-size: 50px; bottom: 8%; right: 4%; }
.math-bg :nth-child(5) { font-size: 38px; top: 44%; left: 2%; }
.math-bg :nth-child(6) { font-size: 44px; top: 28%; right: 3%; }
.math-bg :nth-child(7) { font-size: 36px; bottom: 48%; right: 15%; }
.math-bg :nth-child(8) { font-size: 34px; top: 65%; left: 12%; }
.math-bg :nth-child(9) { font-size: 32px; bottom: 18%; right: 25%; }
.math-bg :nth-child(10) { font-size: 30px; top: 7%; left: 50%; }
.math-bg :nth-child(11) { font-size: 36px; top: 52%; right: 2%; }
.math-bg :nth-child(12) { font-size: 34px; bottom: 38%; left: 55%; }
.math-bg :nth-child(13) { font-size: 40px; top: 78%; left: 5%; }
.math-bg :nth-child(14) { font-size: 32px; bottom: 4%; left: 28%; }
.math-bg :nth-child(15) { font-size: 36px; top: 36%; left: 40%; }
.math-bg :nth-child(16) { font-size: 34px; top: 18%; right: 35%; }
.math-bg :nth-child(17) { font-size: 38px; bottom: 14%; right: 6%; }
.math-bg :nth-child(18) { font-size: 42px; top: 3%; right: 40%; }
.math-bg :nth-child(19) { font-size: 40px; bottom: 55%; left: 8%; }
.math-bg :nth-child(20) { font-size: 34px; top: 72%; right: 8%; }
.math-bg :nth-child(21) { font-size: 32px; bottom: 22%; right: 40%; }
.math-bg :nth-child(22) { font-size: 30px; top: 88%; left: 22%; }
.math-bg :nth-child(23) { font-size: 36px; top: 55%; left: 25%; }
.math-bg :nth-child(24) { font-size: 32px; bottom: 6%; right: 50%; }

/* ── Card ── */
.auth-card {
  position: relative;
  z-index: 1;
  width: 400px;
  max-width: 92vw;
  background: #fff;
  border-radius: 16px;
  padding: 40px 36px 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}

/* ── Header ── */
.card-header { text-align: center; margin-bottom: 28px; }
.logo-mark {
  width: 44px; height: 44px;
  margin: 0 auto 12px;
  background: #2563eb;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.logo-mark svg { width: 22px; height: 22px; }
.card-title { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.card-sub { font-size: 14px; color: #94a3b8; margin: 0; }

/* ── Tabs ── */
.tabs {
  display: flex;
  position: relative;
  margin-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}
.tabs button {
  flex: 1;
  padding: 10px 0 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  transition: color .2s;
}
.tabs button.active { color: #2563eb; }
.tab-bar {
  position: absolute;
  bottom: -1px;
  height: 2px;
  width: 50%;
  background: #2563eb;
  transition: transform .25s;
}
.tab-bar.register { transform: translateX(100%); }

/* ── Form ── */
.form-wrapper { overflow: hidden; }
.form-body { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 13px; font-weight: 500; color: #475569; }
.opt { font-weight: 400; color: #94a3b8; font-size: 12px; margin-left: 4px; }

.input-box {
  position: relative;
  display: flex;
  align-items: center;
}
.i-icon {
  position: absolute; left: 12px;
  width: 16px; height: 16px;
  color: #94a3b8;
  pointer-events: none;
  transition: color .2s;
}
.input-box:focus-within .i-icon { color: #2563eb; }

.input-box input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  transition: border-color .2s;
  box-sizing: border-box;
}
.input-box input:focus { border-color: #2563eb; }
.input-box input::placeholder { color: #94a3b8; }

/* ── Error ── */
.err {
  margin: 0;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  text-align: center;
}

/* ── Submit ── */
.btn-go {
  display: flex; align-items: center; justify-content: center;
  height: 42px;
  border: none; border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-size: 15px; font-weight: 600;
  letter-spacing: 4px;
  cursor: pointer;
  transition: background .2s;
  margin-top: 4px;
}
.btn-go:hover:not([disabled]) { background: #1d4ed8; }
.btn-go[disabled] { opacity: .5; cursor: not-allowed; }

/* ── Spinner ── */
.spinner {
  width: 20px; height: 20px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transitions ── */
.shift-enter-active, .shift-leave-active { transition: all .2s ease; }
.shift-enter-from { opacity: 0; transform: translateX(20px); }
.shift-leave-to { opacity: 0; transform: translateX(-20px); }

.fade-enter-active, .fade-leave-active { transition: opacity .15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
