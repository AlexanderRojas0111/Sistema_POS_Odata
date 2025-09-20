"""
Sync Service - Sistema de Sincronización Multi-Sede
==================================================
Servicio para sincronización de datos entre tiendas Sabrositas.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import redis
from app import db
from app.models.store import Store, StoreProduct
from app.models.product import Product
from app.models.user import User
from app.models.inventory_transfer import InventoryTransfer
from app.services.store_service import StoreService
from app.exceptions import SyncError, ValidationError
import threading
import time

logger = logging.getLogger(__name__)

class SyncService:
    """Servicio de sincronización entre tiendas"""
    
    def __init__(self, redis_client=None):
        self.store_service = StoreService()
        self.redis_client = redis_client or self._get_redis_client()
        self.sync_lock = threading.Lock()
        self.sync_status = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    def _get_redis_client(self):
        """Obtener cliente Redis para caching y queues"""
        try:
            import os
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # Verificar conexión
            client.ping()
            logger.info("✅ Conexión Redis establecida para sincronización")
            return client
            
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible, usando memoria: {e}")
            return None
    
    def queue_sync_operation(self, operation_type: str, store_id: int, data: Dict[str, Any]):
        """Encolar operación de sincronización"""
        try:
            if not self.redis_client:
                # Procesar inmediatamente si no hay Redis
                return self._process_sync_operation(operation_type, store_id, data)
            
            operation = {
                'type': operation_type,
                'store_id': store_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'retry_count': 0
            }
            
            queue_key = f"sync_queue:store:{store_id}"
            self.redis_client.lpush(queue_key, json.dumps(operation))
            
            # Notificar a workers
            self.redis_client.publish('sync_channel', json.dumps({
                'action': 'new_operation',
                'store_id': store_id,
                'operation_type': operation_type
            }))
            
            logger.info(f"Operación de sincronización encolada: {operation_type} para tienda {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error encolando operación de sincronización: {e}")
            # Fallback: procesar inmediatamente
            return self._process_sync_operation(operation_type, store_id, data)
    
    def _process_sync_operation(self, operation_type: str, store_id: int, data: Dict[str, Any]) -> bool:
        """Procesar operación de sincronización"""
        try:
            if operation_type == 'product_update':
                return self._sync_product_update(store_id, data)
            elif operation_type == 'inventory_adjustment':
                return self._sync_inventory_adjustment(store_id, data)
            elif operation_type == 'price_update':
                return self._sync_price_update(store_id, data)
            elif operation_type == 'store_config':
                return self._sync_store_config(store_id, data)
            elif operation_type == 'transfer_notification':
                return self._sync_transfer_notification(store_id, data)
            else:
                logger.warning(f"Tipo de operación desconocido: {operation_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error procesando operación {operation_type}: {e}")
            return False
    
    def _sync_product_update(self, store_id: int, data: Dict[str, Any]) -> bool:
        """Sincronizar actualización de producto"""
        try:
            product_id = data.get('product_id')
            updates = data.get('updates', {})
            
            if not product_id:
                raise ValidationError("product_id requerido para sincronización")
            
            # Obtener producto y relación con tienda
            store_product = StoreProduct.query.filter_by(
                store_id=store_id,
                product_id=product_id
            ).first()
            
            if not store_product:
                logger.warning(f"Producto {product_id} no encontrado en tienda {store_id}")
                return False
            
            # Aplicar actualizaciones
            for field, value in updates.items():
                if hasattr(store_product, field):
                    setattr(store_product, field, value)
            
            store_product.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Actualizar cache
            self._update_product_cache(store_id, product_id, store_product.to_dict())
            
            logger.info(f"Producto {product_id} sincronizado en tienda {store_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando producto: {e}")
            return False
    
    def _sync_inventory_adjustment(self, store_id: int, data: Dict[str, Any]) -> bool:
        """Sincronizar ajuste de inventario"""
        try:
            product_id = data.get('product_id')
            quantity_change = data.get('quantity_change', 0)
            reason = data.get('reason', 'sync_adjustment')
            
            if not product_id or quantity_change == 0:
                return True  # No hay cambio
            
            store_product = StoreProduct.query.filter_by(
                store_id=store_id,
                product_id=product_id
            ).first()
            
            if not store_product:
                return False
            
            # Aplicar ajuste
            success = store_product.adjust_stock(quantity_change, reason)
            if success:
                db.session.commit()
                
                # Notificar a otras tiendas si es necesario
                if abs(quantity_change) > 10:  # Cambios significativos
                    self._notify_inventory_change(store_id, product_id, quantity_change)
                
                logger.info(f"Inventario ajustado: Producto {product_id}, Tienda {store_id}, Cambio: {quantity_change}")
                return True
            else:
                db.session.rollback()
                return False
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando inventario: {e}")
            return False
    
    def _sync_price_update(self, store_id: int, data: Dict[str, Any]) -> bool:
        """Sincronizar actualización de precios"""
        try:
            product_id = data.get('product_id')
            new_price = data.get('new_price')
            
            if not product_id or not new_price:
                return False
            
            store_product = StoreProduct.query.filter_by(
                store_id=store_id,
                product_id=product_id
            ).first()
            
            if not store_product:
                return False
            
            old_price = store_product.local_price
            store_product.local_price = new_price
            store_product.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log del cambio de precio
            logger.info(f"Precio actualizado: Producto {product_id}, Tienda {store_id}, ${old_price} -> ${new_price}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando precio: {e}")
            return False
    
    def _sync_store_config(self, store_id: int, data: Dict[str, Any]) -> bool:
        """Sincronizar configuración de tienda"""
        try:
            store = Store.query.get(store_id)
            if not store:
                return False
            
            # Actualizar configuración
            config_updates = data.get('config', {})
            for field, value in config_updates.items():
                if hasattr(store, field):
                    setattr(store, field, value)
            
            store.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Configuración de tienda {store_id} sincronizada")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando configuración de tienda: {e}")
            return False
    
    def _sync_transfer_notification(self, store_id: int, data: Dict[str, Any]) -> bool:
        """Sincronizar notificación de transferencia"""
        try:
            transfer_id = data.get('transfer_id')
            action = data.get('action')  # created, approved, shipped, delivered
            
            if not transfer_id or not action:
                return False
            
            # Notificar a tiendas involucradas
            transfer = InventoryTransfer.query.get(transfer_id)
            if not transfer:
                return False
            
            notification_data = {
                'transfer_number': transfer.transfer_number,
                'action': action,
                'from_store': transfer.from_store.name,
                'to_store': transfer.to_store.name,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Enviar notificación via Redis si está disponible
            if self.redis_client:
                for target_store_id in [transfer.from_store_id, transfer.to_store_id]:
                    if target_store_id != store_id:  # No notificar a la tienda que originó
                        self.redis_client.publish(
                            f'store_notifications:{target_store_id}',
                            json.dumps(notification_data)
                        )
            
            logger.info(f"Notificación de transferencia enviada: {transfer.transfer_number} - {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error sincronizando notificación de transferencia: {e}")
            return False
    
    def _update_product_cache(self, store_id: int, product_id: int, product_data: Dict):
        """Actualizar cache de producto"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"store_product:{store_id}:{product_id}"
            self.redis_client.setex(
                cache_key,
                3600,  # 1 hora TTL
                json.dumps(product_data)
            )
        except Exception as e:
            logger.warning(f"Error actualizando cache de producto: {e}")
    
    def _notify_inventory_change(self, store_id: int, product_id: int, quantity_change: int):
        """Notificar cambio significativo de inventario"""
        if not self.redis_client:
            return
        
        try:
            notification = {
                'type': 'inventory_alert',
                'store_id': store_id,
                'product_id': product_id,
                'quantity_change': quantity_change,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Publicar a canal de alertas
            self.redis_client.publish('inventory_alerts', json.dumps(notification))
            
        except Exception as e:
            logger.warning(f"Error enviando notificación de inventario: {e}")
    
    def sync_all_stores(self) -> Dict[str, Any]:
        """Sincronizar todas las tiendas activas"""
        with self.sync_lock:
            try:
                stores = Store.query.filter_by(is_active=True).all()
                results = {
                    'total_stores': len(stores),
                    'successful_syncs': 0,
                    'failed_syncs': 0,
                    'sync_details': [],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                for store in stores:
                    try:
                        sync_result = self.sync_store(store.id)
                        if sync_result['success']:
                            results['successful_syncs'] += 1
                        else:
                            results['failed_syncs'] += 1
                        
                        results['sync_details'].append({
                            'store_id': store.id,
                            'store_name': store.name,
                            'success': sync_result['success'],
                            'details': sync_result.get('details', {})
                        })
                        
                    except Exception as e:
                        results['failed_syncs'] += 1
                        results['sync_details'].append({
                            'store_id': store.id,
                            'store_name': store.name,
                            'success': False,
                            'error': str(e)
                        })
                
                logger.info(f"Sincronización masiva completada: {results['successful_syncs']}/{results['total_stores']} exitosas")
                return results
                
            except Exception as e:
                logger.error(f"Error en sincronización masiva: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    def sync_store(self, store_id: int) -> Dict[str, Any]:
        """Sincronizar una tienda específica"""
        try:
            store = Store.query.get(store_id)
            if not store:
                return {'success': False, 'error': 'Tienda no encontrada'}
            
            sync_details = {
                'products_synced': 0,
                'inventory_updates': 0,
                'config_updates': 0,
                'errors': []
            }
            
            # 1. Sincronizar productos
            try:
                products_result = self._sync_store_products(store_id)
                sync_details['products_synced'] = products_result.get('synced_count', 0)
            except Exception as e:
                sync_details['errors'].append(f"Error sincronizando productos: {e}")
            
            # 2. Sincronizar inventario
            try:
                inventory_result = self._sync_store_inventory(store_id)
                sync_details['inventory_updates'] = inventory_result.get('updated_count', 0)
            except Exception as e:
                sync_details['errors'].append(f"Error sincronizando inventario: {e}")
            
            # 3. Actualizar timestamp de sincronización
            store.update_sync_timestamp()
            
            success = len(sync_details['errors']) == 0
            
            return {
                'success': success,
                'store_id': store_id,
                'store_name': store.name,
                'details': sync_details,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sincronizando tienda {store_id}: {e}")
            return {
                'success': False,
                'store_id': store_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _sync_store_products(self, store_id: int) -> Dict[str, Any]:
        """Sincronizar productos de una tienda"""
        try:
            # Obtener productos que necesitan sincronización
            store_products = StoreProduct.query.filter_by(
                store_id=store_id,
                is_available=True
            ).all()
            
            synced_count = 0
            
            for store_product in store_products:
                try:
                    # Verificar si el producto base ha cambiado
                    product = store_product.product
                    if product and product.updated_at > store_product.updated_at:
                        # Actualizar datos del producto en la tienda
                        if store_product.cost_price != product.cost:
                            store_product.cost_price = product.cost
                        
                        store_product.updated_at = datetime.utcnow()
                        synced_count += 1
                
                except Exception as e:
                    logger.warning(f"Error sincronizando producto {store_product.product_id}: {e}")
                    continue
            
            if synced_count > 0:
                db.session.commit()
            
            return {'synced_count': synced_count}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando productos de tienda {store_id}: {e}")
            raise
    
    def _sync_store_inventory(self, store_id: int) -> Dict[str, Any]:
        """Sincronizar inventario de una tienda"""
        try:
            # Procesar transferencias pendientes
            pending_transfers = InventoryTransfer.query.filter(
                (InventoryTransfer.to_store_id == store_id) |
                (InventoryTransfer.from_store_id == store_id),
                InventoryTransfer.status.in_(['approved', 'in_transit'])
            ).all()
            
            updated_count = 0
            
            for transfer in pending_transfers:
                try:
                    # Verificar si necesita procesamiento automático
                    if transfer.status == 'approved' and transfer.transfer_type == 'automatic':
                        # Auto-procesar transferencias automáticas después de 1 hora
                        if (datetime.utcnow() - transfer.approved_at).total_seconds() > 3600:
                            transfer.ship_transfer()
                            updated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error procesando transferencia {transfer.transfer_number}: {e}")
                    continue
            
            if updated_count > 0:
                db.session.commit()
            
            return {'updated_count': updated_count}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sincronizando inventario de tienda {store_id}: {e}")
            raise
    
    def get_sync_status(self, store_id: int = None) -> Dict[str, Any]:
        """Obtener estado de sincronización"""
        try:
            if store_id:
                # Estado de una tienda específica
                store = Store.query.get(store_id)
                if not store:
                    return {'error': 'Tienda no encontrada'}
                
                return {
                    'store_id': store_id,
                    'store_name': store.name,
                    'is_online': store.is_online,
                    'last_sync': store.last_sync_at.isoformat() if store.last_sync_at else None,
                    'auto_sync_enabled': store.auto_sync_inventory,
                    'sync_frequency_minutes': store.sync_frequency_minutes
                }
            else:
                # Estado global de sincronización
                stores = Store.query.filter_by(is_active=True).all()
                online_stores = [s for s in stores if s.is_online]
                
                return {
                    'total_stores': len(stores),
                    'online_stores': len(online_stores),
                    'offline_stores': len(stores) - len(online_stores),
                    'sync_health_percentage': (len(online_stores) / len(stores) * 100) if stores else 0,
                    'last_global_sync': max([s.last_sync_at for s in stores if s.last_sync_at], default=None),
                    'stores_status': [
                        {
                            'id': s.id,
                            'name': s.name,
                            'is_online': s.is_online,
                            'last_sync': s.last_sync_at.isoformat() if s.last_sync_at else None
                        }
                        for s in stores
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de sincronización: {e}")
            return {'error': str(e)}
    
    def start_sync_worker(self):
        """Iniciar worker de sincronización en background"""
        def worker():
            logger.info("🔄 Iniciando worker de sincronización...")
            
            while True:
                try:
                    if not self.redis_client:
                        time.sleep(60)  # Sin Redis, sincronizar cada minuto
                        self.sync_all_stores()
                        continue
                    
                    # Procesar cola de sincronización
                    stores = Store.query.filter_by(is_active=True).all()
                    
                    for store in stores:
                        queue_key = f"sync_queue:store:{store.id}"
                        operation_data = self.redis_client.brpop(queue_key, timeout=1)
                        
                        if operation_data:
                            try:
                                operation = json.loads(operation_data[1])
                                success = self._process_sync_operation(
                                    operation['type'],
                                    operation['store_id'],
                                    operation['data']
                                )
                                
                                if not success and operation['retry_count'] < 3:
                                    # Reencolar con retry
                                    operation['retry_count'] += 1
                                    self.redis_client.lpush(queue_key, json.dumps(operation))
                                
                            except Exception as e:
                                logger.error(f"Error procesando operación de sincronización: {e}")
                    
                    # Sincronización periódica
                    time.sleep(300)  # 5 minutos entre ciclos
                    
                except Exception as e:
                    logger.error(f"Error en worker de sincronización: {e}")
                    time.sleep(30)  # Pausa antes de reintentar
        
        # Ejecutar worker en thread separado
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        logger.info("✅ Worker de sincronización iniciado")
        
        return worker_thread
