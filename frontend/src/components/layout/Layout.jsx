import { Outlet, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Sidebar from './Sidebar'
import Header from './Header'
import { useWebSocket } from '../../hooks/useWebSocket'

const PAGE_TITLES = {
    '/': 'Dashboard',
    '/jobs': 'Job Feed',
    '/applications': 'Application Tracker',
    '/notifications': 'Notifications',
    '/companies': 'Tracked Companies',
    '/cover-letters': 'Cover Letters',
    '/profile': 'Profile',
    '/settings': 'Settings',
}

export default function Layout() {
    useWebSocket()
    const location = useLocation()
    const title = PAGE_TITLES[location.pathname] ||
        (location.pathname.startsWith('/jobs/') ? 'Job Details' : 'Job Tracker Pro')

    return (
        <div className="flex h-screen overflow-hidden bg-slate-950">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Header title={title} />
                <main className="flex-1 overflow-y-auto p-6">
                    <Outlet />
                </main>
            </div>
            <Toaster position="bottom-right" />
        </div>
    )
}
