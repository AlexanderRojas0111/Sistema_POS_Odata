async function globalTeardown(config) {
  console.log('🧹 Limpiando entorno de tests...');
  
  // Aquí podrías agregar limpieza adicional si es necesario
  // Por ejemplo, limpiar archivos temporales, resetear base de datos, etc.
  
  console.log('✅ Limpieza global completada');
}

module.exports = globalTeardown;
