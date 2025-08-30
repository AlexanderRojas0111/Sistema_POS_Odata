# 🤝 Guía de Contribución - Sistema POS O'data

¡Gracias por tu interés en contribuir al Sistema POS O'data! Este documento te guiará a través del proceso de contribución.

## 📋 **Tabla de Contenidos**

- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Features](#solicitar-features)
- [Preguntas Frecuentes](#preguntas-frecuentes)

## 🚀 **Cómo Contribuir**

### **Tipos de Contribuciones**

- 🐛 **Reportar bugs** - Ayuda a mejorar la estabilidad
- 💡 **Solicitar features** - Sugiere nuevas funcionalidades
- 📝 **Mejorar documentación** - Ayuda a otros desarrolladores
- 🔧 **Arreglar bugs** - Contribuye directamente al código
- ✨ **Implementar features** - Agrega nuevas funcionalidades
- 🧪 **Mejorar tests** - Aumenta la calidad del código
- 🌐 **Traducciones** - Ayuda con la internacionalización

### **Antes de Empezar**

1. **Revisa los issues existentes** para evitar duplicados
2. **Lee la documentación** del proyecto
3. **Únete a las discusiones** en GitHub Discussions
4. **Familiarízate con el código** existente

## 🛠️ **Configuración del Entorno**

### **1. Fork y Clone**

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/Sistema_POS_Odata.git
cd Sistema_POS_Odata

# Agrega el repositorio original como upstream
git remote add upstream https://github.com/original/Sistema_POS_Odata.git
```

### **2. Configurar Entorno de Desarrollo**

```bash
# Crear entorno virtual
python -m venv venv_pos
venv_pos\Scripts\activate  # Windows
source venv_pos/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo

# Configurar pre-commit hooks
pre-commit install
```

### **3. Configurar Frontend**

```bash
cd frontend
npm install
npm run build:dev
```

## 📏 **Estándares de Código**

### **Python (Backend)**

- **PEP 8** - Estilo de código Python
- **Black** - Formateo automático
- **Flake8** - Linting
- **MyPy** - Verificación de tipos
- **Docstrings** - Documentación de funciones

```python
def calculate_total(items: List[Product]) -> float:
    """
    Calcula el total de una lista de productos.
    
    Args:
        items: Lista de productos a calcular
        
    Returns:
        float: Total calculado
        
    Raises:
        ValueError: Si la lista está vacía
    """
    if not items:
        raise ValueError("La lista de productos no puede estar vacía")
    
    return sum(item.price for item in items)
```

### **JavaScript/React (Frontend)**

- **ESLint** - Linting de JavaScript
- **Prettier** - Formateo de código
- **PropTypes** - Validación de props
- **Hooks** - Usar hooks de React modernos

```jsx
import React from 'react';
import PropTypes from 'prop-types';

const ProductCard = ({ product, onAddToCart }) => {
  const { name, price, description } = product;
  
  return (
    <div className="product-card">
      <h3>{name}</h3>
      <p>{description}</p>
      <span className="price">${price}</span>
      <button onClick={() => onAddToCart(product)}>
        Agregar al Carrito
      </button>
    </div>
  );
};

ProductCard.propTypes = {
  product: PropTypes.shape({
    name: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
  }).isRequired,
  onAddToCart: PropTypes.func.isRequired,
};

export default ProductCard;
```

### **Base de Datos**

- **SQLAlchemy** - ORM para Python
- **Migrations** - Usar Alembic para cambios de BD
- **Constraints** - Definir restricciones apropiadas
- **Indexes** - Optimizar consultas frecuentes

### **Testing**

- **Cobertura mínima**: 80%
- **Pruebas unitarias** para toda nueva funcionalidad
- **Pruebas de integración** para APIs
- **Pruebas de frontend** con Playwright

```python
def test_calculate_total():
    """Prueba el cálculo del total de productos."""
    items = [
        Product(name="Test1", price=10.0),
        Product(name="Test2", price=20.0)
    ]
    
    total = calculate_total(items)
    assert total == 30.0

def test_calculate_total_empty_list():
    """Prueba que se lance error con lista vacía."""
    with pytest.raises(ValueError, match="no puede estar vacía"):
        calculate_total([])
```

## 🔄 **Proceso de Pull Request**

### **1. Crear una Rama**

```bash
# Actualizar tu fork
git fetch upstream
git checkout main
git merge upstream/main

# Crear rama para tu feature
git checkout -b feature/nombre-del-feature
```

### **2. Desarrollar tu Feature**

- **Escribe código limpio** siguiendo los estándares
- **Agrega tests** para nueva funcionalidad
- **Actualiza documentación** si es necesario
- **Mantén commits pequeños** y descriptivos

```bash
# Hacer commits frecuentes
git add .
git commit -m "feat: agregar funcionalidad de búsqueda avanzada

- Implementar búsqueda por categoría
- Agregar filtros de precio
- Incluir tests unitarios
- Actualizar documentación de API"
```

### **3. Ejecutar Pruebas**

```bash
# Ejecutar todas las pruebas
python run_tests.py --all

# Verificar cobertura
pytest --cov=app --cov-report=html

# Verificar calidad del código
flake8 app/
black --check app/
mypy app/
```

### **4. Crear Pull Request**

1. **Push tu rama** a tu fork
2. **Crear Pull Request** en GitHub
3. **Usar template** de PR
4. **Describir cambios** claramente
5. **Referenciar issues** relacionados

### **Template de Pull Request**

```markdown
## 📝 Descripción

Breve descripción de los cambios realizados.

## 🔗 Issues Relacionados

Closes #123
Relates to #456

## 🧪 Cambios Realizados

- [ ] Nueva funcionalidad
- [ ] Bug fix
- [ ] Mejora de documentación
- [ ] Refactoring de código
- [ ] Mejora de tests

## 📋 Checklist

- [ ] Código sigue los estándares del proyecto
- [ ] Tests pasan localmente
- [ ] Cobertura de código > 80%
- [ ] Documentación actualizada
- [ ] No hay conflictos de merge

## 🖼️ Screenshots (si aplica)

## 📊 Métricas

- Cobertura de código: X%
- Tests ejecutados: X
- Tiempo de build: Xs
```

## 🐛 **Reportar Bugs**

### **Template de Bug Report**

```markdown
## 🐛 Descripción del Bug

Descripción clara y concisa del bug.

## 🔄 Pasos para Reproducir

1. Ir a '...'
2. Hacer click en '...'
3. Scroll hasta '...'
4. Ver error

## ✅ Comportamiento Esperado

Descripción de lo que debería pasar.

## 📱 Información del Sistema

- OS: [e.g. Windows 10, macOS 11.0]
- Browser: [e.g. Chrome 91, Firefox 89]
- Versión: [e.g. 2.0.0]

## 📋 Información Adicional

Capturas de pantalla, logs, etc.
```

## 💡 **Solicitar Features**

### **Template de Feature Request**

```markdown
## 💡 Descripción del Feature

Descripción clara del feature solicitado.

## 🎯 Caso de Uso

Explicar cuándo y por qué sería útil este feature.

## 🔧 Solución Propuesta

Descripción de cómo implementar el feature.

## 📋 Alternativas Consideradas

Otras soluciones que se consideraron.

## 📱 Información Adicional

Capturas de pantalla, mockups, etc.
```

## ❓ **Preguntas Frecuentes**

### **¿Cómo empiezo a contribuir?**

1. **Fork el repositorio**
2. **Clona tu fork**
3. **Configura el entorno**
4. **Elige un issue** marcado como "good first issue"
5. **Crea una rama** y empieza a trabajar

### **¿Qué hago si encuentro un bug?**

1. **Busca en issues existentes** si ya fue reportado
2. **Si no existe**, crea un nuevo issue
3. **Usa el template** de bug report
4. **Proporciona información** detallada

### **¿Cómo puedo ayudar sin escribir código?**

- **Reportar bugs** que encuentres
- **Mejorar documentación**
- **Traducir** a otros idiomas
- **Ayudar en issues** de otros usuarios
- **Compartir** el proyecto

### **¿Qué hago si mi PR no es aceptado?**

- **Revisa los comentarios** del reviewer
- **Haz los cambios** sugeridos
- **Responde** a los comentarios
- **No te desanimes** - es parte del proceso

## 📞 **Obtener Ayuda**

- **GitHub Issues**: Para bugs y features
- **GitHub Discussions**: Para preguntas generales
- **Documentación**: Revisa la carpeta `docs/`
- **Código**: Lee el código fuente y comentarios

## 🎉 **Reconocimientos**

- **Contribuidores** serán listados en el README
- **Badges** para contribuidores activos
- **Menciones** en releases
- **Acceso** a repositorios internos

---

**¡Gracias por contribuir al Sistema POS O'data! 🚀**

Tu contribución ayuda a hacer este proyecto mejor para todos.
