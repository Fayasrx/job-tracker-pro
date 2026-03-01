import { useState, useEffect } from 'react'
import { Key, Clock, Globe, CheckCircle, XCircle, Mail } from 'lucide-react'
import api from '../api/client'

const PLATFORMS = [
    { key: 'indeed', name: 'Indeed', icon: '🔵', color: 'blue', description: "World's largest job site" },
    { key: 'glassdoor', name: 'Glassdoor', icon: '🟢', color: 'green', description: 'Jobs + company reviews' },
    { key: 'linkedin', name: 'LinkedIn', icon: '🔷', color: 'indigo', description: 'Professional network' },
    { key: 'naukri', name: 'Naukri', icon: '🟠', color: 'orange', description: "India's #1 job portal" },
    { key: 'internshala', name: 'Internshala', icon: '🟣', color: 'purple', description: 'Internships & fresher jobs' },
]

const colorMap = {
    blue: 'bg-blue-500/10 border-blue-500/30',
    green: 'bg-green-500/10 border-green-500/30',
    indigo: 'bg-indigo-500/10 border-indigo-500/30',
    orange: 'bg-orange-500/10 border-orange-500/30',
    purple: 'bg-purple-500/10 border-purple-500/30',
}

export default function Settings() {
    const [settings, setSettings] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get('/settings').then(s => { setSettings(s); setLoading(false) }).catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

    const creds = settings?.platform_credentials || {}
    const emails = settings?.platform_emails || {}

    return (
        <div className="max-w-2xl mx-auto space-y-5 animate-fade-in">

            {/* Platform Accounts */}
            <div className="card p-5 space-y-4">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2">
                    <Globe className="w-4 h-4 text-primary-400" /> Platform Accounts
                </h2>
                <p className="text-xs text-slate-500">
                    Credentials stored in <code className="bg-slate-700 px-1 rounded">.env</code> — used for auto-applying. Passwords never reach the frontend.
                </p>

                <div className="grid gap-3">
                    {PLATFORMS.map(p => {
                        const connected = !!creds[p.key]
                        const email = emails[p.key]
                        return (
                            <div key={p.key} className={`flex items-center justify-between p-3.5 rounded-xl border ${colorMap[p.color]}`}>
                                <div className="flex items-center gap-3">
                                    <span className="text-xl">{p.icon}</span>
                                    <div>
                                        <p className="font-semibold text-slate-100 text-sm">{p.name}</p>
                                        <p className="text-xs text-slate-500">{p.description}</p>
                                        {connected && email && (
                                            <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                                                <Mail className="w-3 h-3" />{email}
                                            </p>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                    {connected ? (
                                        <><CheckCircle className="w-4 h-4 text-green-400" /><span className="text-xs font-semibold text-green-400">Connected</span></>
                                    ) : (
                                        <><XCircle className="w-4 h-4 text-slate-500" /><span className="text-xs text-slate-500">Not set</span></>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>

                <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
                    <p className="text-xs text-slate-400">💡 To add/update credentials, edit <code className="bg-slate-700 px-1 rounded">.env</code> and redeploy:</p>
                    <pre className="text-xs text-slate-300 mt-2 font-mono">{`INDEED_EMAIL=your@email.com\nINDEED_PASSWORD=yourpass\nGLASSDOOR_EMAIL=your@email.com\nGLASSDOOR_PASSWORD=yourpass`}</pre>
                </div>
            </div>

            {/* Gemini API */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2">
                    <Key className="w-4 h-4 text-primary-400" /> Gemini AI
                </h2>
                <div className={`flex items-center gap-3 p-3 rounded-xl ${settings?.gemini_configured ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                    <div className={`w-2.5 h-2.5 rounded-full animate-pulse ${settings?.gemini_configured ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className={`text-sm font-medium ${settings?.gemini_configured ? 'text-green-400' : 'text-red-400'}`}>
                        {settings?.gemini_configured ? 'Gemini API key configured ✓' : 'Gemini API key not set — add GEMINI_API_KEY in .env'}
                    </span>
                </div>
            </div>

            {/* Scheduler */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2">
                    <Clock className="w-4 h-4 text-amber-400" /> Scheduler
                </h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><p className="text-slate-500 text-xs">Daily Scan Time</p><p className="font-semibold text-slate-200">{settings?.daily_scan_time || '06:00'}</p></div>
                    <div><p className="text-slate-500 text-xs">Daily Digest Time</p><p className="font-semibold text-slate-200">{settings?.digest_time || '09:00'}</p></div>
                </div>
                <p className="text-xs text-slate-500">Update via <code className="bg-slate-700 px-1 rounded">DAILY_SCAN_TIME</code> / <code className="bg-slate-700 px-1 rounded">DIGEST_TIME</code> in .env</p>
            </div>

            {/* Job Preferences */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base">🎯 Job Preferences</h2>
                <div>
                    <p className="text-xs text-slate-500 mb-2">Target Roles</p>
                    <div className="flex flex-wrap gap-1.5">{(settings?.job_roles || []).map(r => <span key={r} className="badge badge-indigo">{r}</span>)}</div>
                </div>
                <div>
                    <p className="text-xs text-slate-500 mb-2">Locations</p>
                    <div className="flex flex-wrap gap-1.5">{(settings?.job_locations || []).map(l => <span key={l} className="badge badge-slate">{l}</span>)}</div>
                </div>
                <p className="text-xs text-slate-500">Update via <code className="bg-slate-700 px-1 rounded">JOB_ROLES</code> / <code className="bg-slate-700 px-1 rounded">JOB_LOCATIONS</code> in .env</p>
            </div>

            {/* Manual Actions */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base">🔍 Manual Actions</h2>
                <p className="text-xs text-slate-500">Use the "Scan Jobs" button in the header to manually trigger a job search across all platforms.</p>
                <div className="flex gap-2">
                    <a href="https://job-tracker-pro-api.onrender.com/docs" target="_blank" rel="noopener noreferrer" className="btn-secondary text-xs">Open API Docs (Swagger)</a>
                </div>
            </div>
        </div>
    )
}
