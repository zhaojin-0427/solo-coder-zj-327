<template>
  <div class="card group relative">
    <button
      class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-red-50 text-[#9CA3AF] hover:text-[#E53935]"
      @click="$emit('delete', member)"
    >
      <Trash2 :size="16" />
    </button>
    <div class="flex items-start gap-3">
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-base shrink-0"
        :class="heightColor"
      >
        {{ member.name.charAt(0) }}
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-base font-semibold text-[#1F2937] pr-6">{{ member.name }}</h3>
        <span class="badge-gray mt-1">{{ heightLabel }}</span>
      </div>
    </div>
    <div v-if="member.song_ids?.length" class="mt-3 flex flex-wrap gap-1.5">
      <span
        v-for="songId in member.song_ids"
        :key="songId"
        class="badge-primary text-xs"
      >
        {{ getSongName(songId) }}
      </span>
    </div>
    <div v-if="member.substitute_positions?.length" class="mt-2 flex flex-wrap gap-1.5">
      <span
        v-for="pos in member.substitute_positions"
        :key="pos"
        class="badge-accent text-xs"
      >
        {{ pos }}
      </span>
    </div>
    <p class="text-sm text-[#9CA3AF] mt-2">{{ member.phone }}</p>
    <div class="mt-3 flex gap-2">
      <button class="btn-secondary text-sm px-3 py-1" @click="$emit('edit', member)">编辑</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Member, HeightRange } from '@/types'
import { HEIGHT_RANGE_MAP } from '@/types'
import { Trash2 } from 'lucide-vue-next'
import { useSongsStore } from '@/stores/songs'

const props = defineProps<{
  member: Member
}>()

defineEmits<{
  edit: [member: Member]
  delete: [member: Member]
}>()

const songsStore = useSongsStore()

const heightLabel = computed(() => HEIGHT_RANGE_MAP[props.member.height_range])

const heightColorMap: Record<HeightRange, string> = {
  short: 'bg-green-500',
  medium: 'bg-blue-500',
  tall: 'bg-orange-500',
}

const heightColor = computed(() => heightColorMap[props.member.height_range])

function getSongName(songId: number) {
  return songsStore.songs.find((s) => s.id === songId)?.name || `曲目${songId}`
}
</script>
