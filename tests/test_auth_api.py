"""
Tests para API de Autenticación v1 - Integrado desde análisis GitHub
"""

import pytest
import json
from app import create_app
from app.core.database import db

@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Headers con token de autenticación"""
    # Login para obtener token
    response = client.post('/api/v1/auth/login', 
                          json={'username': 'admin', 'password': 'admin'})
    data = json.loads(response.data)
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}

class TestAuthAPI:
    """Suite de pruebas para autenticación"""
    
    def test_login_successful(self, client):
        """Test: Login exitoso"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'admin', 'password': 'admin'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'admin'
        assert data['message'] == 'Login exitoso'
    
    def test_login_invalid_credentials(self, client):
        """Test: Login con credenciales inválidas"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'admin', 'password': 'wrong'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Credenciales inválidas'
    
    def test_login_missing_data(self, client):
        """Test: Login sin datos requeridos"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'admin'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'username y password' in data['error']
    
    def test_login_no_json(self, client):
        """Test: Login sin datos JSON"""
        response = client.post('/api/v1/auth/login')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'datos JSON' in data['error']
    
    def test_get_profile_authenticated(self, client, auth_headers):
        """Test: Obtener perfil con autenticación"""
        response = client.get('/api/v1/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'user' in data
        assert data['user']['username'] == 'admin'
        assert data['user']['role'] == 'admin'
        assert 'permissions' in data['user']
        assert isinstance(data['user']['permissions'], list)
    
    def test_get_profile_unauthenticated(self, client):
        """Test: Obtener perfil sin autenticación"""
        response = client.get('/api/v1/auth/profile')
        
        assert response.status_code == 401
    
    def test_validate_token_valid(self, client, auth_headers):
        """Test: Validar token válido"""
        response = client.get('/api/v1/auth/validate', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['valid'] is True
        assert data['user'] == 'admin'
        assert data['message'] == 'Token válido'
    
    def test_validate_token_invalid(self, client):
        """Test: Validar token inválido"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.get('/api/v1/auth/validate', headers=headers)
        
        assert response.status_code == 422  # JWT invalid format
    
    def test_logout_authenticated(self, client, auth_headers):
        """Test: Logout con autenticación"""
        response = client.post('/api/v1/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout exitoso'
    
    def test_logout_unauthenticated(self, client):
        """Test: Logout sin autenticación"""
        response = client.post('/api/v1/auth/logout')
        
        assert response.status_code == 401
    
    def test_refresh_token(self, client):
        """Test: Renovar token de acceso"""
        # Primero hacer login
        login_response = client.post('/api/v1/auth/login',
                                   json={'username': 'admin', 'password': 'admin'})
        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']
        
        # Usar refresh token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/v1/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data

class TestAuthIntegration:
    """Tests de integración para autenticación"""
    
    def test_auth_flow_complete(self, client):
        """Test: Flujo completo de autenticación"""
        # 1. Login
        login_response = client.post('/api/v1/auth/login',
                                   json={'username': 'admin', 'password': 'admin'})
        assert login_response.status_code == 200
        
        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']
        
        # 2. Usar token para acceder a recurso protegido
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = client.get('/api/v1/auth/profile', headers=headers)
        assert profile_response.status_code == 200
        
        # 3. Validar token
        validate_response = client.get('/api/v1/auth/validate', headers=headers)
        assert validate_response.status_code == 200
        
        # 4. Logout
        logout_response = client.post('/api/v1/auth/logout', headers=headers)
        assert logout_response.status_code == 200
    
    def test_auth_with_health_endpoint(self, client, auth_headers):
        """Test: Autenticación con endpoint de health"""
        # El health endpoint debería funcionar sin autenticación
        response = client.get('/health')
        assert response.status_code == 200
        
        # También debería funcionar con autenticación
        response = client.get('/health', headers=auth_headers)
        assert response.status_code == 200
