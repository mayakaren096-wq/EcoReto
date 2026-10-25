# Realizado por Fhany Mendez y Karen Maya - 305 - Frameworks
# Archivo principal para iniciar la aplicación Flask en desarrollo o producción
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)