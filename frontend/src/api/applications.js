import api from './client'

export const getApplications = (params) => api.get('/applications', { params })
export const getApplicationStats = () => api.get('/applications/stats')
export const createApplication = (data) => api.post('/applications', data)
export const updateApplication = (id, data) => api.patch(`/applications/${id}`, data)
export const deleteApplication = (id) => api.delete(`/applications/${id}`)
export const getApplicationTimeline = (id) => api.get(`/applications/${id}/timeline`)
