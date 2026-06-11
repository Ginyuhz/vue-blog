<template>
  <div class="markdown-editor">
    <div class="editor-header">
      <button class="btn btn-primary" @click="handleSave" :disabled="loading">
        {{ loading ? '保存中...' : '保存' }}
      </button>
    </div>
    <div class="editor-body">
      <div class="editor-pane">
        <div class="pane-header">编辑</div>
        <textarea
          class="editor-textarea"
          v-model="content"
          placeholder="使用 Markdown 编写文章..."
          @input="handleInput"
        ></textarea>
      </div>
      <div class="preview-pane">
        <div class="pane-header">预览</div>
        <div class="preview-content" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import Prism from 'prismjs'
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-css'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-json'
import MarkdownIt from 'markdown-it'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const content = ref(props.modelValue)

// 初始化 markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && Prism.languages[lang]) {
      try {
        return '<pre class="language-' + lang + '"><code>' +
          Prism.highlight(str, Prism.languages[lang], lang) +
          '</code></pre>'
      } catch (e) {
        console.error('Prism highlight error:', e)
      }
    }
    return '<pre><code>' + MarkdownIt().utils.escapeHtml(str) + '</code></pre>'
  }
})

// 动态加载 emoji 插件
import('markdown-it-emoji').then(emoji => {
  md.use(emoji.default || emoji)
}).catch(e => {
  console.warn('Failed to load emoji plugin:', e)
})

const renderedContent = computed(() => {
  if (!content.value) return ''
  try {
    return md.render(content.value)
  } catch (e) {
    console.error('Markdown render error:', e)
    return content.value
  }
})

watch(() => props.modelValue, (val) => {
  content.value = val
})

const handleInput = () => {
  emit('update:modelValue', content.value)
}

const handleSave = () => {
  emit('save', content.value)
}
</script>

<style scoped>
.markdown-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius);
  overflow: hidden;
}

.editor-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: var(--color-card-bg);
}

.editor-body {
  display: flex;
  flex: 1;
  min-height: 450px;
}

.editor-pane,
.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-pane {
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}

.pane-header {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-black-soft);
  background: var(--color-neutral-cool);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  letter-spacing: -0.01em;
}

.editor-textarea {
  flex: 1;
  padding: 1rem;
  border: none;
  resize: none;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  background: var(--color-card-bg);
  color: var(--color-text-black);
}

.editor-textarea:focus {
  outline: none;
}

.preview-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: var(--color-card-bg);
}

.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4) {
  margin: 1.5rem 0 0.75rem;
  color: var(--color-starbucks);
}

.preview-content :deep(h1) { font-size: 1.5rem; }
.preview-content :deep(h2) { font-size: 1.25rem; }
.preview-content :deep(h3) { font-size: 1.1rem; }

.preview-content :deep(p) {
  margin: 0.75rem 0;
  line-height: 1.8;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.preview-content :deep(li) {
  margin: 0.375rem 0;
}

.preview-content :deep(blockquote) {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  border-left: 4px solid var(--color-green-accent);
  background: rgba(0, 117, 74, 0.05);
}

.preview-content :deep(code) {
  background: var(--color-neutral-cool);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.875em;
}

.preview-content :deep(pre) {
  background: var(--color-house-green);
  padding: 1rem;
  border-radius: var(--radius);
  overflow-x: auto;
  margin: 1rem 0;
}

.preview-content :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--color-text-white);
}

.preview-content :deep(a) {
  color: var(--color-green-accent);
}

.preview-content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius);
}

.preview-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  padding: 0.5rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.preview-content :deep(th) {
  background: var(--color-neutral-warm);
}
</style>
