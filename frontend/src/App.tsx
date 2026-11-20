import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './components/common/AuthProvider'
import { NotificationProvider } from './components/common/NotificationProvider'
import { RequireAuth } from './components/common/RequireAuth'
import { Layout } from './components/layout/Layout'
import { Departments } from './pages/Departments'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { CompetenciesList } from './pages/competencies/CompetenciesList'
import { CompetencyForm } from './pages/competencies/CompetencyForm'
import { PlanRecord } from './pages/plans/PlanRecord'
import { PlansList } from './pages/plans/PlansList'

export default function App() {
  return (
    <BrowserRouter>
      <NotificationProvider>
        <AuthProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="login" element={<Login />} />
              <Route element={<RequireAuth />}>
                <Route path="development-plans" element={<PlansList />} />
                <Route path="development-plans/new" element={<PlanRecord mode="form" />} />
                <Route path="development-plans/:id" element={<PlanRecord mode="details" />} />
                <Route path="development-plans/:id/edit" element={<PlanRecord mode="form" />} />
                <Route path="competencies" element={<CompetenciesList />} />
                <Route path="competencies/new" element={<CompetencyForm />} />
                <Route path="competencies/:id/edit" element={<CompetencyForm />} />
                <Route path="departments" element={<Departments />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </AuthProvider>
      </NotificationProvider>
    </BrowserRouter>
  )
}
