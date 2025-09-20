"""
Script para resetear la contraseña del usuario admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """Resetear contraseña del usuario admin"""
    app = create_app()
    
    with app.app_context():
        print("🔧 RESETEANDO CONTRASEÑA DE ADMINISTRADOR")
        print("=" * 50)
        
        # Buscar usuario superadmin
        admin_user = User.query.filter_by(username='superadmin').first()
        
        if admin_user:
            # Resetear contraseña
            new_password = 'admin123'
            admin_user.password_hash = generate_password_hash(new_password)
            
            try:
                db.session.commit()
                print("✅ Contraseña reseteada exitosamente")
                print(f"   Usuario: superadmin")
                print(f"   Nueva contraseña: {new_password}")
                
                # Verificar el hash
                print(f"   Hash generado: {admin_user.password_hash[:50]}...")
                
            except Exception as e:
                print(f"❌ Error reseteando contraseña: {e}")
                db.session.rollback()
        else:
            print("❌ Usuario superadmin no encontrado")
            
            # Crear nuevo usuario admin
            print("\n🔧 CREANDO NUEVO USUARIO ADMIN")
            try:
                new_admin = User(
                    username='admin',
                    email='admin@sabrositas.com',
                    password_hash=generate_password_hash('admin123'),
                    full_name='Administrador del Sistema',
                    is_active=True,
                    is_admin=True
                )
                
                db.session.add(new_admin)
                db.session.commit()
                
                print("✅ Nuevo usuario admin creado")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                
            except Exception as e:
                print(f"❌ Error creando usuario: {e}")
                db.session.rollback()

if __name__ == "__main__":
    reset_admin_password()
