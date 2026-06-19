import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Song } from '@/types'
import { useApi } from '@/composables/useApi'

export const useSongsStore = defineStore('songs', () => {
  const api = useApi()
  const songs = ref<Song[]>([])
  const loading = ref(false)
  const currentSong = ref<Song | null>(null)

  async function fetchSongs() {
    loading.value = true
    try {
      songs.value = await api.songs.list()
    } catch (e) {
      console.error('Failed to fetch songs', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchSong(id: number) {
    loading.value = true
    try {
      currentSong.value = await api.songs.get(id)
    } catch (e) {
      console.error('Failed to fetch song', e)
    } finally {
      loading.value = false
    }
  }

  async function createSong(data: Partial<Song>) {
    try {
      const song = await api.songs.create(data)
      songs.value.push(song)
      return song
    } catch (e) {
      console.error('Failed to create song', e)
      throw e
    }
  }

  async function updateSong(id: number, data: Partial<Song>) {
    try {
      const song = await api.songs.update(id, data)
      const idx = songs.value.findIndex((s) => s.id === id)
      if (idx !== -1) songs.value[idx] = song
      if (currentSong.value?.id === id) currentSong.value = song
      return song
    } catch (e) {
      console.error('Failed to update song', e)
      throw e
    }
  }

  async function deleteSong(id: number) {
    try {
      await api.songs.delete(id)
      songs.value = songs.value.filter((s) => s.id !== id)
      if (currentSong.value?.id === id) currentSong.value = null
    } catch (e) {
      console.error('Failed to delete song', e)
      throw e
    }
  }

  return { songs, loading, currentSong, fetchSongs, fetchSong, createSong, updateSong, deleteSong }
})
