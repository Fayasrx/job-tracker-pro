import { useState, useEffect } from 'react'
import { Building2, Bell, BellOff, X, Plus } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'

export default function Companies() {
    const [companies, setCompanies] = useState([])
    const [loading, setLoading] = useState(true)
    const [showAdd, setShowAdd] = useState(false)
    const [form, setForm] = useState({ name: '', domain: '', notify: true })

    const load = async () => {
        const data = await api.get('/companies')
        setCompanies(data)
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const handleTrack = async () => {
        if (!form.name.trim()) { toast.error('Company name required'); return }
        try {
            await api.post('/companies/track', form)
            toast.success(`Now tracking ${form.name}`)
            setForm({ name: '', domain: '', notify: true })
            setShowAdd(false)
            load()
        } catch (e) { toast.error(e.message) }
    }

    const handleUntrack = async (id, name) => {
        await api.delete(`/companies/${id}/track`)
        toast.success(`Stopped tracking ${name}`)
        load()
    }

    const toggleNotify = async (id, current) => {
        await api.patch(`/companies/${id}`, { notify: !current })
        setCompanies(c => c.map(x => x.id === id ? { ...x, notify: !current } : x))
    }

    return (
        <div className="max-w-2xl mx-auto space-y-4 animate-fade-in">
            <div className="flex justify-end">
                <button onClick={() => setShowAdd(true)} className="btn-primary">
                    <Plus className="w-4 h-4" /> Track Company
                </button>
            </div>

            {showAdd && (
                <div className="card p-5 space-y-3 animate-slide-up">
                    <h3 className="font-semibold text-slate-100">Track a Company</h3>
                    <input className="input" placeholder="Company name (e.g. Google)" value={form.name}
                        onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
                    <input className="input" placeholder="Domain (e.g. google.com) — for logo" value={form.domain}
                        onChange={e => setForm(f => ({ ...f, domain: e.target.value }))} />
                    <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                        <input type="checkbox" checked={form.notify} onChange={e => setForm(f => ({ ...f, notify: e.target.checked }))}
                            className="w-4 h-4 accent-primary-500" />
                        Notify me of new jobs from this company
                    </label>
                    <div className="flex gap-2">
                        <button onClick={handleTrack} className="btn-primary flex-1">Track</button>
                        <button onClick={() => setShowAdd(false)} className="btn-secondary">Cancel</button>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-12">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : companies.length === 0 ? (
                <div className="card p-12 text-center">
                    <Building2 className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                    <p className="text-slate-400">No companies tracked yet</p>
                    <p className="text-slate-600 text-sm mt-1">You can track companies from any job card too</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {companies.map(c => (
                        <div key={c.id} className="card p-4 flex items-center gap-4 hover:border-slate-600/60 transition-all">
                            <img src={c.logo_url} alt={c.name}
                                className="w-10 h-10 rounded-xl bg-slate-700 object-contain flex-shrink-0"
                                onError={e => { e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(c.name)}&background=4f46e5&color=fff&size=40` }} />
                            <div className="flex-1 min-w-0">
                                <p className="font-semibold text-slate-100">{c.name}</p>
                                {c.domain && <p className="text-xs text-slate-500">{c.domain}</p>}
                            </div>
                            <div className="flex items-center gap-2">
                                <button onClick={() => toggleNotify(c.id, c.notify)}
                                    className={`p-2 rounded-lg transition-colors ${c.notify ? 'text-primary-400 bg-primary-500/10 hover:bg-primary-500/20' : 'text-slate-600 hover:text-slate-400'}`}
                                    title={c.notify ? 'Notifications on' : 'Notifications off'}>
                                    {c.notify ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                                </button>
                                <button onClick={() => handleUntrack(c.id, c.name)}
                                    className="p-2 rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
