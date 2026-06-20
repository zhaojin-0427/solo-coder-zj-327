import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
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
import { useApi } from '@/composables/useApi'

export const useSafetyStore = defineStore('safety', () => {
  const api = useApi()

  const healthRecords = ref<MemberHealthRecord[]>([])
  const memberWithHealth = ref<MemberWithHealth | null>(null)
  const checklists = ref<TrainingSafetyChecklist[]>([])
  const currentChecklist = ref<TrainingSafetyChecklist | null>(null)
  const incidents = ref<EmergencyIncident[]>([])
  const currentIncident = ref<EmergencyIncident | null>(null)
  const riskMembers = ref<RiskMember[]>([])
  const currentRiskMember = ref<RiskMember | null>(null)
  const hazards = ref<VenueHazard[]>([])
  const currentHazard = ref<VenueHazard | null>(null)
  const riskAssessment = ref<RiskAssessment | null>(null)

  const statsOverview = ref<SafetyStatOverview | null>(null)
  const incidentTypeStats = ref<IncidentTypeStat[]>([])
  const rehearsalStats = ref<SafetyStatItem[]>([])
  const highRiskMemberStats = ref<HighRiskMemberItem[]>([])
  const hazardTypeStats = ref<HazardTypeStat[]>([])
  const emergencyResponseStats = ref<EmergencyResponseStat | null>(null)

  const loading = ref(false)

  async function fetchHealthRecords(memberId?: number) {
    loading.value = true
    try {
      healthRecords.value = await api.safety.healthRecords.list(memberId)
    } catch (e) {
      console.error('Failed to fetch health records', e)
      healthRecords.value = []
    } finally {
      loading.value = false
    }
  }

  async function getHealthRecord(recordId: number) {
    try {
      return await api.safety.healthRecords.get(recordId)
    } catch (e) {
      console.error('Failed to get health record', e)
      return null
    }
  }

  async function createHealthRecord(data: {
    member_id: number
    record_date: string
    condition_type: string
    description?: string
    is_chronic?: boolean
    needs_accommodation?: boolean
    accommodation_notes?: string
  }) {
    const result = await api.safety.healthRecords.create(data)
    healthRecords.value.push(result)
    return result
  }

  async function updateHealthRecord(
    recordId: number,
    data: {
      condition_type?: string
      description?: string
      is_chronic?: boolean
      needs_accommodation?: boolean
      accommodation_notes?: string
    }
  ) {
    const result = await api.safety.healthRecords.update(recordId, data)
    const idx = healthRecords.value.findIndex((r) => r.id === recordId)
    if (idx >= 0) {
      healthRecords.value[idx] = result
    }
    return result
  }

  async function deleteHealthRecord(recordId: number) {
    await api.safety.healthRecords.delete(recordId)
    healthRecords.value = healthRecords.value.filter((r) => r.id !== recordId)
  }

  async function fetchMemberWithHealth(memberId: number) {
    try {
      memberWithHealth.value = await api.safety.getMemberWithHealth(memberId)
    } catch (e) {
      console.error('Failed to fetch member with health', e)
      memberWithHealth.value = null
    }
  }

  async function fetchChecklists(rehearsalId?: number) {
    loading.value = true
    try {
      checklists.value = await api.safety.checklists.list(rehearsalId)
    } catch (e) {
      console.error('Failed to fetch checklists', e)
      checklists.value = []
    } finally {
      loading.value = false
    }
  }

  async function getChecklist(checklistId: number) {
    loading.value = true
    try {
      currentChecklist.value = await api.safety.checklists.get(checklistId)
    } catch (e) {
      console.error('Failed to get checklist', e)
      currentChecklist.value = null
    } finally {
      loading.value = false
    }
  }

  async function createChecklist(data: {
    rehearsal_id: number
    ground_condition: GroundCondition
    ground_notes?: string
    audio_cables_arranged?: boolean
    audio_cables_notes?: string
    members_illness_reported?: boolean
    illness_notes?: string
    weather_temperature?: number
    weather_condition?: WeatherCondition
    weather_notes?: string
    drinking_water_provided?: boolean
    rest_schedule_arranged?: boolean
    rest_notes?: string
    high_risk_moves_reminded?: boolean
    high_risk_moves_notes?: string
    created_by?: number
  }) {
    const result = await api.safety.checklists.create(data)
    checklists.value.unshift(result)
    return result
  }

  async function updateChecklist(
    checklistId: number,
    data: {
      ground_condition?: GroundCondition
      ground_notes?: string
      audio_cables_arranged?: boolean
      audio_cables_notes?: string
      members_illness_reported?: boolean
      illness_notes?: string
      weather_temperature?: number
      weather_condition?: WeatherCondition
      weather_notes?: string
      drinking_water_provided?: boolean
      rest_schedule_arranged?: boolean
      rest_notes?: string
      high_risk_moves_reminded?: boolean
      high_risk_moves_notes?: string
    }
  ) {
    const result = await api.safety.checklists.update(checklistId, data)
    const idx = checklists.value.findIndex((c) => c.id === checklistId)
    if (idx >= 0) {
      checklists.value[idx] = result
    }
    if (currentChecklist.value?.id === checklistId) {
      currentChecklist.value = result
    }
    return result
  }

  async function deleteChecklist(checklistId: number) {
    await api.safety.checklists.delete(checklistId)
    checklists.value = checklists.value.filter((c) => c.id !== checklistId)
    if (currentChecklist.value?.id === checklistId) {
      currentChecklist.value = null
    }
  }

  async function assessRisks(checklistId: number) {
    loading.value = true
    try {
      riskAssessment.value = await api.safety.checklists.assessRisks(checklistId)
    } catch (e) {
      console.error('Failed to assess risks', e)
      riskAssessment.value = null
    } finally {
      loading.value = false
    }
  }

  async function fetchIncidents(checklistId?: number, memberId?: number) {
    loading.value = true
    try {
      incidents.value = await api.safety.incidents.list(checklistId, memberId)
    } catch (e) {
      console.error('Failed to fetch incidents', e)
      incidents.value = []
    } finally {
      loading.value = false
    }
  }

  async function getIncident(incidentId: number) {
    try {
      currentIncident.value = await api.safety.incidents.get(incidentId)
    } catch (e) {
      console.error('Failed to get incident', e)
      currentIncident.value = null
    }
  }

  async function createIncident(data: {
    checklist_id: number
    member_id: number
    incident_type: IncidentType
    song_id?: number
    position_id?: string
    formation_position?: string
    description?: string
    severity?: IncidentSeverity
    treatment_given?: string
    treated_by?: string
    family_notified?: boolean
    family_notification_details?: string
    community_leader_notified?: boolean
    community_notification_details?: string
    follow_up_required?: boolean
    follow_up_notes?: string
  }) {
    const result = await api.safety.incidents.create(data)
    incidents.value.unshift(result)
    return result
  }

  async function updateIncident(
    incidentId: number,
    data: {
      description?: string
      severity?: IncidentSeverity
      treatment_given?: string
      treated_by?: string
      family_notified?: boolean
      family_notification_details?: string
      community_leader_notified?: boolean
      community_notification_details?: string
      follow_up_required?: boolean
      follow_up_notes?: string
      resolved?: boolean
    }
  ) {
    const result = await api.safety.incidents.update(incidentId, data)
    const idx = incidents.value.findIndex((i) => i.id === incidentId)
    if (idx >= 0) {
      incidents.value[idx] = result
    }
    if (currentIncident.value?.id === incidentId) {
      currentIncident.value = result
    }
    return result
  }

  async function resolveIncident(incidentId: number) {
    const result = await api.safety.incidents.resolve(incidentId)
    const idx = incidents.value.findIndex((i) => i.id === incidentId)
    if (idx >= 0) {
      incidents.value[idx] = result
    }
    return result
  }

  async function fetchRiskMembers(checklistId?: number, memberId?: number) {
    loading.value = true
    try {
      riskMembers.value = await api.safety.riskMembers.list(checklistId, memberId)
    } catch (e) {
      console.error('Failed to fetch risk members', e)
      riskMembers.value = []
    } finally {
      loading.value = false
    }
  }

  async function getRiskMember(riskMemberId: number) {
    try {
      currentRiskMember.value = await api.safety.riskMembers.get(riskMemberId)
    } catch (e) {
      console.error('Failed to get risk member', e)
      currentRiskMember.value = null
    }
  }

  async function createRiskMember(data: {
    checklist_id: number
    member_id: number
    risk_level: string
    risk_factors?: string
    recommendation?: string
  }) {
    const result = await api.safety.riskMembers.create(data)
    riskMembers.value.push(result)
    return result
  }

  async function updateRiskMember(
    riskMemberId: number,
    data: {
      risk_level?: string
      risk_factors?: string
      recommendation?: string
      action_taken?: string
      status?: RiskMemberStatus
    }
  ) {
    const result = await api.safety.riskMembers.update(riskMemberId, data)
    const idx = riskMembers.value.findIndex((r) => r.id === riskMemberId)
    if (idx >= 0) {
      riskMembers.value[idx] = result
    }
    return result
  }

  async function fetchHazards(rehearsalId?: number, unresolvedOnly?: boolean) {
    loading.value = true
    try {
      hazards.value = await api.safety.hazards.list(rehearsalId, unresolvedOnly)
    } catch (e) {
      console.error('Failed to fetch hazards', e)
      hazards.value = []
    } finally {
      loading.value = false
    }
  }

  async function getHazard(hazardId: number) {
    try {
      currentHazard.value = await api.safety.hazards.get(hazardId)
    } catch (e) {
      console.error('Failed to get hazard', e)
      currentHazard.value = null
    }
  }

  async function createHazard(data: {
    rehearsal_id: number
    hazard_type: HazardType
    location?: string
    description?: string
    severity?: string
    reported_by?: number
  }) {
    const result = await api.safety.hazards.create(data)
    hazards.value.unshift(result)
    return result
  }

  async function updateHazard(
    hazardId: number,
    data: {
      hazard_type?: HazardType
      location?: string
      description?: string
      severity?: string
      resolved?: boolean
      resolution_notes?: string
    }
  ) {
    const result = await api.safety.hazards.update(hazardId, data)
    const idx = hazards.value.findIndex((h) => h.id === hazardId)
    if (idx >= 0) {
      hazards.value[idx] = result
    }
    return result
  }

  async function resolveHazard(hazardId: number) {
    const result = await api.safety.hazards.resolve(hazardId)
    const idx = hazards.value.findIndex((h) => h.id === hazardId)
    if (idx >= 0) {
      hazards.value[idx] = result
    }
    return result
  }

  async function fetchStatsOverview() {
    try {
      statsOverview.value = await api.safety.stats.overview()
    } catch (e) {
      console.error('Failed to fetch stats overview', e)
      statsOverview.value = null
    }
  }

  async function fetchIncidentTypeStats() {
    try {
      incidentTypeStats.value = await api.safety.stats.incidentTypes()
    } catch (e) {
      console.error('Failed to fetch incident type stats', e)
      incidentTypeStats.value = []
    }
  }

  async function fetchRehearsalStats() {
    try {
      rehearsalStats.value = await api.safety.stats.rehearsals()
    } catch (e) {
      console.error('Failed to fetch rehearsal stats', e)
      rehearsalStats.value = []
    }
  }

  async function fetchHighRiskMemberStats() {
    try {
      highRiskMemberStats.value = await api.safety.stats.highRiskMembers()
    } catch (e) {
      console.error('Failed to fetch high risk member stats', e)
      highRiskMemberStats.value = []
    }
  }

  async function fetchHazardTypeStats() {
    try {
      hazardTypeStats.value = await api.safety.stats.hazardTypes()
    } catch (e) {
      console.error('Failed to fetch hazard type stats', e)
      hazardTypeStats.value = []
    }
  }

  async function fetchEmergencyResponseStats() {
    try {
      emergencyResponseStats.value = await api.safety.stats.emergencyResponse()
    } catch (e) {
      console.error('Failed to fetch emergency response stats', e)
      emergencyResponseStats.value = null
    }
  }

  async function fetchAllStats() {
    loading.value = true
    try {
      await Promise.all([
        fetchStatsOverview(),
        fetchIncidentTypeStats(),
        fetchRehearsalStats(),
        fetchHighRiskMemberStats(),
        fetchHazardTypeStats(),
        fetchEmergencyResponseStats(),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    healthRecords,
    memberWithHealth,
    checklists,
    currentChecklist,
    incidents,
    currentIncident,
    riskMembers,
    currentRiskMember,
    hazards,
    currentHazard,
    riskAssessment,
    statsOverview,
    incidentTypeStats,
    rehearsalStats,
    highRiskMemberStats,
    hazardTypeStats,
    emergencyResponseStats,
    loading,
    fetchHealthRecords,
    getHealthRecord,
    createHealthRecord,
    updateHealthRecord,
    deleteHealthRecord,
    fetchMemberWithHealth,
    fetchChecklists,
    getChecklist,
    createChecklist,
    updateChecklist,
    deleteChecklist,
    assessRisks,
    fetchIncidents,
    getIncident,
    createIncident,
    updateIncident,
    resolveIncident,
    fetchRiskMembers,
    getRiskMember,
    createRiskMember,
    updateRiskMember,
    fetchHazards,
    getHazard,
    createHazard,
    updateHazard,
    resolveHazard,
    fetchStatsOverview,
    fetchIncidentTypeStats,
    fetchRehearsalStats,
    fetchHighRiskMemberStats,
    fetchHazardTypeStats,
    fetchEmergencyResponseStats,
    fetchAllStats,
  }
})
