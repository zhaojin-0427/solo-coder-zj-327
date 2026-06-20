export type FormationType = 'line' | 'triangle' | 'square' | 'circle' | 'double_row' | 'v_shape'
export type HeightRange = 'short' | 'medium' | 'tall'
export type AttendanceStatus = 'present' | 'absent'
export type ErrorType = 'beat_error' | 'position_error'
export type PerformanceConfirmationStatus = 'unconfirmed' | 'confirmed' | 'leave'

export interface Song {
  id: number
  name: string
  beat_count: number
  formation_type: FormationType
  performance_order: number
  created_at: string
  updated_at: string
}

export interface Member {
  id: number
  name: string
  height_range: HeightRange
  phone: string
  song_ids: number[]
  substitute_positions: string[]
  created_at: string
}

export interface FormationPosition {
  id: number
  position_id: string
  x: number
  y: number
  row_num: number
  col_num: number
  member_id: number | null
}

export interface Formation {
  id: number
  song_id: number
  version: number
  positions: FormationPosition[]
  is_locked: boolean
  created_at: string
}

export interface FormationVersion {
  id: number
  version: number
  is_locked: boolean
  created_at: string
}

export interface RehearsalRecord {
  id: number
  song_id: number
  date: string
  duration_minutes: number
  teacher_notes: string
  created_at: string
}

export interface RehearsalDetail extends RehearsalRecord {
  errors: RehearsalError[]
}

export interface RehearsalError {
  id: number
  position_id: string
  error_type: string
  beat_number: number | null
  description: string | null
}

export interface SubstituteAssignment {
  id: number
  song_id: number
  absent_member_id: number
  substitute_member_id: number
  position_id: string
  priority: number
}

export interface AttendanceRecord {
  id: number
  member_id: number
  song_id: number
  date: string
  status: AttendanceStatus
}

export interface SubstituteRecommend {
  member_id: number
  name: string
  matched_positions: string[]
  priority: number
}

export interface OverviewStats {
  total_songs: number
  total_members: number
  total_rehearsals: number
  total_formations: number
}

export interface RehearsalCountItem {
  song_id: number
  song_name: string
  count: number
}

export interface SubstituteRateItem {
  song_id: number
  song_name: string
  total_assignments: number
  total_rehearsals: number
  rate: number
}

export interface ErrorPositionItem {
  position_id: string
  count: number
}

export interface AttendanceStatItem {
  member_id: number
  member_name: string
  present_count: number
  absent_count: number
  attendance_rate: number
}

export interface PerformanceSongTask {
  id: number
  song_id: number
  song_name: string
  formation_id: number | null
  formation_version: number | null
  performance_order: number
}

export interface PerformanceSongTaskCreate {
  song_id: number
  formation_id?: number | null
  performance_order?: number
}

export interface PerformanceTask {
  id: number
  name: string
  location: string
  meeting_time: string
  start_time: string
  costume_requirements: string | null
  notes: string | null
  created_at: string
  song_tasks: PerformanceSongTask[]
  total_members: number
  confirmed_count: number
  unconfirmed_count: number
  leave_count: number
}

export interface PerformanceConfirmation {
  id: number
  performance_id: number
  member_id: number
  member_name: string
  member_phone: string | null
  status: PerformanceConfirmationStatus
  transport_mode: string | null
  remark: string | null
  phone_reminded: boolean
  confirmed_at: string | null
}

export interface PerformanceTaskDetail extends PerformanceTask {
  confirmations: PerformanceConfirmation[]
}

export interface LeaveMemberItem {
  position_id: string
  member_id: number
  member_name: string
}

export interface ConfirmedSubstituteItem {
  position_id: string
  substitute_member_id: number
  substitute_member_name: string
}

export interface SongPerformanceDetail {
  song_id: number
  song_name: string
  formation_id: number | null
  formation_version: number | null
  total_positions: number
  leave_members: LeaveMemberItem[]
  confirmed_substitutes: ConfirmedSubstituteItem[]
  gap_positions: string[]
}

export interface PerformanceTaskWithSongDetails extends PerformanceTaskDetail {
  song_details: SongPerformanceDetail[]
}

export interface PerformanceConfirmationStatItem {
  performance_id: number
  performance_name: string
  performance_date: string
  total_members: number
  confirmed_count: number
  unconfirmed_count: number
  leave_count: number
  confirmation_rate: number
  phone_reminded_count: number
  phone_reminder_rate: number
}

export const FORMATION_TYPE_MAP: Record<FormationType, string> = {
  line: '一字排',
  triangle: '三角阵',
  square: '方块阵',
  circle: '圆形阵',
  double_row: '双排阵',
  v_shape: 'V字阵',
}

export const HEIGHT_RANGE_MAP: Record<HeightRange, string> = {
  short: '娇小(＜160cm)',
  medium: '中等(160-168cm)',
  tall: '高挑(＞168cm)',
}

export const CONFIRMATION_STATUS_MAP: Record<PerformanceConfirmationStatus, string> = {
  unconfirmed: '未确认',
  confirmed: '已确认',
  leave: '请假',
}

export const CONFIRMATION_STATUS_COLOR_MAP: Record<PerformanceConfirmationStatus, string> = {
  unconfirmed: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-green-100 text-green-700',
  leave: 'bg-red-100 text-red-700',
}

export type CheckItemCategory = 'costume' | 'prop' | 'audio' | 'accompaniment' | 'transport' | 'substitute'
export type CheckItemStatus = 'not_started' | 'in_progress' | 'abnormal' | 'completed'

export interface CheckItem {
  id: number
  checklist_id: number
  song_id: number
  song_name: string
  category: CheckItemCategory
  item_name: string
  responsible_member_id: number | null
  responsible_member_name: string | null
  position_id: string | null
  deadline: string | null
  status: CheckItemStatus
  abnormal_description: string | null
  photo_url: string | null
  completed_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface Checklist {
  id: number
  performance_id: number
  created_at: string | null
  items: CheckItem[]
}

export interface ChecklistSummary {
  performance_id: number
  performance_name: string
  total_items: number
  not_started_count: number
  in_progress_count: number
  abnormal_count: number
  completed_count: number
  completion_rate: number
}

export interface CheckItemAbnormalDetail {
  item_id: number
  item_name: string
  category: CheckItemCategory
  song_id: number
  song_name: string
  responsible_member_id: number | null
  responsible_member_name: string | null
  position_id: string | null
  abnormal_description: string | null
}

export interface PreCheckStatItem {
  performance_id: number
  performance_name: string
  performance_date: string
  total_items: number
  completed_count: number
  abnormal_count: number
  completion_rate: number
}

export interface MemberCompletionRankItem {
  member_id: number
  member_name: string
  total_assigned: number
  completed_count: number
  abnormal_count: number
  completion_rate: number
}

export interface FrequentAbnormalTypeItem {
  category: CheckItemCategory
  count: number
}

export const CHECK_CATEGORY_MAP: Record<CheckItemCategory, string> = {
  costume: '服装',
  prop: '道具',
  audio: '音响',
  accompaniment: '伴奏文件',
  transport: '交通集合',
  substitute: '替补到位',
}

export const CHECK_STATUS_MAP: Record<CheckItemStatus, string> = {
  not_started: '未开始',
  in_progress: '进行中',
  abnormal: '异常',
  completed: '已完成',
}

export const CHECK_STATUS_COLOR_MAP: Record<CheckItemStatus, string> = {
  not_started: 'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-700',
  abnormal: 'bg-red-100 text-red-700',
  completed: 'bg-green-100 text-green-700',
}

export type HealthConditionType = 'heart_disease' | 'hypertension' | 'diabetes' | 'asthma' | 'joint_pain' | 'dizziness' | 'allergy' | 'injury' | 'other'
export type GroundCondition = 'good' | 'fair' | 'poor'
export type WeatherCondition = 'sunny' | 'cloudy' | 'rainy' | 'windy' | 'hot' | 'cold'
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type IncidentType = 'sprain' | 'dizziness' | 'fall' | 'cable_trip' | 'heat_stroke' | 'dehydration' | 'heart_issue' | 'breathing_difficulty' | 'injury' | 'other'
export type IncidentSeverity = 'minor' | 'moderate' | 'severe' | 'critical'
export type HazardType = 'slippery_floor' | 'obstacle' | 'loose_cable' | 'uneven_ground' | 'poor_lighting' | 'sharp_edge' | 'lack_of_first_aid' | 'other'
export type RiskMemberStatus = 'pending' | 'adjusted' | 'resting' | 'monitoring'

export const HEALTH_CONDITION_MAP: Record<HealthConditionType, string> = {
  heart_disease: '心脏病',
  hypertension: '高血压',
  diabetes: '糖尿病',
  asthma: '哮喘',
  joint_pain: '关节疼痛',
  dizziness: '眩晕症',
  allergy: '过敏',
  injury: '旧伤',
  other: '其他',
}

export const GROUND_CONDITION_MAP: Record<GroundCondition, string> = {
  good: '良好',
  fair: '一般',
  poor: '较差',
}

export const WEATHER_CONDITION_MAP: Record<WeatherCondition, string> = {
  sunny: '晴天',
  cloudy: '多云',
  rainy: '雨天',
  windy: '大风',
  hot: '高温',
  cold: '寒冷',
}

export const RISK_LEVEL_MAP: Record<RiskLevel, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '极高风险',
}

export const RISK_LEVEL_COLOR_MAP: Record<RiskLevel, string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
}

export const INCIDENT_TYPE_MAP: Record<IncidentType, string> = {
  sprain: '扭伤',
  dizziness: '头晕',
  fall: '摔倒',
  cable_trip: '设备绊线',
  heat_stroke: '中暑',
  dehydration: '脱水',
  heart_issue: '心脏不适',
  breathing_difficulty: '呼吸困难',
  injury: '受伤',
  other: '其他',
}

export const INCIDENT_SEVERITY_MAP: Record<IncidentSeverity, string> = {
  minor: '轻微',
  moderate: '中等',
  severe: '严重',
  critical: '危急',
}

export const INCIDENT_SEVERITY_COLOR_MAP: Record<IncidentSeverity, string> = {
  minor: 'bg-blue-100 text-blue-700',
  moderate: 'bg-yellow-100 text-yellow-700',
  severe: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
}

export const HAZARD_TYPE_MAP: Record<HazardType, string> = {
  slippery_floor: '地面湿滑',
  obstacle: '障碍物',
  loose_cable: '电线松动',
  uneven_ground: '地面不平',
  poor_lighting: '照明不良',
  sharp_edge: '尖锐边缘',
  lack_of_first_aid: '缺乏急救设备',
  other: '其他',
}

export const RISK_MEMBER_STATUS_MAP: Record<RiskMemberStatus, string> = {
  pending: '待处理',
  adjusted: '已调整站位',
  resting: '安排休息',
  monitoring: '持续观察',
}

export const RISK_MEMBER_STATUS_COLOR_MAP: Record<RiskMemberStatus, string> = {
  pending: 'bg-gray-100 text-gray-700',
  adjusted: 'bg-blue-100 text-blue-700',
  resting: 'bg-green-100 text-green-700',
  monitoring: 'bg-yellow-100 text-yellow-700',
}

export interface MemberHealthRecord {
  id: number
  member_id: number
  member_name: string
  record_date: string
  condition_type: HealthConditionType
  description: string | null
  is_chronic: boolean
  needs_accommodation: boolean
  accommodation_notes: string | null
  created_at: string | null
}

export interface MemberWithHealth extends Member {
  age: number | null
  emergency_contact: string | null
  health_records: MemberHealthRecord[]
}

export interface TrainingSafetyChecklist {
  id: number
  rehearsal_id: number
  song_id: number | null
  song_name: string
  rehearsal_date: string | null
  ground_condition: GroundCondition
  ground_notes: string | null
  audio_cables_arranged: boolean
  audio_cables_notes: string | null
  members_illness_reported: boolean
  illness_notes: string | null
  weather_temperature: number | null
  weather_condition: WeatherCondition | null
  weather_notes: string | null
  drinking_water_provided: boolean
  rest_schedule_arranged: boolean
  rest_notes: string | null
  high_risk_moves_reminded: boolean
  high_risk_moves_notes: string | null
  risk_level: RiskLevel
  risk_assessment_notes: string | null
  created_by: number | null
  created_by_name: string | null
  created_at: string | null
  incident_count: number
}

export interface EmergencyIncident {
  id: number
  checklist_id: number
  rehearsal_id: number | null
  member_id: number
  member_name: string
  member_phone: string | null
  emergency_contact: string | null
  incident_type: IncidentType
  song_id: number | null
  song_name: string | null
  position_id: string | null
  formation_position: string | null
  description: string | null
  severity: IncidentSeverity
  treatment_given: string | null
  treated_by: string | null
  family_notified: boolean
  family_notification_details: string | null
  community_leader_notified: boolean
  community_notification_details: string | null
  follow_up_required: boolean
  follow_up_notes: string | null
  incident_time: string | null
  resolved: boolean
  resolved_time: string | null
}

export interface RiskMember {
  id: number
  checklist_id: number
  rehearsal_id: number | null
  member_id: number
  member_name: string
  member_age: number | null
  risk_level: RiskLevel
  risk_factors: string | null
  recommendation: string | null
  action_taken: string | null
  status: RiskMemberStatus
  created_at: string | null
}

export interface RiskAssessment {
  checklist_id: number
  overall_risk_level: RiskLevel
  risk_score: number
  risk_factors: string[]
  recommendations: string[]
  high_risk_members: RiskMember[]
  weather_warning: string | null
}

export interface VenueHazard {
  id: number
  rehearsal_id: number
  song_id: number | null
  song_name: string | null
  hazard_type: HazardType
  location: string | null
  description: string | null
  severity: RiskLevel
  reported_by: number | null
  reported_by_name: string | null
  resolved: boolean
  resolution_notes: string | null
  resolved_at: string | null
  created_at: string | null
}

export interface SafetyStatOverview {
  total_checklists: number
  total_incidents: number
  total_hazards: number
  high_risk_member_count: number
  incident_rate: number
  hazard_resolution_rate: number
  avg_risk_level: RiskLevel
}

export interface IncidentTypeStat {
  incident_type: IncidentType
  count: number
  rate: number
}

export interface SafetyStatItem {
  rehearsal_id: number
  rehearsal_date: string
  song_name: string
  risk_level: RiskLevel
  incident_count: number
  hazard_count: number
  high_risk_member_count: number
  family_notified_count: number
}

export interface HighRiskMemberItem {
  member_id: number
  member_name: string
  member_age: number | null
  incident_count: number
  risk_level: RiskLevel
  health_conditions: string[]
  last_incident_date: string | null
}

export interface HazardTypeStat {
  hazard_type: HazardType
  count: number
  unresolved_count: number
}

export interface EmergencyResponseStat {
  total_incidents: number
  resolved_count: number
  resolution_rate: number
  family_notified_count: number
  family_notification_rate: number
  community_notified_count: number
  community_notification_rate: number
  avg_response_time_minutes: number | null
}
