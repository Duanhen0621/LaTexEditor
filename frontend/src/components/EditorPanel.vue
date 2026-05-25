<template>
  <div class="editor-panel">
    <div class="panel-header">
      <h3>✍️ 编辑器</h3>
    </div>
    <textarea v-model="content" class="editor-textarea" placeholder="开始输入Markdown..."></textarea>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '../store/useAppStore'

const store = useAppStore()
const content = computed<string>({
  get: () => store.editorContent,
  set: (v: string) => store.setEditorContent(v)
})
</script>

<style scoped>
.editor-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
  margin-bottom: 4px;
}

.panel-header h3 {
  color: #1e40af;
  font-weight: 700;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: 14px;
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.7;
  border: none;
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-primary);
  resize: none;
  transition: all 0.2s ease;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
}

.editor-textarea:focus {
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03), 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}
</style>
