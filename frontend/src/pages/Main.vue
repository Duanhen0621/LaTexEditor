<template>
  <div class="layout">
    <section class="col interaction-col">
      <div class="module-card interaction-card">
        <InteractionPanel />
      </div>
    </section>
    <section class="col editor-col">
      <div class="module-card editor-card">
        <EditorPanel />
      </div>
    </section>
    <section class="col preview-col">
      <div class="module-card preview-card">
        <PreviewPanel />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import EditorPanel from '../components/EditorPanel.vue'
import PreviewPanel from '../components/PreviewPanel.vue'
import InteractionPanel from '../components/InteractionPanel.vue'
</script>

<style scoped>
.layout { display:flex; height:100%; width: 100%; }
.col { flex:1; padding:12px; box-sizing:border-box; overflow:auto }
</style>
