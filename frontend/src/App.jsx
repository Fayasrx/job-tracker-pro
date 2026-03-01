import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import JobFeed from './pages/JobFeed'
import JobDetailPage from './pages/JobDetailPage'
import Applications from './pages/Applications'
import Notifications from './pages/Notifications'
import Companies from './pages/Companies'
import CoverLetters from './pages/CoverLetters'
import Profile from './pages/Profile'
import Settings from './pages/Settings'

// Route wrapper that checks for the PIN
function ProtectedRoute({ children }) {
    const pin = localStorage.getItem('job_tracker_pin')
    const location = useLocation()

    if (!pin) {
        // Redirect them to the /login page, but save the current location they were
        // trying to go to when they were redirected. This allows us to send them
        // along to that page after they login, which is a nicer user experience
        // than dropping them off on the home page.
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return children
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={
                    <ProtectedRoute>
                        <Layout />
                    </ProtectedRoute>
                }>
                    <Route index element={<Dashboard />} />
                    <Route path="jobs" element={<JobFeed />} />
                    <Route path="jobs/:id" element={<JobDetailPage />} />
                    <Route path="applications" element={<Applications />} />
                    <Route path="notifications" element={<Notifications />} />
                    <Route path="companies" element={<Companies />} />
                    <Route path="cover-letters" element={<CoverLetters />} />
                    <Route path="profile" element={<Profile />} />
                    <Route path="settings" element={<Settings />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}
