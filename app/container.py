"""
DI Container Enterprise - Sistema POS O'Data
============================================
Container de inyección de dependencias con auto-wiring y lifecycle management.
"""

from typing import Dict, Any, Type, TypeVar, Callable
import inspect
from functools import wraps

T = TypeVar('T')

class DIContainer:
    """Container de inyección de dependencias enterprise"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Registrar servicio como singleton"""
        key = interface.__name__
        self._factories[key] = implementation
        self._services[key] = None  # Se creará lazy
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Registrar servicio como transient (nueva instancia cada vez)"""
        key = interface.__name__
        self._factories[key] = implementation
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Registrar instancia específica"""
        key = interface.__name__
        self._services[key] = instance
        self._singletons[key] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Obtener instancia del servicio"""
        key = interface.__name__
        
        # Si ya existe como singleton, devolverlo
        if key in self._singletons:
            return self._singletons[key]
        
        # Si existe como instancia registrada, devolverla
        if key in self._services and self._services[key] is not None:
            return self._services[key]
        
        # Crear nueva instancia
        if key in self._factories:
            implementation = self._factories[key]
            instance = self._create_instance(implementation)
            
            # Si es singleton, guardarlo
            if key in self._services and self._services[key] is None:
                self._singletons[key] = instance
                self._services[key] = instance
            
            return instance
        
        raise ValueError(f"Service {key} not registered")
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Crear instancia con auto-wiring"""
        constructor = implementation.__init__
        sig = inspect.signature(constructor)
        
        # Obtener parámetros del constructor
        args = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Intentar resolver dependencia
            if param.annotation != inspect.Parameter.empty:
                try:
                    args[param_name] = self.get(param.annotation)
                except ValueError:
                    # Si no se puede resolver, usar valor por defecto
                    if param.default != inspect.Parameter.empty:
                        args[param_name] = param.default
                    else:
                        raise ValueError(f"Cannot resolve dependency {param_name} for {implementation.__name__}")
        
        return implementation(**args)
    
    def auto_wire(self, func: Callable) -> Callable:
        """Decorator para auto-wiring de dependencias"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            
            # Resolver dependencias automáticamente
            for param_name, param in sig.parameters.items():
                if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                    try:
                        kwargs[param_name] = self.get(param.annotation)
                    except ValueError:
                        pass  # Ignorar si no se puede resolver
            
            return func(*args, **kwargs)
        
        return wrapper

# Instancia global del container
container = DIContainer()

def inject(interface: Type[T]) -> T:
    """Decorator para inyección de dependencias"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Inyectar dependencia
            dependency = container.get(interface)
            kwargs[interface.__name__.lower()] = dependency
            return func(*args, **kwargs)
        return wrapper
    return decorator
