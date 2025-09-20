"""
Script para diagnosticar blueprints registrados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def diagnose_blueprints():
    """Diagnosticar blueprints registrados en la aplicación"""
    print("🔍 DIAGNOSTICANDO BLUEPRINTS REGISTRADOS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print(f"📊 Total de blueprints registrados: {len(app.blueprints)}")
        print("\n📋 Lista de blueprints:")
        
        for name, blueprint in app.blueprints.items():
            print(f"   - {name}: {blueprint.url_prefix}")
            
            # Mostrar rutas del blueprint
            rules = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith(name + '.')]
            if rules:
                print(f"     Rutas ({len(rules)}):")
                for rule in rules[:5]:  # Mostrar máximo 5 rutas
                    print(f"       • {rule.rule} [{', '.join(rule.methods)}]")
                if len(rules) > 5:
                    print(f"       ... y {len(rules) - 5} rutas más")
            else:
                print("     Sin rutas registradas")
        
        # Buscar específicamente rutas de reportes
        print(f"\n🔍 BUSCANDO RUTAS DE REPORTES:")
        report_rules = [rule for rule in app.url_map.iter_rules() if 'report' in rule.rule.lower()]
        
        if report_rules:
            print(f"   ✅ Encontradas {len(report_rules)} rutas de reportes:")
            for rule in report_rules:
                print(f"     • {rule.rule} [{', '.join(rule.methods)}] -> {rule.endpoint}")
        else:
            print("   ❌ No se encontraron rutas de reportes")
        
        # Verificar blueprint específico
        if 'simple_reports' in app.blueprints:
            print(f"\n✅ Blueprint 'simple_reports' está registrado")
            bp = app.blueprints['simple_reports']
            print(f"   URL prefix: {bp.url_prefix}")
        else:
            print(f"\n❌ Blueprint 'simple_reports' NO está registrado")

if __name__ == "__main__":
    diagnose_blueprints()
