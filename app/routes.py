# Realizado por Fhany Mendez y Karen Maya - 305 - Frameworks
# Módulo de rutas y operaciones CRUD conectadas a la base de datos PostgreSQL en Neon
import os
import psycopg
from psycopg.rows import dict_row
from flask import render_template, request, redirect, url_for, current_app as app

def conectar_db():
    """Establece la conexión con la base de datos de Neon usando la variable de entorno"""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta configurar DATABASE_URL")
    return psycopg.connect(url, row_factory=dict_row)

@app.route('/')
def index():
    """Ruta principal: Consulta y muestra todas las acciones ecológicas registradas"""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, titulo, categoria, descripcion, propuesto_por FROM acciones ORDER BY id DESC")
            acciones = cursor.fetchall()
    finally:
        conexion.close()
    return render_template("index.html", acciones=acciones)

@app.route('/nueva', methods=['GET', 'POST'])
def nueva_accion():
    """Ruta para registrar una nueva acción ecológica mediante un formulario POST"""
    if request.method == 'POST':
        titulo = request.form['titulo']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        propuesto_por = request.form['propuesto_por']
        
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO acciones (titulo, categoria, descripcion, propuesto_por) VALUES (%s, %s, %s, %s)",
                    (titulo, categoria, descripcion, propuesto_por)
                )
                conexion.commit()
        finally:
            conexion.close()
        return redirect(url_for('index'))
    
    return render_template("formulario.html")

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    """Ruta para eliminar un registro de acción ecológica basándose en su ID"""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM acciones WHERE id = %s", (id,))
            conexion.commit()
    finally:
        conexion.close()
    return redirect(url_for('index'))