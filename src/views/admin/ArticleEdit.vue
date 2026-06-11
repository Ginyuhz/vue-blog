<template>
  <div class="edit-page">
    <div class="edit-header">
      <h1 class="page-title">{{ isEdit ? '编辑文章' : '新增文章' }}</h1>
      <div class="edit-actions">
        <label class="btn btn-outline import-btn">
          <input type="file" accept=".md" @change="handleFileImport" hidden />
          导入 MD 文件
        </label>
        <label class="btn btn-outline import-btn">
          <input type="file" accept=".md" @change="handleBatchImport" multiple hidden />
          批量导入
        </label>
        <button class="btn btn-primary" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <router-link to="/admin/article" class="btn btn-outline">返回</router-link>
      </div>
    </div>
    
    <!-- 批量导入进度 -->
    <div class="batch-progress card" v-if="batchImporting">
      <h3>正在导入...</h3>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: batchProgress + '%' }"></div>
      </div>
      <p>{{ batchCurrent }} / {{ batchTotal }} 篇</p>
    </div>
    
    <div class="card edit-card">
      <div class="form-group">
        <label class="form-label">标题</label>
        <input
          type="text"
          class="form-input"
          v-model="form.title"
          placeholder="请输入文章标题"
        />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">分类</label>
          <select class="form-input" v-model="form.category_id">
            <option value="">请选择分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">标签（逗号分隔）</label>
          <input
            type="text"
            class="form-input"
            v-model="form.tags"
            placeholder="Vue, JavaScript"
          />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">摘要</label>
        <textarea
          class="form-input form-textarea"
          v-model="form.excerpt"
          placeholder="请输入文章摘要"
          rows="3"
        ></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">内容（Markdown）</label>
        <MarkdownEditor v-model="form.content" :loading="saving" @save="handleSave" />
      </div>
      <div v-if="errorMsg" class="message message-error">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticleById, createArticle, updateArticle, getCategoryList, createCategory, getTagList, createTag } from '../../api/article'
import MarkdownEditor from '../../components/MarkdownEditor.vue'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.query.id)
const articleId = computed(() => route.query.id)

const form = ref({
  title: '',
  category_id: '',
  tags: '',
  excerpt: '',
  content: '',
  created_at: ''
})

const categories = ref([])
const tags = ref([])
const saving = ref(false)
const errorMsg = ref('')

// 批量导入状态
const batchImporting = ref(false)
const batchTotal = ref(0)
const batchCurrent = ref(0)
const batchProgress = computed(() => {
  return batchTotal.value > 0 ? Math.round((batchCurrent.value / batchTotal.value) * 100) : 0
})

// 解析 front matter
const parseFrontMatter = (content) => {
  // 更灵活的 front matter 正则
  const frontMatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n?/
  const match = content.match(frontMatterRegex)
  if (!match) return { content }
  
  const frontMatter = match[1]
  const remainingContent = content.replace(frontMatterRegex, '')
  const metadata = {}
  
  const lines = frontMatter.split('\n')
  let i = 0
  while (i < lines.length) {
    const line = lines[i]
    
    // 跳过空行
    if (!line.trim()) {
      i++
      continue
    }
    
    // 处理多行值 (以 | 开头)
    if (line.trim().startsWith('|')) {
      i++
      continue
    }
    
    const colonIndex = line.indexOf(':')
    if (colonIndex === -1) {
      i++
      continue
    }
    
    const key = line.substring(0, colonIndex).trim().toLowerCase()
    let value = line.substring(colonIndex + 1).trim()
    
    // 处理数组格式: [item1, item2] 或 - item1\n  - item2
    if (value.startsWith('[') && !value.endsWith(']')) {
      // 多行数组
      const arrayItems = []
      // 去掉开头的 [ 和可能的引号
      value = value.slice(1).replace(/^["']/, '')
      if (value) arrayItems.push(value.replace(/["']$/, ''))
      
      i++
      while (i < lines.length) {
        const nextLine = lines[i].trim()
        if (nextLine === ']') break
        if (nextLine.startsWith('-') || nextLine.startsWith('*')) {
          arrayItems.push(nextLine.slice(1).trim().replace(/^["']/, '').replace(/["']$/, ''))
        }
        i++
      }
      value = arrayItems.filter(s => s)
    } else if (value.startsWith('[')) {
      // 单行数组 [item1, item2]
      value = value.slice(1, -1).split(',').map(s => s.trim().replace(/^["']/, '').replace(/["']$/, '')).filter(s => s)
    } else if (value === '' || value === '|' || value === '>') {
      // 多行字符串
      const multilineParts = []
      i++
      while (i < lines.length) {
        const nextLine = lines[i]
        if (!nextLine || nextLine.trim() === '' || nextLine.match(/^[a-zA-Z]+:/)) break
        if (nextLine.trim().startsWith('-') || nextLine.trim().startsWith('*')) {
          multilineParts.push(nextLine.trim().slice(1).trim())
        } else {
          multilineParts.push(nextLine.trim())
        }
        i++
      }
      value = multilineParts.filter(s => s).join(' ')
    } else {
      // 去掉可能的引号
      value = value.replace(/^["']/, '').replace(/["']$/, '')
    }
    
    if (key) {
      metadata[key] = value
    }
    i++
  }
  
  return { ...metadata, content: remainingContent }
}

// 确保标签存在
const ensureTag = async (tagName) => {
  const name = tagName.trim()
  if (!name) return null
  
  let tag = tags.value.find(t => t.name === name)
  if (!tag) {
    try {
      const res = await createTag({ name })
      if (res.data) {
        tags.value.push(res.data)
        tag = res.data
      }
    } catch (e) {
      const tagRes = await getTagList()
      tags.value = tagRes.data || []
      tag = tags.value.find(t => t.name === name)
    }
  }
  return tag
}

// 确保分类存在
const ensureCategory = async (categoryName) => {
  const name = categoryName.trim()
  if (!name) return null
  
  let cat = categories.value.find(c => c.name === name)
  if (!cat) {
    try {
      const res = await createCategory({ name })
      if (res.data) {
        categories.value.push(res.data)
        cat = res.data
      }
    } catch (e) {
      const catRes = await getCategoryList()
      categories.value = catRes.data || []
      cat = categories.value.find(c => c.name === name)
    }
  }
  return cat
}

// 单文件导入
const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    const content = e.target.result
    const parsed = parseFrontMatter(content)
    
    form.value.content = parsed.content || content
    
    if (parsed.title && !form.value.title) {
      form.value.title = parsed.title.trim()
    } else if (!form.value.title) {
      const titleMatch = content.match(/^#\s+(.+)$/m)
      if (titleMatch) form.value.title = titleMatch[1].trim()
    }
    
    // 分类可能是字符串或数组，取第一个
    let categoryName = parsed.category || parsed.categories || ''
    if (Array.isArray(categoryName)) {
      categoryName = categoryName[0] || ''
    }
    categoryName = categoryName.trim()
    if (categoryName && !form.value.category_id) {
      const cat = await ensureCategory(categoryName)
      if (cat) form.value.category_id = cat.id.toString()
    }
    
    const tagsValue = parsed.tags
    if (tagsValue && !form.value.tags) {
      const tagNames = Array.isArray(tagsValue) ? tagsValue : [tagsValue]
      const tagResults = await Promise.all(tagNames.map(t => ensureTag(t)))
      form.value.tags = tagResults.filter(t => t).map(t => t.name).join(', ')
    }
    
    if (!form.value.excerpt) {
      const textContent = parsed.content || content
      const excerptMatch = textContent.replace(/^#+\s+.+\n/gm, '').trim().match(/^[^\n]+/)
      if (excerptMatch) {
        form.value.excerpt = excerptMatch[0].trim().substring(0, 200) + '...'
      }
    }
    
    // 存储创建时间
    if (parsed.date) {
      form.value.created_at = parsed.date
    }
  }
  reader.readAsText(file, 'utf-8')
  event.target.value = ''
}

// 批量导入
const handleBatchImport = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  
  batchImporting.value = true
  batchTotal.value = files.length
  batchCurrent.value = 0
  
  const successList = []
  const failList = []
  
  for (const file of files) {
    try {
      const content = await readFileContent(file)
      const parsed = parseFrontMatter(content)
      
      let title = parsed.title?.trim()
      if (!title) {
        const titleMatch = content.match(/^#\s+(.+)$/m)
        title = titleMatch ? titleMatch[1].trim() : file.name.replace('.md', '')
      }
      
      let categoryId = null
      let categoryName = parsed.category || parsed.categories || ''
      if (Array.isArray(categoryName)) {
        categoryName = categoryName[0] || ''
      }
      categoryName = categoryName.trim()
      if (categoryName) {
        const cat = await ensureCategory(categoryName)
        if (cat) categoryId = cat.id
      }
      
      let tagsStr = ''
      const tagsValue = parsed.tags
      if (tagsValue) {
        const tagResults = await Promise.all(
          (Array.isArray(tagsValue) ? tagsValue : [tagsValue]).map(t => ensureTag(t))
        )
        tagsStr = tagResults.filter(t => t).map(t => t.name).join(',')
      }
      
      let excerpt = parsed.excerpt || ''
      if (!excerpt) {
        const textContent = parsed.content || content
        const excerptMatch = textContent.replace(/^#+\s+.+\n/gm, '').trim().match(/^[^\n]+/)
        if (excerptMatch) excerpt = excerptMatch[0].trim().substring(0, 200) + '...'
      }
      
      // 解析创建时间
      const createdAt = parsed.date || null
      console.log(`[批量导入] ${title} - date:`, createdAt)
      
      await createArticle({
        title,
        content: parsed.content || content,
        category_id: categoryId,
        tags: tagsStr,
        excerpt,
        created_at: createdAt
      })
      
      successList.push(title)
    } catch (e) {
      console.error(`导入文件 ${file.name} 失败:`, e)
      failList.push({ name: file.name.replace('.md', ''), reason: e.message || '未知错误' })
    }
    
    batchCurrent.value++
  }
  
  batchImporting.value = false
  
  // 显示详细结果
  let message = ''
  if (successList.length > 0) {
    message += `导入成功 ${successList.length} 篇：\n`
    successList.forEach(t => { message += `✓ ${t}\n` })
  }
  if (failList.length > 0) {
    message += `\n导入失败 ${failList.length} 篇：\n`
    failList.forEach(f => { message += `✗ ${f.name} - ${f.reason}\n` })
  }
  
  alert(message || '批量导入完成')
  event.target.value = ''
  router.push('/admin/article')
}

const readFileContent = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(e)
    reader.readAsText(file, 'utf-8')
  })
}

const loadData = async () => {
  try {
    const [catRes, tagRes] = await Promise.all([getCategoryList(), getTagList()])
    categories.value = catRes.data || []
    tags.value = tagRes.data || []
    
    if (isEdit.value) {
      const res = await getArticleById(articleId.value)
      const article = res.data
      form.value = {
        title: article.title,
        category_id: article.category_id?.toString() || '',
        tags: article.tags || '',
        excerpt: article.excerpt || '',
        content: article.content || ''
      }
    }
  } catch (e) {
    errorMsg.value = '加载数据失败'
    console.error(e)
  }
}

const handleSave = async () => {
  if (!form.value.title.trim()) {
    errorMsg.value = '请输入文章标题'
    return
  }
  
  saving.value = true
  errorMsg.value = ''
  
  try {
    const data = {
      title: form.value.title,
      content: form.value.content,
      category_id: form.value.category_id ? parseInt(form.value.category_id) : null,
      tags: form.value.tags,
      excerpt: form.value.excerpt
    }
    
    // 新建文章时添加创建时间
    if (!isEdit.value && form.value.created_at) {
      data.created_at = form.value.created_at
    }
    
    if (isEdit.value) {
      await updateArticle(articleId.value, data)
    } else {
      await createArticle(data)
    }
    
    router.push('/admin/article')
  } catch (e) {
    errorMsg.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.edit-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.6rem;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
  padding: 1rem 0;
  background: var(--color-bg);
  border-bottom: 1px solid transparent;
  position: sticky;
  top: 3.5rem;
  z-index: 10;
}

.edit-page:not(:hover) .edit-header {
  border-bottom-color: rgba(0, 0, 0, 0.06);
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-starbucks);
  letter-spacing: -0.16px;
}

.edit-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.import-btn {
  cursor: pointer;
}

.batch-progress {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.batch-progress h3 {
  margin-bottom: 1rem;
  font-size: 1.125rem;
}

.progress-bar {
  height: 8px;
  background: rgba(0, 117, 74, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--color-green-accent);
  transition: width 0.3s ease;
}

.edit-card {
  padding: 1.5rem;
  box-shadow: none;
}

.edit-card:hover {
  box-shadow: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .edit-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .edit-actions {
    flex-wrap: wrap;
  }
}
</style>
