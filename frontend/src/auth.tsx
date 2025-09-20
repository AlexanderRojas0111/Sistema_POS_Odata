import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

type Role = 'super_admin' | 'tech_admin' | 'global_admin' | 'store_admin' | 'admin' | 'manager' | 'cashier'

interface AuthUser {
  id: number
  username: string
  role: Role
  token: string
  refreshToken?: string
}

interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  hasRole: (required: Role) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null)

  useEffect(() => {
    const raw = localStorage.getItem('auth:user')
    if (raw) setUser(JSON.parse(raw))
  }, [])

  const login = async (username: string, password: string) => {
    // Login contra API
    const res = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (!res.ok) throw new Error('Credenciales inválidas')
    const data = await res.json()
    const authUser: AuthUser = {
      id: data.data?.user_id ?? 0,
      username: data.data?.username ?? username,
      role: (data.data?.role ?? 'cashier') as Role,
      token: data.data?.access_token ?? data.token ?? '',
      refreshToken: data.data?.refresh_token
    }
    setUser(authUser)
    localStorage.setItem('auth:user', JSON.stringify(authUser))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('auth:user')
  }

  const hasRole = (required: Role) => {
    const weights: Record<Role, number> = { 
      cashier: 1, 
      manager: 2, 
      admin: 3,
      store_admin: 4,
      global_admin: 5,
      tech_admin: 6,
      super_admin: 7
    }
    const current = user ? weights[user.role] : 0
    return current >= weights[required]
  }

  const value = useMemo(() => ({ 
    user, 
    isAuthenticated: !!user, 
    login, 
    logout, 
    hasRole 
  }), [user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export const RequireRole: React.FC<{ role: Role; children: React.ReactNode }> = ({ role, children }) => {
  const { user, hasRole } = useAuth()
  if (!user) return <p>Debes iniciar sesión</p>
  if (!hasRole(role)) return <p>No autorizado</p>
  return <>{children}</>
}

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth()
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Sistema POS O'Data</h1>
          <p className="text-gray-600 mb-6">Acceso no autorizado</p>
          <a 
            href="/login"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Iniciar Sesión
          </a>
        </div>
      </div>
    )
  }
  return <>{children}</>
}


