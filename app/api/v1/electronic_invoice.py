"""
Electronic Invoice API Endpoints - Sistema POS Sabrositas
========================================================
Endpoints para facturación electrónica.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.electronic_invoice import ElectronicInvoice, ElectronicInvoiceItem
from app.models.sale import Sale
from app.services.auth_service import token_required
from app.repositories.base_repository import BaseRepository
from datetime import datetime
from typing import Dict, Any, List
import logging
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
electronic_invoice_bp = Blueprint('electronic_invoice', __name__, url_prefix='/api/v1/electronic-invoices')

# Repositorios
invoice_repository = BaseRepository(ElectronicInvoice)
invoice_item_repository = BaseRepository(ElectronicInvoiceItem)

@electronic_invoice_bp.route('/', methods=['GET'])
@token_required
def get_invoices(current_user):
    """Obtener facturas electrónicas"""
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Construir consulta
        query = ElectronicInvoice.query
        
        # Filtros
        if status:
            query = query.filter(ElectronicInvoice.fiscal_status == status)
        if date_from:
            query = query.filter(ElectronicInvoice.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(ElectronicInvoice.created_at <= datetime.fromisoformat(date_to))
        
        # Ordenar por fecha descendente
        query = query.order_by(ElectronicInvoice.created_at.desc())
        
        # Paginación
        invoices = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Preparar respuesta
        invoices_data = []
        for invoice in invoices.items:
            invoice_dict = invoice.to_dict()
            invoices_data.append(invoice_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'invoices': invoices_data,
                'pagination': {
                    'page': invoices.page,
                    'pages': invoices.pages,
                    'per_page': invoices.per_page,
                    'total': invoices.total,
                    'has_next': invoices.has_next,
                    'has_prev': invoices.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo facturas: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@electronic_invoice_bp.route('/', methods=['POST'])
@token_required
def create_invoice(current_user):
    """Crear factura electrónica"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['sale_id', 'company_nit', 'company_name', 'customer_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Obtener venta
        sale = Sale.query.get(data['sale_id'])
        if not sale:
            return jsonify({
                'success': False,
                'message': 'Venta no encontrada'
            }), 404
        
        # Crear factura electrónica
        invoice = ElectronicInvoice(
            sale_id=data['sale_id'],
            user_id=current_user.id,
            company_nit=data['company_nit'],
            company_name=data['company_name'],
            customer_nit=data.get('customer_nit'),
            customer_name=data['customer_name'],
            customer_email=data.get('customer_email'),
            subtotal=float(sale.subtotal),
            tax_amount=float(sale.tax_amount),
            discount_amount=float(sale.discount_amount),
            total_amount=float(sale.total_amount)
        )
        
        # Guardar factura
        db.session.add(invoice)
        db.session.flush()  # Para obtener el ID
        
        # Crear items de la factura
        for sale_item in sale.items:
            invoice_item = ElectronicInvoiceItem(
                invoice_id=invoice.id,
                product_id=sale_item.product_id,
                product_code=sale_item.product.sku,
                product_name=sale_item.product.name,
                product_description=sale_item.product.description,
                quantity=sale_item.quantity,
                unit_price=float(sale_item.unit_price),
                total_price=float(sale_item.total_price),
                tax_rate=19.0,  # IVA 19%
                tax_amount=float(sale_item.total_price) * 0.19
            )
            db.session.add(invoice_item)
        
        db.session.commit()
        
        logger.info(f"Factura electrónica creada: {invoice.invoice_number}")
        
        return jsonify({
            'success': True,
            'message': 'Factura electrónica creada exitosamente',
            'data': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando factura: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@electronic_invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@token_required
def get_invoice(current_user, invoice_id):
    """Obtener factura específica"""
    try:
        invoice = ElectronicInvoice.query.get(invoice_id)
        if not invoice:
            return jsonify({
                'success': False,
                'message': 'Factura no encontrada'
            }), 404
        
        invoice_data = invoice.to_dict()
        
        # Agregar items
        items = ElectronicInvoiceItem.query.filter_by(invoice_id=invoice_id).all()
        invoice_data['items'] = [item.to_dict() for item in items]
        
        return jsonify({
            'success': True,
            'data': invoice_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo factura: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@electronic_invoice_bp.route('/<int:invoice_id>/send', methods=['POST'])
@token_required
def send_invoice(current_user, invoice_id):
    """Enviar factura a DIAN"""
    try:
        invoice = ElectronicInvoice.query.get(invoice_id)
        if not invoice:
            return jsonify({
                'success': False,
                'message': 'Factura no encontrada'
            }), 404
        
        if invoice.fiscal_status != 'pending':
            return jsonify({
                'success': False,
                'message': 'La factura ya fue procesada'
            }), 400
        
        # Simular envío a DIAN (aquí iría la integración real)
        invoice.fiscal_status = 'sent'
        invoice.sent_at = datetime.utcnow()
        invoice.cufe = f"CUFE_{invoice.uuid}_{datetime.utcnow().timestamp()}"
        
        # Simular respuesta exitosa
        invoice.dian_response = json.dumps({
            'status': 'accepted',
            'cufe': invoice.cufe,
            'message': 'Documento aceptado por DIAN'
        })
        invoice.fiscal_status = 'accepted'
        invoice.accepted_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Factura enviada a DIAN: {invoice.invoice_number}")
        
        return jsonify({
            'success': True,
            'message': 'Factura enviada exitosamente a DIAN',
            'data': {
                'invoice_number': invoice.invoice_number,
                'cufe': invoice.cufe,
                'fiscal_status': invoice.fiscal_status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enviando factura: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@electronic_invoice_bp.route('/<int:invoice_id>/pdf', methods=['GET'])
@token_required
def generate_invoice_pdf(current_user, invoice_id):
    """Generar PDF de factura"""
    try:
        invoice = ElectronicInvoice.query.get(invoice_id)
        if not invoice:
            return jsonify({
                'success': False,
                'message': 'Factura no encontrada'
            }), 404
        
        # Aquí iría la generación real del PDF
        # Por ahora retornamos información de la factura
        return jsonify({
            'success': True,
            'message': 'PDF generado exitosamente',
            'data': {
                'invoice_number': invoice.invoice_number,
                'pdf_url': f"/api/v1/electronic-invoices/{invoice_id}/download-pdf",
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@electronic_invoice_bp.route('/stats', methods=['GET'])
@token_required
def get_invoice_stats(current_user):
    """Obtener estadísticas de facturas"""
    try:
        # Estadísticas básicas
        total_invoices = ElectronicInvoice.query.count()
        pending_invoices = ElectronicInvoice.query.filter_by(fiscal_status='pending').count()
        accepted_invoices = ElectronicInvoice.query.filter_by(fiscal_status='accepted').count()
        rejected_invoices = ElectronicInvoice.query.filter_by(fiscal_status='rejected').count()
        
        # Total facturado
        total_amount = db.session.query(db.func.sum(ElectronicInvoice.total_amount)).filter_by(fiscal_status='accepted').scalar() or 0
        
        stats = {
            'total_invoices': total_invoices,
            'pending_invoices': pending_invoices,
            'accepted_invoices': accepted_invoices,
            'rejected_invoices': rejected_invoices,
            'total_amount': float(total_amount),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500
