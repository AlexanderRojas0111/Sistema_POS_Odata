import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute, RequireRole } from './auth'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import AdvancedDashboard from './components/AdvancedDashboard'
import ReportsManagementFixed from './components/ReportsManagementFixed'
import PayrollManagement from './components/PayrollManagement'
import AccountsReceivableManagement from './components/AccountsReceivableManagement'
import SalesModule from './components/SalesModule'
import InventoryManagement from './components/InventoryManagement'

export const router = createBrowserRouter([
  { 
    path: '/login', 
    element: <Login /> 
  },
  {
    path: '/',
    element: <ProtectedRoute><Dashboard /></ProtectedRoute>
  },
  {
    path: '/dashboard',
    element: <ProtectedRoute><Dashboard /></ProtectedRoute>
  },
  {
    path: '/analytics',
    element: <ProtectedRoute><AdvancedDashboard /></ProtectedRoute>
  },
  {
    path: '/reports',
    element: <ProtectedRoute><ReportsManagementFixed /></ProtectedRoute>
  },
  {
    path: '/payroll',
    element: <RequireRole role="manager"><PayrollManagement /></RequireRole>
  },
  {
    path: '/accounts-receivable',
    element: <RequireRole role="manager"><AccountsReceivableManagement /></RequireRole>
  },
  {
    path: '/sales',
    element: <RequireRole role="cashier"><SalesModule /></RequireRole>
  },
  {
    path: '/inventory',
    element: <RequireRole role="cashier"><InventoryManagement /></RequireRole>
  },
  {
    path: '/settings',
    element: <RequireRole role="store_admin"><Dashboard /></RequireRole>
  },
  {
    path: '/reports',
    element: <RequireRole role="cashier"><Dashboard /></RequireRole>
  }
], {
  future: {
    v7_startTransition: true
  }
})

