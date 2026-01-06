#!/usr/bin/env python3
"""
Script para Cambiar Contraseña del Administrador
Sistema POS O'Data v2.0.2-enterprise
====================================
Cambia la contraseña del usuario administrador de forma segura.
"""

import sys
import getpass
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User

def change_admin_password():
    """Cambiar contraseña del administrador"""
    app = create_app('production')
    
    with app.app_context():
        # Buscar usuario admin
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ Error: Usuario 'admin' no encontrado")
            return False
        
        print(f"✅ Usuario encontrado: {admin_user.username} ({admin_user.email})")
        print("\n⚠️  IMPORTANTE: La nueva contraseña debe tener al menos 6 caracteres")
        
        # Solicitar nueva contraseña
        while True:
            new_password = getpass.getpass("Ingrese la nueva contraseña: ")
            if len(new_password) < 6:
                print("❌ Error: La contraseña debe tener al menos 6 caracteres")
                continue
            
            confirm_password = getpass.getpass("Confirme la nueva contraseña: ")
            if new_password != confirm_password:
                print("❌ Error: Las contraseñas no coinciden")
                continue
            
            break
        
        try:
            # Cambiar contraseña
            admin_user.set_password(new_password)
            db.session.commit()
            
            print("\n✅ Contraseña cambiada exitosamente")
            print(f"   Usuario: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Fecha de actualización: {admin_user.updated_at}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error cambiando contraseña: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("CAMBIO DE CONTRASEÑA DEL ADMINISTRADOR")
    print("Sistema POS O'Data v2.0.2-enterprise")
    print("=" * 60)
    print()
    
    success = change_admin_password()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso falló")
        sys.exit(1)

