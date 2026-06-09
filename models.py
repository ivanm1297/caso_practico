from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class tbl_admin(db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)
    nombre_admin = db.Column(db.String(80), nullable=False)
    ap_admin = db.Column(db.String(80), nullable=False)
    am_admin = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    imagen = db.Column(db.String(80), nullable=False)
    psw = db.Column(db.String(80), nullable=False)    


class tbl_carrusel(db.Model):
    id_imagen = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(200))
    
class tbl_catal_autos(db.Model):
    id_auto = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    anio = db.Column(db.String(80), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    marca = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(1200), unique=True, nullable=False)
    precio_unidad = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(20000), nullable=False)
    

