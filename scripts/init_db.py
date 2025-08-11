from app import create_app
from app.core.database import db
from app.models.user import User, UserRole

def init_db():
    """Inicializa la base de datos con datos básicos"""
    app = create_app('development')
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario administrador por defecto
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role=UserRole.ADMIN,
                is_active=True
            )
            admin.set_password('admin123')  # Cambiar en producción
            db.session.add(admin)
            
            # Crear usuario empleado de ejemplo
            employee = User(
                username='employee',
                email='employee@example.com',
                role=UserRole.EMPLOYEE,
                is_active=True
            )
            employee.set_password('employee123')  # Cambiar en producción
            db.session.add(employee)
            
            db.session.commit()
            print("Usuarios iniciales creados.")
        else:
            print("Los usuarios ya existen.")

if __name__ == '__main__':
    init_db() 