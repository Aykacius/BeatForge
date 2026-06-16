"use client"

import { create } from "zustand"

interface File {
  id: string
  name: string
  size: number
}

interface Settings {
  difficulty: string
  mappingStyle: string
  targetStarRating: number
}

interface UploadStore {
  file: File | null
  settings: Settings | null
  setFile: (file: File) => void
  setSettings: (settings: Settings) => void
  reset: () => void
}

export const useUploadStore = create<UploadStore>((set) => ({
  file: null,
  settings: null,
  setFile: (file) => set({ file }),
  setSettings: (settings) => set({ settings }),
  reset: () => set({ file: null, settings: null }),
}))
