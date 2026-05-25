<template>
  <div class="preview-panel">
    <div class="panel-header">
      <h3>👁️ 实时预览</h3>
    </div>
    <div v-html="html" class="preview-content"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import katex from 'katex'
import { useAppStore } from '../store/useAppStore'

const md = new MarkdownIt({ html: true, highlight: (str: string, lang?: string) => {
  try {
    if (lang && hljs.getLanguage(lang)) {
      return '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang }).value + '</code></pre>'
    }
  } catch (e) {}
  return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
}})

const store = useAppStore()

function renderMath(html: string) {
  html = html.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => {
    try { return katex.renderToString(decodeHtmlEntities(expr), { displayMode: true }) } catch (e) { return _ }
  })
  html = html.replace(/\$([^\$\n]+?)\$/g, (_, expr) => {
    const decoded = decodeHtmlEntities(expr)
    const hasLineBreak = decoded.includes('\\')
    try { return katex.renderToString(decoded, { displayMode: hasLineBreak }) } catch (e) { return _ }
  })
  return html
}

function decodeHtmlEntities(value: string) {
  return value
    .replace(/&gt;/g, '>')
    .replace(/&lt;/g, '<')
    .replace(/&amp;/g, '&')
}

const html = computed(() => {
  const withMath = renderMath(store.editorContent || '')
  return md.render(withMath)
})
</script>

<style scoped>
.preview-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
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
  color: #b45309;
  font-weight: 700;
}

.preview-content {
  flex: 1;
  padding: 16px;
  background: var(--surface);
  border-radius: 8px;
  overflow-y: auto;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}

.preview-content pre {
  white-space: pre;
  overflow-x: auto;
}
</style>
