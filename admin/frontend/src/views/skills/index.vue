<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NInput, NSwitch, NButton, NIcon, NSpace, NTag, NBadge, NSpin, NEmpty, NGrid, NGridItem, NScrollbar } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'
import CreateSkillModal from './components/CreateSkillModal.vue'

const router = useRouter()
const { t } = useI18n()
const message = useMessage()
const loading = ref(false)
const skills = ref([])
const categories = ref([])
const searchText = ref('')
const selectedCategory = ref('all')
const showCreateModal = ref(false)

// 分类颜色映射
const categoryColors = {
  'data_analysis': '#18a058',
  'web_search': '#2080f0',
  'code': '#f0a020',
  'file': '#d03050',
  'communication': '#8a2be2',
  'default': '#909399',
}

function getCategoryColor(cat) {
  return categoryColors[cat] || categoryColors['default']
}

// 过滤后的 skill 列表
const filteredSkills = computed(() => {
  let list = skills.value
  if (selectedCategory.value !== 'all') {
    list = list.filter(s => s.category === selectedCategory.value)
  }
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(s =>
      (s.name && s.name.toLowerCase().includes(q)) ||
      (s.display_name && s.display_name.toLowerCase().includes(q)) ||
      (s.description && s.description.toLowerCase().includes(q))
    )
  }
  return list
})

// 各分类的 skill 数量
const categoryCounts = computed(() => {
  const counts = { all: skills.value.length }
  skills.value.forEach(s => {
    const cat = s.category || 'uncategorized'
    counts[cat] = (counts[cat] || 0) + 1
  })
  return counts
})

async function loadSkills() {
  loading.value = true
  try {
    const res = await api.getSkillList()
    if (res.code === 200) {
      skills.value = res.data || []
    }
  } catch (e) {
    message.error(t('views.skills.message_load_failed'))
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await api.getCategories()
    if (res.code === 200) {
      categories.value = res.data || []
    }
  } catch (e) {
    // 从 skills 中提取分类
    const cats = [...new Set(skills.value.map(s => s.category).filter(Boolean))]
    categories.value = cats
  }
}

async function toggleSkill(skill) {
  try {
    if (skill.enabled) {
      await api.disableSkill(skill.id)
      skill.enabled = false
      message.success(t('views.skills.message_disable_success') + ': ' + (skill.display_name || skill.name))
    } else {
      await api.enableSkill(skill.id)
      skill.enabled = true
      message.success(t('views.skills.message_enable_success') + ': ' + (skill.display_name || skill.name))
    }
  } catch (e) {
    message.error(t('views.skills.message_reload_failed'))
  }
}

function goToDetail(skill) {
  router.push(`/skills/${skill.id}`)
}

async function handleCreated(newSkill) {
  showCreateModal.value = false
  if (newSkill && newSkill.id) {
    router.push(`/skills/${newSkill.id}`)
  } else {
    await loadSkills()
  }
}

async function handleReloadAll() {
  try {
    await api.reloadAllSkills()
    message.success(t('views.skills.message_reload_success'))
    await loadSkills()
  } catch (e) {
    message.error(t('views.skills.message_reload_failed'))
  }
}

onMounted(async () => {
  await loadSkills()
  await loadCategories()
})
</script>

<template>
  <CommonPage :show-header="false">
    <div class="skills-page">
      <div class="skills-layout">
        <!-- 左侧{{ t('views.skills.label_category') }} -->
        <div class="category-sidebar">
          <div class="sidebar-title">{{ t('views.skills.label_category') }}</div>
          <NScrollbar style="max-height: calc(100vh - 240px);">
            <div
              class="category-item"
              :class="{ active: selectedCategory === 'all' }"
              @click="selectedCategory = 'all'"
            >
              <span>{{ t('views.skills.label_all') }}</span>
              <NBadge :value="categoryCounts.all" :max="999" type="info" />
            </div>
            <div
              v-for="cat in categories"
              :key="cat"
              class="category-item"
              :class="{ active: selectedCategory === cat }"
              @click="selectedCategory = cat"
            >
              <span>{{ cat }}</span>
              <NBadge :value="categoryCounts[cat] || 0" :max="999" type="info" />
            </div>
          </NScrollbar>
        </div>

        <!-- 右侧内容 -->
        <div class="skills-content">
          <!-- 工具栏 -->
          <div class="toolbar">
            <NInput
              v-model:value="searchText"
              :placeholder="t('views.skills.placeholder_search')"
              clearable
              style="width: 320px;"
            >
              <template #prefix>
                <NIcon>
                  <svg viewBox="0 0 24 24"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5A6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5S14 7.01 14 9.5S11.99 14 9.5 14z"/></svg>
                </NIcon>
              </template>
            </NInput>
            <NSpace>
              <NButton @click="handleReloadAll">
                <template #icon>
                  <NIcon>
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
                  </NIcon>
                </template>
                重载全部
              </NButton>
              <NButton type="primary" @click="showCreateModal = true">
                <template #icon>
                  <NIcon>
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                  </NIcon>
                </template>
                新建 Skill
              </NButton>
            </NSpace>
          </div>

          <!-- Skill 卡片列表 -->
          <NSpin :show="loading">
            <div v-if="filteredSkills.length === 0 && !loading" style="padding: 60px 0;">
              <NEmpty :description="t('views.skills.text_no_skills')" />
            </div>
            <NGrid v-else :cols="3" :x-gap="16" :y-gap="16" responsive="screen" :cols-s="1" :cols-m="2" :cols-l="3">
              <NGridItem v-for="skill in filteredSkills" :key="skill.id">
                <NCard
                  class="skill-card"
                  hoverable
                  @click="goToDetail(skill)"
                >
                  <div class="skill-card-header">
                    <div class="skill-name">{{ skill.display_name || skill.name }}</div>
                    <NSwitch
                      :value="skill.enabled"
                      size="small"
                      @click.stop
                      @update:value="() => toggleSkill(skill)"
                    />
                  </div>
                  <div class="skill-id">{{ skill.name }}</div>
                  <div class="skill-desc">{{ skill.description || t('views.knowhow.text_no_description') }}</div>
                  <div class="skill-footer">
                    <NSpace size="small">
                      <NTag size="small" :bordered="false" :color="{ color: getCategoryColor(skill.category) + '15', textColor: getCategoryColor(skill.category) }">
                        {{ skill.category || 'N/A' }}
                      </NTag>
                      <NTag size="small" :bordered="false" type="default">
                        v{{ skill.version || '0.1.0' }}
                      </NTag>
                    </NSpace>
                    <span class="tool-count">
                      <NIcon size="14">
                        <svg viewBox="0 0 24 24"><path fill="currentColor" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9c-2-2-5-2.4-7.4-1.3L9 6 6 9L1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
                      </NIcon>
                      {{ skill.tool_count || 0 }} {{ t('views.skills.label_tools') }}
                    </span>
                  </div>
                </NCard>
              </NGridItem>
            </NGrid>
          </NSpin>
        </div>
      </div>
    </div>

    <!-- 创建弹窗 -->
    <CreateSkillModal
      v-model:show="showCreateModal"
      :categories="categories"
      @created="handleCreated"
    />
  </CommonPage>
</template>

<style scoped>
.skills-page {
  padding: 20px 24px;
}

.skills-layout {
  display: flex;
  gap: 20px;
}

.category-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
}

.category-item:hover {
  background: #f5f5f5;
  color: #333;
}

.category-item.active {
  background: #e8f5e9;
  color: #18a058;
  font-weight: 500;
}

.skills-content {
  flex: 1;
  min-width: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.skill-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.skill-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.skill-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.skill-id {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  font-family: 'Monaco', 'Menlo', monospace;
}

.skill-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
  min-height: 39px;
}

.skill-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .skills-layout {
    flex-direction: column;
  }
  .category-sidebar {
    width: 100%;
  }
  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
