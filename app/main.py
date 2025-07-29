from app import create_app
from flask import jsonify

app = create_app()

@app.route('/health')
def health_check():
    """Endpoint para verificar la salud de la aplicación"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'environment': app.config['FLASK_ENV']
    })

if __name__ == "__main__":
    app.run(debug=True) 