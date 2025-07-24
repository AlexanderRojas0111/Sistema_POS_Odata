from flask import Blueprint, request, jsonify, send_file
from app.crud.sales import get_all_sales, create_sale
from app.models import Sale, Customer, Product, User
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['GET'])
def get_sales():
    sales = get_all_sales()
    return jsonify([s.to_dict() for s in sales])

@sales_bp.route('/', methods=['POST'])
def create_sale_route():
    data = request.json
    # Se espera: product_id, quantity, total, user_id, payment_method, customer_id
    sale = create_sale(data)
    return jsonify(sale.to_dict()), 201

@sales_bp.route('/<int:sale_id>/pdf', methods=['GET'])
def get_sale_pdf(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    customer = Customer.query.get(sale.customer_id) if sale.customer_id else None
    product = Product.query.get(sale.product_id)
    user = User.query.get(sale.user_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Encabezado
    elements.append(Paragraph('<b>Factura de Venta</b>', styles['Title']))
    elements.append(Paragraph('Empresa: Tu Empresa S.A.S.', styles['Normal']))
    elements.append(Spacer(1, 12))

    # Datos de la venta
    datos_venta = f"""
    <b>ID Venta:</b> {sale.id}<br/>
    <b>Cliente:</b> {customer.name if customer else '-'}<br/>
    <b>Atendido por:</b> {user.name if user else '-'}<br/>
    <b>Método de pago:</b> {sale.payment_method}<br/>
    """
    elements.append(Paragraph(datos_venta, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabla de productos
    data = [
        ['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal'],
        [product.name, str(sale.quantity), f"${product.price:.2f}", f"${sale.total:.2f}"]
    ]
    table = Table(data, colWidths=[80*mm, 30*mm, 40*mm, 30*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Total
    elements.append(Paragraph(f'<b>TOTAL: ${sale.total:.2f}</b>', styles['Heading2']))
    elements.append(Spacer(1, 24))
    elements.append(Paragraph('¡Gracias por su compra!', styles['Italic']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'factura_venta_{sale.id}.pdf', mimetype='application/pdf')