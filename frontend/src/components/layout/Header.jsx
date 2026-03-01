import { useState, useEffect, useRef } from 'react'
import { Bell, Search, Sun, Moon, RefreshCw } from 'lucide-react'
import { useNotificationStore } from '../../store/notificationStore'
import { useAppStore } from '../../store/appStore'
import { getNotifications, markAllRead } from '../../api/notifications'
import { searchJobs } from '../../api/jobs'
import { relativeTime } from '../../utils/formatters'
import toast from 'react-hot-toast'

export default function Header({ title }) {
    const { unreadCount, setUnreadCount, setNotifications, markAllRead: markAllReadStore } = useNotificationStore()
    const { theme, toggleTheme } = useAppStore()
    const [showNotifs, setShowNotifs] = useState(false)
    const [notifs, setNotifs] = useState([])
    const [scanning, setScanning] = useState(false)
    const bellRef = useRef()

    const loadNotifs = async () => {
        try {
            const data = await getNotifications({ page: 1, per_page: 8 })
            setNotifs(data.notifications || [])
            setUnreadCount(data.unread_count || 0)
        } catch { }
    }

    useEffect(() => { loadNotifs() }, [])

    // Close on outside click
    useEffect(() => {
        const handler = (e) => {
            if (bellRef.current && !bellRef.current.contains(e.target)) setShowNotifs(false)
        }
        document.addEventListener('mousedown', handler)
        return () => document.removeEventListener('mousedown', handler)
    }, [])

    const handleScan = async () => {
        setScanning(true)
        try {
            await searchJobs({ max_per_platform: 10 })
            toast.success('Job scan started! Check notifications for results.')
        } catch (e) {
            toast.error(e.message)
        } finally {
            setTimeout(() => setScanning(false), 3000)
        }
    }

    const handleMarkAll = async () => {
        try {
            await markAllRead()
            markAllReadStore()
            setNotifs(notifs.map(n => ({ ...n, is_read: true })))
        } catch { }
    }

    const typeIcon = (type) => {
        const m = { new_jobs: '🆕', high_match: '🎯', daily_digest: '📊', follow_up: '⏰', company_update: '🔔' }
        return m[type] || '🔔'
    }

    return (
        <header className="h-16 flex items-center gap-4 px-6 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm flex-shrink-0">
            <h1 className="text-lg font-bold text-slate-100 flex-1">{title}</h1>

            {/* Scan button */}
            <button
                onClick={handleScan}
                disabled={scanning}
                className="btn-secondary text-xs gap-2"
                title="Trigger job scan"
            >
                <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
                {scanning ? 'Scanning...' : 'Scan Jobs'}
            </button>

            {/* Theme toggle */}
            <button onClick={toggleTheme} className="btn-ghost p-2">
                {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {/* Notification bell */}
            <div ref={bellRef} className="relative">
                <button
                    onClick={() => { setShowNotifs(!showNotifs); if (!showNotifs) loadNotifs() }}
                    className="btn-ghost p-2 relative"
                >
                    <Bell className="w-5 h-5" />
                    {unreadCount > 0 && (
                        <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-primary-500 text-white text-xs rounded-full flex items-center justify-center font-bold leading-none">
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </span>
                    )}
                </button>

                {showNotifs && (
                    <div className="absolute right-0 top-full mt-2 w-96 card-elevated shadow-2xl z-50 animate-slide-up overflow-hidden">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
                            <span className="font-semibold text-sm text-slate-100">Notifications</span>
                            {unreadCount > 0 && (
                                <button onClick={handleMarkAll} className="text-xs text-primary-400 hover:text-primary-300">
                                    Mark all read
                                </button>
                            )}
                        </div>
                        <div className="max-h-80 overflow-y-auto divide-y divide-slate-700/50">
                            {notifs.length === 0 ? (
                                <div className="py-8 text-center text-slate-500 text-sm">No notifications yet</div>
                            ) : notifs.map(n => (
                                <div key={n.id} className={`px-4 py-3 hover:bg-slate-700/30 transition-colors ${!n.is_read ? 'bg-primary-500/5' : ''}`}>
                                    <div className="flex gap-3">
                                        <span className="text-lg flex-shrink-0 mt-0.5">{typeIcon(n.type)}</span>
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-sm font-medium ${!n.is_read ? 'text-slate-100' : 'text-slate-300'}`}>{n.title}</p>
                                            <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{n.message}</p>
                                            <p className="text-xs text-slate-600 mt-1">{relativeTime(n.created_at)}</p>
                                        </div>
                                        {!n.is_read && <div className="w-2 h-2 bg-primary-500 rounded-full mt-1.5 flex-shrink-0" />}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="px-4 py-2 border-t border-slate-700">
                            <a href="/notifications" className="text-xs text-primary-400 hover:text-primary-300">View all notifications →</a>
                        </div>
                    </div>
                )}
            </div>
        </header>
    )
}
