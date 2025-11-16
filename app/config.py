# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-segura'
    
    # ✅ CONFIGURACIÓN SQLITE - REEMPLAZA LA CONFIGURACIÓN DE SQL SERVER
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "..", "data", "salarios.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False