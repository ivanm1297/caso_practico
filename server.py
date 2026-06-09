from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, tbl_admin, tbl_carrusel, tbl_catal_autos
from conex import DATABASE_URI
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask_login import current_user, LoginManager
import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import calendar
from flask import jsonify
from random import choice  
import base64
import plotly.express as px

from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# Nota: Configura la secret_key directamente en app.config para que Flask la reconozca para los mensajes flash
app.config['SECRET_KEY'] = 'mwefnknglkskngkds smksdgksng kmdsksdnglks lkmdgklns'
db.init_app(app)

# Configuración de carpetas y extensiones
UPLOAD_FOLDER = 'static/image/carrusel'
UPLOAD_FOLDER_2 = 'static/image/catalogo'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2

# --- FUNCIÓN DE VALIDACIÓN DE ARCHIVOS ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# -----------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'administrador_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    route_name = request.path  # Obtiene la ruta actual

    imagenes = tbl_carrusel.query.all()

    return render_template('clientes/home.html', route_name=route_name, imagenes=imagenes)

# Panel de administrador
@app.get('/dashboard')
@login_required
def dashboard():
    route_name = request.path  # Obtiene la ruta actual
    imagenes = tbl_carrusel.query.all()
    return render_template('dashboard/dashboard.html', route_name=route_name, imagenes=imagenes)

@app.post('/subir_imagen')
def subir_imagen():
    if 'imagen' not in request.files:
        flash('No se ha seleccionado ningún archivo', 'error')
        return redirect(url_for('dashboard')) # Cambiado request.url por la ruta fija para evitar bucles

    imagen = request.files['imagen']

    if imagen.filename == '':
        flash('Archivo de imagen no válido', 'error')
        return redirect(url_for('dashboard'))

    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagen.save(ruta)

        # Guarda la ruta de la imagen en la base de datos
        nueva_imagen = tbl_carrusel(imagen=filename)
        db.session.add(nueva_imagen)
        db.session.commit()

        flash('Imagen subida con éxito', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Extensión de archivo no válida', 'error')
        return redirect(url_for('dashboard'))

# Ruta para servir imágenes desde la carpeta "uploads"
@app.route('/static/image/carrusel/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
@app.get('/eliminar_imagen/<int:id_imagen>')
def eliminar_imagen(id_imagen):
    # Aquí debes escribir el código para eliminar la imagen con el ID proporcionado
    # Puedes utilizar SQLAlchemy o cualquier otra biblioteca que estés utilizando para la base de datos
    # Por ejemplo, si usas SQLAlchemy, puedes hacer algo como esto:
    imagen_a_eliminar = tbl_carrusel.query.get(id_imagen)
    if imagen_a_eliminar:
        db.session.delete(imagen_a_eliminar)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.get('/catalogo')
@login_required
def catalogo():
    route_name = request.path  # Obtiene la ruta actual
    catalogo = tbl_catal_autos.query.all()
    admin = tbl_admin.query.get(session['administrador_id'])

    return render_template('dashboard/catalogo_auto.html', route_name=route_name, catalogo=catalogo, admin=admin)
@app.post('/agregar_auto')
def agregar_auto(): 
    if request.method == 'POST':
        modelo = request.form['modelo']
        anio = request.form['anio']
        km = request.form['km']
        marca = request.form['marca']
        descripcion = request.form['descripcion']
        precio_unidad = request.form['precio_unidad']
        imagen = request.files.getlist('imagen')

        nombres_imagenes = []  

        for imagen in imagen:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                ruta = os.path.join(app.config['UPLOAD_FOLDER_2'], filename)
                imagen.save(ruta)
                nombres_imagenes.append(filename)  

        imagenes_str = ",".join(nombres_imagenes)

        nuevo_auto = tbl_catal_autos(
            modelo=modelo,
            anio=anio,
            km=km,
            marca=marca,
            descripcion=descripcion,
            precio_unidad=precio_unidad,
                        imagen=imagenes_str 

        )
        db.session.add(nuevo_auto)
        db.session.commit()

        flash('Nuevo auto agregado con éxito', 'success')
        return redirect(url_for('catalogo'))     
    else:
        flash('Error al agregar el auto', 'error')
        return redirect(url_for('catalogo'))
@app.get('/eliminar_auto/<id_auto>')
def eliminar_auto(id_auto):
    catalogo = tbl_catal_autos.query.get(id_auto)

    if not catalogo:
        flash('El auto no existe', 'error')
        return redirect(url_for('catalogo'))

    db.session.delete(catalogo)
    db.session.commit()

    flash('Auto eliminado exitosamente', 'success')
    return redirect(url_for('catalogo'))  
@app.post('/actualizar_auto/<id_auto>/post')
def actualizar_auto(id_auto):
    catalogo = tbl_catal_autos.query.get(id_auto)
    act_modelo = request.form['act_modelo']
    act_anio = request.form['act_anio']
    act_km = request.form['act_km']
    act_marca = request.form['act_marca']
    act_descripcion = request.form['act_descripcion']
    act_precio_unidad = request.form['act_precio_unidad']

    
    if act_modelo != None and act_modelo != '':
        catalogo.modelo_auto = act_modelo
        
    if act_anio != None and act_anio != '':
        catalogo.año_auto= act_anio
    
    if act_km != None and act_km != '':
        catalogo.km_auto = act_km
    
    if act_precio_unidad != None and act_precio_unidad != '':
        catalogo.precio_lista = act_precio_unidad
        
    nuevas_imagenes = request.files.getlist('act_imagen')

    nombres_nuevas_imagenes = []  
    for nueva_imagen in nuevas_imagenes:
        if nueva_imagen and allowed_file(nueva_imagen.filename):
            nuevo_nombre = secure_filename(nueva_imagen.filename)
            nueva_ruta = os.path.join(app.config['UPLOAD_FOLDER_2'], nuevo_nombre)
            nueva_imagen.save(nueva_ruta)
            nombres_nuevas_imagenes.append(nuevo_nombre)

    if nombres_nuevas_imagenes:
        imagenes_actuales = catalogo.imagen.split(",") if catalogo.imagen else []
        imagenes_actuales.extend(nombres_nuevas_imagenes)
        catalogo.imagen = ",".join(imagenes_actuales)
    db.session.add(catalogo)
    db.session.commit()

    return redirect(url_for('catalogo'))

#login

@app.get("/login")
def login():
    return render_template('login/login.html')
@app.post("/login_session")
def login_session():
    username = request.form['username']
    password = request.form['password']
    user = tbl_admin.query.filter_by(correo=username, psw=password).first()
    if user:
        # Inicio de sesión exitoso
        session['administrador_id'] = user.id_admin
        return redirect(url_for('dashboard'))
    else:
        # Las credenciales son incorrectas
        error = "Credenciales incorrectas. Inténtalo de nuevo."
        return render_template('login/login.html', error=error)
#Ruta para Cerrar Sesion
@app.route('/logout')
@login_required
def logout():
    session.pop('administrador_id', None)  # Elimina la variable de sesión
    return redirect(url_for('login'))  # Redirige al usuario a la página de inicio de sesión

if __name__ == '__main__':
    app.run("0.0.0.0", 8081, debug=True)
