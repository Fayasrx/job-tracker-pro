import api from './client'

export const getJobs = (params) => api.get('/jobs', { params })
export const getJob = (id) => api.get(`/jobs/${id}`)
export const searchJobs = (data) => api.post('/jobs/search', data)
export const saveJob = (id) => api.post(`/jobs/${id}/save`)
export const unsaveJob = (id) => api.delete(`/jobs/${id}/save`)
export const getDailyDigest = () => api.get('/jobs/daily-digest')
