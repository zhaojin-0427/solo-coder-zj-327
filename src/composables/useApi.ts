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
  MemberHealthRecord,
  MemberWithHealth,
  TrainingSafetyChecklist,
  EmergencyIncident,
  RiskMember,
  RiskAssessment,
  VenueHazard,
  SafetyStatOverview,
  IncidentTypeStat,
  SafetyStatItem,
  HighRiskMemberItem,
  HazardTypeStat,
  EmergencyResponseStat,
  GroundCondition,
  WeatherCondition,
  IncidentType,
  IncidentSeverity,
  HazardType,
  RiskMemberStatus,
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
    safety: {
      healthRecords: {
        list: (memberId?: number) =>
          api.get<MemberHealthRecord[]>('/safety/health-records' + (memberId ? `?member_id=${memberId}` : '')).then((r) => r.data),
        get: (recordId: number) =>
          api.get<MemberHealthRecord>(`/safety/health-records/${recordId}`).then((r) => r.data),
        create: (data: { member_id: number; record_date: string; condition_type: string; description?: string; is_chronic?: boolean; needs_accommodation?: boolean; accommodation_notes?: string }) =>
          api.post<MemberHealthRecord>('/safety/health-records', data).then((r) => r.data),
        update: (recordId: number, data: { condition_type?: string; description?: string; is_chronic?: boolean; needs_accommodation?: boolean; accommodation_notes?: string }) =>
          api.put<MemberHealthRecord>(`/safety/health-records/${recordId}`, data).then((r) => r.data),
        delete: (recordId: number) =>
          api.delete(`/safety/health-records/${recordId}`).then((r) => r.data),
      },
      getMemberWithHealth: (memberId: number) =>
        api.get<MemberWithHealth>(`/safety/members/${memberId}/health`).then((r) => r.data),
      checklists: {
        list: (rehearsalId?: number) =>
          api.get<TrainingSafetyChecklist[]>('/safety/checklists' + (rehearsalId ? `?rehearsal_id=${rehearsalId}` : '')).then((r) => r.data),
        get: (checklistId: number) =>
          api.get<TrainingSafetyChecklist>(`/safety/checklists/${checklistId}`).then((r) => r.data),
        create: (data: { rehearsal_id: number; ground_condition: GroundCondition; ground_notes?: string; audio_cables_arranged?: boolean; audio_cables_notes?: string; members_illness_reported?: boolean; illness_notes?: string; weather_temperature?: number; weather_condition?: WeatherCondition; weather_notes?: string; drinking_water_provided?: boolean; rest_schedule_arranged?: boolean; rest_notes?: string; high_risk_moves_reminded?: boolean; high_risk_moves_notes?: string; created_by?: number }) =>
          api.post<TrainingSafetyChecklist>('/safety/checklists', data).then((r) => r.data),
        update: (checklistId: number, data: { ground_condition?: GroundCondition; ground_notes?: string; audio_cables_arranged?: boolean; audio_cables_notes?: string; members_illness_reported?: boolean; illness_notes?: string; weather_temperature?: number; weather_condition?: WeatherCondition; weather_notes?: string; drinking_water_provided?: boolean; rest_schedule_arranged?: boolean; rest_notes?: string; high_risk_moves_reminded?: boolean; high_risk_moves_notes?: string }) =>
          api.put<TrainingSafetyChecklist>(`/safety/checklists/${checklistId}`, data).then((r) => r.data),
        delete: (checklistId: number) =>
          api.delete(`/safety/checklists/${checklistId}`).then((r) => r.data),
        assessRisks: (checklistId: number) =>
          api.get<RiskAssessment>(`/safety/checklists/${checklistId}/risk-assessment`).then((r) => r.data),
      },
      incidents: {
        list: (checklistId?: number, memberId?: number) => {
          let url = '/safety/incidents'
          const params: string[] = []
          if (checklistId) params.push(`checklist_id=${checklistId}`)
          if (memberId) params.push(`member_id=${memberId}`)
          if (params.length) url += '?' + params.join('&')
          return api.get<EmergencyIncident[]>(url).then((r) => r.data)
        },
        get: (incidentId: number) =>
          api.get<EmergencyIncident>(`/safety/incidents/${incidentId}`).then((r) => r.data),
        create: (data: { checklist_id: number; member_id: number; incident_type: IncidentType; song_id?: number; position_id?: string; formation_position?: string; description?: string; severity?: IncidentSeverity; treatment_given?: string; treated_by?: string; family_notified?: boolean; family_notification_details?: string; community_leader_notified?: boolean; community_notification_details?: string; follow_up_required?: boolean; follow_up_notes?: string }) =>
          api.post<EmergencyIncident>('/safety/incidents', data).then((r) => r.data),
        update: (incidentId: number, data: { description?: string; severity?: IncidentSeverity; treatment_given?: string; treated_by?: string; family_notified?: boolean; family_notification_details?: string; community_leader_notified?: boolean; community_notification_details?: string; follow_up_required?: boolean; follow_up_notes?: string; resolved?: boolean }) =>
          api.put<EmergencyIncident>(`/safety/incidents/${incidentId}`, data).then((r) => r.data),
        resolve: (incidentId: number) =>
          api.post<EmergencyIncident>(`/safety/incidents/${incidentId}/resolve`).then((r) => r.data),
      },
      riskMembers: {
        list: (checklistId?: number, memberId?: number) => {
          let url = '/safety/risk-members'
          const params: string[] = []
          if (checklistId) params.push(`checklist_id=${checklistId}`)
          if (memberId) params.push(`member_id=${memberId}`)
          if (params.length) url += '?' + params.join('&')
          return api.get<RiskMember[]>(url).then((r) => r.data)
        },
        get: (riskMemberId: number) =>
          api.get<RiskMember>(`/safety/risk-members/${riskMemberId}`).then((r) => r.data),
        create: (data: { checklist_id: number; member_id: number; risk_level: string; risk_factors?: string; recommendation?: string }) =>
          api.post<RiskMember>('/safety/risk-members', data).then((r) => r.data),
        update: (riskMemberId: number, data: { risk_level?: string; risk_factors?: string; recommendation?: string; action_taken?: string; status?: RiskMemberStatus }) =>
          api.put<RiskMember>(`/safety/risk-members/${riskMemberId}`, data).then((r) => r.data),
      },
      hazards: {
        list: (rehearsalId?: number, unresolvedOnly?: boolean) => {
          let url = '/safety/hazards'
          const params: string[] = []
          if (rehearsalId) params.push(`rehearsal_id=${rehearsalId}`)
          if (unresolvedOnly) params.push(`unresolved_only=${unresolvedOnly}`)
          if (params.length) url += '?' + params.join('&')
          return api.get<VenueHazard[]>(url).then((r) => r.data)
        },
        get: (hazardId: number) =>
          api.get<VenueHazard>(`/safety/hazards/${hazardId}`).then((r) => r.data),
        create: (data: { rehearsal_id: number; hazard_type: HazardType; location?: string; description?: string; severity?: string; reported_by?: number }) =>
          api.post<VenueHazard>('/safety/hazards', data).then((r) => r.data),
        update: (hazardId: number, data: { hazard_type?: HazardType; location?: string; description?: string; severity?: string; resolved?: boolean; resolution_notes?: string }) =>
          api.put<VenueHazard>(`/safety/hazards/${hazardId}`, data).then((r) => r.data),
        resolve: (hazardId: number) =>
          api.post<VenueHazard>(`/safety/hazards/${hazardId}/resolve`).then((r) => r.data),
      },
      stats: {
        overview: () =>
          api.get<SafetyStatOverview>('/safety/stats/overview').then((r) => r.data),
        incidentTypes: () =>
          api.get<IncidentTypeStat[]>('/safety/stats/incident-types').then((r) => r.data),
        rehearsals: () =>
          api.get<SafetyStatItem[]>('/safety/stats/rehearsals').then((r) => r.data),
        highRiskMembers: () =>
          api.get<HighRiskMemberItem[]>('/safety/stats/high-risk-members').then((r) => r.data),
        hazardTypes: () =>
          api.get<HazardTypeStat[]>('/safety/stats/hazard-types').then((r) => r.data),
        emergencyResponse: () =>
          api.get<EmergencyResponseStat>('/safety/stats/emergency-response').then((r) => r.data),
      },
    },
  }
}
