import axios from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const client = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

export const api = {
  uploadFile: async (file: File): Promise<string> => {
    const formData = new FormData()
    formData.append("file", file)

    const response = await client.post("/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    return response.data.file_id
  },

  generateBeatmap: async (payload: {
    file_id: string
    difficulty: string
    mapping_style: string
    target_star_rating: number
  }) => {
    const response = await client.post("/generate/", payload)
    return response.data
  },

  getJobStatus: async (jobId: string) => {
    const response = await client.get(`/jobs/${jobId}`)
    return response.data
  },

  downloadBeatmap: async (jobId: string) => {
    const response = await client.get(`/download/${jobId}`, {
      responseType: "blob",
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement("a")
    link.href = url
    link.setAttribute("download", `beatmap_${jobId}.osz`)
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)
  },
}
