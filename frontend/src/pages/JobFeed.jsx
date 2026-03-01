import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, Heart, BookmarkPlus, FileText, Building2, MapPin, Clock, ChevronDown } from 'lucide-react'
import { getJobs } from '../api/jobs'
import { createApplication } from '../api/applications'
import { getMatchColor, getPlatformClass, relativeTime, parseSkills, truncate } from '../utils/formatters'
import toast from 'react-hot-toast'

const PLATFORMS = ['all', 'linkedin', 'indeed', 'glassdoor', 'naukri', 'internshala']
const LOCATIONS = ['all', 'Remote', 'Chennai', 'Bangalore', 'Hyderabad']
const SORT_OPTIONS = [
    { value: 'match_score', label: 'Match Score' },
    { value: 'scraped_at', label: 'Date Added' },
    { value: 'company', label: 'Company' },
]

function JobCard({ job, onSave }) {
    const mc = getMatchColor(job.match_score)
    const skills = parseSkills(job.skills_required)

    const handleApply = async (e) => {
        e.preventDefault()
        try {
            await createApplication({ job_id: job.id, status: 'saved' })
            toast.success('Added to applications!')
        } catch (err) { toast.error(err.message) }
    }

    return (
        <Link to={`/jobs/${job.id}`} className="card block p-5 hover:border-slate-600/60 hover:shadow-lg hover:shadow-black/20 transition-all duration-200 group animate-fade-in">
            <div className="flex gap-4">
                <img
                    src={job.company_logo_url}
                    alt={job.company}
                    className="w-12 h-12 rounded-xl object-contain bg-slate-700 flex-shrink-0 border border-slate-600/30"
                    onError={(e) => { e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(job.company)}&background=4f46e5&color=fff&size=48` }}
                />
                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                            <h3 className="font-bold text-slate-100 group-hover:text-primary-300 transition-colors truncate">{job.title}</h3>
                            <p className="text-sm text-slate-400 mt-0.5">{job.company}</p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                            {/* Match score badge */}
                            <div className="relative w-12 h-12">
                                <svg width="48" height="48" className="-rotate-90">
                                    <circle cx="24" cy="24" r="19" fill="none" stroke="#1e293b" strokeWidth="4" />
                                    <circle cx="24" cy="24" r="19" fill="none" stroke={mc.color} strokeWidth="4"
                                        strokeDasharray={`${(2 * Math.PI * 19) * (job.match_score / 100)} ${2 * Math.PI * 19}`}
                                        strokeLinecap="round" />
                                </svg>
                                <span className="absolute inset-0 flex items-center justify-center text-xs font-bold" style={{ color: mc.color }}>
                                    {Math.round(job.match_score)}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span className={`${getPlatformClass(job.platform)} badge`}>{job.platform}</span>
                        <span className="flex items-center gap-1 text-xs text-slate-500">
                            <MapPin className="w-3 h-3" /> {job.location || 'Unknown'}
                        </span>
                        <span className="flex items-center gap-1 text-xs text-slate-500">
                            <Clock className="w-3 h-3" /> {relativeTime(job.scraped_at)}
                        </span>
                        {job.job_type && <span className="badge-slate badge">{job.job_type}</span>}
                    </div>

                    <p className="text-xs text-slate-500 mt-2 line-clamp-2">{truncate(job.description, 150)}</p>

                    {skills.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3">
                            {skills.slice(0, 5).map(s => (
                                <span key={s} className="badge badge-indigo text-xs">{s}</span>
                            ))}
                            {skills.length > 5 && <span className="badge badge-slate text-xs">+{skills.length - 5}</span>}
                        </div>
                    )}
                </div>
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 mt-4 pt-3 border-t border-slate-700/50">
                <button onClick={handleApply}
                    className="btn-secondary flex-1 text-xs justify-center py-1.5">
                    <BookmarkPlus className="w-3.5 h-3.5" /> Save
                </button>
                <a href={job.url} target="_blank" rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="btn-primary flex-1 text-xs justify-center py-1.5">
                    Apply Now
                </a>
            </div>
        </Link>
    )
}

export default function JobFeed() {
    const [jobs, setJobs] = useState([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(1)
    const [filters, setFilters] = useState({
        platform: 'all', location: 'all', search: '',
        sort_by: 'match_score', min_score: 0,
    })

    const load = useCallback(async () => {
        setLoading(true)
        try {
            const params = { ...filters, page, per_page: 20 }
            if (filters.platform === 'all') delete params.platform
            if (filters.location === 'all') delete params.location
            if (!filters.search) delete params.search
            const data = await getJobs(params)
            setJobs(page === 1 ? data.jobs : prev => [...prev, ...data.jobs])
            setTotal(data.total)
        } catch (e) { toast.error(e.message) }
        finally { setLoading(false) }
    }, [filters, page])

    useEffect(() => { setPage(1) }, [filters])
    useEffect(() => { load() }, [load])

    const setFilter = (key, val) => setFilters(f => ({ ...f, [key]: val }))

    return (
        <div className="space-y-5 animate-fade-in">
            {/* Filter bar */}
            <div className="card p-4 flex flex-wrap gap-3 items-center sticky top-0 z-10 backdrop-blur-sm">
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text" placeholder="Search jobs or companies..."
                        className="input pl-9" value={filters.search}
                        onChange={e => setFilter('search', e.target.value)}
                    />
                </div>
                <select className="select w-36" value={filters.platform} onChange={e => setFilter('platform', e.target.value)}>
                    {PLATFORMS.map(p => <option key={p} value={p}>{p === 'all' ? 'All Platforms' : p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
                </select>
                <select className="select w-36" value={filters.location} onChange={e => setFilter('location', e.target.value)}>
                    {LOCATIONS.map(l => <option key={l} value={l}>{l === 'all' ? 'All Locations' : l}</option>)}
                </select>
                <select className="select w-36" value={filters.sort_by} onChange={e => setFilter('sort_by', e.target.value)}>
                    {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>Min: {filters.min_score}%</span>
                    <input type="range" min="0" max="100" step="5" value={filters.min_score}
                        className="w-20 accent-primary-500"
                        onChange={e => setFilter('min_score', Number(e.target.value))} />
                </div>
                <span className="text-xs text-slate-500 ml-auto">{total} jobs</span>
            </div>

            {/* Job grid */}
            {loading && page === 1 ? (
                <div className="flex items-center justify-center h-48">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
            ) : jobs.length === 0 ? (
                <div className="card p-12 text-center">
                    <p className="text-4xl mb-3">🔍</p>
                    <p className="text-slate-400 font-medium">No jobs found</p>
                    <p className="text-slate-600 text-sm mt-1">Try adjusting your filters or run a new scan</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    {jobs.map(job => <JobCard key={job.id} job={job} />)}
                </div>
            )}

            {/* Load more */}
            {jobs.length < total && (
                <div className="text-center pt-2">
                    <button onClick={() => setPage(p => p + 1)} disabled={loading} className="btn-secondary">
                        {loading ? 'Loading...' : `Load More (${total - jobs.length} remaining)`}
                    </button>
                </div>
            )}
        </div>
    )
}
