<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <div class="p-6 border-b border-[#E5E7EB]">
          <h2 class="text-xl font-semibold text-[#1F2937]">{{ isEdit ? '编辑成员' : '新增成员' }}</h2>
        </div>
        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">姓名</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入姓名"
            />
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">身高区间</label>
            <div class="flex gap-2">
              <button
                v-for="(label, key) in HEIGHT_RANGE_MAP"
                :key="key"
                type="button"
                class="flex-1 px-3 py-2.5 rounded-lg border-2 text-sm font-medium transition-colors"
                :class="[
                  form.height_range === key
                    ? 'border-[#E53935] bg-[#E53935]/5 text-[#E53935]'
                    : 'border-[#E5E7EB] text-[#6B7280] hover:border-gray-300',
                ]"
                @click="form.height_range = key"
              >
                {{ label }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">熟练曲目</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="song in songsStore.songs"
                :key="song.id"
                type="button"
                class="px-3 py-1.5 rounded-lg border-2 text-sm font-medium transition-colors"
                :class="[
                  form.song_ids.includes(song.id)
                    ? 'border-[#E53935] bg-[#E53935]/5 text-[#E53935]'
                    : 'border-[#E5E7EB] text-[#6B7280] hover:border-gray-300',
                ]"
                @click="toggleSong(song.id)"
              >
                {{ song.name }}
              </button>
              <span v-if="!songsStore.songs.length" class="text-sm text-[#9CA3AF]">暂无曲目</span>
            </div>
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">可替补位置</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="pos in positionOptions"
                :key="pos"
                type="button"
                class="px-3 py-1.5 rounded-lg border-2 text-sm font-medium transition-colors"
                :class="[
                  form.substitute_positions.includes(pos)
                    ? 'border-[#FFB300] bg-[#FFB300]/10 text-[#E65100]'
                    : 'border-[#E5E7EB] text-[#6B7280] hover:border-gray-300',
                ]"
                @click="togglePosition(pos)"
              >
                {{ pos }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">手机号</label>
            <input
              v-model="form.phone"
              type="tel"
              required
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入手机号"
            />
          </div>
          <div class="flex gap-3 pt-2">
            <button type="submit" class="btn-primary flex-1" :disabled="submitting">
              {{ submitting ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn-secondary flex-1" @click="$emit('close')">取消</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import type { Member, HeightRange } from '@/types'
import { HEIGHT_RANGE_MAP } from '@/types'
import { useMembersStore } from '@/stores/members'
import { useSongsStore } from '@/stores/songs'

const props = defineProps<{
  member?: Member | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const membersStore = useMembersStore()
const songsStore = useSongsStore()
const submitting = ref(false)

const isEdit = computed(() => !!props.member?.id)

const positionOptions = [
  '前排左', '前排中', '前排右',
  '中排左', '中排中', '中排右',
  '后排左', '后排中', '后排右',
]

const form = reactive({
  name: props.member?.name || '',
  height_range: (props.member?.height_range || 'medium') as HeightRange,
  song_ids: [...(props.member?.song_ids || [])] as number[],
  substitute_positions: [...(props.member?.substitute_positions || [])] as string[],
  phone: props.member?.phone || '',
})

function toggleSong(songId: number) {
  const idx = form.song_ids.indexOf(songId)
  if (idx !== -1) form.song_ids.splice(idx, 1)
  else form.song_ids.push(songId)
}

function togglePosition(pos: string) {
  const idx = form.substitute_positions.indexOf(pos)
  if (idx !== -1) form.substitute_positions.splice(idx, 1)
  else form.substitute_positions.push(pos)
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value && props.member?.id) {
      await membersStore.updateMember(props.member.id, { ...form })
    } else {
      await membersStore.createMember({ ...form })
    }
    emit('saved')
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>
