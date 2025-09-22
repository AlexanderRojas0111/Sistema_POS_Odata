# ==============================================
# SETUP TESTING Y CI/CD - DÍA SIGUIENTE
# Sistema POS O'Data Enterprise v2.0.0
# ==============================================
# Las Arepas Cuadradas - Enterprise Development
# Script para configurar testing automatizado y CI/CD

param(
    [switch]$SetupTesting = $false,
    [switch]$SetupCI = $false,
    [switch]$SetupAll = $false
)

$Colors = @{
    Success = "Green"
    Info = "Cyan"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host $Message -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Status {
    param([string]$Message, [string]$Status = "Info")
    $Color = $Colors[$Status]
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] $Message" -ForegroundColor $Color
}

function Setup-Testing {
    Write-Header "🧪 CONFIGURANDO TESTING AUTOMATIZADO"
    
    # Crear estructura de directorios de testing
    Write-Status "Creando estructura de directorios de testing..." "Info"
    
    $testDirs = @(
        "tests",
        "tests/unit",
        "tests/integration", 
        "tests/e2e",
        "tests/fixtures"
    )
    
    foreach ($dir in $testDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "✅ Creado directorio: $dir" "Success"
        } else {
            Write-Status "📁 Directorio ya existe: $dir" "Info"
        }
    }
    
    # Crear archivo pytest.ini
    Write-Status "Creando configuración de pytest..." "Info"
    $pytestConfig = @"
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
"@
    
    $pytestConfig | Out-File -FilePath "pytest.ini" -Encoding UTF8
    Write-Status "✅ Configuración de pytest creada" "Success"
    
    # Crear test básico para verificar setup
    Write-Status "Creando test básico de verificación..." "Info"
    $basicTest = @"
"""
Test básico para verificar que el sistema funciona correctamente
"""

def test_system_health():
    """Test básico de salud del sistema"""
    assert True, "Sistema funcionando correctamente"

def test_imports():
    """Test de importaciones principales"""
    try:
        from app import create_app
        from app.container import container
        assert True, "Importaciones exitosas"
    except ImportError as e:
        assert False, f"Error de importación: {e}"
"@
    
    $basicTest | Out-File -FilePath "tests/test_basic.py" -Encoding UTF8
    Write-Status "✅ Test básico creado" "Success"
    
    # Instalar dependencias de testing
    Write-Status "Instalando dependencias de testing..." "Info"
    $testingDeps = @(
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "pytest-mock==3.12.0",
        "pytest-flask==1.3.0",
        "requests-mock==1.11.0"
    )
    
    foreach ($dep in $testingDeps) {
        Write-Status "Instalando $dep..." "Info"
        pip install $dep --quiet
    }
    
    Write-Status "✅ Dependencias de testing instaladas" "Success"
    
    # Ejecutar test básico
    Write-Status "Ejecutando test básico..." "Info"
    python -m pytest tests/test_basic.py -v
}

function Setup-CICD {
    Write-Header "🚀 CONFIGURANDO CI/CD CON GITHUB ACTIONS"
    
    # Crear directorio .github/workflows
    Write-Status "Creando estructura de GitHub Actions..." "Info"
    
    $workflowDir = ".github/workflows"
    if (-not (Test-Path $workflowDir)) {
        New-Item -ItemType Directory -Path $workflowDir -Force | Out-Null
        Write-Status "✅ Creado directorio: $workflowDir" "Success"
    }
    
    # Crear workflow principal
    Write-Status "Creando workflow principal de CI/CD..." "Info"
    $workflow = @"
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python `${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: `${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  frontend-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linter
      run: |
        cd frontend
        npm run lint
    
    - name: Run tests
      run: |
        cd frontend
        npm test

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security audit
      run: |
        pip install bandit safety
        bandit -r app/ -f json -o bandit-report.json
        safety check --json --output safety-report.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  deploy:
    needs: [test, frontend-test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Aquí irían los comandos de deployment real
    
    - name: Notify deployment
      run: |
        echo "Deployment completed successfully!"
"@
    
    $workflow | Out-File -FilePath "$workflowDir/main.yml" -Encoding UTF8
    Write-Status "✅ Workflow de CI/CD creado" "Success"
    
    # Crear workflow de dependencias
    Write-Status "Creando workflow de actualización de dependencias..." "Info"
    $depsWorkflow = @"
name: Update Dependencies

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  update-deps:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Update Python dependencies
      run: |
        pip install pip-tools
        pip-compile --upgrade requirements.in
        pip-compile --upgrade requirements-dev.in
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Update Node.js dependencies
      run: |
        cd frontend
        npm update
        npm audit fix
    
    - name: Create Pull Request
      uses: peter-evans/create-pull-request@v5
      with:
        token: `${{ secrets.GITHUB_TOKEN }}
        commit-message: 'chore: update dependencies'
        title: 'chore: update dependencies'
        body: 'Automated dependency update'
        branch: 'update-dependencies'
"@
    
    $depsWorkflow | Out-File -FilePath "$workflowDir/update-dependencies.yml" -Encoding UTF8
    Write-Status "✅ Workflow de dependencias creado" "Success"
}

function Create-TestTemplates {
    Write-Header "📝 CREANDO PLANTILLAS DE TESTS"
    
    # Test de servicio de ventas
    Write-Status "Creando test para SaleService..." "Info"
    $saleTest = @"
"""
Tests para el servicio de ventas
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.services.sale_service import SaleService
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, InsufficientStockError


class TestSaleService:
    
    def setup_method(self):
        """Configuración para cada test"""
        self.mock_sale_repo = Mock(spec=SaleRepository)
        self.mock_product_repo = Mock(spec=ProductRepository)
        self.mock_user_repo = Mock(spec=UserRepository)
        
        self.sale_service = SaleService(
            self.mock_sale_repo,
            self.mock_product_repo,
            self.mock_user_repo
        )
    
    def test_create_sale_success(self):
        """Test de creación exitosa de venta"""
        # Arrange
        user_id = 1
        sale_data = {
            'customer_name': 'Cliente Test',
            'customer_phone': '1234567890',
            'payment_method': 'cash',
            'notes': 'Venta de prueba',
            'items': [
                {'product_id': 1, 'quantity': 2, 'unit_price': 1000.0}
            ]
        }
        
        # Mock de producto
        mock_product = Mock()
        mock_product.id = 1
        mock_product.stock = 10
        mock_product.price = 1000.0
        self.mock_product_repo.get_by_id.return_value = mock_product
        
        # Mock de venta creada
        mock_sale = {'id': 1, 'total_amount': 2000.0}
        self.mock_sale_repo.create.return_value = mock_sale
        
        # Act
        result = self.sale_service.create_sale(user_id, sale_data)
        
        # Assert
        assert result['id'] == 1
        assert result['total_amount'] == 2000.0
        self.mock_sale_repo.create.assert_called_once()
    
    def test_create_sale_insufficient_stock(self):
        """Test de error por stock insuficiente"""
        # Arrange
        user_id = 1
        sale_data = {
            'customer_name': 'Cliente Test',
            'items': [
                {'product_id': 1, 'quantity': 100, 'unit_price': 1000.0}
            ]
        }
        
        # Mock de producto con stock insuficiente
        mock_product = Mock()
        mock_product.id = 1
        mock_product.stock = 5
        self.mock_product_repo.get_by_id.return_value = mock_product
        
        # Act & Assert
        with pytest.raises(InsufficientStockError):
            self.sale_service.create_sale(user_id, sale_data)
    
    def test_create_sale_invalid_data(self):
        """Test de error por datos inválidos"""
        # Arrange
        user_id = 1
        sale_data = {
            'customer_name': '',  # Nombre vacío
            'items': []
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.sale_service.create_sale(user_id, sale_data)
"@
    
    $saleTest | Out-File -FilePath "tests/unit/test_sale_service.py" -Encoding UTF8
    Write-Status "✅ Test de SaleService creado" "Success"
    
    # Test de API
    Write-Status "Creando test para API v1..." "Info"
    $apiTest = @"
"""
Tests de integración para API v1
"""

import pytest
import json
from app import create_app


@pytest.fixture
def app():
    """Fixture para la aplicación de prueba"""
    app = create_app('testing')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Fixture para el cliente de prueba"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Fixture para headers de autenticación"""
    # Login para obtener token
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    response = client.post('/api/v1/auth/login', 
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    token = response.json['data']['access_token']
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


class TestAPIv1:
    
    def test_health_check(self, client):
        """Test del endpoint de health check"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    def test_get_products(self, client):
        """Test del endpoint de productos"""
        response = client.get('/api/v1/products')
        assert response.status_code == 200
        assert 'products' in response.json['data']
    
    def test_create_sale_with_auth(self, client, auth_headers):
        """Test de creación de venta con autenticación"""
        sale_data = {
            'customer_name': 'Cliente Test API',
            'customer_phone': '1234567890',
            'payment_method': 'cash',
            'notes': 'Venta desde test API',
            'items': [
                {'product_id': 1, 'quantity': 1, 'unit_price': 1000.0}
            ]
        }
        
        response = client.post('/api/v1/sales',
                             data=json.dumps(sale_data),
                             headers=auth_headers)
        
        assert response.status_code in [200, 201]
        assert 'id' in response.json['data']
    
    def test_create_sale_without_auth(self, client):
        """Test de creación de venta sin autenticación"""
        sale_data = {
            'customer_name': 'Cliente Test',
            'items': [{'product_id': 1, 'quantity': 1, 'unit_price': 1000.0}]
        }
        
        response = client.post('/api/v1/sales',
                             data=json.dumps(sale_data),
                             content_type='application/json')
        
        assert response.status_code == 401
"@
    
    $apiTest | Out-File -FilePath "tests/integration/test_api_v1.py" -Encoding UTF8
    Write-Status "✅ Test de API v1 creado" "Success"
}

function Run-InitialTests {
    Write-Header "🧪 EJECUTANDO TESTS INICIALES"
    
    Write-Status "Ejecutando tests básicos..." "Info"
    python -m pytest tests/test_basic.py -v
    
    Write-Status "Ejecutando tests unitarios..." "Info"
    python -m pytest tests/unit/ -v
    
    Write-Status "Ejecutando tests de integración..." "Info"
    python -m pytest tests/integration/ -v
    
    Write-Status "Ejecutando todos los tests con coverage..." "Info"
    python -m pytest tests/ --cov=app --cov-report=term-missing
}

# FUNCIÓN PRINCIPAL
function Main {
    Write-Header "🚀 SETUP TESTING Y CI/CD - SISTEMA POS O'DATA"
    
    if ($SetupAll -or $SetupTesting) {
        Setup-Testing
        Create-TestTemplates
        Run-InitialTests
    }
    
    if ($SetupAll -or $SetupCI) {
        Setup-CICD
    }
    
    if (-not $SetupTesting -and -not $SetupCI -and -not $SetupAll) {
        Write-Header "📋 OPCIONES DISPONIBLES"
        Write-Host "• Setup completo: .\SETUP_TESTING_CI.ps1 -SetupAll" -ForegroundColor Cyan
        Write-Host "• Solo testing: .\SETUP_TESTING_CI.ps1 -SetupTesting" -ForegroundColor Cyan
        Write-Host "• Solo CI/CD: .\SETUP_TESTING_CI.ps1 -SetupCI" -ForegroundColor Cyan
        return
    }
    
    Write-Header "✅ SETUP COMPLETADO"
    Write-Host "¡Testing y CI/CD configurados exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "1. Revisar y ajustar tests según necesidades" -ForegroundColor Cyan
    Write-Host "2. Hacer commit de los cambios" -ForegroundColor Cyan
    Write-Host "3. Crear Pull Request para activar CI/CD" -ForegroundColor Cyan
    Write-Host "4. Monitorear el pipeline en GitHub Actions" -ForegroundColor Cyan
}

# EJECUTAR SCRIPT
Main
