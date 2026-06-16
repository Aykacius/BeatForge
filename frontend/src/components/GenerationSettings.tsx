"use client"

import { useState } from "react"
import { useUploadStore } from "@/lib/store"

interface GenerationSettingsProps {
  onComplete: () => void
}

export default function GenerationSettings({ onComplete }: GenerationSettingsProps) {
  const [difficulty, setDifficulty] = useState("Normal")
  const [mappingStyle, setMappingStyle] = useState("Hybrid")
  const [targetSR, setTargetSR] = useState(5)
  const setSettings = useUploadStore((state) => state.setSettings)
  const file = useUploadStore((state) => state.file)

  const difficulties = ["Easy", "Normal", "Hard", "Insane", "Expert+"]
  const styles = ["Technical Stream", "Jump", "Hybrid", "Aim", "Stream Practice"]

  const handleContinue = () => {
    setSettings({
      difficulty,
      mappingStyle,
      targetStarRating: targetSR,
    })
    onComplete()
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Generation Settings</h2>

      {/* Selected File Info */}
      <div className="bg-slate-700 rounded-lg p-4 mb-8">
        <p className="text-slate-400 text-sm mb-1">Selected File</p>
        <p className="text-white font-semibold">{file?.name}</p>
        <p className="text-slate-500 text-sm">Size: {(file?.size || 0) / 1024 / 1024} MB</p>
      </div>

      {/* Difficulty Selection */}
      <div className="mb-8">
        <label className="block text-white font-semibold mb-3">Difficulty</label>
        <div className="grid grid-cols-5 gap-2">
          {difficulties.map((diff) => (
            <button
              key={diff}
              onClick={() => setDifficulty(diff)}
              className={`py-2 px-3 rounded-lg font-semibold transition-all text-sm ${
                difficulty === diff
                  ? "bg-pink-500 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Mapping Style */}
      <div className="mb-8">
        <label className="block text-white font-semibold mb-3">Mapping Style</label>
        <div className="grid grid-cols-5 gap-2">
          {styles.map((style) => (
            <button
              key={style}
              onClick={() => setMappingStyle(style)}
              className={`py-2 px-3 rounded-lg font-semibold transition-all text-sm ${
                mappingStyle === style
                  ? "bg-purple-600 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Target Star Rating */}
      <div className="mb-8">
        <label className="block text-white font-semibold mb-3">Target Star Rating: {targetSR}★</label>
        <input
          type="range"
          min="2"
          max="9"
          step="0.5"
          value={targetSR}
          onChange={(e) => setTargetSR(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-slate-400 text-sm mt-2">
          <span>2.0★</span>
          <span>9.0★</span>
        </div>
      </div>

      {/* Continue Button */}
      <button
        onClick={handleContinue}
        className="button-primary w-full py-3"
      >
        Generate Beatmap
      </button>
    </div>
  )
}
