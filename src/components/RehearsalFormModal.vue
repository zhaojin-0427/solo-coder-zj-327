<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <div class="p-6 border-b border-[#E5E7EB]">
          <h2 class="text-xl font-semibold text-[#1F2937]">添加排练记录</h2>
          <p class="text-sm text-[#6B7280] mt-1">曲目：{{ songName }}</p>
        </div>
        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">排练日期</label>
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">时长（分钟）</label>
            <input
              v-model.number="form.duration_minutes"
              type="number"
              required
              min="1"
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入排练时长"
            />
          </div>
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-base font-medium text-[#1F2937]">节拍错误（错拍片段）</label>
            </div>
            <div v-for="(err, idx) in form.beat_errors" :key="'b' + idx" class="flex gap-2 mb-2">
              <select
                v-model="err.position_id"
                class="w-28 px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              >
                <option value="">选择位置</option>
                <option v-for="p in positions" :key="p.position_id" :value="p.position_id">
                  {{ p.position_id }}({{ getMemberShort(p.member_id) }})
                </option>
              </select>
              <input
                v-model.number="err.beat_number"
                type="number"
                placeholder="拍号"
                class="w-20 px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              />
              <input
                v-model="err.description"
                type="text"
                placeholder="描述"
                class="flex-1 px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              />
              <button type="button" class="text-[#E53935] p-1" @click="form.beat_errors.splice(idx, 1)">
                <X :size="16" />
              </button>
            </div>
            <button
              type="button"
              class="text-sm text-[#E53935] font-medium hover:underline"
              @click="form.beat_errors.push({ position_id: '', beat_number: 0, description: '' })"
            >
              + 添加错拍
            </button>
          </div>
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-base font-medium text-[#1F2937]">位置错误（换位失误）</label>
            </div>
            <div v-for="(err, idx) in form.position_errors" :key="'p' + idx" class="flex gap-2 mb-2">
              <select
                v-model="err.position_id"
                class="w-28 px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              >
                <option value="">选择位置</option>
                <option v-for="p in positions" :key="p.position_id" :value="p.position_id">
                  {{ p.position_id }}({{ getMemberShort(p.member_id) }})
                </option>
              </select>
              <input
                v-model="err.description"
                type="text"
                placeholder="描述"
                class="flex-1 px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              />
              <button type="button" class="text-[#E53935] p-1" @click="form.position_errors.splice(idx, 1)">
                <X :size="16" />
              </button>
            </div>
            <button
              type="button"
              class="text-sm text-[#E53935] font-medium hover:underline"
              @click="form.position_errors.push({ position_id: '', description: '' })"
            >
              + 添加换位失误
            </button>
          </div>
          <div>
            <label class="block text-base font-medium text-[#1F2937] mb-1.5">老师提示</label>
            <textarea
              v-model="form.teacher_notes"
              rows="3"
              class="w-full px-4 py-2.5 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935] focus:border-transparent"
              placeholder="请输入老师提示或备注"
            ></textarea>
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
import { X } from 'lucide-vue-next'
import { useRehearsalsStore } from '@/stores/rehearsals'
import { useFormationsStore } from '@/stores/formations'
import { useMembersStore } from '@/stores/members'

const props = defineProps<{
  songId: number
  songName: string
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const rehearsalsStore = useRehearsalsStore()
const formationsStore = useFormationsStore()
const membersStore = useMembersStore()
const submitting = ref(false)

const positions = computed(() => formationsStore.currentFormation?.positions || [])

function getMemberShort(memberId: number | null) {
  if (!memberId) return '空位'
  const member = membersStore.getMemberById(memberId)
  return member?.name?.charAt(0) || '?'
}

const form = reactive({
  date: new Date().toISOString().slice(0, 10),
  duration_minutes: 60,
  beat_errors: [] as { position_id: string; beat_number: number; description: string }[],
  position_errors: [] as { position_id: string; description: string }[],
  teacher_notes: '',
})

async function handleSubmit() {
  submitting.value = true
  try {
    const errors: { position_id: string; error_type: string; beat_number?: number; description?: string }[] = []
    form.beat_errors.forEach((e) => {
      if (e.position_id) {
        errors.push({
          position_id: e.position_id,
          error_type: 'beat_error',
          beat_number: e.beat_number || undefined,
          description: e.description || undefined,
        })
      }
    })
    form.position_errors.forEach((e) => {
      if (e.position_id) {
        errors.push({
          position_id: e.position_id,
          error_type: 'position_error',
          description: e.description || undefined,
        })
      }
    })
    await rehearsalsStore.createRehearsal({
      song_id: props.songId,
      date: form.date,
      duration_minutes: form.duration_minutes,
      teacher_notes: form.teacher_notes,
      errors,
    })
    emit('saved')
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>
