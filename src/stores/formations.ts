import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Formation, FormationVersion, FormationPosition } from '@/types'
import { useApi } from '@/composables/useApi'

export const useFormationsStore = defineStore('formations', () => {
  const api = useApi()
  const versions = ref<FormationVersion[]>([])
  const currentFormation = ref<Formation | null>(null)
  const loading = ref(false)

  async function fetchFormation(songId: number) {
    loading.value = true
    try {
      const [formation, versionList] = await Promise.all([
        api.formations.getCurrent(songId).catch(() => null),
        api.formations.getVersions(songId),
      ])
      currentFormation.value = formation
      versions.value = versionList
    } catch (e) {
      console.error('Failed to fetch formation', e)
    } finally {
      loading.value = false
    }
  }

  async function generateFormation(songId: number) {
    loading.value = true
    try {
      const formation = await api.formations.generate(songId)
      currentFormation.value = formation
      const versionList = await api.formations.getVersions(songId)
      versions.value = versionList
      return formation
    } catch (e) {
      console.error('Failed to generate formation', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function saveFormation(id: number, positions: { id: number; x?: number; y?: number; member_id?: number }[]) {
    try {
      const formation = await api.formations.update(id, { positions })
      currentFormation.value = formation
      return formation
    } catch (e) {
      console.error('Failed to save formation', e)
      throw e
    }
  }

  async function lockFormation(id: number) {
    try {
      const formation = await api.formations.lock(id)
      currentFormation.value = formation
      const idx = versions.value.findIndex((v) => v.id === id)
      if (idx !== -1) versions.value[idx].is_locked = true
      return formation
    } catch (e) {
      console.error('Failed to lock formation', e)
      throw e
    }
  }

  async function loadFormationById(id: number) {
    try {
      const formation = await api.formations.getById(id)
      currentFormation.value = formation
      return formation
    } catch (e) {
      console.error('Failed to load formation by id', e)
      throw e
    }
  }

  function selectFormation(formation: Formation) {
    currentFormation.value = formation
  }

  return {
    versions,
    currentFormation,
    loading,
    fetchFormation,
    generateFormation,
    saveFormation,
    lockFormation,
    loadFormationById,
    selectFormation,
  }
})
