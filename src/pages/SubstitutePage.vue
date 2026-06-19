<template>
  <div>
    <div class="flex items-center justify-between mb-5">
      <h1 class="text-2xl font-bold text-[#1F2937]">替补调整</h1>
      <div class="flex items-center gap-3">
        <label class="text-base font-medium text-[#1F2937]">选择曲目：</label>
        <select
          v-model="selectedSongId"
          class="px-4 py-2 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935"
        >
          <option :value="null">请选择</option>
          <option v-for="song in songsStore.songs" :key="song.id" :value="song.id">
            {{ song.name }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="!selectedSongId" class="text-center py-20">
      <ArrowLeftRight :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">请先选择一个曲目</p>
    </div>

    <div v-else class="flex gap-5 h-[calc(100vh-8rem)]">
      <div class="w-64 bg-white rounded-xl border border-[#E5E7EB] flex flex-col shrink-0">
        <div class="p-4 border-b border-[#E5E7EB] flex items-center justify-between">
          <h3 class="text-base font-semibold text-[#1F2937]">出勤面板</h3>
          <span class="text-xs text-[#9CA3AF]">
            {{ presentCount }}/{{ membersStore.members.length }} 到场
          </span>
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin">
          <div
            v-for="member in membersStore.members"
            :key="member.id"
            class="flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-gray-50"
            :class="isAbsent(member.id) ? 'bg-red-50' : ''"
          >
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold shrink-0"
                :class="getHeightColor(member.height_range)"
              >
                {{ member.name.charAt(0) }}
              </div>
              <span class="text-base text-[#1F2937">{{ member.name }}</span>
            </div>
            <button
              class="px-3 py-1 rounded-full text-sm font-medium transition-colors shrink-0"
              :class="[
                isPresent(member.id)
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700',
              ]"
              @click="toggleAttendance(member.id)"
            >
              {{ isPresent(member.id) ? '到场' : '请假' }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex-1 flex flex-col min-w-0">
        <div class="flex-1 bg-white rounded-xl border border-[#E5E7EB] flex items-center justify-center">
          <div v-if="!currentFormation" class="text-center">
            <p class="text-base text-[#6B7280]">暂无队形数据</p>
          </div>
          <div v-else class="relative" :style="{ width: '550px', height: '380px' }">
            <div
              v-for="pos in currentFormation.positions"
              :key="pos.position_id"
              class="absolute flex items-center justify-center rounded-full select-none"
              :class="isAbsent(pos.member_id) ? 'opacity-30' : ''"
              :style="{
                left: (pos.x / 800) * 550 - 22 + 'px',
                top: (pos.y / 500) * 380 - 22 + 'px',
                width: '44px',
                height: '44px',
              }"
            >
              <div
                v-if="pos.member_id"
                class="w-full h-full rounded-full flex items-center justify-center text-white font-semibold text-sm"
                :class="[
                  isAbsent(pos.member_id) ? 'bg-gray-400' : '',
                  getSubForMember(pos.member_id) ? 'bg-[#FFB300]' : '',
                  !isAbsent(pos.member_id) && !getSubForMember(pos.member_id) ? getHeightBg(pos.member_id) : '',
                ]"
              >
                {{ getMemberName(pos.member_id)?.charAt(0) || '?' }}
              </div>
              <div
                v-else
                class="w-full h-full rounded-full border-2 border-dashed border-gray-300 bg-gray-50"
              ></div>
              <span
                class="absolute -bottom-5 text-xs text-[#1F2937] font-medium whitespace-nowrap"
                :class="isAbsent(pos.member_id) ? 'line-through text-[#9CA3AF]' : ''"
              >
                {{ getSubForMember(pos.member_id) ? getMemberName(getSubForMember(pos.member_id)!.substitute_member_id) : (pos.member_id ? getMemberName(pos.member_id) : '') }}
              </span>
            </div>
          </div>
        </div>

        <div class="mt-3 flex items-center gap-4">
          <span class="flex items-center gap-2 text-sm text-[#6B7280]">
            <span class="w-3 h-3 rounded-full bg-green-500"></span> 到场
          </span>
          <span class="flex items-center gap-2 text-sm text-[#6B7280]">
            <span class="w-3 h-3 rounded-full bg-gray-400"></span> 请假
          </span>
          <span class="flex items-center gap-2 text-sm text-[#6B7280]">
            <span class="w-3 h-3 rounded-full bg-[#FFB300]"></span> 替补
          </span>
          <div class="flex-1"></div>
          <button
            class="btn-primary flex items-center gap-2"
            :disabled="!currentFormation || currentFormation.is_locked"
            @click="handleLock"
          >
            <Lock :size="16" />
            确认锁定
          </button>
        </div>
      </div>

      <div class="w-72 bg-white rounded-xl border border-[#E5E7EB] flex flex-col shrink-0">
        <div class="p-4 border-b border-[#E5E7EB]">
          <h3 class="text-base font-semibold text-[#1F2937]">替补推荐</h3>
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-thin">
          <div v-if="!absentMemberIds.length" class="text-center py-8 text-sm text-[#9CA3AF]">
            暂无请假成员
          </div>
          <template v-for="absentId in absentMemberIds" :key="absentId">
            <div class="mb-2">
              <p class="text-sm font-medium text-[#E53935] mb-2">
                {{ getMemberName(absentId) }} 请假
              </p>
              <div v-if="substitutesStore.loading" class="text-sm text-[#9CA3AF]">查找推荐中...</div>
              <template v-else>
                <SubstituteRecommendCard
                  v-for="rec in getRecommendations(absentId)"
                  :key="rec.member_id"
                  :member-id="rec.member_id"
                  :priority="rec.priority"
                  :confirmed="isSubConfirmed(absentId, rec.member_id)"
                  @confirm="confirmSub(absentId, rec.member_id)"
                />
                <p v-if="!getRecommendations(absentId).length" class="text-sm text-[#9CA3AF]">
                  暂无推荐
                </p>
              </template>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ArrowLeftRight, Lock } from 'lucide-vue-next'
import type { HeightRange, SubstituteRecommend } from '@/types'
import { useSongsStore } from '@/stores/songs'
import { useMembersStore } from '@/stores/members'
import { useFormationsStore } from '@/stores/formations'
import { useSubstitutesStore } from '@/stores/substitutes'
import SubstituteRecommendCard from '@/components/SubstituteRecommendCard.vue'

const songsStore = useSongsStore()
const membersStore = useMembersStore()
const formationsStore = useFormationsStore()
const substitutesStore = useSubstitutesStore()

const selectedSongId = ref<number | null>(null)

const recommendationsMap = ref<Map<number, SubstituteRecommend[]>>(new Map())

const currentFormation = computed(() => {
  return formationsStore.currentFormation
})

const attendanceMap = computed(() => {
  const m = new Map<number, 'present' | 'absent'>()
  if (!selectedSongId.value) return m
  const filtered = substitutesStore.attendance.filter((a) => a.song_id === selectedSongId.value)
  const sorted = [...filtered].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  for (const record of sorted) {
    if (!m.has(record.member_id)) {
      m.set(record.member_id, record.status)
    }
  }
  return m
})

function isPresent(memberId: number) {
  const status = attendanceMap.value.get(memberId)
  return status !== 'absent'
}

function isAbsent(memberId: number | null) {
  if (!memberId) return false
  return attendanceMap.value.get(memberId) === 'absent'
}

const absentMemberIds = computed(() =>
  membersStore.members
    .map((m) => m.id)
    .filter((id) => isAbsent(id))
)

const presentCount = computed(() =>
  membersStore.members
    .map((m) => m.id)
    .filter((id) => isPresent(id)).length
)

function getSubForMember(memberId: number) {
  return substitutesStore.substitutes.find((s) => s.absent_member_id === memberId)
}

function getRecommendations(absentId: number) {
  return recommendationsMap.value.get(absentId) || []
}

function isSubConfirmed(absentId: number, subId: number) {
  return substitutesStore.substitutes.some(
    (s) => s.absent_member_id === absentId && s.substitute_member_id === subId
  )
}

function getMemberName(id: number) {
  return membersStore.getMemberById(id)?.name || `成员${id}`
}

const heightColorMap: Record<HeightRange, string> = {
  short: 'bg-green-500',
  medium: 'bg-blue-500',
  tall: 'bg-orange-500',
}

function getHeightColor(range: HeightRange) {
  return heightColorMap[range]
}

function getHeightBg(memberId: number) {
  const member = membersStore.getMemberById(memberId)
  return member ? heightColorMap[member.height_range] : 'bg-gray-500'
}

async function toggleAttendance(memberId: number) {
  if (!selectedSongId.value) return
  const newStatus: 'present' | 'absent' = isPresent(memberId) ? 'absent' : 'present'
  try {
    await substitutesStore.markAttendance({
      member_id: memberId,
      song_id: selectedSongId.value,
      status: newStatus,
      date: new Date().toISOString().slice(0, 10),
    })
    if (newStatus === 'absent') {
      await substitutesStore.fetchRecommendations(selectedSongId.value, memberId)
      recommendationsMap.value.set(memberId, substitutesStore.recommendations)
    } else {
      recommendationsMap.value.delete(memberId)
    }
  } catch {
    alert('更新出勤状态失败')
  }
}

async function confirmSub(absentId: number, subId: number) {
  if (!selectedSongId.value || !currentFormation.value) return
  const absentPos = currentFormation.value.positions.find((p) => p.member_id === absentId)
  try {
    await substitutesStore.assignSubstitute({
      song_id: selectedSongId.value,
      absent_member_id: absentId,
      substitute_member_id: subId,
      position_id: absentPos?.position_id || '',
      priority: substitutesStore.substitutes.filter((s) => s.absent_member_id === absentId).length + 1,
    })
  } catch {
    alert('确认替补失败')
  }
}

async function handleLock() {
  if (!selectedSongId.value || !currentFormation.value) return
  if (!confirm('确认锁定替补安排？锁定后不可修改。')) return
  try {
    await formationsStore.lockFormation(currentFormation.value.id)
    alert('替补安排已锁定')
  } catch {
    alert('锁定失败')
  }
}

watch(selectedSongId, async (id) => {
  if (id) {
    await Promise.all([
      formationsStore.fetchFormation(id),
      substitutesStore.fetchAttendance(id),
      substitutesStore.fetchSubstitutes(id),
    ])
    recommendationsMap.value.clear()
  }
})

onMounted(() => {
  songsStore.fetchSongs()
  membersStore.fetchMembers()
})
</script>
