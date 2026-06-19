<template>
  <div class="card border-l-4 border-l-[#FFB300]">
    <div class="flex items-center gap-3 mb-2">
      <div
        class="w-9 h-9 rounded-full flex items-center justify-center text-white font-semibold text-sm"
        :class="member ? heightColor : 'bg-gray-400'"
      >
        {{ member?.name.charAt(0) || '?' }}
      </div>
      <div class="flex-1">
        <h4 class="text-base font-semibold text-[#1F2937]">{{ member?.name || '未知成员' }}</h4>
      </div>
      <div class="text-right">
        <span class="text-2xl font-bold text-[#FFB300]">{{ priority }}</span>
        <p class="text-xs text-[#6B7280]">匹配度</p>
      </div>
    </div>
    <div v-if="member" class="flex flex-wrap gap-1.5 mt-2">
      <span class="badge-gray text-xs">{{ heightLabel }}</span>
      <span v-for="songId in member.song_ids" :key="songId" class="badge-primary text-xs">
        {{ getSongName(songId) }}
      </span>
      <span v-for="pos in member.substitute_positions" :key="pos" class="badge-accent text-xs">
        {{ pos }}
      </span>
    </div>
    <button
      class="btn-accent w-full mt-3 text-sm py-2"
      :disabled="confirmed"
      @click="$emit('confirm', memberId)"
    >
      {{ confirmed ? '已确认' : '确认替补' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { HeightRange } from '@/types'
import { HEIGHT_RANGE_MAP } from '@/types'
import { useMembersStore } from '@/stores/members'
import { useSongsStore } from '@/stores/songs'

const props = defineProps<{
  memberId: number
  priority: number
  confirmed?: boolean
}>()

defineEmits<{
  confirm: [memberId: number]
}>()

const membersStore = useMembersStore()
const songsStore = useSongsStore()

const member = computed(() => membersStore.getMemberById(props.memberId))

const heightLabel = computed(() => member.value ? HEIGHT_RANGE_MAP[member.value.height_range] : '')

const heightColorMap: Record<HeightRange, string> = {
  short: 'bg-green-500',
  medium: 'bg-blue-500',
  tall: 'bg-orange-500',
}

const heightColor = computed(() =>
  member.value ? heightColorMap[member.value.height_range] : 'bg-gray-400'
)

function getSongName(songId: number) {
  return songsStore.songs.find((s) => s.id === songId)?.name || `曲目${songId}`
}
</script>
