from flask import Blueprint, request, jsonify, current_app
from app.crud.products import get_all_products, create_product, update_product, delete_product
from flask_restx import Namespace, Resource, fields
from app.models import Product

products_bp = Blueprint('products', __name__)
api = Namespace('products', description='Operaciones de productos')

product_model = api.model('Product', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'stock': fields.Integer(required=True),
    'price': fields.Float(required=True),
    'alert': fields.String(required=False)
})

@products_bp.route('/alerts', methods=['GET'])
def get_products_with_alerts():
    threshold = current_app.config.get('LOW_STOCK_THRESHOLD', 5)
    products = Product.query.all()
    result = [p.to_dict() for p in products if (p.stock == 0 or p.stock <= threshold)]
    return jsonify(result)

@api.route('/')
class ProductList(Resource):
    @api.marshal_list_with(product_model)
    def get(self):
        """Lista todos los productos"""
        return get_all_products()

    @api.expect(product_model)
    @api.marshal_with(product_model, code=201)
    def post(self):
        """Crea un nuevo producto"""
        data = request.json
        return create_product(data), 201

@api.route('/<int:product_id>')
@api.param('product_id', 'El identificador del producto')
class ProductResource(Resource):
    @api.marshal_with(product_model)
    def put(self, product_id):
        """Actualiza un producto"""
        data = request.json
        return update_product(product_id, data)

    def delete(self, product_id):
        """Elimina un producto"""
        delete_product(product_id)
        return {'message': 'Producto eliminado'}