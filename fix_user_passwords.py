"""
Script para corregir los hashes de contraseñas de todos los usuarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def fix_all_user_passwords():
    """Corregir hashes de contraseñas para todos los usuarios"""
    app = create_app()
    
    with app.app_context():
        print("🔧 CORRIGIENDO HASHES DE CONTRASEÑAS")
        print("=" * 60)
        
        # Obtener todos los usuarios
        users = User.query.all()
        print(f"📊 Usuarios encontrados: {len(users)}")
        
        # Definir contraseñas por defecto para cada usuario
        default_passwords = {
            'superadmin': 'admin123',
            'techadmin': 'admin123',
            'support': 'admin123',
            'owner': 'admin123',
            'globaladmin': 'admin123',
            'storeadmin1': 'admin123',
            'cashier1': 'cashier123',
            'waiter1': 'waiter123',
            'kitchen1': 'kitchen123',
            'purchasing1': 'purchasing123',
            'admin': 'admin123'
        }
        
        fixed_count = 0
        
        for user in users:
            try:
                # Obtener contraseña por defecto
                password = default_passwords.get(user.username, 'admin123')
                
                # Generar nuevo hash
                new_hash = generate_password_hash(password)
                
                # Actualizar usuario
                user.password_hash = new_hash
                
                print(f"✅ {user.username}: contraseña actualizada (password: {password})")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error actualizando {user.username}: {e}")
        
        try:
            # Guardar cambios
            db.session.commit()
            print(f"\n🎉 ÉXITO: {fixed_count} usuarios actualizados")
            print("\n🔐 CREDENCIALES ACTUALIZADAS:")
            print("-" * 40)
            
            for username, password in default_passwords.items():
                if any(u.username == username for u in users):
                    print(f"   {username}: {password}")
                    
        except Exception as e:
            print(f"\n❌ Error guardando cambios: {e}")
            db.session.rollback()

def create_test_user():
    """Crear usuario de prueba adicional"""
    app = create_app()
    
    with app.app_context():
        print(f"\n👤 CREANDO USUARIO DE PRUEBA")
        print("-" * 40)
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("⚠️ Usuario 'testuser' ya existe")
            return
        
        try:
            test_user = User(
                username='testuser',
                email='test@sabrositas.com',
                password_hash=generate_password_hash('test123'),
                full_name='Usuario de Prueba',
                is_active=True,
                is_admin=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuario 'testuser' creado")
            print("   Usuario: testuser")
            print("   Contraseña: test123")
            
        except Exception as e:
            print(f"❌ Error creando usuario de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_all_user_passwords()
    create_test_user()
    
    print(f"\n🎯 RESUMEN:")
    print("=" * 60)
    print("✅ Todos los hashes de contraseñas han sido regenerados")
    print("✅ Las credenciales están listas para usar")
    print("✅ El sistema de autenticación debería funcionar ahora")
    print("\n💡 PRUEBA CON:")
    print("   Usuario: superadmin | Contraseña: admin123")
    print("   Usuario: testuser   | Contraseña: test123")

Script para corregir los hashes de contraseñas de todos los usuarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def fix_all_user_passwords():
    """Corregir hashes de contraseñas para todos los usuarios"""
    app = create_app()
    
    with app.app_context():
        print("🔧 CORRIGIENDO HASHES DE CONTRASEÑAS")
        print("=" * 60)
        
        # Obtener todos los usuarios
        users = User.query.all()
        print(f"📊 Usuarios encontrados: {len(users)}")
        
        # Definir contraseñas por defecto para cada usuario
        default_passwords = {
            'superadmin': 'admin123',
            'techadmin': 'admin123',
            'support': 'admin123',
            'owner': 'admin123',
            'globaladmin': 'admin123',
            'storeadmin1': 'admin123',
            'cashier1': 'cashier123',
            'waiter1': 'waiter123',
            'kitchen1': 'kitchen123',
            'purchasing1': 'purchasing123',
            'admin': 'admin123'
        }
        
        fixed_count = 0
        
        for user in users:
            try:
                # Obtener contraseña por defecto
                password = default_passwords.get(user.username, 'admin123')
                
                # Generar nuevo hash
                new_hash = generate_password_hash(password)
                
                # Actualizar usuario
                user.password_hash = new_hash
                
                print(f"✅ {user.username}: contraseña actualizada (password: {password})")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error actualizando {user.username}: {e}")
        
        try:
            # Guardar cambios
            db.session.commit()
            print(f"\n🎉 ÉXITO: {fixed_count} usuarios actualizados")
            print("\n🔐 CREDENCIALES ACTUALIZADAS:")
            print("-" * 40)
            
            for username, password in default_passwords.items():
                if any(u.username == username for u in users):
                    print(f"   {username}: {password}")
                    
        except Exception as e:
            print(f"\n❌ Error guardando cambios: {e}")
            db.session.rollback()

def create_test_user():
    """Crear usuario de prueba adicional"""
    app = create_app()
    
    with app.app_context():
        print(f"\n👤 CREANDO USUARIO DE PRUEBA")
        print("-" * 40)
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("⚠️ Usuario 'testuser' ya existe")
            return
        
        try:
            test_user = User(
                username='testuser',
                email='test@sabrositas.com',
                password_hash=generate_password_hash('test123'),
                full_name='Usuario de Prueba',
                is_active=True,
                is_admin=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuario 'testuser' creado")
            print("   Usuario: testuser")
            print("   Contraseña: test123")
            
        except Exception as e:
            print(f"❌ Error creando usuario de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_all_user_passwords()
    create_test_user()
    
    print(f"\n🎯 RESUMEN:")
    print("=" * 60)
    print("✅ Todos los hashes de contraseñas han sido regenerados")
    print("✅ Las credenciales están listas para usar")
    print("✅ El sistema de autenticación debería funcionar ahora")
    print("\n💡 PRUEBA CON:")
    print("   Usuario: superadmin | Contraseña: admin123")
    print("   Usuario: testuser   | Contraseña: test123")
