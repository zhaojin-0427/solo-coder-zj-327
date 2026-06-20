import axios from 'axios'
import type {
  Song,
  Member,
  HeightRange,
  Formation,
  FormationVersion,
  FormationPosition,
  RehearsalRecord,
  RehearsalDetail,
  SubstituteAssignment,
  AttendanceRecord,
  SubstituteRecommend,
  OverviewStats,
  RehearsalCountItem,
  SubstituteRateItem,
  ErrorPositionItem,
  AttendanceStatItem,
  PerformanceTask,
  PerformanceTaskDetail,
  PerformanceTaskWithSongDetails,
  PerformanceConfirmation,
  PerformanceSongTaskCreate,
  PerformanceConfirmationStatItem,
  Checklist,
  ChecklistSummary,
  CheckItem,
  CheckItemAbnormalDetail,
  PreCheckStatItem,
  MemberCompletionRankItem,
  FrequentAbnormalTypeItem,
} from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export function useApi() {
  return {
    songs: {
      list: () => api.get<Song[]>('/songs').then((r) => r.data),
      get: (id: number) => api.get<Song>(`/songs/${id}`).then((r) => r.data),
      create: (data: Partial<Song>) => api.post<Song>('/songs', data).then((r) => r.data),
      update: (id: number, data: Partial<Song>) => api.put<Song>(`/songs/${id}`, data).then((r) => r.data),
      delete: (id: number) => api.delete(`/songs/${id}`).then((r) => r.data),
    },
    members: {
      list: () => api.get<Member[]>('/members').then((r) => r.data),
      get: (id: number) => api.get<Member>(`/members/${id}`).then((r) => r.data),
      create: (data: { name: string; height_range: HeightRange; phone?: string; song_ids?: number[]; substitute_positions?: string[] }) =>
        api.post<Member>('/members', data).then((r) => r.data),
      update: (id: number, data: Partial<Member>) => api.put<Member>(`/members/${id}`, data).then((r) => r.data),
      delete: (id: number) => api.delete(`/members/${id}`).then((r) => r.data),
    },
    formations: {
      getCurrent: (songId: number) => api.get<Formation>(`/formations/${songId}`).then((r) => r.data),
      getVersions: (songId: number) => api.get<FormationVersion[]>(`/formations/${songId}/versions`).then((r) => r.data),
      getById: (id: number) => api.get<Formation>(`/formations/by-id/${id}`).then((r) => r.data),
      generate: (songId: number) => api.post<Formation>(`/formations/generate/${songId}`).then((r) => r.data),
      update: (id: number, data: { positions: { id: number; x?: number; y?: number; member_id?: number }[] }) =>
        api.put<Formation>(`/formations/${id}`, data).then((r) => r.data),
      lock: (id: number) => api.post<Formation>(`/formations/${id}/lock`).then((r) => r.data),
    },
    rehearsals: {
      list: (songId?: number) =>
        api.get<RehearsalRecord[]>('/rehearsals' + (songId ? `?song_id=${songId}` : '')).then((r) => r.data),
      get: (id: number) => api.get<RehearsalDetail>(`/rehearsals/${id}`).then((r) => r.data),
      create: (data: { song_id: number; date: string; duration_minutes?: number; teacher_notes?: string; errors?: { position_id: string; error_type: string; beat_number?: number; description?: string }[] }) =>
        api.post<RehearsalRecord>('/rehearsals', data).then((r) => r.data),
    },
    substitutes: {
      list: (songId: number) => api.get<SubstituteAssignment[]>(`/substitutes/${songId}`).then((r) => r.data),
      recommend: (songId: number, absentMemberId: number) =>
        api.get<SubstituteRecommend[]>(`/substitutes/recommend?song_id=${songId}&absent_member_id=${absentMemberId}`).then((r) => r.data),
      assign: (data: { song_id: number; absent_member_id: number; substitute_member_id: number; position_id: string; priority?: number }) =>
        api.post<SubstituteAssignment>('/substitutes/assign', data).then((r) => r.data),
      updatePriority: (id: number, priority: number) =>
        api.put<SubstituteAssignment>(`/substitutes/${id}/priority`, { priority }).then((r) => r.data),
    },
    attendance: {
      mark: (data: { member_id: number; song_id: number; date: string; status: string }) =>
        api.post<AttendanceRecord>('/substitutes/attendance', data).then((r) => r.data),
      list: (songId: number) =>
        api.get<AttendanceRecord[]>(`/substitutes/attendance?song_id=${songId}`).then((r) => r.data),
    },
    statistics: {
      overview: () => api.get<OverviewStats>('/statistics/overview').then((r) => r.data),
      rehearsalCounts: () => api.get<RehearsalCountItem[]>('/statistics/rehearsal-counts').then((r) => r.data),
      substituteRates: () => api.get<SubstituteRateItem[]>('/statistics/substitute-rates').then((r) => r.data),
      errorPositions: () => api.get<ErrorPositionItem[]>('/statistics/error-positions').then((r) => r.data),
      attendance: () => api.get<AttendanceStatItem[]>('/statistics/attendance').then((r) => r.data),
      performanceConfirmations: () =>
        api.get<PerformanceConfirmationStatItem[]>('/statistics/performance-confirmations').then((r) => r.data),
    },
    performances: {
      list: () => api.get<PerformanceTask[]>('/performances').then((r) => r.data),
      get: (id: number) => api.get<PerformanceTaskDetail>(`/performances/${id}`).then((r) => r.data),
      getWithSongDetails: (id: number) =>
        api.get<PerformanceTaskWithSongDetails>(`/performances/${id}/details`).then((r) => r.data),
      create: (data: {
        name: string
        location: string
        meeting_time: string
        start_time: string
        costume_requirements?: string | null
        notes?: string | null
        song_tasks?: PerformanceSongTaskCreate[]
        member_ids?: number[]
      }) => api.post<PerformanceTask>('/performances', data).then((r) => r.data),
      update: (
        id: number,
        data: {
          name?: string
          location?: string
          meeting_time?: string
          start_time?: string
          costume_requirements?: string | null
          notes?: string | null
          song_tasks?: PerformanceSongTaskCreate[]
          member_ids?: number[]
        }
      ) => api.put<PerformanceTask>(`/performances/${id}`, data).then((r) => r.data),
      delete: (id: number) => api.delete(`/performances/${id}`).then((r) => r.data),
      updateConfirmation: (taskId: number, memberId: number, data: {
        status?: string
        transport_mode?: string | null
        remark?: string | null
        phone_reminded?: boolean
      }) =>
        api.put<PerformanceConfirmation>(`/performances/${taskId}/confirmations/${memberId}`, data).then((r) => r.data),
      markPhoneReminded: (taskId: number, memberId: number) =>
        api.post<PerformanceConfirmation>(`/performances/${taskId}/confirmations/${memberId}/phone-reminded`).then((r) => r.data),
    },
    checklists: {
      generate: (performanceId: number, items?: { song_id: number; category: string; item_name: string; responsible_member_id?: number; position_id?: string; deadline?: string }[]) =>
        api.post<Checklist>(`/checklists/performances/${performanceId}`, { items: items || [] }).then((r) => r.data),
      getByPerformance: (performanceId: number) =>
        api.get<Checklist>(`/checklists/performances/${performanceId}`).then((r) => r.data),
      getSummary: (performanceId: number) =>
        api.get<ChecklistSummary>(`/checklists/performances/${performanceId}/summary`).then((r) => r.data),
      getAbnormalItems: (performanceId: number) =>
        api.get<CheckItemAbnormalDetail[]>(`/checklists/performances/${performanceId}/abnormal`).then((r) => r.data),
      getMemberItems: (performanceId: number, memberId: number) =>
        api.get<CheckItem[]>(`/checklists/performances/${performanceId}/member/${memberId}`).then((r) => r.data),
      updateItem: (itemId: number, data: { status?: string; abnormal_description?: string; photo_url?: string }) =>
        api.put<CheckItem>(`/checklists/items/${itemId}`, data).then((r) => r.data),
      addItem: (performanceId: number, data: { song_id: number; category: string; item_name: string; responsible_member_id?: number; position_id?: string; deadline?: string }) =>
        api.post<CheckItem>(`/checklists/performances/${performanceId}/items`, data).then((r) => r.data),
      deleteItem: (itemId: number) =>
        api.delete(`/checklists/items/${itemId}`).then((r) => r.data),
      getAllSummaries: () =>
        api.get<ChecklistSummary[]>('/checklists/summaries').then((r) => r.data),
      getPreCheckStats: () =>
        api.get<PreCheckStatItem[]>('/checklists/stats/pre-check').then((r) => r.data),
      getMemberRank: () =>
        api.get<MemberCompletionRankItem[]>('/checklists/stats/member-rank').then((r) => r.data),
      getAbnormalTypes: () =>
        api.get<FrequentAbnormalTypeItem[]>('/checklists/stats/abnormal-types').then((r) => r.data),
    },
  }
}
