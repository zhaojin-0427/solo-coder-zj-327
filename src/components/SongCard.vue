<template>
  <div class="card group relative">
    <div class="cursor-pointer" @click="$emit('edit', song)">
      <button
        class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-red-50 text-[#9CA3AF] hover:text-[#E53935]"
        @click.stop="$emit('delete', song)"
      >
        <Trash2 :size="16" />
      </button>
      <h3 class="text-lg font-semibold text-[#1F2937] mb-3 pr-8">{{ song.name }}</h3>
      <div class="flex flex-wrap gap-2">
        <span class="badge-primary">
          <Music2 :size="14" class="mr-1" />
          {{ song.beat_count }}拍
        </span>
        <span class="badge-accent">
          <component :is="formationIcon" :size="14" class="mr-1" />
          {{ formationLabel }}
        </span>
        <span class="badge-gray">
          第{{ song.performance_order }}位出场
        </span>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t border-[#E5E7EB] flex items-center justify-between">
      <span class="text-sm text-[#6B7280]">
        <FileText :size="14" class="inline mr-1 -mt-0.5" />
        已排练 {{ rehearsalCount }} 次
      </span>
      <button
        class="text-sm text-[#E53935] font-medium hover:underline"
        @click.stop="$emit('view-rehearsals', song)"
      >
        查看记录
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Song, FormationType } from '@/types'
import { FORMATION_TYPE_MAP } from '@/types'
import { Trash2, Music2, AlignStartVertical, Triangle, Square, Circle, Columns2, ChevronsDown, FileText } from 'lucide-vue-next'

const props = defineProps<{
  song: Song
  rehearsalCount?: number
}>()

defineEmits<{
  edit: [song: Song]
  delete: [song: Song]
  'view-rehearsals': [song: Song]
}>()

const formationLabel = computed(() => FORMATION_TYPE_MAP[props.song.formation_type])

const formationIcons: Record<FormationType, ReturnType<typeof AlignStartVertical>> = {
  line: AlignStartVertical,
  triangle: Triangle,
  square: Square,
  circle: Circle,
  double_row: Columns2,
  v_shape: ChevronsDown,
}

const formationIcon = computed(() => formationIcons[props.song.formation_type])
</script>
