import { useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { ExternalLink, Trash2, ChevronDown, Calendar, Building2 } from 'lucide-react'
import { getApplications, updateApplication, deleteApplication } from '../api/applications'
import { getStatusConfig, relativeTime } from '../utils/formatters'
import toast from 'react-hot-toast'

const COLUMNS = [
    { id: 'saved', label: 'Saved', emoji: '🔖', color: 'border-slate-500' },
    { id: 'applied', label: 'Applied', emoji: '📝', color: 'border-primary-500' },
    { id: 'in_review', label: 'In Review', emoji: '👁️', color: 'border-amber-500' },
    { id: 'interview', label: 'Interview', emoji: '🎤', color: 'border-green-500' },
    { id: 'offer', label: 'Offer', emoji: '🎉', color: 'border-emerald-400' },
    { id: 'rejected', label: 'Rejected', emoji: '❌', color: 'border-red-500' },
]

function AppCard({ app, index, onDelete }) {
    const sc = getStatusConfig(app.status)
    return (
        <Draggable draggableId={app.id} index={index}>
            {(prov, snap) => (
                <div ref={prov.innerRef} {...prov.draggableProps} {...prov.dragHandleProps}
                    className={`card p-4 cursor-grab active:cursor-grabbing transition-all duration-150 ${snap.isDragging ? 'shadow-2xl shadow-primary-500/20 rotate-1 scale-105' : ''}`}>
                    <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm text-slate-100 truncate">{app.job_title || 'Unknown Job'}</p>
                            <div className="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                                <Building2 className="w-3 h-3" /> {app.job_company || 'Unknown'}
                            </div>
                        </div>
                        <div className="flex gap-1 flex-shrink-0">
                            {app.job_url && (
                                <a href={app.job_url} target="_blank" rel="noopener noreferrer"
                                    className="p-1 text-slate-500 hover:text-slate-300 rounded-lg hover:bg-slate-700/50 transition-colors">
                                    <ExternalLink className="w-3.5 h-3.5" />
                                </a>
                            )}
                            <button onClick={() => onDelete(app.id)}
                                className="p-1 text-slate-600 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors">
                                <Trash2 className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mt-2">
                        {app.job_platform && <span className="badge badge-slate text-xs">{app.job_platform}</span>}
                        {app.job_match_score > 0 && (
                            <span className="badge badge-indigo text-xs">{Math.round(app.job_match_score)}% match</span>
                        )}
                    </div>

                    {app.notes && (
                        <p className="text-xs text-slate-500 mt-2 line-clamp-2 italic">{app.notes}</p>
                    )}

                    <div className="flex items-center gap-2 mt-2 text-xs text-slate-600">
                        <Calendar className="w-3 h-3" />
                        {app.applied_date ? `Applied ${relativeTime(app.applied_date)}` : `Saved ${relativeTime(app.created_at)}`}
                    </div>
                </div>
            )}
        </Draggable>
    )
}

export default function Applications() {
    const [columns, setColumns] = useState({})
    const [loading, setLoading] = useState(true)

    const load = async () => {
        setLoading(true)
        const data = await getApplications({ per_page: 200 })
        const grouped = {}
        COLUMNS.forEach(c => { grouped[c.id] = [] })
            ; (data.applications || []).forEach(app => {
                if (grouped[app.status]) grouped[app.status].push(app)
                else grouped['saved'].push(app)
            })
        setColumns(grouped)
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const onDragEnd = async (result) => {
        const { source, destination, draggableId } = result
        if (!destination || source.droppableId === destination.droppableId) {
            if (!destination) return
            // Same column reorder
            const col = [...columns[source.droppableId]]
            const [moved] = col.splice(source.index, 1)
            col.splice(destination.index, 0, moved)
            setColumns(prev => ({ ...prev, [source.droppableId]: col }))
            return
        }
        // Move to different column
        const srcCol = [...columns[source.droppableId]]
        const dstCol = [...columns[destination.droppableId]]
        const [moved] = srcCol.splice(source.index, 1)
        moved.status = destination.droppableId
        dstCol.splice(destination.index, 0, moved)
        setColumns(prev => ({
            ...prev,
            [source.droppableId]: srcCol,
            [destination.droppableId]: dstCol,
        }))
        try {
            await updateApplication(draggableId, { status: destination.droppableId })
            toast.success(`Moved to ${destination.droppableId.replace('_', ' ')}`)
        } catch (e) { toast.error(e.message); load() }
    }

    const handleDelete = async (id) => {
        await deleteApplication(id)
        load()
        toast.success('Removed')
    }

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
    )

    const totalApps = Object.values(columns).reduce((sum, c) => sum + c.length, 0)

    return (
        <div className="animate-fade-in">
            <div className="flex items-center gap-3 mb-5">
                <p className="text-slate-400 text-sm">{totalApps} total applications · Drag cards to update status</p>
            </div>

            <DragDropContext onDragEnd={onDragEnd}>
                <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: 'calc(100vh - 180px)' }}>
                    {COLUMNS.map(col => (
                        <div key={col.id} className={`flex-shrink-0 w-64 rounded-2xl flex flex-col bg-slate-900/50 border-t-2 ${col.color}`}>
                            <div className="px-4 py-3 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span>{col.emoji}</span>
                                    <span className="text-sm font-semibold text-slate-200">{col.label}</span>
                                </div>
                                <span className="badge badge-slate text-xs">{columns[col.id]?.length || 0}</span>
                            </div>
                            <Droppable droppableId={col.id}>
                                {(prov, snap) => (
                                    <div ref={prov.innerRef} {...prov.droppableProps}
                                        className={`flex-1 p-3 kanban-col rounded-b-2xl transition-colors ${snap.isDraggingOver ? 'bg-primary-500/5' : ''}`}>
                                        {(columns[col.id] || []).map((app, idx) => (
                                            <AppCard key={app.id} app={app} index={idx} onDelete={handleDelete} />
                                        ))}
                                        {prov.placeholder}
                                        {(columns[col.id] || []).length === 0 && !snap.isDraggingOver && (
                                            <div className="flex-1 flex items-center justify-center py-8 text-slate-700 text-xs text-center">
                                                Drop cards here
                                            </div>
                                        )}
                                    </div>
                                )}
                            </Droppable>
                        </div>
                    ))}
                </div>
            </DragDropContext>
        </div>
    )
}
