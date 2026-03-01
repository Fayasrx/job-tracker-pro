import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, Briefcase, ClipboardList, Clock, Star, ExternalLink, BarChart2 } from 'lucide-react'
import { RadialBarChart, RadialBar, BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import api from '../api/client'
import { getMatchColor, relativeTime, getPlatformClass } from '../utils/formatters'

function StatCard({ icon: Icon, label, value, sub, color = 'text-primary-400' }) {
    return (
        <div className="stat-card hover:scale-[1.02] transition-transform cursor-default">
            <div className="flex items-center justify-between">
                <span className="text-slate-500 text-xs font-medium uppercase tracking-wider">{label}</span>
                <div className={`w-8 h-8 rounded-lg bg-slate-700/60 flex items-center justify-center ${color}`}>
                    <Icon className="w-4 h-4" />
                </div>
            </div>
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            {sub && <p className="text-xs text-slate-500">{sub}</p>}
        </div>
    )
}

function MatchScoreRing({ score, size = 56 }) {
    const { color, label } = getMatchColor(score)
    const r = 22
    const circ = 2 * Math.PI * r
    const filled = circ * (score / 100)
    return (
        <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
            <svg width={size} height={size} className="-rotate-90">
                <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1e293b" strokeWidth="5" />
                <circle
                    cx={size / 2} cy={size / 2} r={r} fill="none"
                    stroke={color.color} strokeWidth="5"
                    strokeDasharray={`${filled} ${circ - filled}`}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dasharray 0.5s' }}
                />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-xs font-bold" style={{ color: color.color }}>
                {Math.round(score)}
            </span>
        </div>
    )
}

const FUNNEL_COLORS = ['#6366f1', '#22c55e', '#3b82f6', '#f59e0b', '#10b981']

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get('/analytics/dashboard').then(setStats).catch(console.error).finally(() => setLoading(false))
    }, [])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
        )
    }

    const funnel = stats?.funnel || {}
    const funnelData = [
        { name: 'Found', value: funnel.found || 0 },
        { name: 'Saved', value: funnel.saved || 0 },
        { name: 'Applied', value: funnel.applied || 0 },
        { name: 'Interview', value: funnel.interview || 0 },
        { name: 'Offer', value: funnel.offer || 0 },
    ]

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Stats row */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <StatCard icon={Briefcase} label="Total Jobs" value={stats?.total_jobs || 0} sub="All platforms" color="text-primary-400" />
                <StatCard icon={Star} label="Avg Match" value={`${stats?.avg_match_score || 0}%`} sub="AI scored" color="text-amber-400" />
                <StatCard icon={ClipboardList} label="Applied This Week" value={stats?.applications_this_week || 0} sub="Applications" color="text-green-400" />
                <StatCard icon={Clock} label="Pending" value={stats?.pending_responses || 0} sub="Awaiting reply" color="text-orange-400" />
                <StatCard icon={TrendingUp} label="Interviews" value={stats?.interviews_scheduled || 0} sub="Scheduled" color="text-violet-400" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Top Matches */}
                <div className="lg:col-span-2 card p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-base font-semibold text-slate-100">🎯 Top Matches Today</h2>
                        <Link to="/jobs" className="text-xs text-primary-400 hover:text-primary-300">View all →</Link>
                    </div>
                    <div className="space-y-3">
                        {(stats?.top_matches || []).length === 0 ? (
                            <p className="text-slate-500 text-sm text-center py-8">No jobs yet. Click "Scan Jobs" to fetch new openings.</p>
                        ) : (stats?.top_matches || []).map(job => {
                            const mc = getMatchColor(job.match_score)
                            return (
                                <Link key={job.id} to={`/jobs/${job.id}`}
                                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-700/30 transition-colors group">
                                    <img
                                        src={job.company_logo_url}
                                        alt={job.company}
                                        className="w-10 h-10 rounded-xl object-contain bg-slate-700 flex-shrink-0"
                                        onError={(e) => { e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(job.company)}&background=6366f1&color=fff&size=40` }}
                                    />
                                    <div className="flex-1 min-w-0">
                                        <p className="font-semibold text-sm text-slate-100 truncate group-hover:text-primary-300 transition-colors">{job.title}</p>
                                        <p className="text-xs text-slate-400">{job.company} · {job.location}</p>
                                    </div>
                                    <div className="flex items-center gap-2 flex-shrink-0">
                                        <span className={`${mc.cls} badge text-xs`}>{Math.round(job.match_score)}%</span>
                                        <ExternalLink className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400" />
                                    </div>
                                </Link>
                            )
                        })}
                    </div>
                </div>

                {/* Application Funnel */}
                <div className="card p-5">
                    <h2 className="text-base font-semibold text-slate-100 mb-4">📊 Application Funnel</h2>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={funnelData} layout="vertical" margin={{ left: -10, right: 10 }}>
                            <XAxis type="number" hide />
                            <Tooltip
                                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12 }}
                                labelStyle={{ color: '#f1f5f9' }}
                                itemStyle={{ color: '#94a3b8' }}
                            />
                            <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                                {funnelData.map((_, i) => (
                                    <Cell key={i} fill={FUNNEL_COLORS[i % FUNNEL_COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="space-y-1.5 mt-2">
                        {funnelData.map((d, i) => (
                            <div key={d.name} className="flex items-center justify-between text-xs">
                                <div className="flex items-center gap-2">
                                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: FUNNEL_COLORS[i] }} />
                                    <span className="text-slate-400">{d.name}</span>
                                </div>
                                <span className="text-slate-200 font-medium">{d.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="card p-5">
                <h2 className="text-base font-semibold text-slate-100 mb-4">⚡ Recent Activity</h2>
                <div className="space-y-3">
                    {(stats?.recent_activity || []).length === 0 ? (
                        <p className="text-slate-500 text-sm text-center py-4">No activity yet. Run a job scan to get started!</p>
                    ) : (stats.recent_activity || []).map(a => (
                        <div key={a.id} className="flex items-start gap-3 py-2 border-b border-slate-700/50 last:border-0">
                            <span className="text-lg flex-shrink-0">
                                {{ new_jobs: '🆕', high_match: '🎯', daily_digest: '📊', follow_up: '⏰', company_update: '🔔' }[a.type] || '🔔'}
                            </span>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-slate-200">{a.title}</p>
                                <p className="text-xs text-slate-500 mt-0.5">{a.message}</p>
                            </div>
                            <span className="text-xs text-slate-600 flex-shrink-0">{relativeTime(a.created_at)}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
