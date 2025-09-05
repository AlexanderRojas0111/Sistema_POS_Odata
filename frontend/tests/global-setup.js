const { chromium } = require('@playwright/test');

async function globalSetup(config) {
  const { baseURL } = config.projects[0].use;
  
  // Verificar que el servidor esté funcionando
  console.log('🚀 Configurando entorno de tests...');
  console.log(`📍 URL base: ${baseURL}`);
  
  // Crear directorio de reports si no existe
  const fs = require('fs');
  const path = require('path');
  const reportsDir = path.join(__dirname, '../../reports');
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true });
    console.log('📁 Directorio de reports creado');
  }
  
  // Verificar conectividad del backend
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      console.log('✅ Backend conectado correctamente');
    } else {
      console.log('⚠️ Backend responde pero con estado no exitoso');
    }
  } catch (error) {
    console.log('⚠️ Backend no disponible (esto es normal si no está ejecutándose)');
  }
  
  console.log('✅ Configuración global completada');
}

module.exports = globalSetup;
