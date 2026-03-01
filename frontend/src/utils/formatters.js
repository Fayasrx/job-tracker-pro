/**
 * Format a match score (0-100) to a color class and label.
 */
export function getMatchColor(score) {
    if (score >= 90) return { cls: 'badge-green', label: '🟢 Excellent', color: '#22c55e' }
    if (score >= 70) return { cls: 'badge-yellow', label: '🟡 Good', color: '#f59e0b' }
    if (score >= 50) return { cls: 'badge-orange', label: '🟠 Fair', color: '#f97316' }
    return { cls: 'badge-red', label: '🔴 Low', color: '#ef4444' }
}

/**
 * Format a date string to relative time (e.g. "2 hours ago").
 */
export function relativeTime(dateStr) {
    if (!dateStr) return 'Unknown'
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const mins = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    if (mins < 1) return 'Just now'
    if (mins < 60) return `${mins}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
}

/**
 * Get platform badge CSS class.
 */
export function getPlatformClass(platform) {
    const map = {
        linkedin: 'platform-badge-linkedin',
        indeed: 'platform-badge-indeed',
        naukri: 'platform-badge-naukri',
        glassdoor: 'platform-badge-glassdoor',
        internshala: 'platform-badge-internshala',
    }
    return map[(platform || '').toLowerCase()] || 'badge-slate'
}

/**
 * Get status badge for applications.
 */
export function getStatusConfig(status) {
    const map = {
        saved: { label: 'Saved', cls: 'badge-slate', emoji: '🔖' },
        applied: { label: 'Applied', cls: 'badge-indigo', emoji: '📝' },
        in_review: { label: 'In Review', cls: 'badge-yellow', emoji: '👁️' },
        interview: { label: 'Interview', cls: 'badge-green', emoji: '🎤' },
        offer: { label: 'Offer', cls: 'badge-green', emoji: '🎉' },
        rejected: { label: 'Rejected', cls: 'badge-red', emoji: '❌' },
    }
    return map[status] || { label: status, cls: 'badge-slate', emoji: '📋' }
}

/**
 * Parse skills JSON string safely.
 */
export function parseSkills(skillsStr) {
    try { return JSON.parse(skillsStr) } catch { return [] }
}

/**
 * Parse match analysis JSON string safely.
 */
export function parseMatchAnalysis(str) {
    try { return JSON.parse(str) } catch { return {} }
}

/**
 * Truncate text to given length.
 */
export function truncate(text, len = 120) {
    if (!text) return ''
    return text.length > len ? text.slice(0, len) + '...' : text
}
