"""
Error Handler Middleware - Sistema POS O'Data
============================================
Middleware enterprise para manejo centralizado de errores.
"""

import logging
import traceback
import uuid
from flask import Flask, jsonify, request
from app.exceptions import POSException

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Middleware para manejo centralizado de errores enterprise"""
    
    def __init__(self, app: Flask):
        self.app = app
        self._register_error_handlers()
    
    def _register_error_handlers(self):
        """Registrar manejadores de errores"""
        
        @self.app.errorhandler(POSException)
        def handle_pos_exception(error: POSException):
            """Manejar excepciones del sistema POS"""
            logger.error(f"POS Exception: {error.error_code} - {error.message}", extra={
                'error_id': error.error_id,
                'error_code': error.error_code,
                'context': error.context,
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify(error.to_dict()), error.status_code
        
        @self.app.errorhandler(400)
        def handle_bad_request(error):
            """Manejar errores 400"""
            logger.warning(f"Bad Request: {error.description}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'BAD_REQUEST',
                    'message': error.description or 'Bad Request',
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 400
        
        @self.app.errorhandler(401)
        def handle_unauthorized(error):
            """Manejar errores 401"""
            logger.warning(f"Unauthorized: {error.description}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Authentication required',
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 401
        
        @self.app.errorhandler(403)
        def handle_forbidden(error):
            """Manejar errores 403"""
            logger.warning(f"Forbidden: {error.description}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Insufficient permissions',
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 403
        
        @self.app.errorhandler(404)
        def handle_not_found(error):
            """Manejar errores 404"""
            logger.info(f"Not Found: {request.url}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Resource not found',
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 404
        
        @self.app.errorhandler(422)
        def handle_unprocessable_entity(error):
            """Manejar errores 422"""
            logger.warning(f"Unprocessable Entity: {error.description}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'UNPROCESSABLE_ENTITY',
                    'message': error.description or 'Unprocessable Entity',
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 422
        
        @self.app.errorhandler(429)
        def handle_rate_limit(error):
            """Manejar errores de rate limiting"""
            logger.warning(f"Rate Limit Exceeded: {error.description}", extra={
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Too many requests',
                    'retry_after': getattr(error, 'retry_after', None),
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 429
        
        @self.app.errorhandler(500)
        def handle_internal_error(error):
            """Manejar errores 500"""
            error_id = str(uuid.uuid4())
            logger.error(f"Internal Server Error: {error.description}", extra={
                'error_id': error_id,
                'request_id': getattr(request, 'request_id', None),
                'traceback': traceback.format_exc()
            })
            
            return jsonify({
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'An internal error occurred',
                    'error_id': error_id,
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 500
        
        @self.app.errorhandler(Exception)
        def handle_unexpected_error(error):
            """Manejar errores inesperados"""
            error_id = str(uuid.uuid4())
            logger.error(f"Unexpected Error: {str(error)}", extra={
                'error_id': error_id,
                'request_id': getattr(request, 'request_id', None),
                'traceback': traceback.format_exc()
            })
            
            return jsonify({
                'error': {
                    'code': 'UNEXPECTED_ERROR',
                    'message': 'An unexpected error occurred',
                    'error_id': error_id,
                    'request_id': getattr(request, 'request_id', None)
                }
            }), 500
