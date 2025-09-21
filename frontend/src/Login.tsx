import { useState, type FormEvent } from 'react'
import { useAuth } from './authSimple'

export default function Login() {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      setError(null)
      await login(username, password)
      window.location.href = '/'
    } catch (err: any) {
      setError(err?.message ?? 'Error de autenticación')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h2>Iniciar sesión</h2>
      <form onSubmit={onSubmit} className="card form">
        <label>
          Usuario
          <input value={username} onChange={e => setUsername(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={loading}>{loading ? 'Accediendo...' : 'Entrar'}</button>
      </form>
      <div className="hint">
        <p>Usuarios del Sistema:</p>
        <ul>
          <li>superadmin / SuperAdmin123!</li>
          <li>globaladmin / Global123!</li>
          <li>storeadmin1 / Store123!</li>
          <li>techadmin / TechAdmin123!</li>
        </ul>
      </div>
    </div>
  )
}

