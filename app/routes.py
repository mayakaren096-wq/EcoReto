from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2

# Función auxiliar para conectar a la base de datos (PostgreSQL / Neon o SQLite según tu configuración)
def get_db_connection():
    # Si usas la variable de entorno DATABASE_URL para Neon.tech:
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

# 1. RUTA PRINCIPAL (Muestra la tabla de acciones ecológicas)
@current_app.route('/')
def index():
    # Opcional: Si quieres forzar que inicien sesión para ver la página, descomenta las siguientes líneas:
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titulo, categoria, descripcion, propuesto_por FROM acciones;")
    acciones = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', acciones=acciones)

# 2. RUTA PARA CREAR UNA NUEVA ACCIÓN ECOLÓGICA
@current_app.route('/nueva', methods=['GET', 'POST'])
def nueva_accion():
    # Protección: Exigir inicio de sesión para agregar registros
    if 'user_id' not in session:
        flash('Debes iniciar sesión para registrar una acción.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        # Usamos el nombre del usuario logueado automáticamente o el campo del formulario
        propuesto_por = session.get('user_name', 'Anónimo')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
        "INSERT INTO acciones (titulo, categoria, descripcion, propuesto_por) VALUES (%s, %s, %s, %s)",
        (titulo, categoria, descripcion, propuesto_por)
    )
        conn.commit()
        cur.close()
        conn.close()
        
        flash('¡Acción registrada exitosamente!', 'success')
        return redirect(url_for('index'))

    return render_template('formulario.html')

# 3. RUTA PARA ELIMINAR UNA ACCIÓN
# 3. RUTA PARA ELIMINAR UNA ACCIÓN
@current_app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_accion(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM acciones WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Acción eliminada correctamente.', 'info')
    return redirect(url_for('index'))

# ==========================================
# RUTAS DE AUTENTICACIÓN (LOGIN Y REGISTRO)
# ==========================================

# 4. RUTA DE REGISTRO DE USUARIOS
@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        # Encriptar la contraseña de forma segura
        password_hashed = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s);",
                (nombre, email, password_hashed)
            )
            conn.commit()
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash('El correo ya está registrado o hubo un error en el registro.', 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

# 5. RUTA DE INICIO DE SESIÓN (LOGIN)
@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, password FROM usuarios WHERE email = %s;", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # Validar si el usuario existe y la contraseña coincide
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash(f'¡Bienvenido de nuevo, {user[1]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos. Inténtalo de nuevo.', 'danger')

    return render_template('login.html')

# 6. RUTA DE CERRAR SESIÓN (LOGOUT)
@current_app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))