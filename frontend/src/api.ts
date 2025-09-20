import { decodeJwt } from 'jose'

export class ApiClient {
  private base: string
  constructor(base = '') { this.base = base }

  private get auth() {
    const raw = localStorage.getItem('auth:user')
    return raw ? JSON.parse(raw) as { token?: string; refreshToken?: string; role?: string; username?: string } : null
  }

  private isExpired(token?: string) {
    if (!token) return true
    try {
      const payload: any = decodeJwt(token)
      if (!payload?.exp) return true
      const now = Math.floor(Date.now() / 1000)
      return payload.exp <= now + 10 // margen 10s
    } catch {
      return true
    }
  }

  private async refreshIfNeeded() {
    const a = this.auth
    if (!a) return
    if (!this.isExpired(a.token)) return
    if (!a.refreshToken) return
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: a.refreshToken, role: a.role })
    })
    if (res.ok) {
      const data = await res.json()
      const next = { ...a, token: data.data?.access_token }
      localStorage.setItem('auth:user', JSON.stringify(next))
    } else {
      // limpiar sesión si refresh falla
      localStorage.removeItem('auth:user')
    }
  }

  async request(path: string, init: RequestInit = {}) {
    await this.refreshIfNeeded()
    const a = this.auth
    const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(init.headers as any || {}) }
    if (a?.token) headers.Authorization = `Bearer ${a.token}`
    const res = await fetch(`${this.base}${path}`, { ...init, headers })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
  }
}

export const api = new ApiClient('')

// API v2 para funcionalidades de IA
export class AIApiClient {
  private base: string
  constructor(base = '') { this.base = base }

  private get auth() {
    const raw = localStorage.getItem('auth:user')
    return raw ? JSON.parse(raw) as { token?: string; refreshToken?: string; role?: string; username?: string } : null
  }

  private isExpired(token?: string) {
    if (!token) return true
    try {
      const payload: any = decodeJwt(token)
      if (!payload?.exp) return true
      const now = Math.floor(Date.now() / 1000)
      return payload.exp <= now + 10 // margen 10s
    } catch {
      return true
    }
  }

  private async refreshIfNeeded() {
    const a = this.auth
    if (!a) return
    if (!this.isExpired(a.token)) return
    if (!a.refreshToken) return
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: a.refreshToken, role: a.role })
    })
    if (res.ok) {
      const data = await res.json()
      const next = { ...a, token: data.data?.access_token }
      localStorage.setItem('auth:user', JSON.stringify(next))
    } else {
      localStorage.removeItem('auth:user')
    }
  }

  async request(path: string, init: RequestInit = {}) {
    await this.refreshIfNeeded()
    const a = this.auth
    const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(init.headers as any || {}) }
    if (a?.token) headers.Authorization = `Bearer ${a.token}`
    const res = await fetch(`${this.base}${path}`, { ...init, headers })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
  }

  // Funciones específicas de IA
  async semanticSearch(query: string, limit: number = 10) {
    return this.request('/api/v2/ai/search/semantic', {
      method: 'POST',
      body: JSON.stringify({ query, limit })
    })
  }

  async getRecommendations(productId: number, limit: number = 5) {
    return this.request(`/api/v2/ai/products/${productId}/recommendations?limit=${limit}`)
  }

  async getSearchSuggestions(query: string, limit: number = 10) {
    return this.request(`/api/v2/ai/search/suggestions?q=${encodeURIComponent(query)}&limit=${limit}`)
  }

  async getAIStats() {
    return this.request('/api/v2/ai/stats')
  }

  async getAIHealth() {
    return this.request('/api/v2/ai/health')
  }
}

export const aiApi = new AIApiClient('')


