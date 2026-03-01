import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Sparkles, BookmarkPlus, Building2, MapPin, Briefcase } from 'lucide-react'
import { getJob } from '../api/jobs'
import { createApplication } from '../api/applications'
import api from '../api/client'
import { getMatchColor, parseSkills, parseMatchAnalysis, getPlatformClass } from '../utils/formatters'
import toast from 'react-hot-toast'

export default function JobDetailPage() {
    const { id } = useParams()
    const [job, setJob] = useState(null)
    const [analysis, setAnalysis] = useState(null)
    const [coverLetter, setCoverLetter] = useState('')
    const [generating, setGenerating] = useState(false)
    const [loading, setLoading] = useState(true)
    const [tab, setTab] = useState('description')

    useEffect(() => {
        getJob(id).then(j => {
            setJob(j)
            if (j.match_analysis) setAnalysis(parseMatchAnalysis(j.match_analysis))
            setLoading(false)
        }).catch(() => setLoading(false))
    }, [id])

    const handleGenCoverLetter = async () => {
        setGenerating(true)
        try {
            const res = await api.post('/cover-letters/generate', { job_id: id })
            setCoverLetter(res.content)
            setTab('cover_letter')
            toast.success(res.cached ? 'Loaded saved cover letter!' : 'Cover letter generated!')
        } catch (e) { toast.error(e.message) }
        finally { setGenerating(false) }
    }

    const handleSave = async () => {
        try {
            await createApplication({ job_id: id, status: 'saved' })
            toast.success('Added to applications!')
        } catch (e) { toast.error(e.message) }
    }

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
    )
    if (!job) return <div className="text-center text-slate-400 py-16">Job not found</div>

    const mc = getMatchColor(job.match_score)
    const skills = parseSkills(job.skills_required)

    const TABS = ['description', 'match_analysis', 'cover_letter']

    return (
        <div className="max-w-4xl mx-auto space-y-5 animate-fade-in">
            <Link to="/jobs" className="inline-flex items-center gap-2 text-slate-400 hover:text-slate-200 text-sm">
                <ArrowLeft className="w-4 h-4" /> Back to Job Feed
            </Link>

            {/* Job header */}
            <div className="card p-6">
                <div className="flex gap-5 flex-wrap">
                    <img
                        src={job.company_logo_url}
                        alt={job.company}
                        className="w-16 h-16 rounded-2xl object-contain bg-slate-700 flex-shrink-0 border border-slate-600/30"
                        onError={(e) => { e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(job.company)}&background=4f46e5&color=fff&size=64` }}
                    />
                    <div className="flex-1 min-w-0">
                        <h1 className="text-2xl font-bold text-slate-100">{job.title}</h1>
                        <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-slate-400">
                            <span className="flex items-center gap-1"><Building2 className="w-4 h-4" />{job.company}</span>
                            <span className="flex items-center gap-1"><MapPin className="w-4 h-4" />{job.location}</span>
                            {job.job_type && <span className="flex items-center gap-1"><Briefcase className="w-4 h-4" />{job.job_type}</span>}
                            <span className={`${getPlatformClass(job.platform)} badge`}>{job.platform}</span>
                        </div>
                    </div>
                    {/* Match score */}
                    <div className="flex-shrink-0 text-center">
                        <div className="relative w-20 h-20">
                            <svg width="80" height="80" className="-rotate-90">
                                <circle cx="40" cy="40" r="34" fill="none" stroke="#1e293b" strokeWidth="6" />
                                <circle cx="40" cy="40" r="34" fill="none" stroke={mc.color} strokeWidth="6"
                                    strokeDasharray={`${2 * Math.PI * 34 * job.match_score / 100} ${2 * Math.PI * 34}`}
                                    strokeLinecap="round" />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-xl font-bold" style={{ color: mc.color }}>{Math.round(job.match_score)}</span>
                                <span className="text-xs text-slate-500">match</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                    <button onClick={handleSave} className="btn-secondary"><BookmarkPlus className="w-4 h-4" /> Save</button>
                    <button onClick={handleGenCoverLetter} disabled={generating} className="btn-primary">
                        <Sparkles className="w-4 h-4" />
                        {generating ? 'Generating...' : 'Generate Cover Letter'}
                    </button>
                    <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                        <ExternalLink className="w-4 h-4" /> Apply on {job.platform}
                    </a>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 bg-slate-900 rounded-xl p-1">
                {TABS.map(t => (
                    <button key={t} onClick={() => setTab(t)}
                        className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${tab === t ? 'bg-primary-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}>
                        {t === 'description' ? '📄 Description' : t === 'match_analysis' ? '🎯 AI Analysis' : '✉️ Cover Letter'}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            <div className="card p-6">
                {tab === 'description' && (
                    <div className="space-y-4">
                        {skills.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Required Skills</p>
                                <div className="flex flex-wrap gap-1.5">
                                    {skills.map(s => <span key={s} className="badge badge-indigo">{s}</span>)}
                                </div>
                            </div>
                        )}
                        <div>
                            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Job Description</p>
                            <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{job.description || 'No description available.'}</div>
                        </div>
                    </div>
                )}

                {tab === 'match_analysis' && (
                    <div className="space-y-4">
                        {analysis ? (
                            <>
                                {analysis.recommendation && (
                                    <div className="p-4 rounded-xl bg-primary-500/10 border border-primary-500/20">
                                        <p className="text-sm text-primary-300 font-medium">💡 Recommendation</p>
                                        <p className="text-sm text-slate-300 mt-1">{analysis.recommendation}</p>
                                    </div>
                                )}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-xs font-semibold text-green-500 uppercase tracking-wider mb-2">✅ Matching Skills</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {(analysis.matching_skills || []).map(s => <span key={s} className="badge badge-green text-xs">{s}</span>)}
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-xs font-semibold text-red-500 uppercase tracking-wider mb-2">❌ Missing Skills</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {(analysis.missing_skills || []).map(s => <span key={s} className="badge badge-red text-xs">{s}</span>)}
                                        </div>
                                    </div>
                                </div>
                                {analysis.tailored_summary && (
                                    <div>
                                        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Tailored Summary</p>
                                        <p className="text-sm text-slate-300 p-3 bg-slate-700/30 rounded-lg">{analysis.tailored_summary}</p>
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="text-slate-500 text-sm text-center py-8">No AI analysis available yet.</p>
                        )}
                    </div>
                )}

                {tab === 'cover_letter' && (
                    <div className="space-y-3">
                        {coverLetter ? (
                            <>
                                <div className="flex justify-end gap-2">
                                    <button onClick={() => { navigator.clipboard.writeText(coverLetter); toast.success('Copied!') }} className="btn-secondary text-xs">Copy</button>
                                </div>
                                <textarea
                                    value={coverLetter}
                                    onChange={e => setCoverLetter(e.target.value)}
                                    className="input min-h-[300px] resize-y text-sm leading-relaxed"
                                />
                            </>
                        ) : (
                            <div className="text-center py-12">
                                <p className="text-4xl mb-3">✉️</p>
                                <p className="text-slate-400 text-sm">No cover letter generated yet</p>
                                <button onClick={handleGenCoverLetter} disabled={generating} className="btn-primary mt-4">
                                    <Sparkles className="w-4 h-4" />
                                    {generating ? 'Generating with Gemini AI...' : 'Generate Cover Letter'}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
