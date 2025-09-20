#!/usr/bin/env python3
"""
Script para corregir errores específicos de TypeScript
Sistema POS O'Data v2.0.0
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class TypeScriptErrorFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.errors = []
        
    def fix_unused_imports(self, filepath: Path, content: str) -> str:
        """Corregir imports no utilizados específicos"""
        fixes = [
            # Dashboard.tsx
            (r"import\s*\{\s*[^}]*Calendar[^}]*\}\s*from\s*['\"]lucide-react['\"];?", 
             lambda m: re.sub(r',?\s*Calendar\s*,?', '', m.group(0)).replace(',,', ',')),
            (r"import\s*\{\s*[^}]*FileText[^}]*\}\s*from\s*['\"]lucide-react['\"];?", 
             lambda m: re.sub(r',?\s*FileText\s*,?', '', m.group(0)).replace(',,', ',')),
            (r"import\s*\{\s*[^}]*UserCheck[^}]*\}\s*from\s*['\"]lucide-react['\"];?", 
             lambda m: re.sub(r',?\s*UserCheck\s*,?', '', m.group(0)).replace(',,', ',')),
            (r"import\s*\{\s*[^}]*PieChart[^}]*\}\s*from\s*['\"]lucide-react['\"];?", 
             lambda m: re.sub(r',?\s*PieChart\s*,?', '', m.group(0)).replace(',,', ',')),
            (r"import\s*\{\s*[^}]*Activity[^}]*\}\s*from\s*['\"]lucide-react['\"];?", 
             lambda m: re.sub(r',?\s*Activity\s*,?', '', m.group(0)).replace(',,', ','))
        ]
        
        for pattern, replacement in fixes:
            if re.search(pattern, content):
                if callable(replacement):
                    content = re.sub(pattern, replacement, content)
                else:
                    content = re.sub(pattern, replacement, content)
                self.fixes_applied += 1
                
        return content
    
    def fix_unused_variables(self, filepath: Path, content: str) -> str:
        """Corregir variables no utilizadas"""
        fixes = [
            # Parámetros no utilizados en callbacks
            (r'\.map\(\([^,]+,\s*index\)\s*=>', r'.map((\1, _index) =>'),
            (r'\.filter\(\([^,]+,\s*index\)\s*=>', r'.filter((\1, _index) =>'),
            (r'\.forEach\(\([^,]+,\s*index\)\s*=>', r'.forEach((\1, _index) =>'),
            
            # Variables destructuradas no utilizadas
            (r'const\s*\{\s*([^}]+),\s*([^}]+)\s*\}\s*=', lambda m: self._fix_destructuring(m)),
            
            # Parámetros de funciones no utilizados
            (r'=\s*\(\s*([^,)]+),\s*options\s*\)\s*=>', r'= (\1, _options) =>'),
            (r'=\s*\(\s*([^,)]+),\s*req\s*,\s*res\s*\)\s*=>', r'= (\1, _req, _res) =>'),
        ]
        
        for pattern, replacement in fixes:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
                
        return content
    
    def _fix_destructuring(self, match):
        """Corregir destructuring con variables no utilizadas"""
        full_match = match.group(0)
        # Si contiene variables comunes no utilizadas, añadir underscore
        unused_vars = ['isDark', 'data', 'entry', 'options', 'req', 'res']
        for var in unused_vars:
            if var in full_match:
                full_match = full_match.replace(var, f'_{var}')
        return full_match
    
    def fix_type_errors(self, filepath: Path, content: str) -> str:
        """Corregir errores de tipos específicos"""
        fixes = []
        
        # Errores específicos por archivo
        filename = filepath.name
        
        if filename == 'InventoryManagement.tsx':
            # Añadir sku al tipo Product si no existe
            if 'sku: product.sku' in content and 'interface Product' in content:
                content = re.sub(
                    r'(interface Product\s*\{[^}]*)',
                    r'\1\n  sku?: string;',
                    content
                )
                
        elif filename == 'ReportsManagementFixed.tsx':
            # Corregir tipos de Recharts
            content = re.sub(
                r'percent\s*\*\s*100',
                r'(percent as number) * 100',
                content
            )
            
        elif filename == 'UsersManagement.tsx':
            # Corregir delete operator
            content = re.sub(
                r'delete\s+submitData\.password;',
                r'const { password, ...submitDataWithoutPassword } = submitData;\n        const finalSubmitData = submitDataWithoutPassword;',
                content
            )
            
            # Corregir formatDate con null check
            content = re.sub(
                r'formatDate\(user\.last_login\)',
                r'user.last_login ? formatDate(user.last_login) : "Nunca"',
                content
            )
            
        elif filename == 'api.client.ts':
            # Corregir imports de tipos
            content = re.sub(
                r'import axios, \{ AxiosInstance, AxiosRequestConfig, AxiosResponse \} from [\'"]axios[\'"];',
                r'import axios from "axios";\nimport type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";',
                content
            )
            
        return content
    
    def fix_null_checks(self, filepath: Path, content: str) -> str:
        """Añadir null checks donde sea necesario"""
        fixes = [
            # Dashboard.tsx - null checks
            (r'data\?\.products\?\.length\s*>\s*0', r'data?.products && data.products.length > 0'),
            (r'data\.products\[0\]\.id', r'data?.products?.[0]?.id'),
            (r'data\.products\[0\]\.product_id', r'data?.products?.[0]?.product_id'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
            
        return content
    
    def fix_comparison_errors(self, filepath: Path, content: str) -> str:
        """Corregir errores de comparación de tipos"""
        if filepath.name == 'products.ts':
            # Corregir comparaciones de categorías
            content = re.sub(
                r"p\.category === 'Bebidas Frías'",
                r"p.category === 'Bebidas' || p.name.includes('Frío')",
                content
            )
            content = re.sub(
                r"p\.category === 'Bebidas Calientes'",
                r"p.category === 'Bebidas' || p.name.includes('Caliente')",
                content
            )
            
        return content
    
    def process_file(self, filepath: Path) -> bool:
        """Procesar un archivo individual"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            content = original_content
            initial_fixes = self.fixes_applied
            
            # Aplicar todas las correcciones
            content = self.fix_unused_imports(filepath, content)
            content = self.fix_unused_variables(filepath, content)
            content = self.fix_type_errors(filepath, content)
            content = self.fix_null_checks(filepath, content)
            content = self.fix_comparison_errors(filepath, content)
            
            # Limpiar líneas vacías múltiples
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            fixes_in_file = self.fixes_applied - initial_fixes
            
            if fixes_in_file > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Aplicadas {fixes_in_file} correcciones")
                return True
            else:
                print(f"  ✅ No se necesitaron correcciones")
                return False
                
        except Exception as e:
            error_msg = f"Error procesando {filepath}: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            return False
    
    def fix_specific_files(self) -> Dict[str, int]:
        """Corregir archivos específicos con errores conocidos"""
        problem_files = [
            'frontend/src/components/Dashboard.tsx',
            'frontend/src/components/InventoryManagement.tsx',
            'frontend/src/components/ReportsManagementFixed.tsx',
            'frontend/src/components/UsersManagement.tsx',
            'frontend/src/components/ProductsManagement.tsx',
            'frontend/src/components/BranchesSection.tsx',
            'frontend/src/services/api.client.ts',
            'frontend/src/data/products.ts',
            'frontend/src/Dashboard.tsx',
            'frontend/src/hooks/usePWA.ts',
            'frontend/src/context/EnhancedCartContext.tsx',
            'frontend/vite.config.ts'
        ]
        
        print("🔧 Corrigiendo errores específicos de TypeScript...")
        print("=" * 60)
        
        processed = 0
        fixed = 0
        
        for filepath in problem_files:
            if os.path.exists(filepath):
                print(f"🔍 Procesando: {filepath}")
                processed += 1
                if self.process_file(Path(filepath)):
                    fixed += 1
            else:
                print(f"⚠️ Archivo no encontrado: {filepath}")
                
        return {
            'processed': processed,
            'fixed': fixed,
            'total_fixes': self.fixes_applied
        }
    
    def print_report(self, results: Dict[str, int]):
        """Imprimir reporte de correcciones"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE CORRECCIONES TYPESCRIPT")
        print("=" * 60)
        
        print(f"📁 Archivos procesados: {results['processed']}")
        print(f"🔧 Archivos corregidos: {results['fixed']}")
        print(f"✅ Total correcciones aplicadas: {results['total_fixes']}")
        
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if results['total_fixes'] > 0:
            print(f"\n🎉 ¡Correcciones aplicadas exitosamente!")
            print(f"💡 Recomendación: Ejecutar 'npm run build' para verificar")
        else:
            print(f"\n✅ ¡No se necesitaron correcciones!")
        
        print("=" * 60)

def main():
    """Función principal"""
    fixer = TypeScriptErrorFixer()
    
    try:
        results = fixer.fix_specific_files()
        fixer.print_report(results)
        
        return 0 if not fixer.errors else 1
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
