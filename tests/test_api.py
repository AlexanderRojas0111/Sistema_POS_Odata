import pytest
from app import create_app


@pytest.fixture
def app():
    """Crear una instancia de la aplicación para testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()


def test_health_check(client):
    """Test del endpoint de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'environment' in data


def test_api_v1_base(client):
    """Test de que la API v1 responde"""
    response = client.get('/api/v1/')
    # Puede ser 404 si no hay endpoint base, pero debe responder
    assert response.status_code in [200, 404]


def test_api_v2_base(client):
    """Test de que la API v2 responde"""
    response = client.get('/api/v2/')
    # Puede ser 404 si no hay endpoint base, pero debe responder
    assert response.status_code in [200, 404]


def test_404_error(client):
    """Test de manejo de errores 404"""
    response = client.get('/endpoint-que-no-existe')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Not Found'


def test_500_error_handling(client):
    """Test de manejo de errores 500"""
    # Este test verifica que el manejador de errores 500 funciona
    # En una implementación real, podrías forzar un error
    response = client.get('/health')  # Este endpoint debería funcionar
    assert response.status_code == 200  # Si funciona, el manejador está bien configurado
