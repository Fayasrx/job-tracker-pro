import { useState, useEffect } from 'react'
import { Save, User, Briefcase, Code, MapPin, Mail, Phone, Link } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'

export default function Profile() {
    const [profile, setProfile] = useState(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        api.get('/profile').then(p => { setProfile(p); setLoading(false) }).catch(() => setLoading(false))
    }, [])

    const handleSave = async () => {
        setSaving(true)
        try {
            await api.put('/profile', { data: profile })
            toast.success('Profile saved!')
        } catch (e) { toast.error(e.message) }
        finally { setSaving(false) }
    }

    const update = (path, val) => {
        setProfile(p => {
            const copy = { ...p }
            path.reduce((obj, key, i) => {
                if (i === path.length - 1) obj[key] = val
                else { obj[key] = { ...obj[key] }; return obj[key] }
                return obj
            }, copy)
            return copy
        })
    }

    if (loading) return <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
    if (!profile) return <div className="text-center text-slate-400 py-16">Profile not found</div>

    return (
        <div className="max-w-2xl mx-auto space-y-5 animate-fade-in">
            <div className="flex justify-end">
                <button onClick={handleSave} disabled={saving} className="btn-primary">
                    <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Profile'}
                </button>
            </div>

            {/* Basic Info */}
            <div className="card p-5 space-y-4">
                <h2 className="font-bold text-slate-100 text-base flex items-center gap-2"><User className="w-4 h-4 text-primary-400" /> Basic Info</h2>
                <div className="grid grid-cols-2 gap-4">
                    <div><label className="text-xs text-slate-500 mb-1 block">Full Name</label>
                        <input className="input" value={profile.name || ''} onChange={e => update(['name'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">Email</label>
                        <input className="input" value={profile.email || ''} onChange={e => update(['email'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">Phone</label>
                        <input className="input" value={profile.phone || ''} onChange={e => update(['phone'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">Location</label>
                        <input className="input" value={profile.location || ''} onChange={e => update(['location'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">LinkedIn</label>
                        <input className="input" value={profile.linkedin || ''} onChange={e => update(['linkedin'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">GitHub</label>
                        <input className="input" value={profile.github || ''} onChange={e => update(['github'], e.target.value)} /></div>
                </div>
                <div><label className="text-xs text-slate-500 mb-1 block">Summary</label>
                    <textarea className="input min-h-[80px] resize-none" value={profile.summary || ''}
                        onChange={e => update(['summary'], e.target.value)} /></div>
            </div>

            {/* Education */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base">🎓 Education</h2>
                <div className="grid grid-cols-2 gap-3">
                    <div><label className="text-xs text-slate-500 mb-1 block">Degree</label>
                        <input className="input" value={profile.education?.degree || ''} onChange={e => update(['education', 'degree'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">College</label>
                        <input className="input" value={profile.education?.college || ''} onChange={e => update(['education', 'college'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">CGPA</label>
                        <input className="input" value={profile.education?.cgpa || ''} onChange={e => update(['education', 'cgpa'], e.target.value)} /></div>
                    <div><label className="text-xs text-slate-500 mb-1 block">Year</label>
                        <input className="input" value={profile.education?.year || ''} onChange={e => update(['education', 'year'], e.target.value)} /></div>
                </div>
            </div>

            {/* Job Preferences */}
            <div className="card p-5 space-y-3">
                <h2 className="font-bold text-slate-100 text-base"><Briefcase className="inline w-4 h-4 mr-1 text-primary-400" />Job Preferences</h2>
                <div><label className="text-xs text-slate-500 mb-1 block">Target Roles (comma-separated)</label>
                    <input className="input" value={(profile.job_preferences?.roles || []).join(', ')}
                        onChange={e => update(['job_preferences', 'roles'], e.target.value.split(',').map(s => s.trim()).filter(Boolean))} /></div>
                <div><label className="text-xs text-slate-500 mb-1 block">Target Locations (comma-separated)</label>
                    <input className="input" value={(profile.job_preferences?.locations || []).join(', ')}
                        onChange={e => update(['job_preferences', 'locations'], e.target.value.split(',').map(s => s.trim()).filter(Boolean))} /></div>
            </div>

            {/* Read-only preview */}
            <div className="card p-5">
                <h2 className="font-bold text-slate-100 text-base mb-3">📄 Profile Preview</h2>
                <div className="text-xs text-slate-400 bg-slate-900/60 rounded-xl p-4 overflow-x-auto">
                    <pre className="whitespace-pre-wrap">{JSON.stringify(profile, null, 2)}</pre>
                </div>
            </div>
        </div>
    )
}
