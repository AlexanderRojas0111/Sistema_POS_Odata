from flask import Blueprint, request, jsonify, send_file
from app.models import Sale, Product
from app.database import db
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

sales = Blueprint('sales', __name__)

@sales.route('/api/sales', methods=['GET'])
def get_sales():
    """Obtiene todas las ventas"""
    sales = Sale.query.all()
    return jsonify([sale.to_dict() for sale in sales])

@sales.route('/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    """Obtiene una venta por su ID"""
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(sale.to_dict())

@sales.route('/api/sales', methods=['POST'])
def create_sale():
    """Crea una nueva venta"""
    data = request.get_json()
    
    # Verificar stock
    product = Product.query.get_or_404(data['product_id'])
    if product.stock < data['quantity']:
        return jsonify({'error': 'Stock insuficiente'}), 400
    
    # Calcular total
    total = product.price * data['quantity']
    
    # Crear venta
    sale = Sale(
        product_id=data['product_id'],
        quantity=data['quantity'],
        total=total,
        user_id=data['user_id'],
        payment_method=data['payment_method'],
        customer_id=data.get('customer_id')
    )
    
    # Actualizar stock
    product.stock -= data['quantity']
    
    db.session.add(sale)
    db.session.commit()
    
    return jsonify(sale.to_dict()), 201

@sales.route('/api/sales/<int:sale_id>/pdf', methods=['GET'])
def generate_sale_pdf(sale_id):
    """Genera un PDF para una venta"""
    sale = Sale.query.get_or_404(sale_id)
    product = Product.query.get(sale.product_id)
    
    # Crear PDF en memoria
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, 750, f"Factura de Venta #{sale.id}")
    
    # Detalles de la venta
    p.setFont("Helvetica", 12)
    p.drawString(30, 700, f"Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(30, 680, f"Producto: {product.name}")
    p.drawString(30, 660, f"Cantidad: {sale.quantity}")
    p.drawString(30, 640, f"Precio unitario: ${product.price:.2f}")
    p.drawString(30, 620, f"Total: ${sale.total:.2f}")
    p.drawString(30, 600, f"Método de pago: {sale.payment_method}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'venta_{sale.id}.pdf',
        mimetype='application/pdf'
    )