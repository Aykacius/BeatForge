"use client"

import { useRouter } from "next/navigation"
import { useState, useRef } from "react"
import { Upload, Music } from "lucide-react"
import { useUploadStore } from "@/lib/store"
import { api } from "@/lib/api"

interface FileUploadProps {
  onComplete: () => void
}

export default function FileUpload({ onComplete }: FileUploadProps) {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const setFile = useUploadStore((state) => state.setFile)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileSelect = async (file: File) => {
    // Validate file
    if (!file.name.endsWith(".mp3")) {
      setError("Only MP3 files are supported")
      return
    }

    if (file.size > 100 * 1024 * 1024) {
      setError("File size must be less than 100MB")
      return
    }

    setError(null)
    setIsLoading(true)

    try {
      const fileId = await api.uploadFile(file)
      setFile({
        id: fileId,
        name: file.name,
        size: file.size,
      })
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Upload Your Music</h2>

      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-pink-500 bg-pink-500 bg-opacity-10"
            : "border-slate-600 hover:border-pink-500"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp3"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              handleFileSelect(e.target.files[0])
            }
          }}
          className="hidden"
          disabled={isLoading}
        />

        <Music size={48} className="mx-auto mb-4 text-pink-500" />
        <h3 className="text-xl font-semibold text-white mb-2">Drop your MP3 here</h3>
        <p className="text-slate-400 mb-4">or click to browse (Max 100MB)</p>
        <p className="text-sm text-slate-500">Supported: MP3</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="mt-4 p-4 bg-blue-500 bg-opacity-20 border border-blue-500 rounded-lg text-blue-300 flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-300 mr-3"></div>
          Uploading...
        </div>
      )}
    </div>
  )
}
