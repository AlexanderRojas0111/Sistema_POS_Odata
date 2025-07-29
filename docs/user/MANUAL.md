# Manual de Usuario - Sistema POS con IA

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Punto de Venta (POS)](#punto-de-venta-pos)
4. [Gestión de Inventario](#gestión-de-inventario)
5. [Reportes de Ventas](#reportes-de-ventas)
6. [Búsqueda Inteligente](#búsqueda-inteligente)
7. [Configuración](#configuración)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

El **Sistema POS con IA** es una solución completa de punto de venta que combina funcionalidades tradicionales con tecnologías avanzadas de inteligencia artificial para optimizar las operaciones de su negocio.

### Características Principales

- ✅ **Punto de Venta Intuitivo**: Interfaz moderna y fácil de usar
- ✅ **Búsqueda Semántica**: Encuentre productos por descripción natural
- ✅ **Gestión de Inventario**: Control automático de stock
- ✅ **Reportes Avanzados**: Análisis detallado de ventas
- ✅ **Agentes Inteligentes**: Monitoreo automático y alertas
- ✅ **Multiplataforma**: Funciona en PC, tablet y móvil

---

## 🔐 Acceso al Sistema

### 1. Inicio de Sesión

1. Abra su navegador web
2. Ingrese la URL del sistema: `http://localhost:3000`
3. Complete los campos:
   - **Usuario**: Su nombre de usuario
   - **Contraseña**: Su contraseña
4. Haga clic en "Iniciar Sesión"

### 2. Navegación Principal

El sistema cuenta con una barra de navegación superior que incluye:

- 🛒 **Punto de Venta**: Acceso directo al POS
- 📦 **Inventario**: Gestión de productos
- 📊 **Ventas**: Reportes y análisis
- ⚙️ **Configuración**: Ajustes del sistema

---

## 🛒 Punto de Venta (POS)

### Interfaz Principal

El POS está dividido en dos secciones principales:

#### Panel Izquierdo - Productos
- **Scanner de Códigos**: Escanee códigos de barras automáticamente
- **Entrada Manual**: Ingrese códigos manualmente
- **Lista de Productos**: Productos agregados al carrito

#### Panel Derecho - Totales
- **Resumen de Venta**: Subtotal, IVA y total
- **Botón Cobrar**: Procesar la venta
- **Ticket Generado**: Vista previa del ticket

### Proceso de Venta

#### 1. Agregar Productos

**Opción A - Scanner Automático:**
1. Active el scanner haciendo clic en "Activar Scanner"
2. Escanee el código de barras del producto
3. El producto se agregará automáticamente al carrito

**Opción B - Entrada Manual:**
1. En el campo "Código de producto", ingrese el código
2. Presione Enter o haga clic en "Agregar"
3. El producto se agregará al carrito

#### 2. Modificar Cantidades

- **Aumentar**: Haga clic en el botón "+" junto al producto
- **Disminuir**: Haga clic en el botón "-" junto al producto
- **Eliminar**: Haga clic en el ícono de papelera

#### 3. Procesar Venta

1. Verifique los productos en el carrito
2. Revise el total en el panel derecho
3. Haga clic en "Cobrar"
4. Seleccione el método de pago:
   - 💰 **Efectivo**
   - 💳 **Tarjeta**
   - 📱 **Transferencia**
5. Haga clic en "Confirmar Venta"

#### 4. Generar Ticket

Después de procesar la venta:
- **Imprimir**: Haga clic en "Imprimir" para imprimir el ticket
- **PDF**: Haga clic en "PDF" para descargar el ticket
- **Compartir**: Haga clic en "Compartir" para enviar por email/WhatsApp

### Funciones Avanzadas

#### Búsqueda Semántica
1. En el campo de búsqueda, escriba una descripción natural
2. Ejemplo: "bebida refrescante" en lugar de "Coca Cola"
3. El sistema encontrará productos similares automáticamente

#### Descuentos
1. Seleccione el producto en el carrito
2. Haga clic en "Editar"
3. Ingrese el porcentaje de descuento
4. El descuento se aplicará automáticamente

---

## 📦 Gestión de Inventario

### Ver Productos

1. Haga clic en "Inventario" en la barra de navegación
2. Verá una lista de todos los productos con:
   - Código del producto
   - Nombre
   - Precio
   - Stock disponible
   - Categoría

### Agregar Producto

1. Haga clic en "Agregar Producto"
2. Complete los campos:
   - **Código**: Código único del producto
   - **Nombre**: Nombre del producto
   - **Descripción**: Descripción detallada
   - **Precio**: Precio de venta
   - **Categoría**: Categoría del producto
3. Haga clic en "Guardar"

### Editar Producto

1. En la lista de productos, haga clic en el ícono de editar
2. Modifique los campos necesarios
3. Haga clic en "Guardar"

### Ajustar Stock

1. Seleccione el producto
2. Haga clic en "Ajustar Stock"
3. Ingrese la cantidad a agregar/quitar
4. Seleccione el tipo de movimiento:
   - **Entrada**: Productos que llegan
   - **Salida**: Productos que salen
   - **Ajuste**: Corrección de inventario
5. Haga clic en "Confirmar"

### Alertas de Stock

El sistema automáticamente:
- ⚠️ **Alerta de Stock Bajo**: Cuando el stock está por debajo del mínimo
- 📧 **Notificaciones**: Envía alertas por email
- 📱 **Notificaciones Push**: En dispositivos móviles

---

## 📊 Reportes de Ventas

### Reporte Diario

1. Haga clic en "Ventas" en la barra de navegación
2. Seleccione la fecha deseada
3. Vea el resumen:
   - Total de ventas del día
   - Número de transacciones
   - Productos más vendidos
   - Métodos de pago utilizados

### Reporte Mensual

1. En la sección de ventas, seleccione "Mensual"
2. Elija el mes y año
3. Analice:
   - Tendencias de ventas
   - Productos con mejor rendimiento
   - Horarios pico de ventas
   - Comparación con meses anteriores

### Reporte de Productos

1. Haga clic en "Reporte de Productos"
2. Vea estadísticas detalladas:
   - Productos más vendidos
   - Productos con menor rotación
   - Margen de ganancia por producto
   - Predicciones de demanda

### Exportar Reportes

1. En cualquier reporte, haga clic en "Exportar"
2. Seleccione el formato:
   - **Excel**: Para análisis detallado
   - **PDF**: Para presentaciones
   - **CSV**: Para importar a otros sistemas
3. Descargue el archivo

---

## 🔍 Búsqueda Inteligente

### Búsqueda Semántica

El sistema utiliza IA para entender búsquedas naturales:

**Ejemplos de búsquedas:**
- "bebida refrescante" → Encuentra Coca Cola, Pepsi, etc.
- "comida rápida" → Encuentra hamburguesas, pizzas, etc.
- "limpieza hogar" → Encuentra detergentes, desinfectantes, etc.

### Búsqueda Híbrida

Combine búsqueda semántica con filtros:

1. Escriba su búsqueda
2. Aplique filtros:
   - **Categoría**: Seleccione categoría específica
   - **Precio**: Rango de precios
   - **Stock**: Solo productos disponibles
3. Vea resultados combinados

### Recomendaciones

El sistema sugiere productos basado en:
- **Historial de compras**: Productos que suele comprar juntos
- **Tendencias**: Productos populares en su área
- **Stock**: Productos que necesita reponer

---

## ⚙️ Configuración

### Configuración de Usuario

1. Haga clic en su avatar en la esquina superior derecha
2. Seleccione "Perfil"
3. Modifique:
   - **Nombre**: Su nombre completo
   - **Email**: Su dirección de email
   - **Teléfono**: Su número de contacto
   - **Contraseña**: Cambie su contraseña

### Configuración del Sistema

1. Haga clic en "Configuración" en la barra lateral
2. Ajuste:

#### Configuración de Ventas
- **IVA**: Porcentaje de impuestos (por defecto 16%)
- **Moneda**: Símbolo de moneda
- **Decimales**: Número de decimales en precios
- **Métodos de Pago**: Active/desactive métodos

#### Configuración de Inventario
- **Stock Mínimo**: Cantidad mínima para alertas
- **Alertas**: Configure notificaciones
- **Categorías**: Gestione categorías de productos

#### Configuración de Tickets
- **Logo**: Suba el logo de su empresa
- **Información**: Datos de la empresa
- **Mensaje**: Mensaje personalizado en tickets

### Configuración de Agentes IA

El sistema incluye agentes inteligentes que:

#### Agente de Inventario
- Monitorea stock automáticamente
- Sugiere reabastecimiento
- Predice demanda futura

#### Agente de Ventas
- Analiza patrones de venta
- Sugiere promociones
- Identifica oportunidades

#### Configuración de Agentes
1. En configuración, seleccione "Agentes IA"
2. Active/desactive agentes
3. Configure parámetros de cada agente
4. Establezca horarios de monitoreo

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### El scanner no funciona
**Solución:**
1. Verifique que el scanner esté conectado
2. Haga clic en "Configurar Scanner"
3. Seleccione el puerto correcto
4. Pruebe escanear un código de prueba

#### No encuentra productos
**Solución:**
1. Verifique que el código esté correcto
2. Use la búsqueda semántica con descripción
3. Revise que el producto esté activo en inventario
4. Contacte al administrador si persiste

#### Error al procesar venta
**Solución:**
1. Verifique la conexión a internet
2. Refresque la página
3. Intente nuevamente
4. Si persiste, contacte soporte técnico

#### Ticket no se imprime
**Solución:**
1. Verifique que la impresora esté conectada
2. Descargue el PDF como alternativa
3. Configure la impresora en configuración
4. Use la función de compartir por email

### Contacto de Soporte

**Soporte Técnico:**
- 📧 Email: soporte@sistemapos.com
- 📱 WhatsApp: +52 55 1234 5678
- 🌐 Web: www.sistemapos.com/soporte

**Horarios de Atención:**
- Lunes a Viernes: 8:00 AM - 6:00 PM
- Sábados: 9:00 AM - 2:00 PM

### Actualizaciones del Sistema

El sistema se actualiza automáticamente, pero puede:

1. **Verificar actualizaciones**: En configuración → "Sistema"
2. **Actualizar manualmente**: Haga clic en "Buscar actualizaciones"
3. **Ver historial**: Vea las últimas actualizaciones aplicadas

---

## 📱 Uso en Dispositivos Móviles

### Acceso Móvil

1. Abra el navegador en su móvil/tablet
2. Ingrese la misma URL del sistema
3. La interfaz se adaptará automáticamente

### Funciones Móviles

- ✅ **Scanner de Cámara**: Use la cámara del móvil como scanner
- ✅ **Touch Optimizado**: Botones grandes para uso táctil
- ✅ **Modo Offline**: Funciona sin internet (datos básicos)
- ✅ **Notificaciones Push**: Alertas en tiempo real

### Configuración Móvil

1. **Permisos**: Permita acceso a cámara y notificaciones
2. **Modo Oscuro**: Active para mejor visibilidad
3. **Tamaño de Texto**: Ajuste según sus preferencias

---

## 🎯 Consejos de Uso

### Para Vendedores

1. **Memorice códigos frecuentes** para ventas rápidas
2. **Use la búsqueda semántica** para productos difíciles de encontrar
3. **Configure atajos de teclado** para operaciones comunes
4. **Revise el stock** antes de prometer productos

### Para Administradores

1. **Monitoree reportes diariamente** para identificar tendencias
2. **Configure alertas de stock** para evitar faltantes
3. **Use los agentes IA** para optimizar inventario
4. **Exporte reportes regularmente** para análisis externo

### Para Dueños

1. **Analice reportes mensuales** para tomar decisiones
2. **Configure promociones** basadas en datos de ventas
3. **Use predicciones de demanda** para planificar compras
4. **Monitoree el rendimiento** de diferentes productos

---

## 📚 Glosario

- **POS**: Point of Sale (Punto de Venta)
- **IA**: Inteligencia Artificial
- **RAG**: Retrieval-Augmented Generation (Búsqueda Aumentada)
- **Stock**: Inventario disponible
- **IVA**: Impuesto al Valor Agregado
- **Scanner**: Dispositivo para leer códigos de barras
- **Ticket**: Comprobante de venta
- **Agente IA**: Sistema inteligente que automatiza tareas

---

*Este manual se actualiza regularmente. Para la versión más reciente, visite: www.sistemapos.com/manual* 