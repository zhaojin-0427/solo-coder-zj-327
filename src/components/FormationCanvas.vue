<template>
  <div
    ref="canvasRef"
    class="relative bg-gray-50 rounded-xl border border-[#E5E7EB] overflow-hidden"
    :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
  >
    <template v-for="pos in positions" :key="pos.position_id">
      <div
        class="absolute flex items-center justify-center rounded-full cursor-grab select-none transition-shadow duration-100"
        :class="[
          dragTarget === pos.id ? 'cursor-grabbing shadow-lg z-10' : 'z-0',
          pos.member_id ? '' : 'border-2 border-dashed border-gray-300 bg-gray-100',
        ]"
        :style="{
          left: (pos.x / 800) * canvasWidth - dotSize / 2 + 'px',
          top: (pos.y / 500) * canvasHeight - dotSize / 2 + 'px',
          width: dotSize + 'px',
          height: dotSize + 'px',
          backgroundColor: pos.member_id ? getMemberColor(pos.member_id) : undefined,
        }"
        @mousedown.stop="startDrag(pos.id, $event)"
      >
        <template v-if="pos.member_id">
          <span class="text-white font-semibold text-sm pointer-events-none">
            {{ getMemberName(pos.member_id)?.charAt(0) || '?' }}
          </span>
        </template>
        <template v-else>
          <span class="text-gray-400 text-xs pointer-events-none">{{ pos.row_num }},{{ pos.col_num }}</span>
        </template>
      </div>
      <div
        v-if="pos.member_id"
        class="absolute text-xs text-[#1F2937] font-medium text-center pointer-events-none whitespace-nowrap"
        :style="{
          left: (pos.x / 800) * canvasWidth - 30 + 'px',
          top: (pos.y / 500) * canvasHeight + dotSize / 2 + 2 + 'px',
          width: '60px',
        }"
      >
        {{ getMemberName(pos.member_id) }}
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { FormationPosition } from '@/types'
import { useMembersStore } from '@/stores/members'

const props = withDefaults(defineProps<{
  positions: FormationPosition[]
  canvasWidth?: number
  canvasHeight?: number
  dotSize?: number
}>(), {
  canvasWidth: 800,
  canvasHeight: 500,
  dotSize: 48,
})

const emit = defineEmits<{
  'position-move': [positionId: number, x: number, y: number]
}>()

const membersStore = useMembersStore()
const canvasRef = ref<HTMLDivElement>()
const dragTarget = ref<number | null>(null)
const dragOffset = ref({ dx: 0, dy: 0 })

const colorPalette = [
  '#E53935', '#1E88E5', '#43A047', '#FB8C00', '#8E24AA',
  '#00ACC1', '#F4511E', '#3949AB', '#7CB342', '#C0CA33',
  '#6D4C41', '#546E7A', '#D81B60', '#00897B', '#FFB300',
]

const memberColorMap = new Map<number, string>()
let colorIndex = 0

function getMemberColor(memberId: number) {
  if (!memberColorMap.has(memberId)) {
    memberColorMap.set(memberId, colorPalette[colorIndex % colorPalette.length])
    colorIndex++
  }
  return memberColorMap.get(memberId)!
}

function getMemberName(memberId: number) {
  return membersStore.getMemberById(memberId)?.name
}

function startDrag(positionId: number, event: MouseEvent) {
  const pos = props.positions.find((p) => p.id === positionId)
  if (!pos) return
  dragTarget.value = positionId
  const relX = pos.x / 800
  const relY = pos.y / 500
  dragOffset.value = {
    dx: event.clientX - relX * props.canvasWidth,
    dy: event.clientY - relY * props.canvasHeight,
  }
}

function onMouseDown(event: MouseEvent) {}

function onMouseMove(event: MouseEvent) {
  if (!dragTarget.value) return
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) return
  const relX = Math.max(0, Math.min(1, (event.clientX - dragOffset.value.dx) / props.canvasWidth))
  const relY = Math.max(0, Math.min(1, (event.clientY - dragOffset.value.dy) / props.canvasHeight))
  const absX = Math.round(relX * 800 * 100) / 100
  const absY = Math.round(relY * 500 * 100) / 100
  emit('position-move', dragTarget.value, absX, absY)
}

function onMouseUp() {
  dragTarget.value = null
}

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    dragTarget.value = null
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>
