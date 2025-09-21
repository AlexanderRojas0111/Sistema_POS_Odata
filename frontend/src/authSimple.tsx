import React, { createContext, useContext, useEffect, useState } from 'react'

// Sistema POS Sabrositas - AuthProvider Simplificado
// Versión estable sin conflictos de hooks
console.log('AuthProvider cargado desde authSimple.tsx')

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
    try {
      const raw = localStorage.getItem('auth:user')
      if (raw) {
        const parsedUser = JSON.parse(raw)
        setUser(parsedUser)
      }
    } catch (error) {
      console.warn('Error loading auth user:', error)
      localStorage.removeItem('auth:user')
    }
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      
      if (!res.ok) {
        throw new Error('Credenciales inválidas')
      }
      
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
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    try {
      localStorage.removeItem('auth:user')
    } catch (error) {
      console.warn('Error removing auth user:', error)
    }
  }

  const hasRole = (required: Role) => {
    if (!user) return false
    
    const weights: Record<Role, number> = { 
      cashier: 1, 
      manager: 2, 
      admin: 3,
      store_admin: 4,
      global_admin: 5,
      tech_admin: 6,
      super_admin: 7
    }
    
    const current = weights[user.role] || 0
    const requiredWeight = weights[required] || 0
    
    return current >= requiredWeight
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    hasRole
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    // Retornar valores por defecto en lugar de lanzar error
    return {
      user: null,
      isAuthenticated: false,
      login: async () => {},
      logout: () => {},
      hasRole: () => false
    }
  }
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
