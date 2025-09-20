"""
Script para validar y corregir archivos de GitHub Workflows
"""

import os
import yaml
import re
from pathlib import Path

def validate_github_workflows():
    """Validar todos los archivos de workflow de GitHub"""
    print("🔍 VALIDANDO ARCHIVOS DE GITHUB WORKFLOWS")
    print("=" * 70)
    
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("❌ Directorio .github/workflows no encontrado")
        return
    
    # Obtener todos los archivos .yml
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    print(f"📁 Archivos encontrados: {len(workflow_files)}")
    
    issues_found = []
    
    for workflow_file in workflow_files:
        print(f"\n🔍 Validando: {workflow_file.name}")
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar versiones de acciones obsoletas
            outdated_actions = {
                'actions/checkout@v3': 'actions/checkout@v4',
                'actions/setup-python@v4': 'actions/setup-python@v5',
                'actions/setup-node@v3': 'actions/setup-node@v4',
                'actions/cache@v3': 'actions/cache@v4',
                'actions/upload-artifact@v3': 'actions/upload-artifact@v4',
                'actions/download-artifact@v3': 'actions/download-artifact@v4',
                'actions/create-release@v1': 'softprops/action-gh-release@v1',
                'codecov/codecov-action@v3': 'codecov/codecov-action@v4',
                'docker/setup-buildx-action@v3': 'docker/setup-buildx-action@v3',
                'github/codeql-action/init@v3': 'github/codeql-action/init@v3',
                'aquasecurity/trivy-action@0.18.3': 'aquasecurity/trivy-action@master'
            }
            
            file_issues = []
            
            for old_action, new_action in outdated_actions.items():
                if old_action in content:
                    file_issues.append({
                        'type': 'outdated_action',
                        'old': old_action,
                        'new': new_action,
                        'line': content.split('\n').index([line for line in content.split('\n') if old_action in line][0]) + 1 if any(old_action in line for line in content.split('\n')) else 'N/A'
                    })
            
            # Verificar sintaxis YAML
            try:
                yaml.safe_load(content)
                print("   ✅ Sintaxis YAML válida")
            except yaml.YAMLError as e:
                file_issues.append({
                    'type': 'yaml_syntax',
                    'error': str(e)
                })
                print(f"   ❌ Error de sintaxis YAML: {e}")
            
            # Verificar versiones de Python inconsistentes
            python_versions = re.findall(r"python-version:\s*['\"]?([0-9.]+)['\"]?", content)
            if len(set(python_versions)) > 1:
                file_issues.append({
                    'type': 'inconsistent_python',
                    'versions': list(set(python_versions))
                })
                print(f"   ⚠️ Versiones de Python inconsistentes: {set(python_versions)}")
            
            # Verificar archivos referenciados que no existen
            referenced_files = re.findall(r"requirements[^.]*\.txt", content)
            for req_file in set(referenced_files):
                if not Path(req_file).exists() and req_file != "requirements.txt":
                    file_issues.append({
                        'type': 'missing_file',
                        'file': req_file
                    })
                    print(f"   ❌ Archivo referenciado no existe: {req_file}")
            
            # Verificar scripts referenciados
            script_refs = re.findall(r"python\s+scripts/([^.\s]+\.py)", content)
            for script in set(script_refs):
                script_path = Path(f"scripts/{script}")
                if not script_path.exists():
                    file_issues.append({
                        'type': 'missing_script',
                        'script': f"scripts/{script}"
                    })
                    print(f"   ❌ Script referenciado no existe: scripts/{script}")
            
            if file_issues:
                issues_found.append({
                    'file': workflow_file.name,
                    'issues': file_issues
                })
                print(f"   ⚠️ {len(file_issues)} problemas encontrados")
            else:
                print("   ✅ Sin problemas detectados")
                
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            issues_found.append({
                'file': workflow_file.name,
                'issues': [{'type': 'read_error', 'error': str(e)}]
            })
    
    # Resumen de problemas
    print(f"\n📊 RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    
    if issues_found:
        print(f"❌ Archivos con problemas: {len(issues_found)}")
        
        # Contar tipos de problemas
        problem_types = {}
        for file_data in issues_found:
            for issue in file_data['issues']:
                issue_type = issue['type']
                if issue_type not in problem_types:
                    problem_types[issue_type] = 0
                problem_types[issue_type] += 1
        
        print(f"\n🔍 TIPOS DE PROBLEMAS:")
        for problem_type, count in problem_types.items():
            print(f"   - {problem_type}: {count} ocurrencias")
        
        # Mostrar detalles por archivo
        print(f"\n📋 DETALLES POR ARCHIVO:")
        for file_data in issues_found:
            print(f"\n📄 {file_data['file']}:")
            for issue in file_data['issues']:
                if issue['type'] == 'outdated_action':
                    print(f"   ⚠️ Acción obsoleta: {issue['old']} → {issue['new']}")
                elif issue['type'] == 'missing_file':
                    print(f"   ❌ Archivo faltante: {issue['file']}")
                elif issue['type'] == 'missing_script':
                    print(f"   ❌ Script faltante: {issue['script']}")
                elif issue['type'] == 'inconsistent_python':
                    print(f"   ⚠️ Versiones Python inconsistentes: {issue['versions']}")
                elif issue['type'] == 'yaml_syntax':
                    print(f"   ❌ Error YAML: {issue['error']}")
    else:
        print("✅ Todos los archivos están correctos")
    
    return issues_found

def generate_fix_script(issues_found):
    """Generar script para corregir los problemas encontrados"""
    print(f"\n🔧 GENERANDO SCRIPT DE CORRECCIÓN")
    print("-" * 70)
    
    if not issues_found:
        print("✅ No se necesitan correcciones")
        return
    
    fixes = []
    
    for file_data in issues_found:
        file_name = file_data['file']
        
        for issue in file_data['issues']:
            if issue['type'] == 'outdated_action':
                fixes.append({
                    'file': file_name,
                    'action': 'replace',
                    'old': issue['old'],
                    'new': issue['new']
                })
    
    if fixes:
        print(f"📝 Se pueden aplicar {len(fixes)} correcciones automáticas:")
        for fix in fixes:
            print(f"   - {fix['file']}: {fix['old']} → {fix['new']}")
    
    return fixes

def main():
    """Función principal"""
    print("🎯 VALIDACIÓN COMPLETA DE GITHUB WORKFLOWS")
    print("=" * 70)
    print(f"Directorio: {os.getcwd()}")
    print(f"Timestamp: {os.popen('date').read().strip()}")
    
    # Validar workflows
    issues = validate_github_workflows()
    
    # Generar script de corrección
    fixes = generate_fix_script(issues)
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    print("-" * 70)
    
    if not issues:
        print("🎉 Todos los workflows están en excelente estado")
        print("✅ No se requieren acciones")
    else:
        print("🔧 Se recomienda aplicar las siguientes correcciones:")
        print("1. Actualizar versiones de acciones obsoletas")
        print("2. Crear archivos faltantes referenciados")
        print("3. Estandarizar versiones de Python")
        print("4. Verificar scripts referenciados")
    
    print(f"\n🎊 VALIDACIÓN COMPLETADA")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
