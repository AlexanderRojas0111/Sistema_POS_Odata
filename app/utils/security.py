# DEPRECATED: Usar app.core.security.SecurityManager en su lugar
# Este archivo se mantiene solo para compatibilidad hacia atrás
# TODO: Migrar todo el código para usar SecurityManager

from flask_bcrypt import generate_password_hash, check_password_hash
import warnings

def hash_password(password):
    """DEPRECATED: Usar SecurityManager.hash_password() en su lugar"""
    warnings.warn(
        "hash_password está deprecated. Usar SecurityManager.hash_password() en su lugar",
        DeprecationWarning,
        stacklevel=2
    )
    return generate_password_hash(password).decode('utf-8')

def verify_password(password, hashed):
    """DEPRECATED: Usar SecurityManager.verify_password() en su lugar"""
    warnings.warn(
        "verify_password está deprecated. Usar SecurityManager.verify_password() en su lugar",
        DeprecationWarning,
        stacklevel=2
    )
    return check_password_hash(hashed, password) 