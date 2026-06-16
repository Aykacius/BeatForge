"use client"

import { useState } from "react"
import { Upload, Music, Settings2 } from "lucide-react"
import { useUploadStore } from "@/lib/store"
import FileUpload from "@/components/FileUpload"
import GenerationSettings from "@/components/GenerationSettings"
import ProgressDisplay from "@/components/ProgressDisplay"

export default function UploadPage() {
  const [currentStep, setCurrentStep] = useState<"upload" | "settings" | "progress">("upload")
  const { file, settings } = useUploadStore()

  const handleUploadComplete = () => {
    setCurrentStep("settings")
  }

  const handleSettingsComplete = () => {
    setCurrentStep("progress")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">BeatForge</h1>
          <p className="text-slate-300">Generate beatmaps from your music</p>
        </div>

        {/* Steps Indicator */}
        <div className="flex justify-between mb-8">
          {[
            { step: "upload", label: "Upload", icon: Upload },
            { step: "settings", label: "Settings", icon: Settings2 },
            { step: "progress", label: "Generate", icon: Music },
          ].map((item) => {
            const Icon = item.icon
            const isActive = currentStep === item.step
            const isCompleted = 
              (item.step === "upload" && currentStep !== "upload") ||
              (item.step === "settings" && currentStep === "progress")

            return (
              <div key={item.step} className="flex flex-col items-center">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all ${
                    isActive
                      ? "bg-pink-500 text-white"
                      : isCompleted
                      ? "bg-green-500 text-white"
                      : "bg-slate-700 text-slate-400"
                  }`}
                >
                  <Icon size={24} />
                </div>
                <span className={`text-sm ${isActive ? "text-white font-semibold" : "text-slate-400"}`}>
                  {item.label}
                </span>
              </div>
            )
          })}
        </div>

        {/* Content */}
        <div className="card p-8">
          {currentStep === "upload" && (
            <FileUpload onComplete={handleUploadComplete} />
          )}
          {currentStep === "settings" && file && (
            <GenerationSettings onComplete={handleSettingsComplete} />
          )}
          {currentStep === "progress" && file && settings && (
            <ProgressDisplay />
          )}
        </div>
      </div>
    </div>
  )
}
