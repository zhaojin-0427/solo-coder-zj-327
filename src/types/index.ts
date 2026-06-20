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
