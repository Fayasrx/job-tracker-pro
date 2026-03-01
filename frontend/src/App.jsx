import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import JobFeed from './pages/JobFeed'
import JobDetailPage from './pages/JobDetailPage'
import Applications from './pages/Applications'
import Notifications from './pages/Notifications'
import Companies from './pages/Companies'
import CoverLetters from './pages/CoverLetters'
import Profile from './pages/Profile'
import Settings from './pages/Settings'

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
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
