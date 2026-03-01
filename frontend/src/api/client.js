import axios from 'axios'

// In production (Vercel), VITE_API_URL = https://job-tracker-api.onrender.com/api
// In local dev, falls back to /api (same-host, Vite will proxy it)
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
})

// Response interceptor for error handling
api.interceptors.response.use(
    (res) => res.data,
    (err) => {
        const msg = err.response?.data?.detail || err.message || 'Something went wrong'
        return Promise.reject(new Error(msg))
    }
)

export default api
