<template>
  <div class="history-page">
    <div class="page-header">
      <div>
        <h2>📚 历史记录</h2>
      </div>
      <div class="page-badge">共 {{ records.length }} 条</div>
    </div>

    <div class="history-body">
      <article v-for="record in records" :key="record.id" class="history-card">
        <div class="history-card-top">
          <div>
            <h3>{{ record.title }}</h3>
            <div class="meta">{{ record.createdAt }}</div>
          </div>
          <div class="history-actions">
            <button class="btn-continue" @click="continueEdit(record.id)">继续编辑</button>
            <button class="btn-delete" @click="removeRecord(record.id)">删除</button>
          </div>
        </div>

        <pre class="history-content">{{ previewContent(record.content) }}</pre>
      </article>

      <div v-if="records.length === 0" class="empty-state">
        暂无历史记录，请先在编辑页点击"保存"生成一条记录。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecords, getRecord, deleteRecord as deleteRecordApi } from '../lib/apiClient'
import { useAppStore } from '../store/useAppStore'

interface RecordItem {
  id: string
  title: string
  content: string
  createdAt: string
}

const router = useRouter()
const store = useAppStore()
const records = ref<RecordItem[]>([])

onMounted(async () => {
  await loadRecords()
})

async function loadRecords() {
  const resp = await getRecords({ page: 1, page_size: 50 })
  if (resp.code === 0) {
    records.value = (resp.data.list || []).map((r: any) => ({
      id: String(r.record_id),
      title: r.title,
      content: r.content,
      createdAt: r.created_at,
    }))
  }
}

async function continueEdit(id: string) {
  const resp = await getRecord(Number(id))
  if (resp.code !== 0) return
  store.editorContent = resp.data.content
  store.currentRecordId = Number(id)
  router.push('/')
}

async function removeRecord(id: string) {
  const ok = window.confirm('确定要删除这条历史记录吗？')
  if (!ok) return
  const resp = await deleteRecordApi(Number(id))
  if (resp.code !== 0) return
  await loadRecords()
}

function previewContent(content: string) {
  const lines = content.split('\n')
  const previewLines = lines.slice(0, 5)
  const suffix = lines.length > 5 ? '\n...' : ''
  return `${previewLines.join('\n')}${suffix}`
}
</script>

<style scoped>
.history-page {
  display: block;
  padding: 24px;
  width: min(100%, 1100px);
  margin: 0 auto;
  overflow: visible;
  box-sizing: border-box;
}

.history-body {
  display: block;
  width: 100%;
  margin-top: 16px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.page-header h2 {
  margin: 0 0 6px;
  color: var(--text-primary);
}

.page-badge {
  flex-shrink: 0;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--primary-light);
  color: var(--primary-dark);
  font-weight: 600;
}

.history-card {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}

.history-card:last-child { margin-bottom: 0; }

.history-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.history-card h3 { margin: 0 0 6px; color: var(--text-primary); }

.meta { color: var(--text-secondary); font-size: 13px; }

.history-actions { display: flex; gap: 8px; flex-shrink: 0; }

.btn-continue, .btn-delete {
  padding: 8px 12px; border: none; border-radius: 8px;
  cursor: pointer; font-weight: 600; transition: all 0.2s ease;
}

.btn-continue {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
}

.btn-delete {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-continue:hover, .btn-delete:hover { transform: translateY(-2px); }

.history-content {
  margin: 0; padding: 14px; border-radius: 12px; background: var(--bg-dark);
  color: var(--text-primary); white-space: pre-wrap; word-break: break-word;
  font-family: 'Fira Code', 'Monaco', monospace; font-size: 13px; line-height: 1.7; overflow: visible;
}

.empty-state {
  min-height: 240px; display: flex; align-items: center; justify-content: center;
  border-radius: 16px; border: 1px dashed var(--border); background: var(--surface);
  color: var(--text-secondary); font-size: 15px;
}
</style>
