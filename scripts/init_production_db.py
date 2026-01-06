#!/usr/bin/env python3
"""
Script de Inicialización Profesional de Base de Datos
Sistema POS O'Data v2.0.2-enterprise
====================================
Inicializa y valida la base de datos PostgreSQL de producción
con migraciones profesionales y validación de integridad.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User
from app.models.role import Role

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Inicializador profesional de base de datos"""
    
    def __init__(self) -> None:  # type: ignore
        self.app = create_app('production')
        self.errors: list[str] = []
        self.warnings: list[str] = []
        
    def validate_connection(self) -> bool:
        """Validar conexión a la base de datos"""
        logger.info("Validando conexión a la base de datos...")
        
        try:
            with self.app.app_context():
                # Intentar conectar
                db.session.execute(db.text('SELECT 1'))
                logger.info("✅ Conexión a base de datos exitosa")
                return True
        except Exception as e:
            error_msg = f"❌ Error conectando a la base de datos: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def create_tables(self) -> bool:
        """Crear todas las tablas"""
        logger.info("Creando tablas de la base de datos...")
        
        try:
            with self.app.app_context():
                db.create_all()
                logger.info("✅ Tablas creadas exitosamente")
                return True
        except Exception as e:
            error_msg = f"❌ Error creando tablas: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def validate_tables(self) -> bool:
        """Validar que todas las tablas existen"""
        logger.info("Validando estructura de tablas...")
        
        required_tables = [
            'users', 'products', 'sales', 'sale_items', 
            'inventory_movements', 'roles',
            'stores', 'quotations', 'multi_payments'
        ]
        
        missing_tables = []
        
        try:
            with self.app.app_context():
                inspector = db.inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                for table in required_tables:
                    if table not in existing_tables:
                        missing_tables.append(table)
                
                if missing_tables:
                    error_msg = f"❌ Tablas faltantes: {', '.join(missing_tables)}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return False
                else:
                    logger.info("✅ Todas las tablas requeridas existen")
                    return True
        except Exception as e:
            error_msg = f"❌ Error validando tablas: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def validate_indexes(self) -> bool:
        """Validar índices importantes"""
        logger.info("Validando índices de la base de datos...")
        
        try:
            with self.app.app_context():
                inspector = db.inspect(db.engine)
                
                # Verificar índices críticos
                critical_indexes = {
                    'users': ['username', 'email'],
                    'products': ['sku', 'barcode'],
                    'sales': ['created_at', 'user_id'],
                    'inventory_movements': ['product_id']
                }
                
                all_ok = True
                for table_name, columns in critical_indexes.items():
                    indexes = inspector.get_indexes(table_name)
                    index_columns = [idx['column_names'][0] for idx in indexes if idx['column_names']]
                    
                    for col in columns:
                        if col not in index_columns:
                            warning_msg = f"⚠️  Índice faltante: {table_name}.{col}"
                            logger.warning(warning_msg)
                            self.warnings.append(warning_msg)
                            all_ok = False
                
                if all_ok:
                    logger.info("✅ Índices críticos validados")
                
                return True  # No es crítico, solo advertencia
        except Exception as e:
            warning_msg = f"⚠️  Error validando índices: {e}"
            logger.warning(warning_msg)
            self.warnings.append(warning_msg)
            return True  # No crítico
    
    def create_default_data(self) -> bool:
        """Crear datos por defecto si no existen"""
        logger.info("Verificando datos por defecto...")
        
        try:
            with self.app.app_context():
                # Verificar si existe usuario admin
                admin_user = User.query.filter_by(username='admin').first()
                
                if not admin_user:
                    logger.info("Creando usuario administrador por defecto...")
                    admin_user = User(
                        username='admin',
                        email='admin@pos-odata.com',
                        password='admin123'  # Debe cambiarse en producción (mínimo 6 caracteres)
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("✅ Usuario administrador creado (username: admin, password: admin123)")
                    logger.warning("⚠️  IMPORTANTE: Cambiar contraseña del administrador en producción")
                else:
                    logger.info("✅ Usuario administrador ya existe")
                
                # Verificar roles básicos
                from app.models.role import RoleType
                roles_config = {
                    'admin': {
                        'display_name': 'Administrador',
                        'description': 'Rol de administrador con acceso completo',
                        'role_type': RoleType.SUPER_ADMIN,
                        'organization': 'odata'
                    },
                    'manager': {
                        'display_name': 'Gerente',
                        'description': 'Rol de gerente con acceso a gestión',
                        'role_type': RoleType.GLOBAL_ADMIN,
                        'organization': 'odata'
                    },
                    'cashier': {
                        'display_name': 'Cajero',
                        'description': 'Rol de cajero para ventas',
                        'role_type': RoleType.CASHIER,
                        'organization': 'odata'
                    },
                    'viewer': {
                        'display_name': 'Visualizador',
                        'description': 'Rol de solo lectura',
                        'role_type': RoleType.SUPERVISOR,
                        'organization': 'odata'
                    }
                }
                for role_name, role_data in roles_config.items():
                    role = Role.query.filter_by(name=role_name).first()
                    if not role:
                        role = Role(
                            name=role_name,
                            display_name=role_data['display_name'],
                            description=role_data['description'],
                            role_type=role_data['role_type'],
                            organization=role_data['organization']
                        )
                        db.session.add(role)
                        logger.info(f"✅ Rol '{role_name}' creado")
                
                db.session.commit()
                logger.info("✅ Datos por defecto verificados")
                return True
        except Exception as e:
            error_msg = f"❌ Error creando datos por defecto: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def validate_foreign_keys(self) -> bool:
        """Validar integridad referencial"""
        logger.info("Validando integridad referencial...")
        
        try:
            with self.app.app_context():
                # Verificar que las foreign keys están habilitadas
                result = db.session.execute(
                    db.text("SELECT COUNT(*) FROM pg_constraint WHERE contype = 'f'")
                )
                fk_count = result.scalar()
                
                if fk_count > 0:
                    logger.info(f"✅ {fk_count} foreign keys encontradas")
                else:
                    warning_msg = "⚠️  No se encontraron foreign keys"
                    logger.warning(warning_msg)
                    self.warnings.append(warning_msg)
                
                return True
        except Exception as e:
            # Puede fallar si no es PostgreSQL
            logger.debug(f"Validación de foreign keys no aplicable: {e}")
            return True
    
    def generate_report(self) -> Dict[str, any]:  # type: ignore
        """Generar reporte de inicialización"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'errors': self.errors,
            'warnings': self.warnings,
            'success': len(self.errors) == 0
        }
    
    def run(self) -> bool:
        """Ejecutar inicialización completa"""
        logger.info("=" * 60)
        logger.info("INICIALIZACIÓN PROFESIONAL DE BASE DE DATOS")
        logger.info("=" * 60)
        
        steps = [
            ("Validar conexión", self.validate_connection),
            ("Crear tablas", self.create_tables),
            ("Validar tablas", self.validate_tables),
            ("Validar índices", self.validate_indexes),
            ("Crear datos por defecto", self.create_default_data),
            ("Validar foreign keys", self.validate_foreign_keys)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            if not step_func():
                if step_name in ["Validar conexión", "Crear tablas", "Validar tablas"]:
                    logger.error(f"❌ Paso crítico falló: {step_name}")
                    return False
        
        # Generar reporte
        report = self.generate_report()
        
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DE INICIALIZACIÓN")
        logger.info("=" * 60)
        
        if report['success']:
            logger.info("✅ Inicialización completada exitosamente")
        else:
            logger.error("❌ Inicialización completada con errores")
            for error in report['errors']:
                logger.error(f"  - {error}")
        
        if report['warnings']:
            logger.warning("⚠️  Advertencias encontradas:")
            for warning in report['warnings']:
                logger.warning(f"  - {warning}")
        
        return report['success']

def main():
    """Función principal"""
    initializer = DatabaseInitializer()
    success = initializer.run()
    
    if success:
        logger.info("\n🎉 Base de datos lista para producción")
        sys.exit(0)
    else:
        logger.error("\n❌ Error inicializando base de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()

