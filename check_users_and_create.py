"""
Script para verificar usuarios existentes y crear uno si es necesario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def check_and_create_users():
    """Verificar usuarios existentes y crear admin si no existe"""
    app = create_app()
    
    with app.app_context():
        print("👥 VERIFICANDO USUARIOS EN BASE DE DATOS")
        print("=" * 50)
        
        # Verificar usuarios existentes
        users = User.query.all()
        print(f"📊 Usuarios encontrados: {len(users)}")
        
        for user in users:
            print(f"   - {user.username} ({user.email}) - Activo: {user.is_active}")
        
        if len(users) == 0:
            print("\n🔧 CREANDO USUARIO ADMINISTRADOR")
            try:
                admin_user = User(
                    username='admin',
                    email='admin@sabrositas.com',
                    password_hash=generate_password_hash('admin123'),
                    full_name='Administrador Sistema',
                    is_active=True,
                    is_admin=True
                )
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Usuario admin creado exitosamente")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                
            except Exception as e:
                print(f"❌ Error creando usuario: {e}")
                db.session.rollback()
        
        else:
            print("\n🔐 CREDENCIALES SUGERIDAS:")
            for user in users:
                if user.is_active:
                    print(f"   Usuario: {user.username}")
                    print(f"   Prueba con contraseñas: admin123, {user.username}123, admin")

if __name__ == "__main__":
    check_and_create_users()
