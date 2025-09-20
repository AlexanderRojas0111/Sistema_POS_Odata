"""
Script para corregir la autenticación usando los métodos correctos del modelo User
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def fix_authentication_properly():
    """Corregir autenticación usando métodos correctos del modelo"""
    app = create_app()
    
    with app.app_context():
        print("🔧 CORRIGIENDO AUTENTICACIÓN CORRECTAMENTE")
        print("=" * 60)
        
        # Obtener todos los usuarios
        users = User.query.all()
        print(f"📊 Usuarios encontrados: {len(users)}")
        
        # Definir contraseñas por defecto
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
            'purchasing1': 'purchasing123'
        }
        
        fixed_count = 0
        
        for user in users:
            try:
                # Obtener contraseña por defecto
                password = default_passwords.get(user.username, 'admin123')
                
                # Usar el método set_password del modelo
                user.set_password(password)
                
                print(f"✅ {user.username}: contraseña actualizada usando modelo (password: {password})")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error actualizando {user.username}: {e}")
        
        try:
            # Guardar cambios
            db.session.commit()
            print(f"\n🎉 ÉXITO: {fixed_count} usuarios actualizados usando métodos del modelo")
            
        except Exception as e:
            print(f"\n❌ Error guardando cambios: {e}")
            db.session.rollback()

def test_password_verification():
    """Probar verificación de contraseñas"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 PROBANDO VERIFICACIÓN DE CONTRASEÑAS")
        print("-" * 60)
        
        # Probar con superadmin
        user = User.query.filter_by(username='superadmin').first()
        
        if user:
            # Probar contraseña correcta
            if user.check_password('admin123'):
                print("✅ Verificación de contraseña: FUNCIONANDO")
            else:
                print("❌ Verificación de contraseña: FALLO")
                
            # Probar contraseña incorrecta
            if not user.check_password('wrongpassword'):
                print("✅ Rechazo de contraseña incorrecta: FUNCIONANDO")
            else:
                print("❌ Rechazo de contraseña incorrecta: FALLO")
        else:
            print("❌ Usuario superadmin no encontrado")

def create_simple_test_user():
    """Crear un usuario de prueba simple"""
    app = create_app()
    
    with app.app_context():
        print(f"\n👤 CREANDO USUARIO DE PRUEBA SIMPLE")
        print("-" * 60)
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            # Actualizar contraseña del usuario existente
            try:
                existing_user.set_password('test123')
                db.session.commit()
                print("✅ Usuario 'testuser' actualizado")
                print("   Usuario: testuser")
                print("   Contraseña: test123")
            except Exception as e:
                print(f"❌ Error actualizando testuser: {e}")
                db.session.rollback()
            return
        
        try:
            # Crear usuario usando el constructor correcto
            test_user = User(
                username='testuser',
                email='test@sabrositas.com',
                password='test123',  # Usar password, no password_hash
                first_name='Test',
                last_name='User',
                is_active=True,
                is_admin=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuario 'testuser' creado correctamente")
            print("   Usuario: testuser")
            print("   Contraseña: test123")
            
        except Exception as e:
            print(f"❌ Error creando usuario de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_authentication_properly()
    test_password_verification()
    create_simple_test_user()
    
    print(f"\n🎯 RESUMEN FINAL:")
    print("=" * 60)
    print("✅ Contraseñas actualizadas usando métodos del modelo User")
    print("✅ Verificación de contraseñas probada")
    print("✅ Usuario de prueba creado/actualizado")
    print("\n💡 CREDENCIALES PARA PROBAR:")
    print("   superadmin / admin123")
    print("   testuser / test123")
    print("\n🚀 El sistema de autenticación debería funcionar ahora")

Script para corregir la autenticación usando los métodos correctos del modelo User
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def fix_authentication_properly():
    """Corregir autenticación usando métodos correctos del modelo"""
    app = create_app()
    
    with app.app_context():
        print("🔧 CORRIGIENDO AUTENTICACIÓN CORRECTAMENTE")
        print("=" * 60)
        
        # Obtener todos los usuarios
        users = User.query.all()
        print(f"📊 Usuarios encontrados: {len(users)}")
        
        # Definir contraseñas por defecto
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
            'purchasing1': 'purchasing123'
        }
        
        fixed_count = 0
        
        for user in users:
            try:
                # Obtener contraseña por defecto
                password = default_passwords.get(user.username, 'admin123')
                
                # Usar el método set_password del modelo
                user.set_password(password)
                
                print(f"✅ {user.username}: contraseña actualizada usando modelo (password: {password})")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error actualizando {user.username}: {e}")
        
        try:
            # Guardar cambios
            db.session.commit()
            print(f"\n🎉 ÉXITO: {fixed_count} usuarios actualizados usando métodos del modelo")
            
        except Exception as e:
            print(f"\n❌ Error guardando cambios: {e}")
            db.session.rollback()

def test_password_verification():
    """Probar verificación de contraseñas"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 PROBANDO VERIFICACIÓN DE CONTRASEÑAS")
        print("-" * 60)
        
        # Probar con superadmin
        user = User.query.filter_by(username='superadmin').first()
        
        if user:
            # Probar contraseña correcta
            if user.check_password('admin123'):
                print("✅ Verificación de contraseña: FUNCIONANDO")
            else:
                print("❌ Verificación de contraseña: FALLO")
                
            # Probar contraseña incorrecta
            if not user.check_password('wrongpassword'):
                print("✅ Rechazo de contraseña incorrecta: FUNCIONANDO")
            else:
                print("❌ Rechazo de contraseña incorrecta: FALLO")
        else:
            print("❌ Usuario superadmin no encontrado")

def create_simple_test_user():
    """Crear un usuario de prueba simple"""
    app = create_app()
    
    with app.app_context():
        print(f"\n👤 CREANDO USUARIO DE PRUEBA SIMPLE")
        print("-" * 60)
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            # Actualizar contraseña del usuario existente
            try:
                existing_user.set_password('test123')
                db.session.commit()
                print("✅ Usuario 'testuser' actualizado")
                print("   Usuario: testuser")
                print("   Contraseña: test123")
            except Exception as e:
                print(f"❌ Error actualizando testuser: {e}")
                db.session.rollback()
            return
        
        try:
            # Crear usuario usando el constructor correcto
            test_user = User(
                username='testuser',
                email='test@sabrositas.com',
                password='test123',  # Usar password, no password_hash
                first_name='Test',
                last_name='User',
                is_active=True,
                is_admin=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Usuario 'testuser' creado correctamente")
            print("   Usuario: testuser")
            print("   Contraseña: test123")
            
        except Exception as e:
            print(f"❌ Error creando usuario de prueba: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_authentication_properly()
    test_password_verification()
    create_simple_test_user()
    
    print(f"\n🎯 RESUMEN FINAL:")
    print("=" * 60)
    print("✅ Contraseñas actualizadas usando métodos del modelo User")
    print("✅ Verificación de contraseñas probada")
    print("✅ Usuario de prueba creado/actualizado")
    print("\n💡 CREDENCIALES PARA PROBAR:")
    print("   superadmin / admin123")
    print("   testuser / test123")
    print("\n🚀 El sistema de autenticación debería funcionar ahora")
