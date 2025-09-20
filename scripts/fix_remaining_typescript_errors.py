#!/usr/bin/env python3
"""
Script para corregir errores restantes de TypeScript
Sistema POS O'Data v2.0.0
"""

import os
import re
import sys
from pathlib import Path

def fix_file(filepath: Path):
    """Corregir errores específicos en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = 0
        
        filename = filepath.name
        
        # Correcciones específicas por archivo
        if filename == 'ReportsManagementFixed.tsx':
            # Remover imports no utilizados
            content = re.sub(r',\s*BarChart\s*,', ',', content)
            content = re.sub(r',\s*Bar\s*(?=\n|})', '', content)
            # Remover destructuring no utilizado
            content = re.sub(r'const\s*\{\s*isDark\s*\}\s*=\s*useTheme\(\);\s*\n?', '', content)
            fixes_applied += 3
            
        elif filename == 'ProductsManagement.tsx':
            # Remover imports no utilizados
            content = re.sub(r',?\s*Eye\s*,?', '', content)
            content = re.sub(r',?\s*EyeOff\s*,?', '', content)
            content = re.sub(r',?\s*Tag\s*(?=\n|})', '', content)
            # Limpiar comas dobles
            content = re.sub(r',,+', ',', content)
            fixes_applied += 3
            
        elif filename == 'UsersManagement.tsx':
            # Remover imports no utilizados
            content = re.sub(r',?\s*Plus\s*,?', '', content)
            content = re.sub(r',?\s*Eye\s*,?', '', content)
            content = re.sub(r',?\s*EyeOff\s*,?', '', content)
            content = re.sub(r',?\s*Phone\s*,?', '', content)
            content = re.sub(r',?\s*Calendar\s*,?', '', content)
            content = re.sub(r',?\s*UserCheck\s*(?=\n|})', '', content)
            # Limpiar comas dobles
            content = re.sub(r',,+', ',', content)
            fixes_applied += 6
            
        elif filename == 'MenuSection.tsx':
            # Renombrar parámetro no utilizado
            content = re.sub(r'{ onProductClick }', '{ onProductClick: _onProductClick }', content)
            fixes_applied += 1
            
        elif filename == 'EnhancedCartContext.tsx':
            # Remover import no utilizado
            content = re.sub(r',\s*CartItem\s*(?=})', '', content)
            fixes_applied += 1
            
        elif filename == 'SabrositasApp.tsx':
            # Renombrar variable no utilizada
            content = re.sub(r'const \[searchQuery, setSearchQuery\]', 'const [_searchQuery, setSearchQuery]', content)
            fixes_applied += 1
            
        elif filename == 'usePWA.ts':
            # Renombrar variable no utilizada
            content = re.sub(r'const { type, data } = event.data;', 'const { type, data: _data } = event.data;', content)
            fixes_applied += 1
            
        elif filename == 'api.client.ts':
            # Remover exports duplicados
            content = re.sub(r'export type \{ ApiResponse, PaginatedResponse \};?\s*\n?', '', content)
            fixes_applied += 1
            
        elif filename == 'products.ts':
            # Corregir comparaciones de tipos
            content = re.sub(r"p\.category === 'Bebidas Frías'", "p.name.toLowerCase().includes('frío') || p.name.toLowerCase().includes('fría')", content)
            content = re.sub(r"p\.category === 'Bebidas Calientes'", "p.name.toLowerCase().includes('caliente') || p.name.toLowerCase().includes('café')", content)
            fixes_applied += 2
            
        elif filename == 'Dashboard.tsx':
            # Corregir null checks
            content = re.sub(r'data\?\.products\?\.length > 0', 'data?.products && data.products.length > 0', content)
            content = re.sub(r'data\.products\[0\]\.id', 'data?.products?.[0]?.id', content)
            content = re.sub(r'data\.products\[0\]\.product_id', 'data?.products?.[0]?.product_id', content)
            fixes_applied += 3
            
        elif filename == 'InventoryManagement.tsx':
            # Añadir sku al interface Product si no existe
            if 'interface Product' in content and 'sku?' not in content:
                content = re.sub(
                    r'(interface Product\s*{[^}]*)',
                    r'\1\n  sku?: string;',
                    content
                )
                fixes_applied += 1
        
        # Limpiar líneas vacías múltiples
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✅ {filepath.name} - {fixes_applied} correcciones aplicadas')
            return True
        else:
            print(f'ℹ️ {filepath.name} - Sin cambios necesarios')
            return False
            
    except Exception as e:
        print(f'❌ Error en {filepath}: {str(e)}')
        return False

def main():
    """Función principal"""
    print('🔧 CORRIGIENDO ERRORES RESTANTES DE TYPESCRIPT')
    print('=' * 60)
    
    # Archivos problemáticos identificados
    problem_files = [
        'frontend/src/components/ReportsManagementFixed.tsx',
        'frontend/src/components/ProductsManagement.tsx', 
        'frontend/src/components/UsersManagement.tsx',
        'frontend/src/components/MenuSection.tsx',
        'frontend/src/components/InventoryManagement.tsx',
        'frontend/src/context/EnhancedCartContext.tsx',
        'frontend/src/SabrositasApp.tsx',
        'frontend/src/hooks/usePWA.ts',
        'frontend/src/services/api.client.ts',
        'frontend/src/data/products.ts',
        'frontend/src/Dashboard.tsx'
    ]
    
    fixed_count = 0
    processed_count = 0
    
    for filepath in problem_files:
        if os.path.exists(filepath):
            processed_count += 1
            if fix_file(Path(filepath)):
                fixed_count += 1
        else:
            print(f'⚠️ {filepath} - Archivo no encontrado')
    
    print('\n' + '=' * 60)
    print('📊 RESUMEN DE CORRECCIONES:')
    print(f'📁 Archivos procesados: {processed_count}')
    print(f'🔧 Archivos corregidos: {fixed_count}')
    
    if fixed_count > 0:
        print('\n✅ ¡Correcciones aplicadas exitosamente!')
        print('💡 Ejecute "npm run build" para verificar')
    else:
        print('\nℹ️ No se necesitaron correcciones')
    
    return fixed_count

if __name__ == '__main__':
    fixes = main()
    sys.exit(0)
