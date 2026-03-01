import { useState, useEffect } from 'react'
import { Sparkles, Copy, Trash2, FileText } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'
import { relativeTime } from '../utils/formatters'

export default function CoverLetters() {
    const [letters, setLetters] = useState([])
    const [selected, setSelected] = useState(null)
    const [editing, setEditing] = useState('')
    const [loading, setLoading] = useState(true)

    const load = async () => {
        const data = await api.get('/cover-letters')
        setLetters(data)
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const handleSelect = (cl) => { setSelected(cl); setEditing(cl.content) }

    const handleSave = async () => {
        if (!selected) return
        await api.put(`/cover-letters/${selected.id}`, { content: editing })
        toast.success('Saved!')
        setLetters(ls => ls.map(l => l.id === selected.id ? { ...l, content: editing } : l))
        setSelected({ ...selected, content: editing })
    }

    const handleDelete = async (id) => {
        await api.delete(`/cover-letters/${id}`)
        if (selected?.id === id) { setSelected(null); setEditing('') }
        setLetters(ls => ls.filter(l => l.id !== id))
        toast.success('Deleted')
    }

    const handleCopy = () => { navigator.clipboard.writeText(editing); toast.success('Copied!') }

    return (
        <div className="flex gap-5 h-[calc(100vh-130px)] animate-fade-in">
            {/* List panel */}
            <div className="w-72 flex-shrink-0 flex flex-col gap-3 overflow-y-auto">
                <div className="card p-3 text-center text-xs text-slate-500">
                    Generate cover letters from the Job Detail page
                </div>
                {loading ? (
                    <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
                ) : letters.length === 0 ? (
                    <div className="card p-8 text-center">
                        <FileText className="w-10 h-10 text-slate-700 mx-auto mb-2" />
                        <p className="text-slate-500 text-sm">No cover letters yet</p>
                    </div>
                ) : letters.map(cl => (
                    <div key={cl.id} onClick={() => handleSelect(cl)}
                        className={`card p-4 cursor-pointer hover:border-slate-600/60 transition-all ${selected?.id === cl.id ? 'border-primary-500/40 bg-primary-500/5' : ''}`}>
                        <p className="font-semibold text-sm text-slate-100 truncate">{cl.job_title}</p>
                        <p className="text-xs text-slate-500 mt-0.5">{cl.job_company}</p>
                        <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-slate-600">{relativeTime(cl.created_at)}</span>
                            <button onClick={(e) => { e.stopPropagation(); handleDelete(cl.id) }}
                                className="p-1 text-slate-600 hover:text-red-400 rounded hover:bg-red-500/10 transition-colors">
                                <Trash2 className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Editor panel */}
            <div className="flex-1 flex flex-col gap-3 min-w-0">
                {selected ? (
                    <>
                        <div className="flex items-center gap-2">
                            <div className="flex-1">
                                <p className="font-bold text-slate-100">{selected.job_title} — {selected.job_company}</p>
                            </div>
                            <button onClick={handleCopy} className="btn-secondary text-xs"><Copy className="w-3.5 h-3.5" /> Copy</button>
                            <button onClick={handleSave} className="btn-primary text-xs">Save</button>
                        </div>
                        <textarea
                            value={editing}
                            onChange={e => setEditing(e.target.value)}
                            className="input flex-1 resize-none text-sm leading-relaxed"
                            placeholder="Your cover letter..."
                        />
                    </>
                ) : (
                    <div className="card flex-1 flex items-center justify-center">
                        <div className="text-center">
                            <FileText className="w-14 h-14 text-slate-700 mx-auto mb-3" />
                            <p className="text-slate-400">Select a cover letter to edit</p>
                            <p className="text-slate-600 text-sm mt-1">Or generate from a Job Detail page</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
