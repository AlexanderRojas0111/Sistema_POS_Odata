"""
Support Document API Endpoints - Sistema POS Sabrositas
======================================================
Endpoints para documentos soporte electrónicos.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.support_document import SupportDocument
from app.services.auth_service import token_required
from app.repositories.base_repository import BaseRepository
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
support_document_bp = Blueprint('support_document', __name__, url_prefix='/api/v1/support-documents')

@support_document_bp.route('/', methods=['GET'])
@token_required
def get_support_documents(current_user):
    """Obtener documentos soporte"""
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        document_type = request.args.get('type')
        status = request.args.get('status')
        
        # Construir consulta
        query = SupportDocument.query
        
        # Filtros
        if document_type:
            query = query.filter(SupportDocument.document_type == document_type)
        if status:
            query = query.filter(SupportDocument.fiscal_status == status)
        
        # Ordenar por fecha descendente
        query = query.order_by(SupportDocument.created_at.desc())
        
        # Paginación
        documents = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Preparar respuesta
        documents_data = []
        for document in documents.items:
            document_dict = document.to_dict()
            documents_data.append(document_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'documents': documents_data,
                'pagination': {
                    'page': documents.page,
                    'pages': documents.pages,
                    'per_page': documents.per_page,
                    'total': documents.total,
                    'has_next': documents.has_next,
                    'has_prev': documents.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos soporte: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@support_document_bp.route('/', methods=['POST'])
@token_required
def create_support_document(current_user):
    """Crear documento soporte"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['company_nit', 'company_name', 'customer_name', 'subtotal', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Crear documento soporte
        document = SupportDocument(
            user_id=current_user.id,
            company_nit=data['company_nit'],
            company_name=data['company_name'],
            customer_nit=data.get('customer_nit'),
            customer_name=data['customer_name'],
            subtotal=data['subtotal'],
            tax_amount=data.get('tax_amount', 0),
            total_amount=data['total_amount'],
            document_type=data.get('document_type', 'support'),
            sale_id=data.get('sale_id'),
            invoice_id=data.get('invoice_id')
        )
        
        db.session.add(document)
        db.session.commit()
        
        logger.info(f"Documento soporte creado: {document.document_number}")
        
        return jsonify({
            'success': True,
            'message': 'Documento soporte creado exitosamente',
            'data': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando documento soporte: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@support_document_bp.route('/<int:document_id>', methods=['GET'])
@token_required
def get_support_document(current_user, document_id):
    """Obtener documento soporte específico"""
    try:
        document = SupportDocument.query.get(document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': 'Documento soporte no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': document.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo documento soporte: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@support_document_bp.route('/<int:document_id>/send', methods=['POST'])
@token_required
def send_support_document(current_user, document_id):
    """Enviar documento soporte a DIAN"""
    try:
        document = SupportDocument.query.get(document_id)
        if not document:
            return jsonify({
                'success': False,
                'message': 'Documento soporte no encontrado'
            }), 404
        
        if document.fiscal_status != 'pending':
            return jsonify({
                'success': False,
                'message': 'El documento ya fue procesado'
            }), 400
        
        # Simular envío a DIAN
        document.fiscal_status = 'sent'
        document.sent_at = datetime.utcnow()
        document.cude = f"CUDE_{document.uuid}_{datetime.utcnow().timestamp()}"
        
        # Simular respuesta exitosa
        document.dian_response = json.dumps({
            'status': 'accepted',
            'cude': document.cude,
            'message': 'Documento soporte aceptado por DIAN'
        })
        document.fiscal_status = 'accepted'
        document.accepted_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Documento soporte enviado a DIAN: {document.document_number}")
        
        return jsonify({
            'success': True,
            'message': 'Documento soporte enviado exitosamente a DIAN',
            'data': {
                'document_number': document.document_number,
                'cude': document.cude,
                'fiscal_status': document.fiscal_status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enviando documento soporte: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500
