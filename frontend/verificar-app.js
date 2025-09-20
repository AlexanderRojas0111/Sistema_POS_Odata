// Script para verificar que la aplicación esté funcionando correctamente
const fs = require('fs');
const path = require('path');

console.log('🔍 Verificando la aplicación Sabrositas...\n');

// Verificar archivos principales
const archivosRequeridos = [
  'src/SabrositasApp.tsx',
  'src/components/Header.tsx',
  'src/components/HeroSection.tsx',
  'src/components/MenuSection.tsx',
  'src/components/ProductCard.tsx',
  'src/components/CartSidebar.tsx',
  'src/components/BranchesSection.tsx',
  'src/components/ContactSection.tsx',
  'src/components/Footer.tsx',
  'src/context/CartContext.tsx',
  'src/data/products.ts',
  'src/data/branches.ts',
  'package.json',
  'tailwind.config.js',
  'postcss.config.js'
];

let errores = 0;
let archivosExistentes = 0;

archivosRequeridos.forEach(archivo => {
  const rutaCompleta = path.join(__dirname, archivo);
  if (fs.existsSync(rutaCompleta)) {
    console.log(`✅ ${archivo}`);
    archivosExistentes++;
  } else {
    console.log(`❌ ${archivo} - NO ENCONTRADO`);
    errores++;
  }
});

// Verificar dependencias en package.json
try {
  const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
  const dependenciasRequeridas = [
    'react',
    'react-dom',
    'react-router-dom',
    'tailwindcss',
    'framer-motion',
    'lucide-react',
    'react-hook-form'
  ];

  console.log('\n📦 Verificando dependencias:');
  dependenciasRequeridas.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`✅ ${dep}: ${packageJson.dependencies[dep]}`);
    } else {
      console.log(`❌ ${dep} - NO INSTALADA`);
      errores++;
    }
  });
} catch (error) {
  console.log('❌ Error al leer package.json:', error.message);
  errores++;
}

// Resumen final
console.log('\n📊 RESUMEN:');
console.log(`Archivos encontrados: ${archivosExistentes}/${archivosRequeridos.length}`);
console.log(`Errores: ${errores}`);

if (errores === 0) {
  console.log('\n🎉 ¡Aplicación Sabrositas lista y funcionando!');
  console.log('🌐 URL: http://localhost:5173');
  console.log('📱 Ruta Sabrositas: http://localhost:5173/sabrositas');
} else {
  console.log('\n⚠️  Se encontraron errores que deben corregirse.');
}

process.exit(errores > 0 ? 1 : 0);
