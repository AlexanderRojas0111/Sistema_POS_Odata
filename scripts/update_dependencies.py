#!/usr/bin/env python3
"""
Script de Actualización de Dependencias - Sistema POS Odata
Actualiza automáticamente todas las dependencias del proyecto a las últimas versiones estables.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class DependencyUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups" / f"deps_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_backup(self):
        """Crear backup de archivos de dependencias actuales"""
        self.log("Creando backup de dependencias actuales...")
        
        # Crear directorio de backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup de requirements.txt
        if (self.project_root / "requirements.txt").exists():
            shutil.copy2(self.project_root / "requirements.txt", self.backup_dir / "requirements.txt")
            
        # Backup de package.json
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            shutil.copy2(package_json, self.backup_dir / "package.json")
            
        self.log(f"Backup creado en: {self.backup_dir}")
        
    def update_python_dependencies(self):
        """Actualizar dependencias de Python"""
        self.log("Actualizando dependencias de Python...")
        
        try:
            # Verificar si existe el archivo actualizado
            updated_reqs = self.project_root / "requirements_updated.txt"
            if not updated_reqs.exists():
                self.log("ERROR: No se encontró requirements_updated.txt", "ERROR")
                return False
                
            # Hacer backup del requirements.txt actual
            current_reqs = self.project_root / "requirements.txt"
            if current_reqs.exists():
                shutil.copy2(current_reqs, self.backup_dir / "requirements_old.txt")
                
            # Copiar el archivo actualizado
            shutil.copy2(updated_reqs, current_reqs)
            
            # Actualizar dependencias
            self.log("Instalando dependencias actualizadas...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.log("✅ Dependencias de Python actualizadas exitosamente")
                return True
            else:
                self.log(f"❌ Error actualizando Python: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error en actualización Python: {str(e)}", "ERROR")
            return False
            
    def update_node_dependencies(self):
        """Actualizar dependencias de Node.js"""
        self.log("Actualizando dependencias de Node.js...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            self.log("ERROR: No se encontró el directorio frontend", "ERROR")
            return False
            
        try:
            # Verificar si existe el archivo actualizado
            updated_package = frontend_dir / "package_updated.json"
            if not updated_package.exists():
                self.log("ERROR: No se encontró package_updated.json", "ERROR")
                return False
                
            # Hacer backup del package.json actual
            current_package = frontend_dir / "package.json"
            if current_package.exists():
                shutil.copy2(current_package, self.backup_dir / "package_old.json")
                
            # Copiar el archivo actualizado
            shutil.copy2(updated_package, current_package)
            
            # Limpiar node_modules y package-lock.json
            self.log("Limpiando instalación anterior...")
            node_modules = frontend_dir / "node_modules"
            package_lock = frontend_dir / "package-lock.json"
            
            if node_modules.exists():
                shutil.rmtree(node_modules)
            if package_lock.exists():
                package_lock.unlink()
                
            # Instalar dependencias actualizadas
            self.log("Instalando dependencias actualizadas...")
            result = subprocess.run([
                "npm", "install"
            ], capture_output=True, text=True, cwd=frontend_dir)
            
            if result.returncode == 0:
                self.log("✅ Dependencias de Node.js actualizadas exitosamente")
                return True
            else:
                self.log(f"❌ Error actualizando Node.js: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error en actualización Node.js: {str(e)}", "ERROR")
            return False
            
    def verify_installations(self):
        """Verificar que las instalaciones fueron exitosas"""
        self.log("Verificando instalaciones...")
        
        # Verificar Python
        try:
            result = subprocess.run([
                sys.executable, "-c", "import flask; print(f'Flask {flask.__version__}')"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ {result.stdout.strip()}")
            else:
                self.log("❌ Error verificando Flask", "ERROR")
        except Exception as e:
            self.log(f"❌ Error verificando Python: {str(e)}", "ERROR")
            
        # Verificar Node.js
        try:
            result = subprocess.run([
                "npm", "list", "--depth=0"
            ], capture_output=True, text=True, cwd=self.project_root / "frontend")
            if result.returncode == 0:
                self.log("✅ Dependencias de Node.js verificadas")
            else:
                self.log("❌ Error verificando Node.js", "ERROR")
        except Exception as e:
            self.log(f"❌ Error verificando Node.js: {str(e)}", "ERROR")
            
    def generate_report(self):
        """Generar reporte de actualización"""
        report_file = self.backup_dir / "update_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE ACTUALIZACIÓN DE DEPENDENCIAS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Backup: {self.backup_dir}\n\n")
            
            # Información del sistema
            f.write("INFORMACIÓN DEL SISTEMA:\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Directorio: {self.project_root}\n\n")
            
            # Listar archivos de backup
            f.write("ARCHIVOS DE BACKUP:\n")
            for file in self.backup_dir.iterdir():
                if file.is_file():
                    f.write(f"- {file.name}\n")
                    
        self.log(f"Reporte generado: {report_file}")
        
    def run(self):
        """Ejecutar proceso completo de actualización"""
        self.log("🚀 Iniciando actualización de dependencias del Sistema POS Odata")
        self.log("=" * 60)
        
        # Crear backup
        self.create_backup()
        
        # Actualizar Python
        python_success = self.update_python_dependencies()
        
        # Actualizar Node.js
        node_success = self.update_node_dependencies()
        
        # Verificar instalaciones
        self.verify_installations()
        
        # Generar reporte
        self.generate_report()
        
        # Resumen final
        self.log("=" * 60)
        self.log("📊 RESUMEN DE ACTUALIZACIÓN:")
        self.log(f"Python: {'✅ Exitoso' if python_success else '❌ Falló'}")
        self.log(f"Node.js: {'✅ Exitoso' if node_success else '❌ Falló'}")
        
        if python_success and node_success:
            self.log("🎉 ¡Todas las dependencias fueron actualizadas exitosamente!")
            self.log("💡 Próximos pasos:")
            self.log("   1. Ejecutar tests: python -m pytest")
            self.log("   2. Verificar frontend: cd frontend && npm start")
            self.log("   3. Revisar cambios en el código si es necesario")
        else:
            self.log("⚠️  Algunas actualizaciones fallaron. Revisa los logs arriba.")
            self.log("💡 Puedes restaurar desde el backup si es necesario.")
            
        self.log(f"📁 Backup disponible en: {self.backup_dir}")

if __name__ == "__main__":
    updater = DependencyUpdater()
    updater.run()
