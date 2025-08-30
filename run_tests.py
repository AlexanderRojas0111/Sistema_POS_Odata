#!/usr/bin/env python3
"""
Script principal para ejecutar pruebas automatizadas del Sistema POS O'data
Autor: Ingeniero de Software Senior
Versión: 2.0.0
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_system_status():
    """Verificar que el sistema esté funcionando antes de ejecutar pruebas"""
    print("🔍 Verificando estado del sistema...")
    
    # Verificar backend
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando en http://127.0.0.1:8000")
        else:
            print("⚠️ Backend respondiendo pero con código:", response.status_code)
    except Exception as e:
        print("❌ Backend no disponible:", e)
        print("💡 Asegúrate de que el servidor esté corriendo: python run_server_8000.py")
        return False
    
    # Verificar frontend (opcional)
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend funcionando en http://localhost:3000")
        else:
            print("⚠️ Frontend respondiendo pero con código:", response.status_code)
    except Exception as e:
        print("⚠️ Frontend no disponible:", e)
        print("💡 Para pruebas completas, inicia el frontend: cd frontend && npm start")
    
    # Verificar base de datos
    db_path = Path("pos_odata_dev.db")
    if db_path.exists():
        print("✅ Base de datos SQLite encontrada")
    else:
        print("⚠️ Base de datos no encontrada")
        print("💡 Ejecuta las migraciones si es necesario")
    
    return True

def run_tests(category=None, coverage=False, parallel=False, html_report=False):
    """Ejecutar las pruebas según la categoría especificada"""
    
    # Comando base
    cmd = ["pytest"]
    
    # Agregar opciones
    if category:
        cmd.extend([f"tests/{category}/", "-v", "-m", category])
    else:
        cmd.extend(["tests/", "-v"])
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-fail-under=80"])
    
    if parallel:
        cmd.extend(["-n", "auto", "--dist=loadfile"])
    
    if html_report:
        cmd.extend(["--html=reports/test_report.html", "--self-contained-html"])
    
    # Crear directorio de reportes si no existe
    if html_report:
        os.makedirs("reports", exist_ok=True)
    
    print(f"🚀 Ejecutando pruebas: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Error: pytest no encontrado")
        print("💡 Instala pytest: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Ejecutar pruebas automatizadas del Sistema POS O'data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py                    # Ejecutar todas las pruebas
  python run_tests.py --backend         # Solo pruebas de backend
  python run_tests.py --frontend        # Solo pruebas de frontend
  python run_tests.py --database        # Solo pruebas de base de datos
  python run_tests.py --integration     # Solo pruebas de integración
  python run_tests.py --performance     # Solo pruebas de rendimiento
  python run_tests.py --coverage        # Con reporte de cobertura
  python run_tests.py --parallel        # Ejecutar en paralelo
  python run_tests.py --html            # Generar reporte HTML
  python run_tests.py --all             # Todas las opciones
        """
    )
    
    parser.add_argument("--backend", action="store_true", help="Ejecutar solo pruebas de backend")
    parser.add_argument("--frontend", action="store_true", help="Ejecutar solo pruebas de frontend")
    parser.add_argument("--database", action="store_true", help="Ejecutar solo pruebas de base de datos")
    parser.add_argument("--integration", action="store_true", help="Ejecutar solo pruebas de integración")
    parser.add_argument("--performance", action="store_true", help="Ejecutar solo pruebas de rendimiento")
    parser.add_argument("--coverage", action="store_true", help="Incluir reporte de cobertura")
    parser.add_argument("--parallel", action="store_true", help="Ejecutar pruebas en paralelo")
    parser.add_argument("--html", action="store_true", help="Generar reporte HTML")
    parser.add_argument("--all", action="store_true", help="Todas las opciones habilitadas")
    parser.add_argument("--quick", action="store_true", help="Ejecutar solo pruebas rápidas (sin frontend)")
    
    args = parser.parse_args()
    
    print("🧪 SISTEMA POS ODATA - FRAMEWORK DE PRUEBAS AUTOMATIZADAS")
    print("=" * 60)
    print("Versión: 2.0.0")
    print("Autor: Ingeniero de Software Senior")
    print("=" * 60)
    
    # Verificar estado del sistema
    if not check_system_status():
        print("\n❌ No se puede continuar. Verifica el estado del sistema.")
        sys.exit(1)
    
    # Determinar categoría
    category = None
    if args.backend:
        category = "backend"
    elif args.frontend:
        category = "frontend"
    elif args.database:
        category = "database"
    elif args.integration:
        category = "integration"
    elif args.performance:
        category = "performance"
    
    # Configurar opciones
    coverage = args.coverage or args.all
    parallel = args.parallel or args.all
    html_report = args.html or args.all
    
    # Modo rápido (sin frontend)
    if args.quick:
        if category == "frontend" or category == "integration":
            print("⚠️ Modo rápido: saltando pruebas de frontend")
            if category == "frontend":
                category = "backend"  # Cambiar a backend
            elif category == "integration":
                category = "database"  # Cambiar a database
    
    print(f"\n🎯 Categoría seleccionada: {category or 'Todas'}")
    print(f"📊 Cobertura: {'Sí' if coverage else 'No'}")
    print(f"⚡ Paralelo: {'Sí' if parallel else 'No'}")
    print(f"🌐 Reporte HTML: {'Sí' if html_report else 'No'}")
    print("=" * 60)
    
    # Ejecutar pruebas
    success = run_tests(category, coverage, parallel, html_report)
    
    # Resultado final
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El sistema cumple con los estándares de calidad")
    else:
        print("❌ Algunas pruebas fallaron")
        print("🔍 Revisa los logs para identificar problemas")
    
    print("=" * 60)
    
    # Información adicional
    if html_report:
        print(f"📊 Reporte HTML generado: reports/test_report.html")
    
    if coverage:
        print(f"📈 Reporte de cobertura: reports/coverage/index.html")
    
    print("\n💡 Para más opciones: python run_tests.py --help")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
