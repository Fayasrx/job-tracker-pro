import { useState, useEffect } from 'react'
import { Bell, Check, CheckCheck, Trash2 } from 'lucide-react'
import { getNotifications, markRead, markAllRead, deleteNotification } from '../api/notifications'
import { useNotificationStore } from '../store/notificationStore'
import { relativeTime } from '../utils/formatters'
import toast from 'react-hot-toast'

const TYPE_ICON = {
    new_jobs: '🆕', high_match: '🎯', daily_digest: '📊',
    follow_up: '⏰', company_update: '🔔', weekly_report: '📈'
}

export default function Notifications() {
    const [notifs, setNotifs] = useState([])
    const [loading, setLoading] = useState(true)
    const { setUnreadCount, markAllRead: storeMarkAll } = useNotificationStore()

    const load = async () => {
        setLoading(true)
        const data = await getNotifications({ page: 1, per_page: 50 })
        setNotifs(data.notifications || [])
        setUnreadCount(data.unread_count || 0)
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const handleMarkRead = async (id) => {
        await markRead(id)
        setNotifs(n => n.map(x => x.id === id ? { ...x, is_read: true } : x))
        setUnreadCount(n => Math.max(0, n - 1))
    }

    const handleMarkAll = async () => {
        await markAllRead()
        setNotifs(n => n.map(x => ({ ...x, is_read: true })))
        storeMarkAll()
        toast.success('All marked as read')
    }

    const handleDelete = async (id) => {
        await deleteNotification(id)
        setNotifs(n => n.filter(x => x.id !== id))
    }

    const unread = notifs.filter(n => !n.is_read).length

    return (
        <div className="max-w-3xl mx-auto space-y-4 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-slate-400 text-sm">{notifs.length} notifications · {unread} unread</p>
                </div>
                {unread > 0 && (
                    <button onClick={handleMarkAll} className="btn-secondary text-xs">
                        <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                    </button>
                )}
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-48">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : notifs.length === 0 ? (
                <div className="card p-12 text-center">
                    <Bell className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                    <p className="text-slate-400">No notifications yet</p>
                    <p className="text-slate-600 text-sm mt-1">Run a job scan to receive notifications</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {notifs.map(n => (
                        <div key={n.id}
                            className={`card p-4 flex gap-4 items-start transition-all hover:border-slate-600/60 ${!n.is_read ? 'border-primary-500/20 bg-primary-500/5' : ''}`}>
                            <span className="text-2xl flex-shrink-0">{TYPE_ICON[n.type] || '🔔'}</span>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between gap-2">
                                    <p className={`text-sm font-semibold ${!n.is_read ? 'text-slate-100' : 'text-slate-300'}`}>{n.title}</p>
                                    <span className="text-xs text-slate-600 flex-shrink-0">{relativeTime(n.created_at)}</span>
                                </div>
                                <p className="text-sm text-slate-400 mt-0.5">{n.message}</p>
                            </div>
                            <div className="flex gap-1 flex-shrink-0">
                                {!n.is_read && (
                                    <button onClick={() => handleMarkRead(n.id)}
                                        className="p-1.5 text-slate-500 hover:text-green-400 rounded-lg hover:bg-green-500/10 transition-colors" title="Mark read">
                                        <Check className="w-3.5 h-3.5" />
                                    </button>
                                )}
                                <button onClick={() => handleDelete(n.id)}
                                    className="p-1.5 text-slate-600 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors" title="Delete">
                                    <Trash2 className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
