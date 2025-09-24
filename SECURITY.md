# 🔒 Política de Seguridad

## Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad en el Sistema POS Odata, por favor sigue estos pasos:

### 1. **NO** crear un issue público
- Las vulnerabilidades de seguridad deben ser reportadas de forma privada
- No publiques detalles en GitHub Issues o en foros públicos

### 2. Contacto Privado
Envía un email a: **security@odata.com**

### 3. Información Requerida
Incluye en tu reporte:
- Descripción detallada de la vulnerabilidad
- Pasos para reproducir el problema
- Impacto potencial
- Sugerencias de mitigación (si las tienes)

### 4. Respuesta
- Recibirás confirmación en 24-48 horas
- Mantendremos comunicación durante la investigación
- Te notificaremos cuando se publique el fix

## Versiones Soportadas

| Versión | Soportada          |
| ------- | ------------------ |
| 2.x.x   | ✅ Sí              |
| 1.x.x   | ❌ No              |

## Mejores Prácticas de Seguridad

### Para Desarrolladores
- Nunca committear credenciales o secrets
- Usar variables de entorno para configuraciones sensibles
- Validar todas las entradas de usuario
- Mantener dependencias actualizadas
- Seguir principios de seguridad por defecto

### Para Usuarios
- Mantener el sistema actualizado
- Usar contraseñas fuertes
- Habilitar autenticación de dos factores
- Revisar logs regularmente
- Hacer backups frecuentes

## Historial de Vulnerabilidades

### 2024-01-15
- **CVE-2024-XXXX**: Vulnerabilidad en autenticación JWT
  - **Estado**: Parcheado en v2.0.1
  - **Impacto**: Bajo
  - **Solución**: Actualizar a la última versión

## Agradecimientos

Gracias a todos los investigadores de seguridad que han reportado vulnerabilidades de forma responsable.

---

**Equipo de Seguridad de Odata**
