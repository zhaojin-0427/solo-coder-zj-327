<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">训练安全检查</h1>
    </div>

    <div v-if="rehearsalsStore.loading || safetyStore.loading" class="text-center py-16 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!rehearsalsStore.rehearsals.length" class="text-center py-16">
      <ShieldCheck :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无排练记录</p>
    </div>

    <div v-else class="space-y-5">
      <div
        v-for="rehearsal in rehearsalsStore.rehearsals"
        :key="rehearsal.id"
        class="card"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-[#1F2937]">{{ getSongName(rehearsal.song_id) }}</h3>
              <span
                v-if="getChecklistForRehearsal(rehearsal.id)"
                class="px-2 py-0.5 text-xs rounded-full font-medium"
                :class="RISK_LEVEL_COLOR_MAP[getChecklistForRehearsal(rehearsal.id)!.risk_level]"
              >
                {{ RISK_LEVEL_MAP[getChecklistForRehearsal(rehearsal.id)!.risk_level] }}
              </span>
              <span v-else class="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                未检查
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-[#6B7280]">
              <span class="flex items-center gap-1.5">
                <Calendar :size="14" />
                {{ formatDate(rehearsal.date) }}
              </span>
              <span class="flex items-center gap-1.5">
                <Clock :size="14" />
                {{ rehearsal.duration_minutes }} 分钟
              </span>
              <span v-if="getChecklistForRehearsal(rehearsal.id)" class="flex items-center gap-1.5">
                <AlertTriangle :size="14" />
                {{ getChecklistForRehearsal(rehearsal.id)!.incident_count }} 起事件
              </span>
            </div>
            <p v-if="rehearsal.teacher_notes" class="text-sm text-[#6B7280] mt-2 line-clamp-1">
              备注: {{ rehearsal.teacher_notes }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!getChecklistForRehearsal(rehearsal.id)"
              class="btn-primary text-sm flex items-center gap-1.5"
              @click="openCreateChecklist(rehearsal)"
            >
              <Plus :size="16" />
              创建检查单
            </button>
            <template v-else>
              <button
                class="btn-secondary text-sm flex items-center gap-1.5"
                @click="viewChecklistDetail(rehearsal)"
              >
                <Eye :size="16" />
                查看详情
              </button>
              <button
                class="btn-accent text-sm flex items-center gap-1.5"
                @click="viewRiskAssessment(rehearsal)"
              >
                <BarChart3 :size="16" />
                风险评估
              </button>
            </template>
          </div>
        </div>

        <div v-if="getHazardsForRehearsal(rehearsal.id).length" class="border-t border-[#E5E7EB] pt-4">
          <div class="flex items-center gap-2 mb-3">
            <AlertTriangle class="text-[#E53935]" :size="16" />
            <h4 class="text-sm font-semibold text-[#1F2937]">场地隐患记录</h4>
            <span class="text-xs text-[#6B7280]">
              {{ getHazardsForRehearsal(rehearsal.id).filter(h => !h.resolved).length }} 项待处理
            </span>
          </div>
          <div class="space-y-2">
            <div
              v-for="hazard in getHazardsForRehearsal(rehearsal.id).slice(0, 3)"
              :key="hazard.id"
              class="flex items-center gap-3 p-2 rounded-lg bg-gray-50"
            >
              <div
                class="w-2 h-2 rounded-full shrink-0"
                :class="hazard.resolved ? 'bg-green-500' : 'bg-red-500'"
              ></div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-[#1F2937]">
                    {{ HAZARD_TYPE_MAP[hazard.hazard_type] }}
                  </span>
                  <span
                    class="px-1.5 py-0.5 text-xs rounded-full font-medium"
                    :class="RISK_LEVEL_COLOR_MAP[hazard.severity]"
                  >
                    {{ RISK_LEVEL_MAP[hazard.severity] }}
                  </span>
                </div>
                <p v-if="hazard.location" class="text-xs text-[#6B7280]">
                  位置: {{ hazard.location }}
                </p>
              </div>
              <span class="text-xs shrink-0" :class="hazard.resolved ? 'text-green-600' : 'text-red-600'">
                {{ hazard.resolved ? '已处理' : '待处理' }}
              </span>
            </div>
            <button
              v-if="getHazardsForRehearsal(rehearsal.id).length > 3"
              class="text-sm text-[#E53935] hover:text-[#C62828]"
              @click="viewHazards(rehearsal)"
            >
              查看全部 {{ getHazardsForRehearsal(rehearsal.id).length }} 项隐患
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
        <div class="modal-content w-[700px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              创建安全检查单 - {{ getSongName(selectedRehearsal?.song_id || 0) }}
            </h3>
            <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="closeCreateModal">
              <X :size="18" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6">
            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                  <MapPin :size="16" class="text-[#E53935]" />
                  场地地面情况 <span class="text-red-500">*</span>
                </label>
                <div class="grid grid-cols-3 gap-3">
                  <button
                    v-for="cond in GROUND_CONDITIONS"
                    :key="cond.value"
                    type="button"
                    class="p-3 rounded-lg border-2 transition-all text-center"
                    :class="checklistForm.ground_condition === cond.value
                      ? 'border-[#E53935] bg-red-50'
                      : 'border-[#E5E7EB] hover:border-gray-300'"
                    @click="checklistForm.ground_condition = cond.value"
                  >
                    <div class="font-medium text-[#1F2937]">{{ cond.label }}</div>
                  </button>
                </div>
                <input
                  v-model="checklistForm.ground_notes"
                  type="text"
                  class="input mt-2"
                  placeholder="地面情况备注（选填）"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                  <Cable :size="16" class="text-[#E53935]" />
                  音响电线摆放
                </label>
                <div class="flex items-center gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.audio_cables_arranged"
                      :value="true"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">已整理妥当</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.audio_cables_arranged"
                      :value="false"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">需要注意</span>
                  </label>
                </div>
                <input
                  v-model="checklistForm.audio_cables_notes"
                  type="text"
                  class="input mt-2"
                  placeholder="电线摆放备注（选填）"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                  <Heart :size="16" class="text-[#E53935]" />
                  队员身体不适
                </label>
                <div class="flex items-center gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.members_illness_reported"
                      :value="false"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">无异常</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.members_illness_reported"
                      :value="true"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">有不适情况</span>
                  </label>
                </div>
                <textarea
                  v-model="checklistForm.illness_notes"
                  class="input mt-2 min-h-[60px] resize-none"
                  placeholder="身体不适情况说明（选填）"
                ></textarea>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                    <Thermometer :size="16" class="text-[#E53935]" />
                    温度 (°C)
                  </label>
                  <input
                    v-model.number="checklistForm.weather_temperature"
                    type="number"
                    class="input"
                    placeholder="如：28"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                    <CloudSun :size="16" class="text-[#E53935]" />
                    天气状况
                  </label>
                  <select v-model="checklistForm.weather_condition" class="input">
                    <option :value="null">请选择</option>
                    <option v-for="cond in WEATHER_CONDITIONS" :key="cond.value" :value="cond.value">
                      {{ cond.label }}
                    </option>
                  </select>
                </div>
              </div>
              <input
                v-model="checklistForm.weather_notes"
                type="text"
                class="input"
                placeholder="天气情况备注（选填）"
              />

              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                  <Droplets :size="16" class="text-[#E53935]" />
                  饮水休息安排
                </label>
                <div class="grid grid-cols-2 gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="checklistForm.drinking_water_provided"
                      class="w-4 h-4 text-[#E53935] rounded"
                    />
                    <span class="text-sm">饮用水已准备</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      v-model="checklistForm.rest_schedule_arranged"
                      class="w-4 h-4 text-[#E53935] rounded"
                    />
                    <span class="text-sm">休息时间已安排</span>
                  </label>
                </div>
                <input
                  v-model="checklistForm.rest_notes"
                  type="text"
                  class="input mt-2"
                  placeholder="休息安排备注（选填）"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-2 flex items-center gap-2">
                  <Zap :size="16" class="text-[#E53935]" />
                  高风险动作提示
                </label>
                <div class="flex items-center gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.high_risk_moves_reminded"
                      :value="true"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">已提示</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      v-model="checklistForm.high_risk_moves_reminded"
                      :value="false"
                      class="w-4 h-4 text-[#E53935]"
                    />
                    <span class="text-sm">无高风险动作</span>
                  </label>
                </div>
                <textarea
                  v-model="checklistForm.high_risk_moves_notes"
                  class="input mt-2 min-h-[60px] resize-none"
                  placeholder="高风险动作说明（选填）"
                ></textarea>
              </div>
            </div>
          </div>

          <div class="p-6 pt-4 border-t border-[#E5E7EB] flex gap-3">
            <button class="btn-secondary flex-1" @click="closeCreateModal">取消</button>
            <button class="btn-primary flex-1" @click="submitChecklist" :disabled="submitting">
              {{ submitting ? '提交中...' : '创建检查单' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
        <div class="modal-content w-[800px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              安全检查单详情 - {{ getSongName(selectedRehearsal?.song_id || 0) }}
            </h3>
            <div class="flex items-center gap-3">
              <span
                class="px-3 py-1 text-sm rounded-full font-medium"
                :class="RISK_LEVEL_COLOR_MAP[currentChecklist?.risk_level || 'low']"
              >
                {{ RISK_LEVEL_MAP[currentChecklist?.risk_level || 'low'] }}
              </span>
              <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="closeDetailModal">
                <X :size="18" />
              </button>
            </div>
          </div>

          <div v-if="safetyStore.loading" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            加载中...
          </div>

          <div v-else-if="!currentChecklist" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            暂无检查单数据
          </div>

          <div v-else class="flex-1 overflow-y-auto p-6">
            <div class="space-y-6">
              <div class="grid grid-cols-2 gap-6">
                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <MapPin :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">场地地面情况</span>
                  </div>
                  <div class="flex items-center gap-2 mb-1">
                    <span class="px-2 py-0.5 text-sm rounded-full font-medium"
                      :class="getGroundConditionColor(currentChecklist.ground_condition)">
                      {{ GROUND_CONDITION_MAP[currentChecklist.ground_condition] }}
                    </span>
                  </div>
                  <p v-if="currentChecklist.ground_notes" class="text-sm text-[#6B7280]">
                    {{ currentChecklist.ground_notes }}
                  </p>
                </div>

                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <Cable :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">音响电线摆放</span>
                  </div>
                  <div class="flex items-center gap-2 mb-1">
                    <CheckCircle v-if="currentChecklist.audio_cables_arranged" :size="18" class="text-green-500" />
                    <XCircle v-else :size="18" class="text-red-500" />
                    <span class="text-sm">{{ currentChecklist.audio_cables_arranged ? '已整理妥当' : '需要注意' }}</span>
                  </div>
                  <p v-if="currentChecklist.audio_cables_notes" class="text-sm text-[#6B7280]">
                    {{ currentChecklist.audio_cables_notes }}
                  </p>
                </div>

                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <Heart :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">队员身体不适</span>
                  </div>
                  <div class="flex items-center gap-2 mb-1">
                    <CheckCircle v-if="!currentChecklist.members_illness_reported" :size="18" class="text-green-500" />
                    <XCircle v-else :size="18" class="text-red-500" />
                    <span class="text-sm">{{ currentChecklist.members_illness_reported ? '有不适情况' : '无异常' }}</span>
                  </div>
                  <p v-if="currentChecklist.illness_notes" class="text-sm text-[#6B7280]">
                    {{ currentChecklist.illness_notes }}
                  </p>
                </div>

                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <Thermometer :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">天气温度</span>
                  </div>
                  <div class="text-sm text-[#1F2937] mb-1">
                    <span v-if="currentChecklist.weather_temperature !== null">
                      {{ currentChecklist.weather_temperature }}°C
                    </span>
                    <span v-else>未记录</span>
                    <span v-if="currentChecklist.weather_condition" class="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                      {{ WEATHER_CONDITION_MAP[currentChecklist.weather_condition] }}
                    </span>
                  </div>
                  <p v-if="currentChecklist.weather_notes" class="text-sm text-[#6B7280]">
                    {{ currentChecklist.weather_notes }}
                  </p>
                </div>

                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <Droplets :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">饮水休息安排</span>
                  </div>
                  <div class="space-y-1 text-sm">
                    <div class="flex items-center gap-2">
                      <CheckCircle v-if="currentChecklist.drinking_water_provided" :size="16" class="text-green-500" />
                      <XCircle v-else :size="16" class="text-red-500" />
                      <span>饮用水</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <CheckCircle v-if="currentChecklist.rest_schedule_arranged" :size="16" class="text-green-500" />
                      <XCircle v-else :size="16" class="text-red-500" />
                      <span>休息时间</span>
                    </div>
                  </div>
                  <p v-if="currentChecklist.rest_notes" class="text-sm text-[#6B7280] mt-1">
                    {{ currentChecklist.rest_notes }}
                  </p>
                </div>

                <div class="p-4 rounded-lg bg-gray-50">
                  <div class="flex items-center gap-2 mb-3">
                    <Zap :size="18" class="text-[#E53935]" />
                    <span class="font-medium text-[#1F2937]">高风险动作提示</span>
                  </div>
                  <div class="flex items-center gap-2 mb-1">
                    <CheckCircle v-if="currentChecklist.high_risk_moves_reminded" :size="18" class="text-green-500" />
                    <XCircle v-else :size="18" class="text-gray-400" />
                    <span class="text-sm">{{ currentChecklist.high_risk_moves_reminded ? '已提示' : '无高风险动作' }}</span>
                  </div>
                  <p v-if="currentChecklist.high_risk_moves_notes" class="text-sm text-[#6B7280]">
                    {{ currentChecklist.high_risk_moves_notes }}
                  </p>
                </div>
              </div>

              <div v-if="currentChecklist.risk_assessment_notes" class="p-4 rounded-lg bg-orange-50 border border-orange-200">
                <div class="flex items-center gap-2 mb-2">
                  <AlertTriangle :size="18" class="text-orange-600" />
                  <span class="font-medium text-orange-800">风险评估备注</span>
                </div>
                <p class="text-sm text-orange-700">{{ currentChecklist.risk_assessment_notes }}</p>
              </div>

              <div class="text-xs text-[#9CA3AF] pt-2 border-t border-[#E5E7EB]">
                <div class="flex items-center justify-between">
                  <span>创建人: {{ currentChecklist.created_by_name || '未知' }}</span>
                  <span>创建时间: {{ formatDateTime(currentChecklist.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showRiskModal" class="modal-overlay" @click.self="closeRiskModal">
        <div class="modal-content w-[750px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              风险评估报告 - {{ getSongName(selectedRehearsal?.song_id || 0) }}
            </h3>
            <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="closeRiskModal">
              <X :size="18" />
            </button>
          </div>

          <div v-if="safetyStore.loading" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            评估中...
          </div>

          <div v-else-if="!riskAssessment" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            暂无评估数据
          </div>

          <div v-else class="flex-1 overflow-y-auto p-6">
            <div class="space-y-6">
              <div class="text-center p-6 rounded-xl" :class="getRiskBgColor(riskAssessment.overall_risk_level)">
                <div class="text-sm mb-2" :class="getRiskTextColor(riskAssessment.overall_risk_level)">整体风险等级</div>
                <div class="text-4xl font-bold mb-2" :class="getRiskTextColor(riskAssessment.overall_risk_level)">
                  {{ RISK_LEVEL_MAP[riskAssessment.overall_risk_level] }}
                </div>
                <div class="text-lg" :class="getRiskTextColor(riskAssessment.overall_risk_level)">
                  风险评分: {{ riskAssessment.risk_score }}/100
                </div>
                <div v-if="riskAssessment.weather_warning" class="mt-3 p-3 bg-white/50 rounded-lg">
                  <div class="flex items-center justify-center gap-2 text-orange-700">
                    <CloudLightning :size="18" />
                    <span class="font-medium">{{ riskAssessment.weather_warning }}</span>
                  </div>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-red-50 border border-red-200">
                <div class="flex items-center gap-2 mb-3">
                  <AlertTriangle :size="18" class="text-red-600" />
                  <h4 class="font-medium text-red-800">风险因素</h4>
                </div>
                <ul class="space-y-2">
                  <li v-for="(factor, idx) in riskAssessment.risk_factors" :key="idx" class="flex items-start gap-2">
                    <span class="text-red-500 mt-0.5">•</span>
                    <span class="text-sm text-red-700">{{ factor }}</span>
                  </li>
                </ul>
              </div>

              <div class="p-4 rounded-lg bg-green-50 border border-green-200">
                <div class="flex items-center gap-2 mb-3">
                  <ShieldCheck :size="18" class="text-green-600" />
                  <h4 class="font-medium text-green-800">建议措施</h4>
                </div>
                <ul class="space-y-2">
                  <li v-for="(rec, idx) in riskAssessment.recommendations" :key="idx" class="flex items-start gap-2">
                    <span class="text-green-500 mt-0.5">✓</span>
                    <span class="text-sm text-green-700">{{ rec }}</span>
                  </li>
                </ul>
              </div>

              <div v-if="riskAssessment.high_risk_members.length">
                <div class="flex items-center gap-2 mb-3">
                  <Users :size="18" class="text-[#E53935]" />
                  <h4 class="font-medium text-[#1F2937]">高风险成员列表</h4>
                  <span class="text-xs text-[#6B7280]">({{ riskAssessment.high_risk_members.length }} 人)</span>
                </div>
                <div class="space-y-3">
                  <div
                    v-for="member in riskAssessment.high_risk_members"
                    :key="member.id"
                    class="p-4 rounded-lg border border-[#E5E7EB]"
                  >
                    <div class="flex items-start justify-between mb-2">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                          <User :size="20" class="text-[#6B7280]" />
                        </div>
                        <div>
                          <div class="font-medium text-[#1F2937]">{{ member.member_name }}</div>
                          <div v-if="member.member_age" class="text-xs text-[#6B7280]">{{ member.member_age }} 岁</div>
                        </div>
                      </div>
                      <span
                        class="px-2 py-0.5 text-xs rounded-full font-medium"
                        :class="RISK_LEVEL_COLOR_MAP[member.risk_level]"
                      >
                        {{ RISK_LEVEL_MAP[member.risk_level] }}
                      </span>
                    </div>
                    <div v-if="member.risk_factors" class="text-sm text-[#6B7280] mb-2">
                      风险因素: {{ member.risk_factors }}
                    </div>
                    <div v-if="member.recommendation" class="text-sm text-[#1F2937] bg-yellow-50 p-2 rounded">
                      建议: {{ member.recommendation }}
                    </div>
                    <div class="flex items-center gap-3 mt-3 pt-3 border-t border-[#E5E7EB]">
                      <span
                        class="px-2 py-0.5 text-xs rounded-full font-medium"
                        :class="RISK_MEMBER_STATUS_COLOR_MAP[member.status]"
                      >
                        {{ RISK_MEMBER_STATUS_MAP[member.status] }}
                      </span>
                      <span v-if="member.action_taken" class="text-xs text-[#6B7280]">
                        已采取: {{ member.action_taken }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showHazardsModal" class="modal-overlay" @click.self="showHazardsModal = false">
        <div class="modal-content w-[650px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              场地隐患记录 - {{ getSongName(selectedRehearsal?.song_id || 0) }}
            </h3>
            <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="showHazardsModal = false">
              <X :size="18" />
            </button>
          </div>

          <div v-if="!currentHazards.length" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            暂无隐患记录
          </div>

          <div v-else class="flex-1 overflow-y-auto p-6">
            <div class="space-y-3">
              <div
                v-for="hazard in currentHazards"
                :key="hazard.id"
                class="p-4 rounded-lg border"
                :class="hazard.resolved ? 'border-green-200 bg-green-50/50' : 'border-red-200 bg-red-50/50'"
              >
                <div class="flex items-start justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-0.5 text-xs rounded-full font-medium"
                      :class="RISK_LEVEL_COLOR_MAP[hazard.severity]"
                    >
                      {{ RISK_LEVEL_MAP[hazard.severity] }}
                    </span>
                    <span class="font-medium text-[#1F2937]">{{ HAZARD_TYPE_MAP[hazard.hazard_type] }}</span>
                  </div>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full"
                    :class="hazard.resolved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                  >
                    {{ hazard.resolved ? '已处理' : '待处理' }}
                  </span>
                </div>
                <div v-if="hazard.location" class="text-sm text-[#6B7280] mb-1">
                  <span class="flex items-center gap-1">
                    <MapPin :size="12" />
                    {{ hazard.location }}
                  </span>
                </div>
                <div v-if="hazard.description" class="text-sm text-[#1F2937] mb-2">
                  {{ hazard.description }}
                </div>
                <div v-if="hazard.resolved && hazard.resolution_notes" class="text-sm text-green-700 bg-green-100/50 p-2 rounded">
                  处理结果: {{ hazard.resolution_notes }}
                </div>
                <div class="text-xs text-[#9CA3AF] mt-2 flex items-center justify-between">
                  <span>上报人: {{ hazard.reported_by_name || '未知' }}</span>
                  <span>{{ formatDateTime(hazard.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Plus, Eye, ShieldCheck, Calendar, Clock, AlertTriangle, X,
  MapPin, Cable, Heart, Thermometer, CloudSun, Droplets, Zap,
  CheckCircle, XCircle, Users, User, BarChart3, CloudLightning
} from 'lucide-vue-next'
import type {
  RehearsalRecord,
  TrainingSafetyChecklist,
  GroundCondition,
  WeatherCondition,
  RiskLevel,
  RiskAssessment,
  VenueHazard
} from '@/types'
import {
  GROUND_CONDITION_MAP,
  WEATHER_CONDITION_MAP,
  RISK_LEVEL_MAP,
  RISK_LEVEL_COLOR_MAP,
  HAZARD_TYPE_MAP,
  RISK_MEMBER_STATUS_MAP,
  RISK_MEMBER_STATUS_COLOR_MAP
} from '@/types'
import { useRehearsalsStore } from '@/stores/rehearsals'
import { useSafetyStore } from '@/stores/safety'
import { useSongsStore } from '@/stores/songs'
import { useMembersStore } from '@/stores/members'

const rehearsalsStore = useRehearsalsStore()
const safetyStore = useSafetyStore()
const songsStore = useSongsStore()
const membersStore = useMembersStore()

const GROUND_CONDITIONS = [
  { value: 'good' as GroundCondition, label: '良好' },
  { value: 'fair' as GroundCondition, label: '一般' },
  { value: 'poor' as GroundCondition, label: '较差' }
]

const WEATHER_CONDITIONS = [
  { value: 'sunny' as WeatherCondition, label: '晴天' },
  { value: 'cloudy' as WeatherCondition, label: '多云' },
  { value: 'rainy' as WeatherCondition, label: '雨天' },
  { value: 'windy' as WeatherCondition, label: '大风' },
  { value: 'hot' as WeatherCondition, label: '高温' },
  { value: 'cold' as WeatherCondition, label: '寒冷' }
]

const selectedRehearsal = ref<RehearsalRecord | null>(null)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showRiskModal = ref(false)
const showHazardsModal = ref(false)
const submitting = ref(false)

const checklistForm = ref({
  ground_condition: 'good' as GroundCondition,
  ground_notes: '',
  audio_cables_arranged: true,
  audio_cables_notes: '',
  members_illness_reported: false,
  illness_notes: '',
  weather_temperature: null as number | null,
  weather_condition: null as WeatherCondition | null,
  weather_notes: '',
  drinking_water_provided: true,
  rest_schedule_arranged: true,
  rest_notes: '',
  high_risk_moves_reminded: false,
  high_risk_moves_notes: ''
})

const currentChecklist = computed(() => safetyStore.currentChecklist)
const riskAssessment = computed(() => safetyStore.riskAssessment)
const currentHazards = computed(() => {
  if (!selectedRehearsal.value) return []
  return safetyStore.hazards.filter(h => h.rehearsal_id === selectedRehearsal.value!.id)
})

function getSongName(songId: number): string {
  const song = songsStore.songs.find(s => s.id === songId)
  return song?.name || '未知曲目'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hours}:${minutes}`
}

function getChecklistForRehearsal(rehearsalId: number): TrainingSafetyChecklist | undefined {
  return safetyStore.checklists.find(c => c.rehearsal_id === rehearsalId)
}

function getHazardsForRehearsal(rehearsalId: number): VenueHazard[] {
  return safetyStore.hazards.filter(h => h.rehearsal_id === rehearsalId)
}

function getGroundConditionColor(condition: GroundCondition): string {
  switch (condition) {
    case 'good': return 'bg-green-100 text-green-700'
    case 'fair': return 'bg-yellow-100 text-yellow-700'
    case 'poor': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function getRiskBgColor(level: RiskLevel): string {
  switch (level) {
    case 'low': return 'bg-green-100'
    case 'medium': return 'bg-yellow-100'
    case 'high': return 'bg-orange-100'
    case 'critical': return 'bg-red-100'
    default: return 'bg-gray-100'
  }
}

function getRiskTextColor(level: RiskLevel): string {
  switch (level) {
    case 'low': return 'text-green-800'
    case 'medium': return 'text-yellow-800'
    case 'high': return 'text-orange-800'
    case 'critical': return 'text-red-800'
    default: return 'text-gray-800'
  }
}

function openCreateChecklist(rehearsal: RehearsalRecord) {
  selectedRehearsal.value = rehearsal
  checklistForm.value = {
    ground_condition: 'good',
    ground_notes: '',
    audio_cables_arranged: true,
    audio_cables_notes: '',
    members_illness_reported: false,
    illness_notes: '',
    weather_temperature: null,
    weather_condition: null,
    weather_notes: '',
    drinking_water_provided: true,
    rest_schedule_arranged: true,
    rest_notes: '',
    high_risk_moves_reminded: false,
    high_risk_moves_notes: ''
  }
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
  selectedRehearsal.value = null
}

async function submitChecklist() {
  if (!selectedRehearsal.value) return
  submitting.value = true
  try {
    await safetyStore.createChecklist({
      rehearsal_id: selectedRehearsal.value.id,
      ground_condition: checklistForm.value.ground_condition,
      ground_notes: checklistForm.value.ground_notes || undefined,
      audio_cables_arranged: checklistForm.value.audio_cables_arranged,
      audio_cables_notes: checklistForm.value.audio_cables_notes || undefined,
      members_illness_reported: checklistForm.value.members_illness_reported,
      illness_notes: checklistForm.value.illness_notes || undefined,
      weather_temperature: checklistForm.value.weather_temperature ?? undefined,
      weather_condition: checklistForm.value.weather_condition || undefined,
      weather_notes: checklistForm.value.weather_notes || undefined,
      drinking_water_provided: checklistForm.value.drinking_water_provided,
      rest_schedule_arranged: checklistForm.value.rest_schedule_arranged,
      rest_notes: checklistForm.value.rest_notes || undefined,
      high_risk_moves_reminded: checklistForm.value.high_risk_moves_reminded,
      high_risk_moves_notes: checklistForm.value.high_risk_moves_notes || undefined
    })
    closeCreateModal()
  } catch {
    alert('创建检查单失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function viewChecklistDetail(rehearsal: RehearsalRecord) {
  selectedRehearsal.value = rehearsal
  showDetailModal.value = true
  const checklist = getChecklistForRehearsal(rehearsal.id)
  if (checklist) {
    await safetyStore.getChecklist(checklist.id)
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedRehearsal.value = null
}

async function viewRiskAssessment(rehearsal: RehearsalRecord) {
  selectedRehearsal.value = rehearsal
  showRiskModal.value = true
  const checklist = getChecklistForRehearsal(rehearsal.id)
  if (checklist) {
    await safetyStore.assessRisks(checklist.id)
  }
}

function closeRiskModal() {
  showRiskModal.value = false
  selectedRehearsal.value = null
}

function viewHazards(rehearsal: RehearsalRecord) {
  selectedRehearsal.value = rehearsal
  showHazardsModal.value = true
}

onMounted(async () => {
  await Promise.all([
    rehearsalsStore.fetchRehearsals(),
    songsStore.fetchSongs(),
    membersStore.fetchMembers(),
    safetyStore.fetchChecklists(),
    safetyStore.fetchHazards()
  ])
})
</script>
