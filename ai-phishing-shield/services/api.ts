import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ScanResponse {
  prediction: 'Phishing' | 'Safe'
  confidence: number
  risk_score: number
  attack_type: string
  severity: 'Low' | 'Medium' | 'High' | 'Critical'
  indicators: string[]
  highlighted_email: string
  model: string
}

export interface DashboardData {
  total_emails: number
  threats: number
  accuracy: number
  avg_confidence: number
  best_model: string
  safe_emails: number
  critical_threats: number
  roc: number
}

export interface ModelData {
  name: string
  accuracy: number
  precision: number
  recall: number
  f1: number
  roc: number
  latency: string
  status: string
  highlight: boolean
}

export const scanEmail = async (emailText: string): Promise<ScanResponse> => {
  const response = await api.post<ScanResponse>('/api/analyze-email', { email: emailText })
  return response.data
}

export const uploadImage = async (formData: FormData): Promise<ScanResponse> => {
  const response = await api.post<ScanResponse>('/api/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const fetchDashboard = async (): Promise<DashboardData> => {
  const response = await api.get<DashboardData>('/api/dashboard')
  return response.data
}

export const fetchModels = async (): Promise<ModelData[]> => {
  const response = await api.get<ModelData[]>('/api/models')
  return response.data
}

export const fetchReport = async (id: string): Promise<ScanResponse> => {
  const response = await api.get<ScanResponse>(`/api/report/${id}`)
  return response.data
}

export const getReportPdfUrl = (id: string): string => {
  return `${API_URL}/api/report/${id}/download-pdf`
}
