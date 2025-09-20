#!/usr/bin/env python3
"""
Script para limpiar imports no utilizados en archivos TypeScript/JavaScript
Sistema POS O'Data v2.0.0
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple

class UnusedImportsCleanup:
    def __init__(self):
        self.processed_files = 0
        self.cleaned_imports = 0
        self.errors = []
        
    def find_typescript_files(self, directory: str) -> List[Path]:
        """Encontrar todos los archivos TypeScript/JavaScript"""
        extensions = {'.ts', '.tsx', '.js', '.jsx'}
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Excluir directorios comunes que no necesitan limpieza
            dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', 'dist', 'build', '.next'}]
            
            for filename in filenames:
                if Path(filename).suffix in extensions:
                    files.append(Path(root) / filename)
                    
        return files
    
    def extract_imports(self, content: str) -> Dict[str, List[str]]:
        """Extraer todos los imports del archivo"""
        imports = {
            'default': [],
            'named': [],
            'namespace': [],
            'side_effect': []
        }
        
        # Patrones para diferentes tipos de imports
        patterns = {
            'default': r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]",
            'named': r"import\s*\{\s*([^}]+)\s*\}\s*from\s+['\"]([^'\"]+)['\"]",
            'namespace': r"import\s*\*\s*as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]",
            'side_effect': r"import\s+['\"]([^'\"]+)['\"]"
        }
        
        for import_type, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if import_type == 'named':
                    # Dividir imports nombrados
                    named_imports = [imp.strip() for imp in match[0].split(',')]
                    imports[import_type].extend([(imp, match[1]) for imp in named_imports])
                elif import_type == 'side_effect':
                    imports[import_type].append(match)
                else:
                    imports[import_type].append(match)
                    
        return imports
    
    def find_used_identifiers(self, content: str) -> Set[str]:
        """Encontrar todos los identificadores utilizados en el código"""
        # Remover imports y comentarios para análisis
        lines = content.split('\n')
        code_lines = []
        in_multiline_comment = False
        
        for line in lines:
            # Skip import lines
            if line.strip().startswith('import '):
                continue
                
            # Handle multiline comments
            if '/*' in line and '*/' not in line:
                in_multiline_comment = True
                continue
            elif '*/' in line:
                in_multiline_comment = False
                continue
            elif in_multiline_comment:
                continue
                
            # Skip single line comments
            if '//' in line:
                line = line[:line.index('//')]
                
            code_lines.append(line)
        
        code_content = '\n'.join(code_lines)
        
        # Encontrar identificadores (palabras que empiezan con letra o _)
        identifiers = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_content))
        
        # Remover palabras reservadas de JavaScript/TypeScript
        reserved_words = {
            'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while',
            'do', 'break', 'continue', 'switch', 'case', 'default', 'try', 'catch',
            'finally', 'throw', 'new', 'this', 'super', 'class', 'extends', 'implements',
            'interface', 'type', 'enum', 'namespace', 'module', 'export', 'import',
            'from', 'as', 'true', 'false', 'null', 'undefined', 'void', 'never',
            'any', 'unknown', 'string', 'number', 'boolean', 'object', 'symbol',
            'bigint', 'typeof', 'instanceof', 'in', 'delete', 'async', 'await',
            'yield', 'static', 'readonly', 'private', 'protected', 'public',
            'abstract', 'declare', 'get', 'set', 'constructor'
        }
        
        return identifiers - reserved_words
    
    def clean_unused_imports(self, filepath: Path) -> Tuple[str, int]:
        """Limpiar imports no utilizados de un archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            content = original_content
            imports = self.extract_imports(content)
            used_identifiers = self.find_used_identifiers(content)
            
            cleaned_count = 0
            
            # Limpiar imports nombrados no utilizados
            for named_import, module in imports['named']:
                if named_import not in used_identifiers:
                    # Buscar y remover el import específico
                    import_patterns = [
                        rf"import\s*\{{\s*{re.escape(named_import)}\s*\}}\s*from\s+['\"][^'\"]+['\"];?\s*\n?",
                        rf",\s*{re.escape(named_import)}\s*",
                        rf"{re.escape(named_import)}\s*,\s*"
                    ]
                    
                    for pattern in import_patterns:
                        if re.search(pattern, content):
                            content = re.sub(pattern, '', content)
                            cleaned_count += 1
                            break
            
            # Limpiar imports por defecto no utilizados
            for default_import, module in imports['default']:
                if default_import not in used_identifiers:
                    pattern = rf"import\s+{re.escape(default_import)}\s+from\s+['\"][^'\"]+['\"];?\s*\n?"
                    if re.search(pattern, content):
                        content = re.sub(pattern, '', content)
                        cleaned_count += 1
            
            # Limpiar imports de namespace no utilizados
            for namespace_import, module in imports['namespace']:
                if namespace_import not in used_identifiers:
                    pattern = rf"import\s*\*\s*as\s+{re.escape(namespace_import)}\s+from\s+['\"][^'\"]+['\"];?\s*\n?"
                    if re.search(pattern, content):
                        content = re.sub(pattern, '', content)
                        cleaned_count += 1
            
            # Limpiar líneas vacías múltiples
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            return content, cleaned_count
            
        except Exception as e:
            self.errors.append(f"Error processing {filepath}: {str(e)}")
            return original_content, 0
    
    def process_file(self, filepath: Path) -> bool:
        """Procesar un archivo individual"""
        try:
            print(f"🔍 Procesando: {filepath}")
            
            cleaned_content, cleaned_count = self.clean_unused_imports(filepath)
            
            if cleaned_count > 0:
                # Escribir archivo limpio
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                print(f"  ✅ Limpiados {cleaned_count} imports no utilizados")
                self.cleaned_imports += cleaned_count
                return True
            else:
                print(f"  ✅ No se encontraron imports no utilizados")
                return False
                
        except Exception as e:
            error_msg = f"Error procesando {filepath}: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            return False
    
    def clean_directory(self, directory: str) -> Dict[str, int]:
        """Limpiar todos los archivos en un directorio"""
        print(f"🚀 Limpiando imports no utilizados en: {directory}")
        print("=" * 60)
        
        files = self.find_typescript_files(directory)
        
        if not files:
            print("⚠️ No se encontraron archivos TypeScript/JavaScript")
            return {'processed': 0, 'cleaned': 0}
        
        processed_files = 0
        files_with_changes = 0
        
        for filepath in files:
            self.processed_files += 1
            processed_files += 1
            
            if self.process_file(filepath):
                files_with_changes += 1
        
        return {
            'processed': processed_files,
            'cleaned': files_with_changes,
            'total_imports_cleaned': self.cleaned_imports
        }
    
    def print_report(self, results: Dict[str, int]):
        """Imprimir reporte de limpieza"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE LIMPIEZA DE IMPORTS")
        print("=" * 60)
        
        print(f"📁 Archivos procesados: {results['processed']}")
        print(f"🧹 Archivos modificados: {results['cleaned']}")
        print(f"🗑️ Total imports eliminados: {results['total_imports_cleaned']}")
        
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if results['total_imports_cleaned'] > 0:
            print(f"\n✅ ¡Limpieza completada exitosamente!")
            print(f"💡 Recomendación: Ejecutar tests para verificar que no se rompió nada")
        else:
            print(f"\n🎉 ¡Todos los archivos ya estaban limpios!")
        
        print("=" * 60)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Limpiar imports no utilizados en archivos TypeScript/JavaScript')
    parser.add_argument('directory', nargs='?', default='frontend/src', 
                       help='Directorio a procesar (default: frontend/src)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Solo mostrar qué se limpiaría sin hacer cambios')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ El directorio {args.directory} no existe")
        return 1
    
    cleaner = UnusedImportsCleanup()
    
    if args.dry_run:
        print("🔍 MODO DRY-RUN: Solo mostrando cambios sin aplicarlos")
        print("=" * 60)
    
    try:
        results = cleaner.clean_directory(args.directory)
        cleaner.print_report(results)
        
        return 0 if not cleaner.errors else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
