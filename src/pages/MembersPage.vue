<template>
  <div class="flex gap-5 h-[calc(100vh-3rem)]">
    <div class="w-80 flex flex-col shrink-0">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-2xl font-bold text-[#1F2937]">成员站位</h1>
        <button class="btn-primary flex items-center gap-2 text-sm" @click="showModal = true">
          <Plus :size="16" />
          新增
        </button>
      </div>

      <div class="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin">
        <div v-if="membersStore.loading" class="text-center py-8 text-[#6B7280]">加载中...</div>
        <div v-else-if="!membersStore.members.length" class="text-center py-12">
          <Users :size="40" class="mx-auto text-[#D1D5DB] mb-3" />
          <p class="text-base text-[#6B7280]">暂无成员</p>
        </div>
        <template v-else>
          <MemberCard
            v-for="member in membersStore.members"
            :key="member.id"
            :member="member"
            @edit="openEdit"
            @delete="confirmDelete"
          />
        </template>
      </div>
    </div>

    <div class="flex-1 flex flex-col min-w-0">
      <div class="mb-4 flex items-center gap-3">
        <label class="text-base font-medium text-[#1F2937]">预览曲目：</label>
        <select
          v-model="previewSongId"
          class="px-4 py-2 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
        >
          <option :value="null">请选择曲目</option>
          <option v-for="song in songsStore.songs" :key="song.id" :value="song.id">
            {{ song.name }}
          </option>
        </select>
      </div>

      <div class="flex-1 flex items-center justify-center bg-white rounded-xl border border-[#E5E7EB]">
        <div v-if="!previewSongId" class="text-center">
          <LayoutGrid :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
          <p class="text-lg text-[#6B7280]">选择曲目查看站位预览</p>
        </div>
        <div v-else-if="!previewFormation" class="text-center">
          <p class="text-base text-[#6B7280]">该曲目暂无队形数据</p>
          <p class="text-sm text-[#9CA3AF] mt-1">请先到队形编排页生成队形</p>
        </div>
        <FormationCanvas
          v-else
          :positions="previewFormation.positions"
          :canvas-width="650"
          :canvas-height="400"
          :dot-size="44"
        />
      </div>

      <div v-if="previewFormation" class="mt-3 flex flex-wrap gap-2">
        <div
          v-for="member in assignedMembers"
          :key="member.id"
          class="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg text-sm"
        >
          <div
            class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold"
            :class="getHeightColor(member.height_range)"
          >
            {{ member.name.charAt(0) }}
          </div>
          <span class="text-[#1F2937]">{{ member.name }}</span>
        </div>
      </div>
    </div>

    <MemberFormModal
      v-if="showModal"
      :member="editingMember"
      @close="closeModal"
      @saved="onSaved"
    />

    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认删除</h2>
          <p class="text-base text-[#6B7280] mb-5">确定要删除成员「{{ deleteTarget.name }}」吗？</p>
          <div class="flex gap-3">
            <button class="btn-primary flex-1" @click="doDelete">确认删除</button>
            <button class="btn-secondary flex-1" @click="deleteTarget = null">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Users, LayoutGrid } from 'lucide-vue-next'
import type { Member, HeightRange } from '@/types'
import { useMembersStore } from '@/stores/members'
import { useSongsStore } from '@/stores/songs'
import { useFormationsStore } from '@/stores/formations'
import MemberCard from '@/components/MemberCard.vue'
import MemberFormModal from '@/components/MemberFormModal.vue'
import FormationCanvas from '@/components/FormationCanvas.vue'

const membersStore = useMembersStore()
const songsStore = useSongsStore()
const formationsStore = useFormationsStore()

const showModal = ref(false)
const editingMember = ref<Member | null>(null)
const deleteTarget = ref<Member | null>(null)
const previewSongId = ref<number | null>(null)

const previewFormation = computed(() => {
  if (!previewSongId.value) return null
  return formationsStore.currentFormation
})

const assignedMembers = computed(() => {
  if (!previewFormation.value) return []
  const memberIds = previewFormation.value.positions
    .filter((p) => p.member_id)
    .map((p) => p.member_id!)
  const uniqueIds = [...new Set(memberIds)]
  return uniqueIds
    .map((id) => membersStore.getMemberById(id))
    .filter(Boolean) as Member[]
})

const heightColorMap: Record<HeightRange, string> = {
  short: 'bg-green-500',
  medium: 'bg-blue-500',
  tall: 'bg-orange-500',
}

function getHeightColor(range: HeightRange) {
  return heightColorMap[range]
}

function openEdit(member: Member) {
  editingMember.value = member
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingMember.value = null
}

function onSaved() {
  membersStore.fetchMembers()
}

function confirmDelete(member: Member) {
  deleteTarget.value = member
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await membersStore.deleteMember(deleteTarget.value.id)
    deleteTarget.value = null
  } catch {
    alert('删除失败，请重试')
  }
}

onMounted(() => {
  membersStore.fetchMembers()
  songsStore.fetchSongs()
})

watch(previewSongId, (id) => {
  if (id) {
    formationsStore.fetchFormation(id)
  }
})
</script>
