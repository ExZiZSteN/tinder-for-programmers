import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { AppLayout } from './components/layout/AppLayout'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import ProjectsPage from './pages/ProjectPage'
import CreateProjectPage from './pages/CreateProjectPage'
import EditProjectPage from './pages/EditProjectPage'
import AdminPage from './pages/AdminPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import MatchesPage from './pages/MatchesPage'
import FeedPage from './pages/FeedPage'
import InboxPage from './pages/InboxPage'
import ChatPage from './pages/ChatPage'
import ProjectChatPage from './pages/ProjectChatPage'
import PublicProfilePage from './pages/PublicProfilePage'

// Protected Route
const ProtectedRoute = ({ children, requireAdmin = false }: { children: React.ReactNode, requireAdmin?: boolean }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (requireAdmin && user?.user_role !== 'admin'){
    return <Navigate to='/feed' replace />
  }

  return <AppLayout>{children}</AppLayout>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route
          path="/feed"
          element={
            <ProtectedRoute>
              <FeedPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/matches"
          element={
            <ProtectedRoute>
              <MatchesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/users/:id"
          element={
            <ProtectedRoute>
              <PublicProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <ProjectsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/create"
          element={
            <ProtectedRoute>
              <CreateProjectPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:id/edit"
          element={
            <ProtectedRoute>
              <EditProjectPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:id"
          element={
            <ProtectedRoute>
              <ProjectDetailPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/inbox"
          element={
            <ProtectedRoute>
              <InboxPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/matches/:matchId/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/projects/:projectId/chat"
          element={
            <ProtectedRoute>
              <ProjectChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          } 
        />
        {/* Redirect */}
        <Route path="/" element={<Navigate to="/feed" replace />} />
        <Route path="*" element={<Navigate to="/feed" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App