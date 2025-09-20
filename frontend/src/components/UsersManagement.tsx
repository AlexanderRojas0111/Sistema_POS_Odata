import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Edit, 
  Trash2, 
  Search, 
  Filter,
  Users,
  User
  ShieldOff,
  CheckCircle,
  X,
  Save,
  AlertTriangle,
  Mail
  Lock} from 'lucide-react';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

interface UserFormData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
}

const UsersManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'cashier',
    is_active: true
  });

  const roles = [
    { value: 'admin', label: 'Administrador', color: 'bg-red-100 text-red-800' },
    { value: 'manager', label: 'Gerente', color: 'bg-orange-100 text-orange-800' },
    { value: 'cashier', label: 'Cajero', color: 'bg-blue-100 text-blue-800' },
    { value: 'staff', label: 'Personal', color: 'bg-green-100 text-green-800' }
  ];

  const roleFilters = ['all', ...roles.map(r => r.value)];

  // Obtener token de autenticación
  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  // Headers de autenticación
  const getHeaders = () => {
    const token = getAuthToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  // Cargar usuarios
  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/users', {
        headers: getHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.data?.users || []);
      } else {
        setError('Error cargando usuarios');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // Filtrar usuarios
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = selectedRole === 'all' || user.role === selectedRole;
    return matchesSearch && matchesRole;
  });

  // Abrir modal para nuevo usuario
  const handleNewUser = () => {
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'cashier',
      is_active: true
    });
    setShowModal(true);
  };

  // Abrir modal para editar usuario
  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // No mostrar password existente
      first_name: user.first_name,
      last_name: user.last_name,
      role: user.role,
      is_active: user.is_active
    });
    setShowModal(true);
  };

  // Guardar usuario
  const handleSaveUser = async () => {
    try {
      const url = editingUser 
        ? `http://localhost:8000/api/v1/users/${editingUser.id}`
        : 'http://localhost:8000/api/v1/users';
      
      const method = editingUser ? 'PUT' : 'POST';
      
      // Preparar datos (no enviar password vacío en edición)
      const submitData = { ...formData };
      if (editingUser && !submitData.password) {
        delete submitData.password;
      }
      
      const response = await fetch(url, {
        method,
        headers: getHeaders(),
        body: JSON.stringify(submitData)
      });

      if (response.ok) {
        await loadUsers();
        setShowModal(false);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Error guardando usuario');
      }
    } catch (err) {
      setError('Error de conexión');
    }
  };

  // Eliminar usuario
  const handleDeleteUser = async (user: User) => {
    if (user.role === 'admin') {
      setError('No se puede eliminar un usuario administrador');
      return;
    }

    if (!confirm(`¿Estás seguro de eliminar el usuario "${user.username}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/users/${user.id}`, {
        method: 'DELETE',
        headers: getHeaders()
      });

      if (response.ok) {
        await loadUsers();
      } else {
        setError('Error eliminando usuario');
      }
    } catch (err) {
      setError('Error de conexión');
    }
  };

  // Toggle estado activo
  const handleToggleActive = async (user: User) => {
    if (user.role === 'admin') {
      setError('No se puede desactivar un usuario administrador');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/users/${user.id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({
          ...user,
          is_active: !user.is_active
        })
      });

      if (response.ok) {
        await loadUsers();
      } else {
        setError('Error actualizando usuario');
      }
    } catch (err) {
      setError('Error de conexión');
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Nunca';
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRoleInfo = (role: string) => {
    return roles.find(r => r.value === role) || { value: role, label: role, color: 'bg-gray-100 text-gray-800' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando usuarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
              <p className="text-gray-600 mt-1">Administra usuarios y permisos del sistema</p>
            </div>
            <button
              onClick={handleNewUser}
              className="btn-primary flex items-center space-x-2"
            >
              <UserclassName="w-5 h-5" />
              <span>Nuevo Usuario</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y búsqueda */}
        <div className="bg-white rounded-xl shadow-amber p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar usuarios..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field pl-10"
              />
            </div>
            <div className="relative">
              <Filter className="w-5 h-5 absolute left-3 top-3 text-gray-400" />
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="input-field pl-10"
              >
                {roleFilters.map(role => (
                  <option key={role} value={role}>
                    {role === 'all' ? 'Todos los roles' : roles.find(r => r.value === role)?.label || role}
                  </option>
                ))}
              </select>
            </div>
            <div className="text-sm text-gray-600 flex items-center">
              <Users className="w-4 h-4 mr-2" />
              {filteredUsers.length} usuarios encontrados
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3"
          >
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}

        {/* Tabla de usuarios */}
        <div className="bg-white rounded-xl shadow-amber overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Último Acceso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user, index) => {
                  const roleInfo = getRoleInfo(user.role);
                  return (
                    <motion.tr
                      key={user.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-amber rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">
                              {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.first_name} {user.last_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              @{user.username}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${roleInfo.color}`}>
                          <Shield className="w-3 h-3 mr-1" />
                          {roleInfo.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleToggleActive(user)}
                          disabled={user.role === 'admin'}
                          className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${
                            user.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          } ${user.role === 'admin' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          {user.is_active ? (
                            <>
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Activo
                            </>
                          ) : (
                            <>
                              <X className="w-3 h-3 mr-1" />
                              Inactivo
                            </>
                          )}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEditUser(user)}
                            className="text-sabrositas-primary hover:text-sabrositas-accent"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          {user.role !== 'admin' && (
                            <button
                              onClick={() => handleDeleteUser(user)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal de usuario */}
        <AnimatePresence>
          {showModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
              onClick={(e) => e.target === e.currentTarget && setShowModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white rounded-2xl shadow-amber-lg max-w-2xl w-full max-h-[90vh] overflow-hidden"
              >
                {/* Header */}
                <div className="bg-gradient-amber text-white p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <UserclassName="w-6 h-6" />
                      <div>
                        <h2 className="text-2xl font-bold">
                          {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
                        </h2>
                        <p className="text-amber-100">
                          {editingUser ? 'Modifica la información del usuario' : 'Agrega un nuevo usuario al sistema'}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowModal(false)}
                      className="text-white hover:text-amber-200 transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>

                {/* Form */}
                <div className="p-6 max-h-[60vh] overflow-y-auto">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username *
                      </label>
                      <input
                        type="text"
                        value={formData.username}
                        onChange={(e) => setFormData({...formData, username: e.target.value})}
                        className="input-field"
                        placeholder="usuario123"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email *
                      </label>
                      <div className="relative">
                        <Mail className="w-5 h-5 absolute left-3 top-3 text-gray-400" />
                        <input
                          type="email"
                          value={formData.email}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                          className="input-field pl-10"
                          placeholder="usuario@ejemplo.com"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre *
                      </label>
                      <input
                        type="text"
                        value={formData.first_name}
                        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                        className="input-field"
                        placeholder="Juan"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Apellido *
                      </label>
                      <input
                        type="text"
                        value={formData.last_name}
                        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                        className="input-field"
                        placeholder="Pérez"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contraseña {editingUser ? '' : '*'}
                      </label>
                      <div className="relative">
                        <Lock className="w-5 h-5 absolute left-3 top-3 text-gray-400" />
                        <input
                          type="password"
                          value={formData.password}
                          onChange={(e) => setFormData({...formData, password: e.target.value})}
                          className="input-field pl-10"
                          placeholder={editingUser ? "Dejar vacío para mantener actual" : "mínimo 6 caracteres"}
                          required={!editingUser}
                        />
                      </div>
                      {editingUser && (
                        <p className="text-xs text-gray-500 mt-1">
                          Dejar vacío para mantener la contraseña actual
                        </p>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rol *
                      </label>
                      <select
                        value={formData.role}
                        onChange={(e) => setFormData({...formData, role: e.target.value})}
                        className="input-field"
                      >
                        {roles.map(role => (
                          <option key={role.value} value={role.value}>{role.label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="md:col-span-2">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.is_active}
                          onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                          className="rounded border-gray-300 text-sabrositas-primary focus:ring-sabrositas-primary"
                        />
                        <span className="text-sm font-medium text-gray-700">
                          Usuario activo
                        </span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-gray-50 border-t flex justify-end space-x-3">
                  <button
                    onClick={() => setShowModal(false)}
                    className="btn-secondary"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSaveUser}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>{editingUser ? 'Actualizar' : 'Crear'}</span>
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default UsersManagement;
