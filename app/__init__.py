# Realizado por Fhany Mendez y Karen Maya - 305 - Frameworks
# Inicializador de la aplicación Flask usando el patrón de factoría (Factory Pattern)
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-eco-reto'

    with app.app_context():
        from . import routes

    return app