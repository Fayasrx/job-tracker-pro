import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard, Briefcase, ClipboardList, Bell,
    Building2, FileText, User, Settings, Zap, ChevronLeft
} from 'lucide-react'
import { useAppStore } from '../../store/appStore'
import clsx from 'clsx'

const NAV = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/jobs', icon: Briefcase, label: 'Job Feed' },
    { to: '/applications', icon: ClipboardList, label: 'Applications' },
    { to: '/notifications', icon: Bell, label: 'Notifications' },
    { to: '/companies', icon: Building2, label: 'Companies' },
    { to: '/cover-letters', icon: FileText, label: 'Cover Letters' },
    { to: '/profile', icon: User, label: 'Profile' },
    { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
    const { sidebarOpen, setSidebarOpen } = useAppStore()

    return (
        <aside className={clsx(
            'h-screen flex flex-col bg-slate-900/80 backdrop-blur border-r border-slate-800 transition-all duration-300 flex-shrink-0',
            sidebarOpen ? 'w-60' : 'w-16'
        )}>
            {/* Logo */}
            <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-800">
                <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-600/30">
                    <Zap className="w-5 h-5 text-white" />
                </div>
                {sidebarOpen && (
                    <div className="flex-1 min-w-0">
                        <p className="font-bold text-slate-100 text-sm leading-tight">Job Tracker</p>
                        <p className="text-primary-400 text-xs font-medium">Pro</p>
                    </div>
                )}
                <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="ml-auto text-slate-500 hover:text-slate-300 transition-colors flex-shrink-0"
                >
                    <ChevronLeft className={clsx('w-4 h-4 transition-transform', !sidebarOpen && 'rotate-180')} />
                </button>
            </div>

            {/* Nav */}
            <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
                {NAV.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        className={({ isActive }) =>
                            clsx('sidebar-link', isActive && 'active')
                        }
                        title={!sidebarOpen ? label : undefined}
                    >
                        <Icon className="w-5 h-5 flex-shrink-0" />
                        {sidebarOpen && <span className="truncate">{label}</span>}
                    </NavLink>
                ))}
            </nav>

            {/* User badge */}
            {sidebarOpen && (
                <div className="px-3 py-4 border-t border-slate-800">
                    <div className="flex items-center gap-3 px-2 py-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                            AP
                        </div>
                        <div className="min-w-0">
                            <p className="text-xs font-semibold text-slate-200 truncate">Al Mahaboob Phyas</p>
                            <p className="text-xs text-slate-500">Fresher • AI/ML</p>
                        </div>
                    </div>
                </div>
            )}
        </aside>
    )
}
