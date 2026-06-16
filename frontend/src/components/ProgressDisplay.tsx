"use client"

import { useEffect, useState } from "react"
import { useUploadStore } from "@/lib/store"
import { api } from "@/lib/api"
import { Download, CheckCircle, AlertCircle } from "lucide-react"

export default function ProgressDisplay() {
  const { file, settings } = useUploadStore()
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<"queued" | "processing" | "completed" | "failed">("queued")
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState("Initializing...")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const startGeneration = async () => {
      if (!file || !settings) return

      try {
        const response = await api.generateBeatmap({
          file_id: file.id,
          difficulty: settings.difficulty,
          mapping_style: settings.mappingStyle,
          target_star_rating: settings.targetStarRating,
        })

        setJobId(response.job_id)
        await pollJobStatus(response.job_id)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Generation failed")
        setStatus("failed")
      }
    }

    startGeneration()
  }, [file, settings])

  const pollJobStatus = async (jid: string) => {
    const maxAttempts = 600 // 10 minutes with 1 second intervals
    let attempts = 0

    while (attempts < maxAttempts) {
      try {
        const statusData = await api.getJobStatus(jid)
        setStatus(statusData.status)
        setProgress(statusData.progress)
        setCurrentStep(statusData.current_step)

        if (statusData.status === "completed" || statusData.status === "failed") {
          break
        }

        await new Promise((resolve) => setTimeout(resolve, 1000))
        attempts++
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch status")
        break
      }
    }
  }

  const progressSteps = [
    "Uploading...",
    "Analyzing BPM...",
    "Detecting beats...",
    "Building sections...",
    "Generating patterns...",
    "Packaging beatmap...",
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Generating Your Beatmap</h2>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-slate-300 font-semibold">Overall Progress</span>
          <span className="text-pink-500 font-bold">{progress}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Current Step */}
      <div className="bg-slate-700 rounded-lg p-6 mb-8">
        <h3 className="text-white font-semibold mb-4">Processing Steps</h3>
        <div className="space-y-3">
          {progressSteps.map((step, index) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm font-semibold ${
                  progress > (index * (100 / progressSteps.length))
                    ? "bg-green-500 text-white"
                    : progress === index * (100 / progressSteps.length)
                    ? "bg-pink-500 text-white animate-pulse"
                    : "bg-slate-600 text-slate-400"
                }`}
              >
                {progress > (index * (100 / progressSteps.length)) ? "✓" : index + 1}
              </div>
              <span
                className={`${
                  progress >= (index * (100 / progressSteps.length))
                    ? "text-white"
                    : "text-slate-500"
                }`}
              >
                {step}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="bg-red-500 bg-opacity-20 border border-red-500 rounded-lg p-4 mb-8 flex items-start">
          <AlertCircle className="text-red-400 mr-3 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-red-300 font-semibold">Generation Failed</p>
            <p className="text-red-200 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {status === "completed" && (
        <div className="bg-green-500 bg-opacity-20 border border-green-500 rounded-lg p-4 mb-8 flex items-start">
          <CheckCircle className="text-green-400 mr-3 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-green-300 font-semibold">Beatmap Ready!</p>
            <p className="text-green-200 text-sm mt-1">Your beatmap has been generated successfully.</p>
          </div>
        </div>
      )}

      {/* Download Button */}
      {status === "completed" && jobId && (
        <button
          onClick={() => api.downloadBeatmap(jobId)}
          className="button-primary w-full py-3 flex items-center justify-center gap-2"
        >
          <Download size={20} />
          Download Beatmap (.osz)
        </button>
      )}

      {/* Retry Button */}
      {status === "failed" && (
        <button
          onClick={() => window.location.href = "/upload"}
          className="button-secondary w-full py-3"
        >
          Try Again
        </button>
      )}
    </div>
  )
}
