"""
Digital Certificate API Endpoints - Sistema POS Sabrositas
=========================================================
Endpoints para gestión de certificados digitales.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.digital_certificate import DigitalCertificate, CertificateUsage
from app.services.auth_service import token_required
from app.repositories.base_repository import BaseRepository
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
digital_certificate_bp = Blueprint('digital_certificate', __name__, url_prefix='/api/v1/digital-certificates')

@digital_certificate_bp.route('/', methods=['GET'])
@token_required
def get_certificates(current_user):
    """Obtener certificados digitales"""
    try:
        certificates = DigitalCertificate.query.order_by(DigitalCertificate.created_at.desc()).all()
        
        certificates_data = []
        for cert in certificates:
            cert_dict = cert.to_dict()
            certificates_data.append(cert_dict)
        
        return jsonify({
            'success': True,
            'data': certificates_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo certificados: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@digital_certificate_bp.route('/', methods=['POST'])
@token_required
def create_certificate(current_user):
    """Crear certificado digital"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['certificate_name', 'serial_number', 'subject', 'issuer', 'valid_from', 'valid_until', 'company_nit', 'company_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar si ya existe un certificado por defecto
        if data.get('is_default', False):
            # Desactivar otros certificados por defecto
            DigitalCertificate.query.filter_by(is_default=True).update({'is_default': False})
        
        # Crear certificado digital
        certificate = DigitalCertificate(
            certificate_name=data['certificate_name'],
            serial_number=data['serial_number'],
            subject=data['subject'],
            issuer=data['issuer'],
            valid_from=datetime.fromisoformat(data['valid_from']),
            valid_until=datetime.fromisoformat(data['valid_until']),
            company_nit=data['company_nit'],
            company_name=data['company_name'],
            is_default=data.get('is_default', False),
            certificate_file=base64.b64decode(data['certificate_file']) if data.get('certificate_file') else None,
            private_key_file=base64.b64decode(data['private_key_file']) if data.get('private_key_file') else None,
            password=data.get('password')
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        logger.info(f"Certificado digital creado: {certificate.certificate_name}")
        
        return jsonify({
            'success': True,
            'message': 'Certificado digital creado exitosamente',
            'data': certificate.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando certificado: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@digital_certificate_bp.route('/<int:certificate_id>', methods=['GET'])
@token_required
def get_certificate(current_user, certificate_id):
    """Obtener certificado específico"""
    try:
        certificate = DigitalCertificate.query.get(certificate_id)
        if not certificate:
            return jsonify({
                'success': False,
                'message': 'Certificado no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': certificate.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo certificado: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@digital_certificate_bp.route('/<int:certificate_id>/validate', methods=['POST'])
@token_required
def validate_certificate(current_user, certificate_id):
    """Validar certificado digital"""
    try:
        certificate = DigitalCertificate.query.get(certificate_id)
        if not certificate:
            return jsonify({
                'success': False,
                'message': 'Certificado no encontrado'
            }), 404
        
        # Validar certificado
        validation_result = {
            'is_valid': certificate.is_valid(),
            'is_expired': certificate.is_expired(),
            'days_until_expiry': certificate.days_until_expiry(),
            'status': certificate.status,
            'valid_from': certificate.valid_from.isoformat() if certificate.valid_from else None,
            'valid_until': certificate.valid_until.isoformat() if certificate.valid_until else None
        }
        
        return jsonify({
            'success': True,
            'data': validation_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error validando certificado: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@digital_certificate_bp.route('/default', methods=['GET'])
@token_required
def get_default_certificate(current_user):
    """Obtener certificado por defecto"""
    try:
        certificate = DigitalCertificate.query.filter_by(is_default=True).first()
        if not certificate:
            return jsonify({
                'success': False,
                'message': 'No hay certificado por defecto configurado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': certificate.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo certificado por defecto: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@digital_certificate_bp.route('/usage', methods=['GET'])
@token_required
def get_certificate_usage(current_user):
    """Obtener historial de uso de certificados"""
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        certificate_id = request.args.get('certificate_id', type=int)
        
        # Construir consulta
        query = CertificateUsage.query
        
        if certificate_id:
            query = query.filter(CertificateUsage.certificate_id == certificate_id)
        
        # Ordenar por fecha descendente
        query = query.order_by(CertificateUsage.used_at.desc())
        
        # Paginación
        usage_records = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Preparar respuesta
        usage_data = []
        for record in usage_records.items:
            usage_dict = record.to_dict()
            usage_data.append(usage_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'usage_records': usage_data,
                'pagination': {
                    'page': usage_records.page,
                    'pages': usage_records.pages,
                    'per_page': usage_records.per_page,
                    'total': usage_records.total,
                    'has_next': usage_records.has_next,
                    'has_prev': usage_records.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de uso: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500
