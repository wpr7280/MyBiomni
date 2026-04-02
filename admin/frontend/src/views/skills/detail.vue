<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NTabs, NTabPane, NButton, NIcon, NSpace, NSpin, NTag } from 'naive-ui'
import { useMessage } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'
import OverviewTab from './components/OverviewTab.vue'
import HowToTab from './components/HowToTab.vue'
import ToolsTab from './components/ToolsTab.vue'
import SettingsTab from './components/SettingsTab.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const loading = ref(false)
const skill = ref(null)
const activeTab = ref('overview')

const skillId = computed(() => route.params.id)

async function loadSkill() {
  loading.value = true
  try {
    const res = await api.getSkillDetail(skillId.value)
    if (res.code === 200) {
      skill.value = res.data
    } else {
      message.error('加载 Skill 失败')
    }
  } catch (e) {
    message.error('加载 Skill 失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/skills')
}

async function handleReload() {
  try {
    await api.reloadSkill(skillId.value)
    message.success('重载成功')
    await loadSkill()
  } catch (e) {
    message.error('重载失败')
  }
}

function handleDeleted() {
  router.push('/skills')
}

function handleUpdated() {
  loadSkill()
}

onMounted(() => {
  loadSkill()
})
</script>

<template>
  <CommonPage :show-header="false">
    <div class="detail-page">
      <NSpin :show="loading">
        <div v-if="skill" class="detail-container">
          <!-- 顶部信息栏 -->
          <div class="detail-header">
            <div class="header-left">
              <NButton text @click="goBack">
                <template #icon>
                  <NIcon size="20">
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8l8 8l1.41-1.41L7.83 13H20v-2z"/></svg>
                  </NIcon>
                </template>
                返回列表
              </NButton>
              <div class="header-info">
                <div class="header-title">
                  {{ skill.display_name || skill.name }}
                  <NTag v-if="skill.enabled" size="small" type="success" :bordered="false">已启用</NTag>
                  <NTag v-else size="small" type="warning" :bordered="false">已禁用</NTag>
                </div>
                <div class="header-meta">
                  <span class="meta-id">{{ skill.name }}</span>
                  <span v-if="skill.version" class="meta-version">v{{ skill.version }}</span>
                  <span v-if="skill.category" class="meta-category">{{ skill.category }}</span>
                </div>
              </div>
            </div>
            <NSpace>
              <NButton @click="handleReload">
                <template #icon>
                  <NIcon>
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
                  </NIcon>
                </template>
                重载
              </NButton>
            </NSpace>
          </div>

          <!-- Tabs -->
          <NCard class="detail-card">
            <NTabs v-model:value="activeTab" type="line" animated>
              <NTabPane name="overview" tab="概览">
                <OverviewTab :skill="skill" @updated="handleUpdated" />
              </NTabPane>
              <NTabPane name="howto" tab="使用指南">
                <HowToTab :skill-id="skillId" />
              </NTabPane>
              <NTabPane name="tools" tab="工具列表">
                <ToolsTab :skill-id="skillId" />
              </NTabPane>
              <NTabPane name="settings" tab="设置">
                <SettingsTab :skill="skill" @deleted="handleDeleted" @updated="handleUpdated" />
              </NTabPane>
            </NTabs>
          </NCard>
        </div>

        <div v-else-if="!loading" style="padding: 60px; text-align: center;">
          <p style="color: #999;">Skill 不存在或已被删除</p>
          <NButton type="primary" style="margin-top: 16px;" @click="goBack">返回列表</NButton>
        </div>
      </NSpin>
    </div>
  </CommonPage>
</template>

<style scoped>
.detail-page {
  padding: 20px 24px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.header-info {
  margin-top: 2px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
  font-size: 13px;
  color: #999;
}

.meta-id {
  font-family: 'Monaco', 'Menlo', monospace;
}

.meta-version {
  padding: 1px 6px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
}

.meta-category {
  padding: 1px 6px;
  background: #e8f5e9;
  color: #18a058;
  border-radius: 4px;
  font-size: 12px;
}

.detail-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
