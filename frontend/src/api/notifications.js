import api from './client'

export const getNotifications = (params) => api.get('/notifications', { params })
export const getUnreadCount = () => api.get('/notifications/unread-count')
export const markRead = (id) => api.patch(`/notifications/${id}/read`)
export const markAllRead = () => api.post('/notifications/read-all')
export const deleteNotification = (id) => api.delete(`/notifications/${id}`)
