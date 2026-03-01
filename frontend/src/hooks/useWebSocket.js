import { useEffect } from 'react'
import toast from 'react-hot-toast'
import { useNotificationStore } from '../store/notificationStore'

export function useWebSocket() {
    const addNotification = useNotificationStore((s) => s.addNotification)

    useEffect(() => {
        let ws
        let retryCount = 0

        const connect = () => {
            // In production, VITE_WS_URL = wss://job-tracker-api.onrender.com/ws
            // In local dev, connect to same host (Vite dev server)
            const wsUrl = import.meta.env.VITE_WS_URL
                ? `${import.meta.env.VITE_WS_URL}/notifications`
                : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/notifications`
            ws = new WebSocket(wsUrl)

            ws.onopen = () => { retryCount = 0 }

            ws.onmessage = (e) => {
                try {
                    const msg = JSON.parse(e.data)
                    if (msg.event === 'notification') {
                        addNotification({
                            id: msg.data?.id || Date.now(),
                            type: msg.type,
                            title: msg.title,
                            message: msg.message,
                            data: JSON.stringify(msg.data || {}),
                            is_read: false,
                            created_at: new Date().toISOString(),
                        })
                        // Show simple toast (no JSX)
                        const icon = {
                            new_jobs: '🆕', high_match: '🎯', daily_digest: '📊',
                            follow_up: '⏰', company_update: '🔔',
                        }[msg.type] || '🔔'
                        toast(`${icon} ${msg.title}: ${msg.message}`, {
                            duration: 5000,
                            style: {
                                background: '#1e293b',
                                color: '#f1f5f9',
                                border: '1px solid #334155',
                                borderRadius: '12px',
                            },
                        })
                    }
                } catch { }
            }

            ws.onclose = () => {
                const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)
                retryCount++
                setTimeout(connect, delay)
            }
        }

        connect()
        return () => ws?.close()
    }, [addNotification])
}
