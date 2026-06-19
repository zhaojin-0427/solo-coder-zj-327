<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <div class="p-6 border-b border-[#E5E7EB]">
          <h2 class="text-xl font-semibold text-[#1F2937]">{{ isEdit ? '编辑曲目' : '新增曲目' }}</h2>
        </div>
        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">曲名</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入曲名"
            />
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">节拍数</label>
            <input
              v-model.number="form.beat_count"
              type="number"
              required
              min="1"
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入节拍数"
            />
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">队形类型</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="opt in formationOptions"
                :key="opt.value"
                type="button"
                class="flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-colors text-sm font-medium"
                :class="[
                  form.formation_type === opt.value
                    ? 'border-[#E53935] bg-[#E53935]/5 text-[#E53935]'
                    : 'border-[#E5E7EB] text-[#6B7280] hover:border-gray-300',
                ]"
                @click="form.formation_type = opt.value"
              >
                <component :is="opt.icon" :size="22" />
                <span>{{ opt.label }}</span>
              </button>
            </div>
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">出场顺序</label>
            <input
              v-model.number="form.performance_order"
              type="number"
              required
              min="1"
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入出场顺序"
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
import type { Song, FormationType } from '@/types'
import { FORMATION_TYPE_MAP } from '@/types'
import { AlignStartVertical, Triangle, Square, Circle, Columns2, ChevronsDown } from 'lucide-vue-next'
import { useSongsStore } from '@/stores/songs'

const props = defineProps<{
  song?: Song | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const songsStore = useSongsStore()
const submitting = ref(false)

const isEdit = computed(() => !!props.song?.id)

const form = reactive({
  name: props.song?.name || '',
  beat_count: props.song?.beat_count || 8,
  formation_type: (props.song?.formation_type || 'line') as FormationType,
  performance_order: props.song?.performance_order || 1,
})

const formationOptions: { value: FormationType; label: string; icon: any }[] = [
  { value: 'line', label: FORMATION_TYPE_MAP.line, icon: AlignStartVertical },
  { value: 'triangle', label: FORMATION_TYPE_MAP.triangle, icon: Triangle },
  { value: 'square', label: FORMATION_TYPE_MAP.square, icon: Square },
  { value: 'circle', label: FORMATION_TYPE_MAP.circle, icon: Circle },
  { value: 'double_row', label: FORMATION_TYPE_MAP.double_row, icon: Columns2 },
  { value: 'v_shape', label: FORMATION_TYPE_MAP.v_shape, icon: ChevronsDown },
]

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value && props.song?.id) {
      await songsStore.updateSong(props.song.id, { ...form })
    } else {
      await songsStore.createSong({ ...form })
    }
    emit('saved')
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>
