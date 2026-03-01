import { useState, useEffect } from 'react'
import { Save, Key, Clock, ToggleLeft, ToggleRight } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'

export default function Settings() {
    const [settings, setSettings] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.get('/settings').then(s => { setSettings(s); setLoading(false) }).catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

    return (
        <div className="max-w-xl mx-auto space-y-5 animate-fade-in">
            {/* Gemini API */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2">
                    <Key className="w-4 h-4 text-primary-400" /> Gemini AI
                </h2>
                <div className={`flex items-center gap-3 p-3 rounded-xl ${settings?.gemini_configured ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                    <div className={`w-2.5 h-2.5 rounded-full animate-pulse ${settings?.gemini_configured ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className={`text-sm font-medium ${settings?.gemini_configured ? 'text-green-400' : 'text-red-400'}`}>
                        {settings?.gemini_configured ? 'Gemini API key configured ✓' : 'Gemini API key not set — set GEMINI_API_KEY in .env'}
                    </span>
                </div>
                <p className="text-xs text-slate-500">
                    Edit the <code className="bg-slate-700 px-1 rounded">.env</code> file in the project root to update your API key. The key is used for match scoring, cover letter generation, and resume tips.
                </p>
            </div>

            {/* Scheduler */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2">
                    <Clock className="w-4 h-4 text-amber-400" /> Scheduler
                </h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                        <p className="text-slate-500 text-xs">Daily Scan Time</p>
                        <p className="font-semibold text-slate-200">{settings?.daily_scan_time || '06:00'}</p>
                    </div>
                    <div className="space-y-1">
                        <p className="text-slate-500 text-xs">Daily Digest Time</p>
                        <p className="font-semibold text-slate-200">{settings?.digest_time || '09:00'}</p>
                    </div>
                </div>
                <p className="text-xs text-slate-500">Update times in <code className="bg-slate-700 px-1 rounded">.env</code> → <code className="bg-slate-700 px-1 rounded">DAILY_SCAN_TIME</code>, <code className="bg-slate-700 px-1 rounded">DIGEST_TIME</code></p>
            </div>

            {/* Job Preferences */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base">🎯 Job Preferences</h2>
                <div>
                    <p className="text-xs text-slate-500 mb-2">Target Roles</p>
                    <div className="flex flex-wrap gap-1.5">
                        {(settings?.job_roles || []).map(r => (
                            <span key={r} className="badge badge-indigo">{r}</span>
                        ))}
                    </div>
                </div>
                <div>
                    <p className="text-xs text-slate-500 mb-2">Locations</p>
                    <div className="flex flex-wrap gap-1.5">
                        {(settings?.job_locations || []).map(l => (
                            <span key={l} className="badge badge-slate">{l}</span>
                        ))}
                    </div>
                </div>
                <p className="text-xs text-slate-500">Update roles/locations in <code className="bg-slate-700 px-1 rounded">.env</code> → <code className="bg-slate-700 px-1 rounded">JOB_ROLES</code>, <code className="bg-slate-700 px-1 rounded">JOB_LOCATIONS</code></p>
            </div>

            {/* Manual scan */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base">🔍 Manual Actions</h2>
                <p className="text-xs text-slate-500">Use the "Scan Jobs" button in the top-right header to manually trigger a job search across all platforms. Results will appear in the Job Feed and trigger notifications.</p>
                <div className="flex gap-2">
                    <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer"
                        className="btn-secondary text-xs">Open API Docs (Swagger)</a>
                </div>
            </div>
        </div>
    )
}
