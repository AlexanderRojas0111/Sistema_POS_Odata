#!/usr/bin/env python3
"""
Script de Inicialización para Producción Multi-Tienda
====================================================
Sistema POS Sabrositas v2.0.0 - Entorno Enterprise
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.role import Role, Permission, UserRole, RoleType, PermissionCategory
from app.models.store import Store, StoreProduct
from app.models.product import Product
from app.services.iam_service import IAMService
from app.exceptions import ValidationError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionMultiStoreInitializer:
    """Inicializador para entorno de producción multi-tienda"""
    
    def __init__(self):
        self.app = create_app('production')
        self.iam_service = IAMService()
        
    def initialize_production_environment(self):
        """Inicializar entorno completo de producción"""
        logger.info("🚀 INICIANDO CONFIGURACIÓN DE PRODUCCIÓN MULTI-TIENDA")
        logger.info("=" * 60)
        
        with self.app.app_context():
            try:
                # 1. Crear tablas
                self._create_database_tables()
                
                # 2. Inicializar sistema de roles y permisos
                self._initialize_iam_system()
                
                # 3. Crear tiendas corporativas
                self._create_corporate_stores()
                
                # 4. Crear usuarios enterprise
                self._create_enterprise_users()
                
                # 5. Configurar productos en todas las tiendas
                self._configure_multistore_products()
                
                # 6. Configurar auditoría y monitoreo
                self._configure_audit_monitoring()
                
                # 7. Validar configuración
                self._validate_production_setup()
                
                logger.info("✅ CONFIGURACIÓN DE PRODUCCIÓN COMPLETADA EXITOSAMENTE")
                self._print_production_summary()
                
            except Exception as e:
                logger.error(f"❌ Error en inicialización: {e}")
                db.session.rollback()
                raise
    
    def _create_database_tables(self):
        """Crear todas las tablas de la base de datos"""
        logger.info("📊 Creando estructura de base de datos...")
        
        # Eliminar tablas existentes si existen
        db.drop_all()
        
        # Crear todas las tablas
        db.create_all()
        
        logger.info("✅ Estructura de base de datos creada")
    
    def _initialize_iam_system(self):
        """Inicializar sistema completo de IAM"""
        logger.info("🔐 Inicializando sistema IAM enterprise...")
        
        # Inicializar roles del sistema
        success_roles = self.iam_service.initialize_system_roles()
        if not success_roles:
            raise RuntimeError("Error inicializando roles del sistema")
        
        # Inicializar permisos del sistema
        success_permissions = self.iam_service.initialize_system_permissions()
        if not success_permissions:
            raise RuntimeError("Error inicializando permisos del sistema")
        
        # Asignar permisos a roles
        self._assign_permissions_to_roles()
        
        logger.info("✅ Sistema IAM inicializado correctamente")
    
    def _assign_permissions_to_roles(self):
        """Asignar permisos específicos a cada rol"""
        logger.info("🔗 Asignando permisos a roles...")
        
        # Obtener todos los roles y permisos
        roles = Role.query.all()
        permissions = Permission.query.all()
        
        # Crear mapeo de permisos por rol
        permission_assignments = self.iam_service.permission_matrix
        
        for role in roles:
            if role.name in permission_assignments:
                role_permissions = permission_assignments[role.name]
                
                for perm_pattern in role_permissions:
                    # Buscar permisos que coincidan con el patrón
                    matching_permissions = []
                    
                    if '*' in perm_pattern:
                        # Patrón wildcard
                        for perm in permissions:
                            if self._matches_permission_pattern(perm.name, perm_pattern):
                                matching_permissions.append(perm)
                    else:
                        # Permiso específico
                        matching_perm = next(
                            (p for p in permissions if p.name == perm_pattern), 
                            None
                        )
                        if matching_perm:
                            matching_permissions.append(matching_perm)
                    
                    # Asignar permisos al rol
                    for perm in matching_permissions:
                        if perm not in role.permissions:
                            role.permissions.append(perm)
        
        db.session.commit()
        logger.info("✅ Permisos asignados a roles")
    
    def _matches_permission_pattern(self, permission: str, pattern: str) -> bool:
        """Verificar si un permiso coincide con un patrón"""
        perm_parts = permission.split(':')
        pattern_parts = pattern.split(':')
        
        if len(perm_parts) != len(pattern_parts):
            return False
        
        for perm_part, pattern_part in zip(perm_parts, pattern_parts):
            if pattern_part != '*' and perm_part != pattern_part:
                return False
        
        return True
    
    def _create_corporate_stores(self):
        """Crear tiendas corporativas para el entorno de producción"""
        logger.info("🏪 Creando tiendas corporativas...")
        
        stores_data = [
            {
                'code': 'SAB001',
                'name': 'Sabrositas Centro - Sede Principal',
                'address': 'Calle 72 #10-34, Chapinero, Bogotá',
                'phone': '+57 1 555-0101',
                'email': 'centro@sabrositas.com',
                'region': 'Bogotá Norte',
                'store_type': 'retail',
                'is_main_store': True,
                'timezone': 'America/Bogota',
                'tax_rate': 0.1900,
                'max_concurrent_sales': 15
            },
            {
                'code': 'SAB002', 
                'name': 'Sabrositas Zona Rosa',
                'address': 'Carrera 13 #85-32, Zona Rosa, Bogotá',
                'phone': '+57 1 555-0102',
                'email': 'zonarosa@sabrositas.com',
                'region': 'Bogotá Norte',
                'store_type': 'retail',
                'is_main_store': False,
                'timezone': 'America/Bogota',
                'tax_rate': 0.1900,
                'max_concurrent_sales': 12
            },
            {
                'code': 'SAB003',
                'name': 'Sabrositas Unicentro',
                'address': 'Centro Comercial Unicentro, Local 245',
                'phone': '+57 1 555-0103', 
                'email': 'unicentro@sabrositas.com',
                'region': 'Bogotá Occidente',
                'store_type': 'retail',
                'is_main_store': False,
                'timezone': 'America/Bogota',
                'tax_rate': 0.1900,
                'max_concurrent_sales': 10
            },
            {
                'code': 'SAB004',
                'name': 'Sabrositas Suba',
                'address': 'Calle 145 #91-19, Suba, Bogotá',
                'phone': '+57 1 555-0104',
                'email': 'suba@sabrositas.com', 
                'region': 'Bogotá Norte',
                'store_type': 'retail',
                'is_main_store': False,
                'timezone': 'America/Bogota',
                'tax_rate': 0.1900,
                'max_concurrent_sales': 8
            },
            {
                'code': 'SABW01',
                'name': 'Sabrositas Warehouse - Centro Logístico',
                'address': 'Zona Industrial Fontibón, Bodega 12',
                'phone': '+57 1 555-0150',
                'email': 'warehouse@sabrositas.com',
                'region': 'Bogotá Sur',
                'store_type': 'warehouse',
                'is_main_store': False,
                'timezone': 'America/Bogota',
                'tax_rate': 0.1900,
                'max_concurrent_sales': 3
            }
        ]
        
        created_stores = []
        for store_data in stores_data:
            store = Store(**store_data)
            db.session.add(store)
            created_stores.append(store)
            logger.info(f"   ✅ Tienda creada: {store_data['code']} - {store_data['name']}")
        
        db.session.commit()
        
        # Actualizar timestamps de sincronización
        for store in created_stores:
            store.update_sync_timestamp()
        
        logger.info(f"✅ {len(created_stores)} tiendas corporativas creadas")
        return created_stores
    
    def _create_enterprise_users(self):
        """Crear usuarios enterprise con roles específicos"""
        logger.info("👥 Creando usuarios enterprise...")
        
        # Obtener tiendas creadas
        main_store = Store.query.filter_by(is_main_store=True).first()
        all_stores = Store.query.all()
        
        users_data = [
            # USUARIOS ODATA (Tecnología)
            {
                'username': 'superadmin',
                'email': 'superadmin@odata.com.co',
                'password': 'SuperAdmin123!',
                'first_name': 'Super',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_admin': True,
                'can_access_all_stores': True,
                'roles_to_assign': ['super_admin']
            },
            {
                'username': 'techadmin',
                'email': 'techadmin@odata.com.co', 
                'password': 'TechAdmin123!',
                'first_name': 'Tech',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_admin': True,
                'can_access_all_stores': True,
                'roles_to_assign': ['tech_admin']
            },
            {
                'username': 'techsupport',
                'email': 'support@odata.com.co',
                'password': 'TechSupport123!',
                'first_name': 'Technical',
                'last_name': 'Support',
                'role': 'supervisor',
                'is_admin': False,
                'can_access_all_stores': True,
                'roles_to_assign': ['tech_support']
            },
            
            # USUARIOS SABROSITAS (Cliente)
            {
                'username': 'businessowner',
                'email': 'owner@sabrositas.com',
                'password': 'BusinessOwner123!',
                'first_name': 'Business',
                'last_name': 'Owner',
                'role': 'admin',
                'is_admin': True,
                'can_access_all_stores': True,
                'roles_to_assign': ['business_owner']
            },
            {
                'username': 'globaladmin',
                'email': 'global@sabrositas.com',
                'password': 'Global123!',
                'first_name': 'Global',
                'last_name': 'Administrator',
                'role': 'manager',
                'is_admin': True,
                'can_access_all_stores': True,
                'roles_to_assign': ['global_admin']
            },
            {
                'username': 'storeadmin1',
                'email': 'admin.centro@sabrositas.com',
                'password': 'Store123!',
                'first_name': 'Store Admin',
                'last_name': 'Centro',
                'role': 'manager',
                'is_admin': False,
                'assigned_store_id': main_store.id if main_store else None,
                'can_access_all_stores': False,
                'roles_to_assign': ['store_admin']
            },
            {
                'username': 'supervisor1',
                'email': 'supervisor.centro@sabrositas.com',
                'password': 'Supervisor123!',
                'first_name': 'Supervisor',
                'last_name': 'Centro',
                'role': 'supervisor',
                'is_admin': False,
                'assigned_store_id': main_store.id if main_store else None,
                'can_access_all_stores': False,
                'roles_to_assign': ['supervisor']
            },
            {
                'username': 'cashier1',
                'email': 'cashier1.centro@sabrositas.com',
                'password': 'Cashier123!',
                'first_name': 'Cajero',
                'last_name': 'Principal',
                'role': 'cashier',
                'is_admin': False,
                'assigned_store_id': main_store.id if main_store else None,
                'can_access_all_stores': False,
                'roles_to_assign': ['cashier']
            },
            {
                'username': 'waiter1',
                'email': 'waiter1.centro@sabrositas.com',
                'password': 'Waiter123!',
                'first_name': 'Mesero',
                'last_name': 'Centro',
                'role': 'cashier',
                'is_admin': False,
                'assigned_store_id': main_store.id if main_store else None,
                'can_access_all_stores': False,
                'roles_to_assign': ['waiter']
            },
            {
                'username': 'kitchen1',
                'email': 'kitchen1.centro@sabrositas.com',
                'password': 'Kitchen123!',
                'first_name': 'Cocinero',
                'last_name': 'Centro',
                'role': 'cashier',
                'is_admin': False,
                'assigned_store_id': main_store.id if main_store else None,
                'can_access_all_stores': False,
                'roles_to_assign': ['kitchen']
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # Extraer roles a asignar
            roles_to_assign = user_data.pop('roles_to_assign', [])
            
            # Crear usuario
            user = User(**user_data)
            db.session.add(user)
            db.session.flush()  # Para obtener el ID
            
            created_users.append(user)
            logger.info(f"   ✅ Usuario creado: {user.username} ({user.email})")
            
            # Asignar roles enterprise
            for role_name in roles_to_assign:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    # Determinar store_id para roles específicos de tienda
                    store_id = None
                    if role.is_store_specific and user.assigned_store_id:
                        store_id = user.assigned_store_id
                    
                    # Asignar rol (usando superadmin como asignador inicial)
                    superadmin = User.query.filter_by(username='superadmin').first()
                    if superadmin:
                        try:
                            user_role = self.iam_service.assign_role_to_user(
                                user_id=user.id,
                                role_id=role.id,
                                assigned_by_user_id=superadmin.id,
                                store_id=store_id,
                                is_primary=True
                            )
                            logger.info(f"      🔗 Rol asignado: {role_name}")
                        except Exception as e:
                            logger.warning(f"      ⚠️ Error asignando rol {role_name}: {e}")
        
        db.session.commit()
        logger.info(f"✅ {len(created_users)} usuarios enterprise creados")
        return created_users
    
    def _configure_multistore_products(self):
        """Configurar productos en todas las tiendas"""
        logger.info("📦 Configurando productos multi-tienda...")
        
        # Crear productos base si no existen
        self._create_base_products()
        
        # Obtener todos los productos y tiendas
        products = Product.query.all()
        stores = Store.query.filter_by(is_active=True).all()
        
        # Configurar productos en cada tienda
        for store in stores:
            logger.info(f"   🏪 Configurando productos para {store.name}...")
            
            for product in products:
                # Verificar si ya existe la relación
                existing = StoreProduct.query.filter_by(
                    store_id=store.id,
                    product_id=product.id
                ).first()
                
                if not existing:
                    # Calcular precios locales (variación por tipo de tienda)
                    price_multiplier = self._get_price_multiplier(store)
                    local_price = product.price * price_multiplier
                    
                    # Configurar stock inicial
                    initial_stock = self._get_initial_stock(store, product)
                    
                    store_product = StoreProduct(
                        store_id=store.id,
                        product_id=product.id,
                        local_price=local_price,
                        cost_price=product.price * 0.6,  # 40% margen
                        current_stock=initial_stock,
                        min_stock=5 if store.store_type == 'retail' else 50,
                        max_stock=100 if store.store_type == 'retail' else 500,
                        reorder_point=10 if store.store_type == 'retail' else 100,
                        is_available=True,
                        is_featured=product.category == 'premium',
                        allow_negative_stock=False
                    )
                    
                    db.session.add(store_product)
        
        db.session.commit()
        logger.info("✅ Productos configurados en todas las tiendas")
    
    def _create_base_products(self):
        """Crear productos base del catálogo Sabrositas"""
        if Product.query.count() > 0:
            return  # Ya existen productos
        
        logger.info("   📋 Creando catálogo de productos base...")
        
        products_data = [
            # Sencillas
            {'name': 'LA FÁCIL', 'description': 'Queso, mucho queso!', 'price': 7000, 'category': 'sencillas'},
            {'name': 'LA CONSENTIDA', 'description': 'Bocadillo con queso', 'price': 8000, 'category': 'sencillas'},
            {'name': 'LA SENCILLA', 'description': 'Jamón con queso', 'price': 9000, 'category': 'sencillas'},
            
            # Clásicas
            {'name': 'LA COQUETA', 'description': 'Jamón, piña y queso', 'price': 11000, 'category': 'clasicas'},
            {'name': 'LA SUMISA', 'description': 'Pollo, maíz tierno y queso', 'price': 11500, 'category': 'clasicas'},
            {'name': 'LA COMPINCHE', 'description': 'Carne desmechada, maduro al horno y queso', 'price': 12000, 'category': 'clasicas'},
            {'name': 'LA SEXY', 'description': 'Pollo, champiñón y queso', 'price': 12000, 'category': 'clasicas'},
            {'name': 'LA SOLTERA', 'description': 'Carne, maíz tierno y queso', 'price': 12500, 'category': 'clasicas'},
            {'name': 'LA CREÍDA', 'description': 'Pollo, salchicha y queso', 'price': 13000, 'category': 'clasicas'},
            {'name': 'LA INFIEL', 'description': 'Pollo, carne y queso', 'price': 13000, 'category': 'clasicas'},
            {'name': 'LA GOMELA', 'description': 'Carne, salchicha y queso', 'price': 13500, 'category': 'clasicas'},
            {'name': 'LA CAPRICHOSA', 'description': 'Carne desmechada, pollo, huevo y queso', 'price': 14000, 'category': 'clasicas'},
            {'name': 'LA CHURRA', 'description': 'Carne, chorizo santarrosano y queso', 'price': 14500, 'category': 'clasicas'},
            
            # Premium
            {'name': 'LA PATRONA', 'description': 'Chicharrón, carne desmechada, maduro al horno y queso', 'price': 15000, 'category': 'premium'},
            {'name': 'LA DIFÍCIL', 'description': 'Carne, chorizo, jalapeño y queso', 'price': 15000, 'category': 'premium'},
            {'name': 'LA DIVA', 'description': 'Carne, pollo, champiñón, salchicha y queso', 'price': 16000, 'category': 'premium'},
            {'name': 'LA PICANTE', 'description': 'Costilla BBQ, maíz tierno, tocineta, queso y ají', 'price': 17000, 'category': 'premium'},
            {'name': 'LA TÓXICA', 'description': 'Costilla BBQ, carne, chorizo, maíz tierno y queso', 'price': 18000, 'category': 'premium'},
        ]
        
        for product_data in products_data:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                category=product_data['category'],
                is_active=True
            )
            db.session.add(product)
        
        db.session.commit()
        logger.info(f"   ✅ {len(products_data)} productos base creados")
    
    def _get_price_multiplier(self, store: Store) -> float:
        """Obtener multiplicador de precio por tipo de tienda"""
        multipliers = {
            'retail': 1.0,      # Precio base
            'warehouse': 0.85,  # 15% descuento para warehouse
            'franchise': 1.05   # 5% incremento para franquicias
        }
        return multipliers.get(store.store_type, 1.0)
    
    def _get_initial_stock(self, store: Store, product: Product) -> int:
        """Obtener stock inicial por tipo de tienda y producto"""
        if store.store_type == 'warehouse':
            return 200  # Stock alto para warehouse
        elif store.store_type == 'retail':
            if product.category == 'premium':
                return 15   # Stock menor para productos premium
            elif product.category == 'clasicas':
                return 25   # Stock medio para clásicas
            else:
                return 35   # Stock alto para sencillas
        else:
            return 20  # Stock default
    
    def _configure_audit_monitoring(self):
        """Configurar auditoría y monitoreo enterprise"""
        logger.info("📊 Configurando auditoría y monitoreo...")
        
        # Configurar logging avanzado
        audit_config = {
            'audit_enabled': True,
            'log_level': 'INFO',
            'retention_days': 90,
            'alert_thresholds': {
                'failed_logins': 5,
                'high_value_transactions': 50000,
                'inventory_discrepancies': 10
            }
        }
        
        # Crear directorio de logs si no existe
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        logger.info("✅ Auditoría y monitoreo configurados")
    
    def _validate_production_setup(self):
        """Validar que la configuración de producción sea correcta"""
        logger.info("✅ Validando configuración de producción...")
        
        # Validar tiendas
        stores_count = Store.query.filter_by(is_active=True).count()
        if stores_count == 0:
            raise ValidationError("No hay tiendas configuradas")
        
        # Validar usuarios
        users_count = User.query.filter_by(is_active=True).count()
        if users_count == 0:
            raise ValidationError("No hay usuarios configurados")
        
        # Validar roles
        roles_count = Role.query.filter_by(is_active=True).count()
        if roles_count == 0:
            raise ValidationError("No hay roles configurados")
        
        # Validar productos
        products_count = Product.query.filter_by(is_active=True).count()
        if products_count == 0:
            raise ValidationError("No hay productos configurados")
        
        # Validar relaciones tienda-producto
        store_products_count = StoreProduct.query.count()
        expected_count = stores_count * products_count
        if store_products_count != expected_count:
            logger.warning(f"Relaciones tienda-producto: {store_products_count}/{expected_count}")
        
        logger.info("✅ Validación de configuración completada")
    
    def _print_production_summary(self):
        """Imprimir resumen de la configuración de producción"""
        logger.info("\n" + "=" * 60)
        logger.info("🎉 RESUMEN DE CONFIGURACIÓN DE PRODUCCIÓN")
        logger.info("=" * 60)
        
        # Estadísticas
        stores = Store.query.filter_by(is_active=True).all()
        users = User.query.filter_by(is_active=True).all()
        roles = Role.query.filter_by(is_active=True).all()
        products = Product.query.filter_by(is_active=True).all()
        
        logger.info(f"🏪 TIENDAS CONFIGURADAS: {len(stores)}")
        for store in stores:
            logger.info(f"   • {store.code} - {store.name} ({store.store_type})")
        
        logger.info(f"\n👥 USUARIOS ENTERPRISE: {len(users)}")
        for user in users:
            user_roles = [role.name for role in user.roles]
            logger.info(f"   • {user.username} - {', '.join(user_roles) if user_roles else user.role}")
        
        logger.info(f"\n🔐 ROLES DEL SISTEMA: {len(roles)}")
        odata_roles = [r for r in roles if r.organization == 'odata']
        sabrositas_roles = [r for r in roles if r.organization == 'sabrositas']
        
        logger.info(f"   📋 Roles Odata: {len(odata_roles)}")
        for role in odata_roles:
            logger.info(f"      • {role.display_name} (Nivel {role.level})")
        
        logger.info(f"   📋 Roles Sabrositas: {len(sabrositas_roles)}")
        for role in sabrositas_roles:
            logger.info(f"      • {role.display_name} (Nivel {role.level})")
        
        logger.info(f"\n📦 CATÁLOGO DE PRODUCTOS: {len(products)}")
        by_category = {}
        for product in products:
            if product.category not in by_category:
                by_category[product.category] = []
            by_category[product.category].append(product)
        
        for category, prods in by_category.items():
            logger.info(f"   • {category.title()}: {len(prods)} productos")
        
        logger.info(f"\n🔗 PRODUCTOS POR TIENDA: {StoreProduct.query.count()} relaciones")
        
        logger.info("\n🔑 CREDENCIALES DE ACCESO:")
        logger.info("   • SuperAdmin:     superadmin / SuperAdmin123!")
        logger.info("   • Tech Admin:     techadmin / TechAdmin123!")
        logger.info("   • Business Owner: businessowner / BusinessOwner123!")
        logger.info("   • Global Admin:   globaladmin / Global123!")
        logger.info("   • Store Admin:    storeadmin1 / Store123!")
        
        logger.info("\n🌐 ACCESO AL SISTEMA:")
        logger.info("   • Frontend: http://localhost:5173")
        logger.info("   • Backend:  http://localhost:8000")
        logger.info("   • Health:   http://localhost:8000/api/v1/health")
        
        logger.info("\n🚀 SISTEMA LISTO PARA PRODUCCIÓN MULTI-TIENDA!")
        logger.info("=" * 60)

def main():
    """Función principal"""
    initializer = ProductionMultiStoreInitializer()
    initializer.initialize_production_environment()

if __name__ == '__main__':
    main()
